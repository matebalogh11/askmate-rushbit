
import db
import helper


def retrieve_comments(question_id, answers):
    """Return comments for question and each answer."""
    SQL1 = """SELECT * FROM comment WHERE question_id = %s ORDER BY submission_time DESC;"""
    data1 = (question_id,)
    fetch = "all"

    if answers:
        SQL2 = """SELECT * FROM comment WHERE answer_id IN %s ORDER BY submission_time DESC;"""
        answer_ids = tuple(answer[0] for answer in answers)
        data2 = (answer_ids,)
        q_comments, a_comments = db.run_statements(((SQL1, data1, fetch), (SQL2, data2, fetch)))
    else:
        q_comments = db.run_statements(((SQL1, data1, fetch),))[0]
        a_comments = None

    return q_comments, a_comments


def edit_comment(new_comment, comment_id):
    """Update comment with new message, refreshing edited_count and submission_time."""
    submission_time = helper.create_timestamp()
    SQL = """UPDATE comment SET message = %s,
                                edited_count = edited_count + 1,
                                submission_time = %s
             WHERE id = %s;"""
    data = (new_comment, submission_time, comment_id)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def insert_comment(question_id, answer_id, message):
    """Initialize comment and insert into comment table."""
    init_time = helper.create_timestamp()
    init_edit = 0
    comment = (question_id, answer_id, message, init_time, init_edit)

    SQL = """INSERT INTO comment (question_id, answer_id,
                                    message, submission_time, edited_count)
            VALUES (%s, %s, %s, %s, %s);"""
    data = (question_id, answer_id, message, init_time, init_edit)
    fetch = None
    db.run_statements(((SQL, data, fetch),))
