
from binascii import hexlify
from datetime import datetime, timedelta
from functools import wraps
from hashlib import sha512
from os import urandom
from string import ascii_lowercase, digits

from flask import (abort, flash, redirect, render_template, request, session,
                   url_for)

import db
import helper
from answers_logic import valid_answer_id
from comments_logic import valid_comment_id
from questions_logic import valid_question_id


def login_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_name' in session:
                if role == "user":
                    if session.get('role') in ('user', 'admin'):
                        return func(*args, **kwargs)
                elif role == "admin":
                    if session.get('role') == 'admin':
                        return func(*args, **kwargs)
                elif role == "author":
                    url_parts = request.url.split('/')
                    entry_id = url_parts[4]
                    entry_type = url_parts[3]
                    owner = get_author(entry_type, entry_id, is_accept_answer(url_parts))
                    if session.get('user_name') == owner or session.get('role') == 'admin':
                        return func(*args, **kwargs)

                flash("You requested a restricted operation. Permission denied.", "error")
                return redirect(url_for('show_index'))
            else:
                flash("You are not logged in. Please log in first.", "error")
                return redirect(url_for('login'))
        return wrapper
    return decorator


def not_loggedin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_name' not in session:
            return func(*args, **kwargs)
        else:
            flash("Cannot access page. You are already logged in.", "error")
            return redirect(url_for("show_index"))
    return wrapper


def make_session_permanent(app):
    """Makes session permanent, set lifetime to 5 minutes, refresh upon each request."""
    if 'user_name' in session:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)


def check_for_valid_request():
    """Check if HTTP request is any of the allowed request methods,
    and if function does not exist for requested URL, then abort.
    """
    allowed_req_methods = ('GET', 'POST')
    if request.method not in allowed_req_methods:
        abort(405)
    if request.endpoint is None:
        abort(404)


def check_for_valid_id_variable():
    """Check whether requested URL has valid id variable in it, found in corresponding table."""
    url_parts = request.url.split('/')
    if len(url_parts) >= 5:
        entry_type = url_parts[3]
        entry_id = url_parts[4]
        if entry_type == "question":
            if not valid_question_id(entry_id):
                return abort(404)
        if entry_type == "answer":
            if not valid_answer_id(entry_id):
                return abort(404)
    if len(url_parts) >= 6 and entry_type == "comment":
        q_id = url_parts[5]
        if not valid_comment_id(entry_id) or not valid_question_id(q_id):
            return abort(404)


def register_account():
    """Register account after validation and hashing process."""
    user_name = request.form.get('user_name')
    pw_1 = request.form.get('password_1')
    pw_2 = request.form.get('password_2')
    user_names = get_user_names()

    if user_name in user_names:
        flash("User name already exists. Please choose another one.", "error")
        return redirect(url_for('registration'))

    if not valid_user_name(user_name):
        flash("Invalid user name. Should be 8-16 characters long, contain only letters and numbers.", "error")
        return redirect(url_for('registration'))

    if not valid_password(pw_1, pw_2):
        flash("Invalid password or not matching. 8-16 characters long passwords \
        containing only letters and numbers are accepted.", "error")
        return redirect(url_for('registration'))

    create_account(user_name, pw_1)
    flash("Successful registration. Please log in.", "success")
    return redirect(url_for('login'))


def login_user():
    """Login user after validating credentials. Store user name and role in session cookies."""
    if not valid_credentials(request.form):
        flash("Invalid credentials.", "error")
        return redirect(url_for('login'))

    user_name = request.form['user_name']
    session['user_name'] = user_name
    session['role'] = get_user_role(user_name)

    return redirect(url_for('show_index'))


def logout_user():
    """Logout user, removing session cookies accordingly."""
    session.pop('user_name', None)
    session.pop('role', None)

    flash("You are now logged out.", "success")
    return redirect(url_for('show_index'))


def get_user_names():
    """Return user names."""
    SQL = """SELECT user_name FROM users;"""
    data = None
    fetch = "col"
    user_names = db.run_statements(((SQL, data, fetch),))[0]
    return user_names


def valid_user_name(user_name):
    """Return True if user name string is valid.
    Valid characters: lowercase, digits, underscore.
    """
    if len(user_name) >= 8 and len(user_name) <= 16:
        for char in user_name:
            if char not in (ascii_lowercase + digits + '_'):
                break
        else:
            return True
    return False


def valid_password(password_1, password_2):
    """Return True if password string is valid.
    Valid characters: lowercase, uppercase, digits.
    """
    if password_1 == password_2:
        if len(password_1) >= 8 and len(password_1) <= 16:
            for char in password_1.lower():
                if char not in (ascii_lowercase + digits):
                    break
            else:
                return True
    return False


def create_account(user_name, pw):
    """Create new account upon successful registration, insert into user table."""
    salt = generate_salt()
    password = hash_password(pw, salt)
    role = "user"
    reg_date = helper.create_timestamp()
    reputation = 0

    SQL = """INSERT INTO users
                (user_name, password, salt, role, reputation, reg_date)
             VALUES (%s, %s, %s, %s, %s, %s);"""
    data = (user_name, password, salt, role, reputation, reg_date)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def hash_password(password, salt):
    """Return hashed password. Before hashing,
    combines password with salt byte-string.
    """
    salted_password = bytes(password + salt, "utf-8")
    hashed = sha512()
    hashed.update(salted_password)
    return hashed.hexdigest()


def generate_salt():
    """Return 16 bytes long random bytes object."""
    return str(hexlify(urandom(16)), 'utf-8')


def valid_credentials(form):
    """Return True if input credentials are valid."""
    user_names = get_user_names()
    user_name = form.get('user_name')
    if user_name in user_names:
        user_salt = get_user_salt(user_name)
        stored_password = get_stored_password(user_name)
        if hash_password(form.get('password'), user_salt) == stored_password:
            return True
    return False


def get_user_salt(user_name):
    SQL = """SELECT salt FROM users WHERE user_name = %s;"""
    data = (user_name,)
    fetch = "cell"
    salt = db.run_statements(((SQL, data, fetch),))[0]
    return salt


def get_stored_password(user_name):
    """Return the stored hash password for certain user."""
    SQL = """SELECT password FROM users WHERE user_name = %s;"""
    data = (user_name,)
    fetch = "cell"
    stored_user_pw = db.run_statements(((SQL, data, fetch),))[0]
    return stored_user_pw


def get_user_role(user_name):
    """Return role for user_name."""
    SQL = """SELECT role FROM users WHERE user_name = %s;"""
    data = (user_name,)
    fetch = "cell"
    role = db.run_statements(((SQL, data, fetch),))[0]
    return role


def get_author(entry_type, entry_id, is_accept_answer):
    """Return author from entry_type table where entry_id."""
    if entry_type not in ('question', 'answer', 'comment'):
        return None

    try:
        entry_id = int(entry_id)
    except ValueError:
        return None

    fetch = "cell"

    if is_accept_answer:
        q_id = get_q_id_by_a_id(entry_id)
        SQL = """SELECT user_name FROM question WHERE id = %s;"""
        data = (q_id,)
    else:
        SQL = """SELECT user_name FROM {} WHERE id = %s;""".format(entry_type)
        data = (entry_id,)

    author = db.run_statements(((SQL, data, fetch),))[0]
    return author


def is_accept_answer(url_parts):
    """Return True if certain part of the url has 'accept' substring in it."""
    if len(url_parts) >= 7:
        if "accept" in url_parts[6]:
            return True
    return False


def get_q_id_by_a_id(answer_id):
    """Return question_id based on given answer_id."""
    SQL = """SELECT question_id FROM answer WHERE id = %s;"""
    data = (answer_id,)
    fetch = "cell"

    question_id = db.run_statements(((SQL, data, fetch),))[0]
    return question_id
