from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

from flaskr.auth import login_required
from flaskr.db import get_db, get_current_stocks, get_user_stocks, sell_stock, purchase_stock, get_companies, \
    get_company_info, get_stock_graph, get_leaderboard

bp = Blueprint('interactions', __name__)


@bp.route('/')
def index():
    TopStocks = get_current_stocks()
    user_id = session.get('user_id')
    yourStocks = get_user_stocks(g.user)
    leaderboard = get_leaderboard()
    names = [i[0] for i in leaderboard]
    scores = [i[1] for i in leaderboard]
    value = 0
    if (yourStocks != []):
        for i in yourStocks:
            value += i[4]
    return render_template('user/index.html', TopStocks=TopStocks, yourStocks=yourStocks, value=value, names=names, scores=scores)


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
    value = round(value, 2)
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


@bp.route('/companies', methods=('GET', 'POST'))
@login_required
def companies():
    company_names = get_companies()
    if request.method == 'POST':
        companyId = request.form['companyId']
        return redirect(url_for('interactions.company_page', companyId=companyId))
    return render_template('user/companies.html', company_names=company_names)


@bp.route('/companies/<companyId>')
@login_required
def company_page(companyId):
    comp_info = get_company_info(companyId)
    print(comp_info)
    companyName = comp_info[0][0]
    stockTicker = comp_info[0][1]
    stockPrice = comp_info[0][2]

    graph_points = get_stock_graph(companyId)
    print(graph_points)
    x_points = [x[0] for x in graph_points]
    y_points = [y[1] for y in graph_points]

    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.plot(x_points, y_points, marker='o')
    plt.gcf().autofmt_xdate()
    plt.xlabel("Date")
    plt.ylabel("Stock Price")
    plt.title("Stock Prices for {}".format(companyName))
    plt.savefig("flaskr/static/{}_stockplot.png".format(companyName))
    plt.close()
    imagePath = "/static/{}_stockplot.png".format(companyName)
    return render_template('user/companyPage.html', companyName=companyName, stockTicker=stockTicker,
                           imagePath=imagePath, stockPrice=stockPrice)


@bp.route('/nothing')
def nothing():
    return render_template('extras/default.html')
