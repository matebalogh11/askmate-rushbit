from psycopg2 import DatabaseError
import db
import helper


def change_reputation_q(question_id, direction):
    """Update user reputation if a question of theirs is voted on."""
    if direction == "up":
        amount = 5
    elif direction == "down":
        amount = -2
    SQL = """UPDATE users
            SET reputation = reputation + %s
            FROM question
            WHERE users.user_name = question.user_name AND question.id = %s;"""
    data = (amount, question_id)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def change_reputation_a(answer_id, direction, acc=None):
    """Update user reputation if an answer of theirs is voted on or accepted."""
    if acc:
        if direction == "up":
            amount = 15
        elif direction == "down":
            amount = -15
    elif direction == "up":
        amount = 10
    elif direction == "down":
        amount = -2
    SQL = """UPDATE users
            SET reputation = reputation + %s
            FROM answer
            WHERE users.user_name = answer.user_name AND answer.id = %s;"""
    data = (amount, answer_id)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def get_user_list(criterium, order):
    """List all user infromation except id, password and salt
    in a table on the user_list page.
    """
    valid_criterium = ("user_name", "role", "reputation", "reg_date", "q_count", "a_count", "c_count", )
    valid_order = ("asc", "desc")

    if criterium not in valid_criterium or order not in valid_order:
        criterium = "role"
        order = "asc"

    SQL = """SELECT u.id, u.user_name, u.role, u.reputation, u.reg_date,
            (SELECT COUNT(q.user_name) FROM question q WHERE q.user_name = u.user_name) AS q_count,
            (SELECT COUNT(a.user_name) FROM answer a WHERE a.user_name = u.user_name) AS a_count,
            (SELECT COUNT(c.user_name) FROM comment c WHERE c.user_name = u.user_name) AS c_count
            FROM users u
            ORDER BY {} {};""".format(criterium, order)
    data = None
    fetch = "all"

    users = db.run_statements(((SQL, data, fetch),))
    return users


def valid_user(user_id):
    """Check whether the user is in the tabe and return the name."""
    SQL = """SELECT user_name FROM users WHERE id = %s;"""
    data = (user_id,)
    fetch = "cell"
    try:
        user_name = db.run_statements(((SQL, data, fetch),))[0]
    except(DatabaseError, TypeError):
        return False
    return user_name


def valid_user_by_name(user_name):
    """Check whether the user is in the tabe and return the name."""
    SQL = """SELECT id FROM users WHERE user_name = %s;"""
    data = (user_name,)
    fetch = "cell"
    try:
        user_id = db.run_statements(((SQL, data, fetch),))[0]
    except(DatabaseError, TypeError):
        return False
    return True


def fetch_user_detail(user_name):
    """Fetch all the data for a specific user."""

    SQL_c = """SELECT question_id, answer_id, message, submission_time, edited_count
               FROM comment
               WHERE user_name = %s;"""

    SQL_a = """SELECT question_id, id, submission_time, vote_number,  message, accepted
               FROM answer
               WHERE user_name = %s;"""

    SQL_q = """SELECT id, title, message, answer_count, submission_time, view_number, vote_number
               FROM question
               WHERE user_name = %s;"""

    data = (user_name,)
    fetch = "all"
    user_details = db.run_statements(((SQL_q, data, fetch), (SQL_a, data, fetch), (SQL_c, data, fetch)))

    question = user_details[0]
    answer = user_details[1]
    comment = user_details[2]

    return question, answer, comment


def delete_user_and_get_name(user_id):
    """Delete user from users table based on user_id."""
    SQL1 = """SELECT user_name FROM users WHERE id = %s;"""
    fetch1 = "cell"
    SQL2 = """DELETE FROM users WHERE id = %s;"""
    fetch2 = None
    data = (user_id,)

    user_name = db.run_statements(((SQL1, data, fetch1), (SQL2, data, fetch2)))[0]
    return user_name
