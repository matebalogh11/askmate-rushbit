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
