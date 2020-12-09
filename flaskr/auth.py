import functools
from flaskr.orm_classes import User
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db, get_session

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        orm_session = get_session()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:
            if len(orm_session.query(User.UserId).filter(User.UserId == username).all()) > 0:
                error = 'User {} is already registered.'.format(username)

        if error is None:
            new_user = User(UserId=username, HashedPassword=password)
            orm_session.add(new_user)
            orm_session.commit()
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        orm_session = get_session()
        error = None
        user = orm_session.query(User).filter(User.UserId == username).first()

        if user is None:
            error = 'Incorrect username.'
        elif not user.HashedPassword == password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.UserId
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        orm_session = get_session()
        user = orm_session.query(User.UserId).filter(User.UserId == user_id).first()
        g.user = user[0]

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view