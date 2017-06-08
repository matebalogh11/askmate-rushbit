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
