import telebot
from telebot import types
import dbfunctions
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot('6587283552:AAFTgkV3fG0JcpuwsvZwysHTIx0uJN2DgU0')


@bot.message_handler(commands=["start"])  # начало кода
def handle_start(message):
    logging.info(f"Пользователь {message.chat.id} начал работу с ботом.")
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row('Начать заново')
    user_markup.row('Проверить заказ')
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    callback_button = types.InlineKeyboardButton(text="Нажмите чтобы увидеть наше меню", callback_data="menu")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, f'Добро пожаловать в McDonalds, {message.from_user.first_name}!', reply_markup=user_markup)
    bot.send_message(message.chat.id, "Пожалуйста, выберите опцию ниже, чтобы продолжить", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def query_text(call):
    if call.message:
        logging.info(f"Получен запрос callback от пользователя {call.message.chat.id} с данными {call.data}")
        if call.data == "menu":  # показывает меню
            food_list = dbfunctions.show_menu()
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            for item in food_list:
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(types.InlineKeyboardButton(text='Добавить в корзину', callback_data=str(item)))
                bot.send_message(call.message.chat.id, item)
                bot.send_photo(call.message.chat.id, dbfunctions.show_photo(item))
                bot.send_message(call.message.chat.id, dbfunctions.show_descr(item))
                bot.send_message(call.message.chat.id, 'Цена: ' + str(dbfunctions.show_price(item)) + ' тг', reply_markup=keyboard)

        elif call.data in dbfunctions.show_menu():  # добавляет товары в корзину
            id = call.from_user.id
            price = dbfunctions.show_price(call.data)
            dbfunctions.addtocart(id, call.data, price)
            x = str(call.data) + ' (1) добавлено в корзину'
            bot.send_message(call.message.chat.id, x)

        elif call.data == 'location':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton(text="Отправить как текст", callback_data='confirmed'))
            bot.send_message(call.message.chat.id, "Отправьте нам местоположение, куда вы хотели бы, чтобы мы доставили ваш заказ.", reply_markup=keyboard)
            dbfunctions.save_order(call.from_user.id, 'loc_text')

        elif call.data == 'confirmed':
            dbfunctions.save_order(call.from_user.id, 'Confirmed')
            bot.send_message(call.message.chat.id, "Спасибо за ваш заказ!")
            dbfunctions.empty_cart(call.from_user.id)


@bot.message_handler(content_types=['location'])  # обрабатывает местоположение
def handle_location(message):
    logging.info(f"Получено местоположение от пользователя {message.from_user.id}")
    if dbfunctions.show_status(message.from_user.id) == 'loc':
        bot.send_message(message.from_user.id, "Выбранное местоположение сохранено. Заказ в пути.")
        print(message.location)
        dbfunctions.location(message.from_user.id, str(message.location))
        dbfunctions.status('Confirmed', message.chat.id)


@bot.message_handler(commands=["checkout"])
def handle_checkout(message):
    logging.info(f"Пользователь {message.from_user.id} запросил оформление заказа.")
    dbfunctions.showcart(message.from_user.id)
    order = dbfunctions.showcart(message.from_user.id)
    bot.send_message(message.from_user.id, "Ваш заказ:")
    for item in order:
        bot.send_message(message.from_user.id, item[0])
    bot.send_message(message.from_user.id, "Итог: " + str(dbfunctions.summary(message.from_user.id)) + ' тг.')

    # Запрашиваем местоположение в текстовом виде
    bot.send_message(message.chat.id, 'Хотели бы вы завершить заказ? Отправьте ваше местоположение в текстовом виде:')
    bot.register_next_step_handler(message, handle_text_location)


# Новый обработчик для получения текстового местоположения
def handle_text_location(message):
    logging.info(f"Получено текстовое местоположение от пользователя {message.from_user.id}: {message.text}")

    # Сохраняем текстовое местоположение в файл
    with open('user_locations.txt', 'a') as file:
        file.write(f"User ID: {message.from_user.id}, Location: {message.text}\n")

    # Отправляем подтверждение и завершаем заказ
    bot.send_message(message.from_user.id, "Ваше местоположение сохранено. Спасибо за заказ!")
    dbfunctions.empty_cart(message.from_user.id)


@bot.message_handler(commands=["empty"])
def empty(message):
    logging.info(f"Пользователь {message.from_user.id} очистил корзину.")
    dbfunctions.empty_cart(message.from_user.id)
    bot.send_message(message.from_user.id, "Ваша корзина сейчас пуста")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    logging.info(f"Получено текстовое сообщение от пользователя {message.from_user.id}: {message.text}")
    if message.text == "Проверить заказ":  # корзина
        dbfunctions.showcart(message.from_user.id)
        order = dbfunctions.showcart(message.from_user.id)
        bot.send_message(message.from_user.id, "Ваш заказ:")
        for item in order:
            bot.send_message(message.from_user.id, item[0])
        bot.send_message(message.from_user.id, "Итог: " + str(dbfunctions.summary(message.from_user.id)) + ' тг')

        # Запрашиваем местоположение в текстовом виде
        bot.send_message(message.chat.id, 'Хотели бы вы завершить заказ? Отправьте ваше местоположение в текстовом виде:')
        bot.register_next_step_handler(message, handle_text_location)

    elif message.text == "Начать заново":  # перезапускает взаимодействие пользователя с ботом
        handle_start(message)
        dbfunctions.delete_order(message.from_user.id)


def error(update, context):
    logging.error(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    logging.info("Бот начал работу.")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Ошибка: {e}")