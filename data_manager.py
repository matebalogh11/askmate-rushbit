import base64
import csv
from copy import deepcopy
from datetime import datetime
from random import choice
import time


def write_csv(file, data):

    copied_data = deepcopy(data)
    with open(file, "w", newline="") as text:
        writer = csv.writer(text)
        for i, items in enumerate(copied_data):
            for n, details in enumerate(items):
                if n == 4 or n == 5 or n == 6:
                    old_string_obj = copied_data[i][n]
                    byte_obj = bytearray(old_string_obj, "utf-8")
                    base64_obj = base64.b64encode(byte_obj)
                    new_string_obj = base64_obj.decode("utf-8")
                    copied_data[i][n] = new_string_obj
        for story in copied_data:
            writer.writerow(story)


def read_csv(file):

    csv_type = True if file == "question.csv" else False
    with open(file, "r") as text:
        reader = csv.reader(text)
        requested_data = list(reader)
        if csv_type:
            for n, data in enumerate(requested_data):
                for i, items in enumerate(data):
                    if i == 1:
                        requested_data[n][i] = float(requested_data[n][i])
                    if i == 2 or i == 3 or i == 7:
                        requested_data[n][i] = int(requested_data[n][i])
                    if i == 4 or i == 5 or i == 6:
                        requested_data[n][i] = base64.b64decode(requested_data[n][i]).decode("utf-8")
        else:
            for n, data in enumerate(requested_data):
                for i, items in enumerate(data):
                    if i == 1:
                        requested_data[n][i] = float(requested_data[n][i])
                    if i == 2:
                        requested_data[n][i] = int(requested_data[n][i])
                    if i == 4 or i == 5 or i == 6:
                        requested_data[n][i] = base64.b64decode(requested_data[n][i]).decode("utf-8")
    return requested_data


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


def get_unix_timestamp():
    """Get current time as Unix timestamp."""
    return time.time()


def convert_unix(unix_timestamp):
    """Converts Unix timestamp to human readable format.
    @unixtime int: Unix time running total of seconds.
    @return string: human readable timestamp as example: Apr 28 - 18:49
    """
    return '{:%Y %b %d - %H:%M}'.format(datetime.fromtimestamp(unix_timestamp))


def select_ordering(questions, order, criterium):
    """Default ordering: most recent on top.
    Based on query string, selected ordering will be dominant.
    """
    questions = sorted(questions, key=lambda x: x[1], reverse=True)

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


def add_to_view_count(questions, question_id, if_valid_view):
    for i, question_ in enumerate(questions):
        if question_[0] == question_id:
            question = questions[i]
            if if_valid_view != 'False':
                questions[i][2] += 1
                write_csv("question.csv", questions)
            questions[i][1] = convert_unix(questions[i][1])
            return question
