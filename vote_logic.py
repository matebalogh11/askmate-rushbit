
import db


def vote_question(direction, question_id):
    """Manage vote count of question."""
    if direction == "up":
        increase_question_vote(question_id)
    elif direction == "down":
        decrease_question_vote(question_id)


def vote_answer(direction, answer_id):
    """Manage vote count of answer."""
    if direction == "up":
        increase_answer_vote(answer_id)
    elif direction == "down":
        decrease_answer_vote(answer_id)


def increase_question_vote(question_id):
    """Update question by increasing vote by one."""
    SQL = """UPDATE question SET vote_number = vote_number + 1 WHERE id = %s;"""
    data = (question_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def decrease_question_vote(question_id):
    """Update question by decreasing vote by one."""
    SQL = """UPDATE question SET vote_number = vote_number - 1 WHERE id = %s;"""
    data = (question_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def increase_answer_vote(answer_id):
    """Update answer by increasing vote by one."""
    SQL = """UPDATE answer SET vote_number = vote_number + 1 WHERE id = %s;"""
    data = (answer_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def decrease_answer_vote(answer_id):
    """Update answer by decreasing vote by one."""
    SQL = """UPDATE answer SET vote_number = vote_number - 1 WHERE id = %s;"""
    data = (answer_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))
