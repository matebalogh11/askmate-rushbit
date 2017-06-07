from psycopg2 import DatabaseError
import db
import helper


def insert_account(form):
    user_name = form['username']
    pw = form['password']
    pw2 = form['confirm_password']
    salt = "asdfads"
    role = "user"
    reputation = 0
    reg_date = helper.create_timestamp()

    SQL = """INSERT INTO users
             (user_name, password, salt, role, reputation, reg_date)
             VALUES (%s, %s, %s, %s, %s, %s, %s)"""
