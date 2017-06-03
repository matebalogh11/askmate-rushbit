
import os

from werkzeug.utils import secure_filename

import db
import helper


def create_new_question_no_image(q_form):
    """Create new question from successfully filled question form
    with unique ID in questions, actual unix timestamp and additional initial values.
    @questions list: 2d list.
    @q_form dict: q_title and q_desc are the expected keys.
    @return list: id(str), unix timestamp(int), views(int), votes(int),
                        title(str), desc(str), image path(str), answer count(int).
    """
    intial_views = 0
    initial_votes = 0
    empty_image = None
    initial_answer_count = 0
    new_question = [helper.create_timestamp(), intial_views, initial_votes, q_form['q_title'], q_form['q_desc'],
                    empty_image, initial_answer_count]
    return new_question


def insert_question(new_question):
    """Insert question."""
    SQL = """INSERT INTO question (submission_time, view_number, vote_number,
                                   title, message, image, answer_count)
             VALUES (%s, %s, %s, %s, %s, %s, %s)
             RETURNING id, image;"""
    data = (new_question[0], new_question[1], new_question[2], new_question[3],
            new_question[4], new_question[5], new_question[6])
    fetch = "one"

    results = db.run_statements(((SQL, data, fetch),))
    result = results[0]

    return result


def update_question_image(question_id, previous_image, files):
    """Update path to question image and manage filesystem.
    If image belonged to question already and new image is uploaded,
    then delete previous image and upload new image.
    If no image belonged to question, then simply upload new image upon request.

    Files being uploaded to /static/uploads.
    Validated server-side if file has been really sent with HTTP request
    and if extension is valid.

    @question list: id(str), unix timestamp(int), views(int), votes(int),
                        title(str), desc(str), image path(str), answer count(int).
    @files dict: q_image key is the only expected key.
    @return str: status to know what message should be flashed to user.
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
    """"""
    SQL = """UPDATE question SET image = %s WHERE id = %s;"""
    data = (filename, question_id)
    fetch = None

    db.run_statements(((SQL, data, fetch),))
