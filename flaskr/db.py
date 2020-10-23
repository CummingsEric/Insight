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