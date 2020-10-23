from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db, get_current_stocks, get_user_stocks, sell_stock, purchase_stock

bp = Blueprint('interactions', __name__)

@bp.route('/')
def index():
    TopStocks = get_current_stocks()
    user_id = session.get('user_id')
    yourStocks = get_user_stocks(g.user)
    value = 0
    if(yourStocks!=[]):
        for i in yourStocks:
            value+=i[4]
    return render_template('user/index.html', TopStocks=TopStocks, yourStocks=yourStocks, value=value)

@bp.route('/buysell')
@login_required
def buysell():
    TopStocks = get_current_stocks()
    user_id = session.get('user_id')
    yourStocks = get_user_stocks(g.user)
    value = 0
    if (yourStocks != []):
        for i in yourStocks:
            value += i[4]
    return render_template('user/buysell.html', TopStocks=TopStocks, yourStocks=yourStocks, value=value)

@bp.route('/buy', methods=('GET', 'POST'))
def buy():
    if request.method == 'POST':
        stockId = request.form['stockId']
        amount = request.form['amount']
        purchase_stock(stockId, g.user, amount)
    return redirect(url_for('interactions.buysell'))

@bp.route('/sell', methods=('GET', 'POST'))
def sell():
    if request.method == 'POST':
        stockId = request.form['stockId']
        amount = request.form['amount']
        sell_stock(stockId, g.user, amount)
    return redirect(url_for('interactions.buysell'))

@bp.route('/companies')
@login_required
def companies():
    return render_template('user/companies.html')

@bp.route('/nothing')
def nothing():
    return render_template('extras/default.html')