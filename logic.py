
import os
import time
from datetime import datetime
from random import choice

from werkzeug.utils import secure_filename

from data_manager import *


def create_timestamp():
    """Create timestamp."""
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    return timestamp


def allowed_extension(filename):
    """Takes a filename and validates by extension.
    @filename string: filename string.
    @return bool: True if file extension in allowed extensions, else False.
    """
    ALLOWED_EXTENSIONS = ['jpeg', 'jpg', 'png', 'gif']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_id(table, prefix):
    """Generate unique ID in the selected table.
    @table list: 2D list generated from CSV.
    @prefix string: either has the value of 'q' or 'a' to avoid identical IDs in 2 tables,
    which could cause trouble in saving files to uploads folder.
    @return string: unique ID in table.
    """
    lowerletters = list("abcdefghiklmnopqrstuvwxyz")
    upperletters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    decimals = list("0123456789")
    used_IDs = [row[0] for row in table]

    valid_ID = False
    while not valid_ID:
        generated_id = ("{}_id_{}{}{}".format(prefix, choice(lowerletters),
                                              choice(upperletters), choice(decimals)))
        if generated_id not in used_IDs:
            valid_ID = True
    return generated_id


def select_ordering(questions, order, criterium):
    """Default ordering: most recent on top.
    Based on query string, selected ordering will be dominant.
    """
    if not order and not criterium:
        questions = sorted(questions, key=lambda x: x[1], reverse=True)
    else:
        keys_and_indices = [('title', 4), ('time', 1), ('views', 2), ('votes', 3), ('answers', 7)]
        for key, index in keys_and_indices:
            if key == 'title':
                if order == 'asc':
                    questions = sorted(questions, key=lambda x: x[index].lower(), reverse=False)
                elif order == 'desc':
                    questions = sorted(questions, key=lambda x: x[index].lower(), reverse=True)
            else:
                if criterium == key:
                    if order == 'asc':
                        questions = sorted(questions, key=lambda x: x[index], reverse=True)
                    elif order == 'desc':
                        questions = sorted(questions, key=lambda x: x[index], reverse=False)
    return questions


def select_question(questions, question_id):
    """Return selected question."""
    selected_question = None
    for i in range(len(questions)):
        if questions[i][0] == question_id:
            selected_question = questions[i]
            break
    return selected_question


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
    new_question = [create_timestamp(), intial_views, initial_votes, q_form['q_title'], q_form['q_desc'],
                    empty_image, initial_answer_count]
    return new_question


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
        if allowed_extension(image.filename):
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


def valid_request(q_form):
    """Return True if HTTP request was sent with at least 10
    characters long title and description, else False"""
    title_length = len(q_form.get('q_title', ''))
    desc_length = len(q_form.get('q_desc', ''))
    if title_length >= 10 and desc_length >= 10:
        return True
    return False


def valid_answer_message(a_form):
    """Answer message must be at least 10 characters long to return True, else False."""
    answer_message = len(a_form.get("message", ''))
    if answer_message >= 10:
        return True
    return False


def create_edited_question_no_image(questions, q_form, question_id):
    """Return edited_question based on existing data and filled HTTP request form,
    and also return the index number of selected question for later use.
    @return tuple: list, int.
    """
    for i, question in enumerate(questions):
        if question[0] == question_id:
            selected_question_index = i
            edited_question = [question[0], question[1], question[2], question[3],
                               q_form['q_title'], q_form['q_desc'], question[6], question[7]]
            break
    else:
        edited_question = None
        selected_question_index = None

    return (edited_question, selected_question_index)


def filter_questions(question_id, question_image):
    """Return filtered questions, removing question with question_id,
    also return a status indicator whether any question was found with question_id.
    @return tuple: 2d list, bool.
    """
    delete_question(question_id)

    if question_image:
        try:
            os.remove('static/uploads/' + question_image)
        except FileNotFoundError:
            pass


def remove_answer_images_by_q_id(question_id):
    """Return filtered answers, removing answers with question_id.
    @return list: 2d list of filtered answers.
    """
    images = fetch_answer_images(question_id)

    for image in images:
        try:
            os.remove('static/uploads/' + image)
        except (FileNotFoundError, TypeError):
            pass


def create_new_answer_no_image(message, question_id):
    """Return new answer, based on HTTP request form, initialized without image.
    @answers list: 2d list.
    @message str: message from request.form.
    @return list: id(str), unix_timestamp(int), votes(int), question_id(str), message(str), image_path(str).
    """

    init_time = create_timestamp()
    init_votes = 0
    init_image = None
    new_answer = [init_time, init_votes, question_id, message, init_image]
    return new_answer


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
        if allowed_extension(image.filename):
            filename = str(answer_id) + "_" + secure_filename(image.filename)
            image.save("static/uploads/" + filename)
            rename_answer_image(filename, answer_id)
            image_status = "uploaded"
        else:
            image_status = "not_allowed_ext"
    return image_status


def remove_answer(answer_id):
    """Return filtered answers, removing answer with answer_id,
    also return status message whether id was ever found or not,
    and return question_id for later use.
    Deletes answer image from filesystem if found.
    @return tuple: 2d list, bool, str.
    """
    image_to_delete, question_id = get_answer_image(answer_id)

    try:
        os.remove("static/uploads/" + image_to_delete)
    except (FileNotFoundError, TypeError):
        pass

    delete_answer_by_id(answer_id)
    return question_id


def do_vote(direction, question_id=None, answer_id=None):
    """Increase or decrese vote count by 1 of question or answer.
    @return str: return ONLY if called with answer_id, otherwise would be needless.
    """
    if question_id:
        if direction == "up":
            change_vote_count("up", question_id=question_id)
        elif direction == "down":
            change_vote_count("down", question_id=question_id)

    if answer_id:
        if direction == "up":
            question_id = change_vote_count("up", answer_id=answer_id)
        elif direction == "down":
            question_id = change_vote_count("down", answer_id=answer_id)
        return question_id


def do_delete_image(question_id):
    """Delete image belonging to a question with question_id."""
    current_image = get_question_image(question_id)

    try:
        os.remove("static/uploads/" + current_image)
    except FileNotFoundError:
        pass


def new_comment(question_id=None, comment_data, answer_id=None):
    init_time = create_timestamp()
    init_edit = 0
    comment = (question_id, answer_id, comment_data, init_time, init_edit)
    return comment


def collect_answer_ids(answers):
    answer_ids = []
    for answer in answers:
        answer_ids.append(answer[0])
    return answer_ids
