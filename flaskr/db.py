import mysql.connector

import click
from flask import current_app, g
from flask.cli import with_appcontext

@click.command('start_db')
@with_appcontext
def start_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Successfully connected to the database')

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(user='root', password="stonks", host='34.68.197.158', database='insight_database')
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(start_db_command)

def get_current_stocks():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT C.Name, C.StockTicker, P.Price From Company C JOIN (SELECT S.StockId, S.CompanyId, S.Price '
        'FROM Stock S JOIN '
        '(SELECT StockId, Max(date) as Date '
        'FROM Stock '
        'GROUP BY StockId) F '
        'ON S.Date = F.Date and S.StockId = F.StockId) P ON C.CompanyId = P.CompanyId '
        'ORDER BY P.Price DESC;'
    )
    TopStocks = cursor.fetchall()
    cursor.close()
    return TopStocks

def get_user_stocks(userId):
    db = get_db()
    cursor = db.cursor()
    user_id = userId
    yourStocks = None
    query = (
        'Select  Name, StockTicker, Amount, Price, (Amount * Price) as TotalValue FROM '
        '(Select StockId, Amount From Portfolio Where UserId=%s) A JOIN '
        '(SELECT P.StockId, C.Name, C.StockTicker, P.Price From Company C JOIN (SELECT S.StockId, S.CompanyId, S.Price '
        'FROM Stock S JOIN '
        '(SELECT StockId, Max(date) as Date '
        'FROM Stock '
        'GROUP BY StockId) F '
        'ON S.Date = F.Date and S.StockId = F.StockId) P ON C.CompanyId = P.CompanyId) B '
        'ON A.StockId = B.StockId;')
    cursor.execute(query, (user_id,))
    yourStocks = cursor.fetchall()
    cursor.close()
    return yourStocks

def purchase_stock(stockId, userId, amount):
    db = get_db()
    cursor = db.cursor()
    yourStocks = None
    #query = ('INSERT INTO Transactions (UserId, StockId, Delta) VALUES (%s,%s,%s);')
    #ursor.execute(query, (userId,stockId,amount,))
    query = ('UPDATE Portfolio '
             'SET Amount = Amount + %s '
             'WHERE UserId=%s and StockId=%s;')
    cursor.execute(query, (amount, userId, stockId,))
    cursor.close()
    return

def sell_stock(stockId, userId, amount):
    #find the amount of stock the user has
    db = get_db()
    cursor = db.cursor()
    query = ('SELECT Amount FROM Portfolio WHERE UserId=%s and StockId=%s;')
    cursor.execute(query, (userId, stockId))
    owned = cursor.fetchall()[0][0]
    namount = -amount
    if(owned+namount>=0):

    #only sell if they have enough

        #query = ('INSERT INTO Transactions (UserId, StockId, Delta) VALUES (%s,%s,%s);')
        #cursor.execute(query, (userId, stockId, namount,))
        query = ('UPDATE Portfolio '
                 'SET Amount = Amount - %s '
                 'WHERE UserId=%s and StockId=%s;')
        cursor.execute(query, (amount, userId, stockId,))
        cursor.close()
    return