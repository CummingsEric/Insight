import mysql.connector

import click
import sqlalchemy as sqla
from flask import current_app, g
from flask.cli import with_appcontext

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from flaskr.orm_classes import Company

@click.command('start_db')
@with_appcontext
def start_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Successfully connected to the database')


def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(user='root', password="stonks", host='34.68.197.158',
                                       database='insight_database', autocommit=True)
    return g.db

def get_session():
    if 'session' not in g:
        engine = create_engine('mysql+mysqldb://root:stonks@34.68.197.158/insight_database')
        Session = sessionmaker(bind=engine)
        g.session = Session()

    return g.session


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    session = get_session()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(start_db_command)


def get_current_stocks():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT C.Name, C.StockTicker, P.Price, P.StockId From Company C JOIN (SELECT S.StockId, S.CompanyId, S.Price '
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
        'Select  Name, StockTicker, Amount, Price, round((Amount * Price),2) as TotalValue FROM '
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

def get_leaderboard():
    db = get_db()
    cursor = db.cursor()
    leaderboard = None
    query = (
        'Select UserId, sum(TotalValue) as TotalValue From'
        '(Select UserId, round((Amount * Price),2) as TotalValue FROM '
        '(Select UserId, StockId, Amount From Portfolio) A JOIN '
        '(SELECT P.StockId, C.Name, C.StockTicker, P.Price From Company C JOIN (SELECT S.StockId, S.CompanyId, S.Price '
        'FROM Stock S JOIN '
        '(SELECT StockId, Max(date) as Date '
        'FROM Stock '
        'GROUP BY StockId) F '
        'ON S.Date = F.Date and S.StockId = F.StockId) P ON C.CompanyId = P.CompanyId) B '
        'ON A.StockId = B.StockId) T '
        'Group By UserId '
        'Order By TotalValue DESC '
        'Limit 5;')
    cursor.execute(query)
    leaderboard = cursor.fetchall()
    cursor.close()
    return leaderboard


def purchase_stock(stockId, userId, amount):
    try:
        db = get_db()
        cursor = db.cursor(buffered=True)

        # Transaction is Read Committed because this transaction should be accurate, but we also want to know if the
        # amount has been updated so that it is accurately reflected, unlike repeatable read which won't update until
        # the transaction is over.
        db.start_transaction(isolation_level='READ COMMITTED')

        query = """
        SELECT UserId, StockId FROM Portfolio
        WHERE UserId=%s AND StockId=%s;
        """
        cursor.execute(query, (userId, stockId,))
        result = cursor.fetchall()
        if len(result) == 0:
            query = ('INSERT INTO Portfolio (UserId, StockId, Amount) VALUES (%s,%s,%s);')
            cursor.execute(query, (userId,stockId,amount,))
        else:
            query = ('UPDATE Portfolio '
                     'SET Amount = Amount + %s '
                     'WHERE UserId=%s and StockId=%s;')
            cursor.execute(query, (amount, userId, stockId,))
        db.commit()
    except mysql.connector.errors.Error as e:
        db.rollback()
        print("Rolling back...")
        print(e)
    finally:
        cursor.close()


def sell_stock(stockId, userId, amount):
    # find the amount of stock the user has
    try:
        db = get_db()
        cursor = db.cursor(buffered=True)

        # Transaction is Read Committed because this transaction should be accurate, but we also want to know if the
        # amount has been updated so that it is accurately reflected, unlike repeatable read which won't update until
        # the transaction is over.
        db.start_transaction(isolation_level='READ COMMITTED')

        query = ('SELECT Amount FROM Portfolio WHERE UserId=%s and StockId=%s;')
        cursor.execute(query, (userId, stockId))
        owned = cursor.fetchall()[0][0]
        namount = -int(amount)
        if (owned + namount > 0):
            # only sell if they have enough

            # query = ('INSERT INTO Transactions (UserId, StockId, Delta) VALUES (%s,%s,%s);')
            # cursor.execute(query, (userId, stockId, namount,))
            query = ('UPDATE Portfolio '
                     'SET Amount = Amount - %s '
                     'WHERE UserId=%s and StockId=%s;')
            cursor.execute(query, (amount, userId, stockId,))
        elif owned + namount == 0:
            query = """
            DELETE FROM Portfolio
            WHERE UserId=%s AND StockId=%s;
            """
            cursor.execute(query, (userId, stockId,))
        db.commit()
        print("Transaction complete")
    except mysql.connector.errors.Error as e:
        db.rollback()
        print("Rolling back...")
        print(e)
    finally:
        cursor.close()


def get_companies():
    orm_session = get_session()
    result = orm_session.query(Company.Name, Company.CompanyId).order_by(Company.Name).all()
    return result


def get_company_info(companyId):
    db = get_db()
    cursor = db.cursor()
    query = """
    SELECT c.Name, c.StockTicker, s.Price
    FROM Company c JOIN Stock s ON c.CompanyId = s.CompanyId
    WHERE c.CompanyId = %s
    ORDER BY s.Date DESC
    LIMIT 1;
    """
    cursor.execute(query, (companyId,))
    result = cursor.fetchall()
    return result


def get_stock_graph(company_id):
    try:
        db = get_db()
        cursor = db.cursor(buffered=True)

        # Transaction is Read committed because this transaction should be accurate, but it doesn't need to be higher
        # because we don't need to worry about subsequent reads.
        db.start_transaction(isolation_level='READ COMMITTED', readonly=True)

        sql_statement = """
        SELECT Date, Price
        FROM Stock
        WHERE CompanyId=%s
        ORDER BY Date DESC
        LIMIT 5;
        """

        cursor.execute(sql_statement, (company_id,))
        db.commit()
        result = cursor.fetchall()
        print("Transaction committed.")
        return result
    except mysql.connector.errors.Error as e:
        db.rollback()
        print("Rolling back...")
        print(e)
    finally:
        cursor.close()
