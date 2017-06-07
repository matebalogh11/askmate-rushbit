import db
from psycopg2 import DatabaseError


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
