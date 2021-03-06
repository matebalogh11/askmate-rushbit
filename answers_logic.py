
import os

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


def create_new_answer_no_image(message, question_id, user_name):
    """Return new answer with message from form, initialized without image."""
    init_time = helper.create_timestamp()
    init_votes = 0
    init_image = None
    accepted = False
    new_answer = [init_time, init_votes, question_id, message, init_image, accepted, user_name]
    return new_answer


def insert_answer(new_answer):
    """Insert new answer into answer table."""
    SQL = """INSERT INTO answer
             (submission_time, vote_number,question_id, message, image, accepted, user_name)
             VALUES (%s, %s, %s, %s, %s, %s, %s)
             RETURNING id, image;"""
    data = (new_answer[0], new_answer[1], new_answer[2],
            new_answer[3], new_answer[4], new_answer[5], new_answer[6])
    fetch = "one"

    answer_id, image = db.run_statements(((SQL, data, fetch),))[0]
    return answer_id, image


def update_answer_image(answer_id, previous_image, files):
    """Handles filesystem by uploading new images, deleting unused ones,
    also manages filenames stored in database.
    """
    image = files.get('a_image', None)
    image_status = None
    if image and image.filename:
        if helper.allowed_extension(image.filename):
            filename = "a_id_" + str(answer_id) + "_" + secure_filename(image.filename)
            image.save("static/uploads/" + filename)
            rename_answer_image(filename, answer_id)
            image_status = "uploaded"
            if previous_image:
                image_status = "updated"
                try:
                    os.remove("static/uploads/" + previous_image)
                except FileNotFoundError:
                    pass
        else:
            image_status = "not_allowed_ext"
    return image_status


def rename_answer_image(filename, answer_id):
    """Rename answer image and question_id as tuple from answer table."""
    SQL = """UPDATE answer SET image = %s WHERE id = %s;"""
    data = (filename, answer_id)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def get_answer_image_and_q_id(answer_id):
    """Return answer image and question_id based on answer_id."""
    SQL = """SELECT image, question_id FROM answer WHERE id = %s;"""
    data = (answer_id,)
    fetch = "one"

    a_img_and_id = db.run_statements(((SQL, data, fetch),))[0]
    return a_img_and_id


def get_answer_details(answer_id):
    """Return whole answer with all details where answer_id found."""
    SQL = """SELECT id, submission_time, vote_number, question_id, message, image
             FROM answer WHERE id = %s;"""
    data = (answer_id,)
    fetch = "one"

    answer = db.run_statements(((SQL, data, fetch),))[0]
    return answer


def update_answer_message(answer_id, message):
    """Update answer message in answer tabel where answer_id found."""
    SQL = """UPDATE answer SET message = %s WHERE id = %s;"""
    data = (message, answer_id)
    fetch = None

    db.run_statements(((SQL, data, fetch),))


def remove_answer_and_get_q_id(answer_id):
    """Remove answer record and its image,
    then return its question_id.
    """
    image_to_delete, question_id = get_answer_image_and_q_id(answer_id)
    if image_to_delete:
        try:
            os.remove("static/uploads/" + image_to_delete)
        except (FileNotFoundError, TypeError):
            pass

    delete_answer_by_id(answer_id)
    return question_id


def delete_answer_by_id(answer_id):
    """Deletes answer by answer ID."""
    SQL = """DELETE FROM answer WHERE id = %s;"""
    data = (answer_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def delete_a_image(answer_id):
    """Delete image belonging to an answer with answer_id."""
    current_image = get_answer_image(answer_id)
    if current_image:
        remove_answer_image(answer_id)
        try:
            os.remove("static/uploads/" + current_image)
        except FileNotFoundError:
            pass


def get_answer_image(answer_id):
    """Return answer image name."""
    SQL = """SELECT image FROM answer WHERE id = %s;"""
    data = (answer_id,)
    fetch = "one"
    q_img = db.run_statements(((SQL, data, fetch),))[0][0]
    return q_img


def remove_answer_image(answer_id):
    """Remove answer image by updating database, setting image to NULL."""
    SQL = """UPDATE answer SET image = NULL WHERE id = %s;"""
    data = (answer_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def get_question_id(answer_id):
    """Return question_id based on answer_id."""
    SQL = """SELECT question_id FROM answer WHERE id = %s;"""
    data = (answer_id,)
    fetch = "one"

    question_id = db.run_statements(((SQL, data, fetch),))[0][0]
    return question_id


def mark_accepted_exclusively(answer_id, question_id):
    """Mark an answer accepted. De-select any previously
    marked answer, since only one accepted question might remain.
    """
    other_answer_ids = get_other_answer_ids(answer_id, question_id)
    if not other_answer_ids:
        other_answer_ids = (None,)

    SQL1 = """UPDATE answer SET accepted = true WHERE id = %s;"""
    data1 = (answer_id,)
    SQL2 = """UPDATE answer SET accepted = false WHERE accepted = true and id IN %s;"""
    data2 = (tuple(other_answer_ids),)
    fetch = None
    db.run_statements(((SQL1, data1, fetch), (SQL2, data2, fetch)))


def get_other_answer_ids(answer_id, question_id):
    """Return all answer ids for question with question_id, other than answer_id."""
    SQL = """SELECT id FROM answer WHERE question_id = %s AND id != %s;"""
    data = (question_id, answer_id)
    fetch = "col"
    other_answer_ids = db.run_statements(((SQL, data, fetch),))[0]
    return other_answer_ids


def remove_accept_mark(answer_id):
    """Remove accept mark from answer."""
    SQL = """UPDATE answer SET accepted = false WHERE accepted = true and id = %s;"""
    data = (answer_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))
