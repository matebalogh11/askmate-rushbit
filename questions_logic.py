
import os

from psycopg2 import DatabaseError
from werkzeug.utils import secure_filename

import db
import helper


def valid_request(q_form):
    """Return True if HTTP request was sent with at least 10
    characters long title and description, else False"""
    title_length = len(q_form.get('q_title', ''))
    desc_length = len(q_form.get('q_desc', ''))
    if title_length >= 10 and desc_length >= 10:
        return True
    return False


def create_new_question_no_image(q_form, user_name):
    """Create new question from successfully filled question form."""
    intial_views = 0
    initial_votes = 0
    empty_image = None
    initial_answer_count = 0
    new_question = [helper.create_timestamp(), intial_views, initial_votes,
                    q_form['q_title'], q_form['q_desc'],
                    empty_image, initial_answer_count, user_name]
    return new_question


def insert_question(new_question):
    """Insert new question into question table."""
    SQL = """INSERT INTO question
             (submission_time, view_number, vote_number, title, message, image, answer_count, user_name)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
             RETURNING id, image;"""
    data = (new_question[0], new_question[1], new_question[2], new_question[3],
            new_question[4], new_question[5], new_question[6], new_question[7])
    fetch = "one"
    results = db.run_statements(((SQL, data, fetch),))
    result = results[0]
    return result


def update_question_image(question_id, previous_image, files):
    """Handles filesystem by uploading new images, deleting unused ones,
    also manages filenames stored in database.
    """
    image = files.get('q_image', None)
    image_status = None
    if image and image.filename:
        if helper.allowed_extension(image.filename):
            filename = "q_id_" + str(question_id) + "_" + secure_filename(image.filename)
            image.save("static/uploads/" + filename)
            rename_question_image(filename, question_id)
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


def rename_question_image(filename, question_id):
    """Rename a question image by updating database cell where id found."""
    SQL = """UPDATE question SET image = %s WHERE id = %s;"""
    data = (filename, question_id)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def get_question_details(question_id):
    """Return a question title, message and image name, where id is found."""
    SQL = """SELECT title, message, image FROM question WHERE id = %s;"""
    data = (question_id,)
    fetch = "one"
    question = db.run_statements(((SQL, data, fetch),))[0]
    return question


def update_question(q_form, question_id):
    """Update a question title and message where id found."""
    SQL = """UPDATE question SET title = %s, message = %s WHERE id = %s;"""
    data = (q_form['q_title'], q_form['q_desc'], question_id)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def get_image_for_update_question(question_id):
    """Get image name for question with question_id."""
    SQL = """SELECT image FROM question WHERE id = %s;"""
    data = (question_id,)
    fetch = "one"
    image = db.run_statements(((SQL, data, fetch),))[0][0]
    return image


def get_5_questions():
    """Return 5 most recent questions."""
    SQL = """SELECT id, title, submission_time, view_number, vote_number, answer_count
             FROM question ORDER BY submission_time DESC LIMIT 5;"""
    data = None
    fetch = "all"
    questions = db.run_statements(((SQL, data, fetch),))[0]
    return questions


def get_questions(criterium, order):
    """Return questions list ordered by a criterium and in certain order."""
    check_criterium = ("title", "submission_time", "view_number", "vote_number", "answer_count")
    check_order = ("asc", "desc")

    if criterium not in check_criterium or order not in check_order:
        criterium = "submission_time"
        order = "desc"

    SQL = """SELECT id, title, submission_time, view_number, vote_number, answer_count
             FROM question ORDER BY {} {};""".format(criterium, order)
    data = None
    fetch = "all"
    questions = db.run_statements(((SQL, data, fetch),))[0]
    return questions


def update_view_count(question_id):
    """Update view count by plus one."""
    SQL = """UPDATE question SET view_number = view_number + 1 WHERE id = %s;"""
    data = (question_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def valid_question_id(question_id):
    """Return True if question_id found in question table."""
    SQL = """SELECT id FROM question WHERE id = %s;"""
    data = (question_id,)
    fetch = "one"
    try:
        found_id = db.run_statements(((SQL, data, fetch),))[0][0]
    except (DatabaseError, TypeError):
        return False
    return True


def get_all_for_question(question_id):
    """Return tuple: 1. question record with question_id, 2. answers 2d list for question."""
    SQL1 = """SELECT
                  id, submission_time, view_number, vote_number, title, message, image, answer_count, user_name
              FROM question WHERE id = %s;"""
    SQL2 = """SELECT
                  id, submission_time, vote_number, question_id, message, image, accepted, user_name
              FROM answer WHERE question_id = %s
              ORDER BY
                  CASE WHEN accepted = true THEN 0 ELSE 1 END, vote_number DESC, submission_time DESC;"""
    data = (question_id,)
    fetch1 = "one"
    fetch2 = "all"
    results = db.run_statements(((SQL1, data, fetch1), (SQL2, data, fetch2)))
    return results


def get_added_tag_ids_and_names(question_id):
    """Return added tags for question with question_id."""
    SQL = """SELECT tag.id, tag.name FROM question_tag AS qt
             JOIN tag ON
                qt.tag_id = tag.id
             WHERE qt.question_id = %s;"""
    data = (question_id,)
    fetch = "all"
    added_tags = db.run_statements(((SQL, data, fetch),))[0]
    return added_tags


def remove_answer_images_by_q_id(question_id):
    """Return filtered answers (2d list), removing answers with question_id."""
    SQL = """SELECT image from answer WHERE question_id = %s;"""
    data = (question_id,)
    fetch = "col"
    images = db.run_statements(((SQL, data, fetch),))[0]

    if images:
        for image in images:
            if image:
                try:
                    os.remove('static/uploads/' + image)
                except FileNotFoundError:
                    pass


def delete_question_with_image(question_id, question_image):
    """Delete question record and image from filesystem."""
    SQL = """DELETE FROM question WHERE id = %s;"""
    data = (question_id, )
    fetch = None
    db.run_statements(((SQL, data, fetch),))

    if question_image:
        try:
            os.remove('static/uploads/' + question_image)
        except FileNotFoundError:
            pass


def delete_q_image(question_id):
    """Delete image belonging to a question with question_id."""
    current_image = get_question_image(question_id)
    if current_image:
        remove_question_image(question_id)
    try:
        os.remove("static/uploads/" + current_image)
    except FileNotFoundError:
        pass


def get_question_image(question_id):
    """Return question image name."""
    SQL = """SELECT image FROM question WHERE id = %s;"""
    data = (question_id,)
    fetch = "one"
    q_img = db.run_statements(((SQL, data, fetch),))[0][0]
    return q_img


def remove_question_image(question_id):
    """Remove question image by updating database, setting image to NULL."""
    SQL = """UPDATE question SET image = NULL WHERE id = %s;"""
    data = (question_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))
