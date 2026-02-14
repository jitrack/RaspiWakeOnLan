"""Front routes – pages (login, dashboard, manifest)."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from config import ADMIN_PASSWORD, ADMIN_USERNAME
from auth import login_required

front = Blueprint('front', __name__)


@front.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('front.dashboard'))
        error = 'Invalid credentials'
    return render_template('login.html', error=error)


@front.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('front.login'))


@front.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')
