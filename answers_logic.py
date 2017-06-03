
from psycopg2 import DatabaseError
from werkzeug.utils import secure_filename

import db
import helper


def valid_answer_id(answer_id):
    """Return True if answer_id found in answer table."""
    SQL = """SELECT id FROM answer WHERE id = %s;"""
    data = (answer_id,)
    fetch = "one"
    try:
        found_id = db.run_statements(((SQL, data, fetch),))[0][0]
    except (DatabaseError, TypeError):
        return False
    return True


def valid_answer_message(a_form):
    """Answer message must be at least 10 characters long to return True, else False."""
    answer_message = len(a_form.get("message", ''))
    if answer_message >= 10:
        return True
    return False


def update_answer_counter(question_id, operation):
    """Add 1 to answer counter of question with question_id,
    or reduce counter by one, depending on operation.
    """
    number = 1 if operation == "ADD" else 0
    if number:
        SQL = """UPDATE question SET answer_count = answer_count + 1 WHERE id = %s;"""
    else:
        SQL = """UPDATE question SET answer_count = answer_count - 1 WHERE id = %s;"""

    data = (question_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def create_new_answer_no_image(message, question_id):
    """Return new answer with message from form, initialized without image."""
    init_time = helper.create_timestamp()
    init_votes = 0
    init_image = None
    new_answer = [init_time, init_votes, question_id, message, init_image]
    return new_answer


def insert_answer(new_answer):
    """Insert new answer into answer table."""
    SQL = """INSERT INTO answer
             (submission_time, vote_number,question_id, message, image)
             VALUES (%s, %s, %s, %s, %s)
             RETURNING id, image;"""
    data = (new_answer[0], new_answer[1], new_answer[2],
            new_answer[3], new_answer[4])
    fetch = "one"

    answer_id, image = db.run_statements(((SQL, data, fetch),))[0]
    return answer_id, image


def update_answer_image(answer_id, files):
    """Update path to answer image and upload file to filesystem (/static/uploads).
    Validated server-side if file has been really sent with HTTP request
    and if extension is valid.
    @answer list: id(str), unix_timestamp(int), votes(int), question_id(str), message(str), image_path(str).
    @files dict: a_image key is the only expected key.
    @return str: status to know what message should be flashed to user.
    """
    image = files.get('a_image', None)
    image_status = None
    if image and image.filename:
        if helper.allowed_extension(image.filename):
            filename = 'a_id_' + str(answer_id) + "_" + secure_filename(image.filename)
            image.save("static/uploads/" + filename)
            rename_answer_image(filename, answer_id)
            image_status = "uploaded"
        else:
            image_status = "not_allowed_ext"
    return image_status


def rename_answer_image(filename, answer_id):
    """Rename answer image in answer table."""
    SQL = """UPDATE answer SET image = %s WHERE id = %s;"""
    data = (filename, answer_id)
    fetch = None
    db.run_statements(((SQL, data, fetch),))
