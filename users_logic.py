from psycopg2 import DatabaseError
import db
import helper


def change_reputation_q(question_id, direction):
    """Update user reputation if a question of theirs is voted on."""
    if direction == "up":
        amount = 5
    elif direction == "down":
        amount = -2
    SQL1 = """SELECT user_name FROM questions WHERE question_id = %s;"""
    data1 = (question_id,)
    fetch1 = "one"
    q_user_name = db.run_statements(((SQL1, data1, fetch1),))

    SQL2 = """UPDATE users SET reputation = (reputation + %s)
                WHERE users.user_name = %s;"""
    data2 = (amount, q_user_name)
    fetch2 = None
    db.run_statements(((SQL2, data2, fetch2),))


# once the accpeted answer functions is written, this funtion should be called
# within it with direction=None, acc=True
def change_reputation_a(answer_id, direction=None, acc=None):
    """Update user reputation if an answer of theirs is voted on or accepted."""
    if acc:
        amount = 15
    elif direction == "up":
        amount = 10votevote
    elif direction == "down":
        amount = -2
    SQL1 = """SELECT user_name FROM answers WHERE answer_id = %s;"""
    data1 = (answer_id,)
    fetch1 = "one"
    a_user_name = db.run_statements(((SQL1, data1, fetch1),))

    SQL2 = """UPDATE users SET reputation = (reputation + %s)
                WHERE users.user_name = %s;"""
    data2 = (amount, a_user_name)
    fetch2 = None
    db.run_statements(((SQL2, data2, fetch2),))
