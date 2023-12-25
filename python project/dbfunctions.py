import sqlite3
import const


"""Context manager

Usage:

...
with SqliteCursor(dbname) as cur:
    do_smth()
    ...
"""


class SqliteCursor:
    def __init__(self, dbname):
        self.connection = sqlite3.connect(dbname)

    def __enter__(self):
        return self.connection.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.connection.commit()
        except sqlite3.Error as e:
            print(e)
            self.connection.rollback()


def show_menu():
    with SqliteCursor(const.dbname) as cur:
        queryvar = "SELECT dish FROM menu"
        cur.execute(queryvar)
        all = cur.fetchall()
        return [e[0] for e in all]


def show_descr(item):
    with SqliteCursor(const.dbname) as cur:
        queryvar = "SELECT description FROM menu WHERE dish =:dish"
        cur.execute(queryvar, {"dish": item})
        all = cur.fetchall()
        # return [e[0] for e in all[0]] # or like that?
        return all[0][0]


def show_price(item):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    queryvar = "SELECT price FROM menu WHERE dish =:dish"
    c.execute(queryvar, {"dish": item})
    all = c.fetchall()
    lst = list()
    for e in all:
        e = e[0]
        lst.append(e)
    return lst[0]


def show_photo(item):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    queryvar = "SELECT picture FROM menu WHERE Dish =:dish"
    c.execute(queryvar, {"dish": item})
    all = c.fetchall()
    lst = list()
    for e in all:
        e = e[0]
        lst.append(e)
    return lst[0]


def addtocart(id, item, price):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    queryvar = "INSERT INTO cart VALUES(?,?,?)"
    c.execute(queryvar, (id, item, price))
    conn.commit()


def showcart(id):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    queryvar = "SELECT Dish FROM cart WHERE user =:user"
    c.execute(queryvar, {"user": id})
    return c.fetchall()


def summary(id):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    queryvar = "SELECT Price FROM cart WHERE user =:user"
    c.execute(queryvar, {"user": id})
    sum = 0
    for item in c.fetchall():
        sum += item[0]
    return sum


def empty_cart(id):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    queryvar = "DELETE from cart WHERE user =:user"
    c.execute(queryvar, {"user": id})
    conn.commit()


def save_order(id, status):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    queryvar = "INSERT INTO orders(user,status) VALUES(?,?)"
    c.execute(queryvar, (id, status))
    conn.commit()


def location(id, loc):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    # queryvar = "INSERT INTO orders(location) VALUES(?)"
    queryvar = "UPDATE orders SET location = (?) WHERE user = (?)"
    c.execute(queryvar,(loc,id))
    conn.commit()


def status(st, id):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    queryvar = "UPDATE orders SET status = (?) WHERE user = (?)"
    c.execute(queryvar,(st, id))
    conn.commit()


def show_status(id):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    queryvar = "SELECT status FROM Orders WHERE user =:user"
    c.execute(queryvar, {"user": id})
    return (c.fetchall()[0][0])


def delete_order(id):
    conn = sqlite3.connect('menu.db')
    c = conn.cursor()
    queryvar = "DELETE from Orders WHERE user =:user"
    c.execute(queryvar, {"user": id})
    conn.commit()