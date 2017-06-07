
from binascii import hexlify
from datetime import datetime
from hashlib import sha512
from os import urandom
from string import ascii_lowercase, digits

from flask import (abort, flash, redirect, render_template, request, session,
                   url_for)

import db
import helper


def register_account():
    """Register account after validation and hashing process."""
    user_name = request.form.get('user_name')
    user_names = get_user_names()
    pw_1 = request.form.get('password_1')
    pw_2 = request.form.get('password_2')
    if user_name in user_names:
        flash("User name already exists. Please choose another one.", "error")
        page = "registration"
        return page

    if valid_user_name(user_name):
        if valid_password(pw_1, pw_2):
            create_account(user_name, pw_1)
            flash("Successful registration. Please log in.", "success")
            page = "login"
            return page
        else:
            flash("Invalid password. Should be 8-16 characters long, contain only letters and numbers.", "error")
            page = "registration"
            return page
    else:
        flash("Invalid user name. Should be 8-16 characters long, contain only letters and numbers.", "error")
        page = "registration"
        return page


def login_user():
    """Login user after validating credentials. Store user name and role in session cookies."""
    if valid_credentials(request.form):
        user_name = request.form['user_name']
        session['user_name'] = user_name
        session['role'] = get_user_role(user_name)
        page = "show_index"
        return page
    else:
        flash("Invalid credentials.", "error")
        page = "login"
        return page


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
    role = db.run_statements(((SQL, data, "one"),))[0][0]
    return role
