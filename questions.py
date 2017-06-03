
import os

from werkzeug.utils import secure_filename

import db
import helper


def create_new_question_no_image(q_form):
    """Create new question from successfully filled question form."""
    intial_views = 0
    initial_votes = 0
    empty_image = None
    initial_answer_count = 0
    new_question = [helper.create_timestamp(), intial_views, initial_votes,
                    q_form['q_title'], q_form['q_desc'],
                    empty_image, initial_answer_count]
    return new_question


def insert_question(new_question):
    """Insert new question into question table."""
    SQL = """INSERT INTO question
             (submission_time, view_number, vote_number, title, message, image, answer_count)
             VALUES (%s, %s, %s, %s, %s, %s, %s)
             RETURNING id, image;"""
    data = (new_question[0], new_question[1], new_question[2], new_question[3],
            new_question[4], new_question[5], new_question[6])
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
