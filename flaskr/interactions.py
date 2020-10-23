from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('interactions', __name__)

@bp.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT C.Name, C.StockTicker, P.Price From Company C JOIN (SELECT S.StockId, S.CompanyId, S.Price '
         'FROM Stock S JOIN '
         '(SELECT StockId, Max(date) as Date '
         'FROM Stock '
         'GROUP BY StockId) F '
         'ON S.Date = F.Date and S.StockId = F.StockId) P ON C.CompanyId = P.CompanyId;'
    )
    TopStocks = cursor.fetchall()
    user_id = session.get('user_id')
    yourStocks = None
    value = 0
    if user_id:
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

        for i in yourStocks:
            value+=i[4]
    return render_template('user/index.html', TopStocks=TopStocks, yourStocks=yourStocks, value=value)

@bp.route('/buysell')
def buysell():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT * FROM Company'
    )
    TopStocks = cursor.fetchall()
    return render_template('user/buysell.html')

@bp.route('/companies')
def companies():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT * FROM Company'
    )
    TopStocks = cursor.fetchall()
    return render_template('user/companies.html')