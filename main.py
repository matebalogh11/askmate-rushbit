
import os
import time
from datetime import datetime
from random import choice

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from data_manager import read_csv, write_csv

app = Flask(__name__)


def allowed_file(filename):
    """Takes a filename and validates by extension.
    @filename string: filename string.
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
    """Gets current time as Unix timestamp."""
    return time.time()


def count_answers(questions, answers):
    number_of_answers = {}
    for question in questions:
        answer_counter = 0
        number_of_answers.update({question[0]: 0})
        for answer in answers:
            if answer[3] == question[0]:
                answer_counter += 1
        number_of_answers[question[0]] = answer_counter
    print(number_of_answers)
    return number_of_answers


@app.route('/new-question/post', methods=['POST'])
def ask_question():
    """Post a new question."""
    if len(request.form.get('q_title', 0)) >= 10 and len(request.form.get('q_desc', 0)) >= 10:
        questions = read_csv('question.csv')
        intial_views = 0
        initial_votes = 0
        new_question = [generate_id(questions, 'q'), get_unix_timestamp(),
                        intial_views, initial_votes,
                        request.form['q_title'], request.form['q_desc']]

        question_id = new_question[0]
        image = request.files.get('q_image', None)
        if image and image.filename:
            # Allowing only certain extensions:
            if allowed_file(image.filename):
                # Making sure that filename is secure:
                filename = question_id + "_" + secure_filename(image.filename)
                path_with_filename = "uploads/" + filename
                # Save file to Uploads folder:
                image.save(path_with_filename)
                # Append to new question to be added to CSV:
                new_question.append(filename)
            else:
                new_question.append('')
                flash("File was not uploaded. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")
        else:
            new_question.append('')

        flash("Question posted.", "success")
        questions.append(new_question)
        write_csv('question.csv', questions)

        return redirect(url_for('show_question_page', question_id=question_id, valid_view=False))

    flash("Title and description must be filled and at least 10 characters long.", "error")

    return redirect(url_for('show_question_list'))


@app.route('/question/<question_id>/post-edit', methods=['POST'])
def edit_question(question_id):
    """Edit a question in question.csv and redirects to the question page.
    Image of a question can be deleted or a new one uploaded.
    Uploading a new image overwrites path in question.csv, deletes old file, saves new file.
    """
    if len(request.form.get('q_title', 0)) >= 10 and len(request.form.get('q_desc', 0)) >= 10:
        questions = read_csv('question.csv')
        for i, question in enumerate(questions):
            if question[0] == question_id:
                selected_question_index = i
                current_id = question[0]
                current_timestamp = question[1]
                current_views = question[2]
                current_votes = question[3]
                if len(question) == 7:
                    current_image = question[6]
                else:
                    current_image = ""
                break
        else:
            flash("Question ID does not exist. Please use the GUI to navigate.", "error")
            return redirect(url_for('show_question_list'))

        edited_question = [current_id, current_timestamp,
                           current_views, current_votes,
                           request.form['q_title'], request.form['q_desc'], current_image]

        image = request.files.get('q_image', None)
        if image and image.filename:
            # Allowing only certain extensions:
            if allowed_file(image.filename):
                filename = current_id + "_" + secure_filename(image.filename)
                path_with_filename = "uploads/" + filename
                image.save(path_with_filename)

                # If there is a previous image:
                if current_image:
                    os.remove("/uploads/" + current_image)

                edited_question[6] = filename

            else:
                flash("File was not updated. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")

        flash("Question edited.", "success")

        # Overwrite question line in CSV, which was selected for editing:
        questions[selected_question_index] = edited_question
        write_csv('question.csv', questions)
        return redirect(url_for('show_question_page', question_id=question_id, valid_view=False))

    flash("Title and description must be filled and at least 10 characters long.", "error")

    return redirect(url_for('show_question_list'))


def convert_unix(unix_timestamp):
    """Converts Unix timestamp to human readable format.
    @unixtime int: Unix time running total of seconds.
    @return string: human readable timestamp as example: Apr 28 - 18:49
    """
    return '{:%Y %b %d - %H:%M}'.format(datetime.fromtimestamp(unix_timestamp))


@app.route("/")
@app.route("/list/")
def show_question_list():
    """Display list of questions as a table and an 'Ask a question' button."""
    questions = read_csv("question.csv")
    answers = read_csv("answer.csv")
    number_of_answers = count_answers(questions, answers)
    # Sort questions to display most recent on top:
    questions = sorted(questions, key=lambda x: x[2], reverse=True)
    # Convert all timestamps to human readable form:
    for i, question in enumerate(questions):
        questions[i][1] = convert_unix(questions[i][1])
    return render_template("list.html", questions=questions, title="Questions", number_of_answers=number_of_answers)


@app.route("/new-question/")
def show_new_question_form():
    """View function of new question form."""
    title = "Ask New Question"
    return render_template("q_form.html", title=title)


@app.route("/question/<question_id>/new-answer")
def show_new_answer_form(question_id):
    """View function of new answer form."""
    title = "Add new answer to question: {}".format(question_id)
    return render_template("a_form.html", title=title, question_id=question_id)


@app.route("/question/<question_id>")
def show_question_page(question_id, valid_view=True):
    """View function of question page, with details and answers."""
    questions = read_csv("question.csv")
    # Redirect to list if ID is not found in table:
    validate_id(question_id, questions)
    answers = read_csv("answer.csv")

    for i, asnwer in enumerate(answers):
        answers[i][1] = convert_unix(answers[i][1])

    answers = [item for item in answers if question_id == item[3]]
    answers = sorted(answers, key=lambda x: x[2], reverse=True)
    answers = sorted(answers, key=lambda x: x[1], reverse=True)
    for i, question_ in enumerate(questions):
        if question_[0] == question_id:
            question = questions[i]
            if request.args.get('valid_view') != 'False':
                questions[i][2] += 1
                write_csv("question.csv", questions)
            questions[i][1] = convert_unix(questions[i][1])
            break

    return render_template("question.html", question_id=question_id, answers=answers,
                           question=question, title=("Question" + question_id))


def validate_id(id_, table):
    """Redirect to list if ID is not found in table."""
    id_list = [line[0] for line in table]
    if id_ not in id_list:
        flash("That ID does not exist. Use GUI to navigate the web page.", "error")
        return redirect(url_for('show_question_list'))


@app.route("/question/<question_id>/edit")
def show_edit_question_form(question_id):
    """View function of edit question form"""
    questions = read_csv("question.csv")
    # Redirect to list if ID is not found in table:
    validate_id(question_id, questions)

    for question in questions:
        if question[0] == question_id:
            selected_question = question
            break

    return render_template("q_form.html", title="Edit Question",
                           selected_question=selected_question, question_id=question_id)


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    """Delete question based on its question_id and corresponding answers
    upon hitting delete button on a question page and redirects to the root page.
    """
    questions = read_csv("question.csv")
    # Redirect to list if ID is not found in table:
    validate_id(question_id, questions)

    answers = read_csv("answer.csv")

    for question in questions:
        if question[0] == question_id:
            questions.remove(question)
            for answer in answers:
                if answer[3] == question_id:
                    answers.remove(answer)

    write_csv("question.csv", questions)
    write_csv("answer.csv", answers)

    return redirect(url_for("show_question_list"))


@app.route("/question/<question_id>/new-answer", methods=["POST"])
def add_answer(question_id):
    """Add answer and redirect to question page."""
    questions = read_csv("question.csv")
    # Redirect to list if ID is not found in table:
    validate_id(question_id, questions)

    if len(request.form.get("message", 0)) >= 10:
        answers = read_csv("answer.csv")
        answer_id = generate_id(answers, 'a')
        time = get_unix_timestamp()
        init_votes = 0
        message = request.form["message"]
        new_answer = [answer_id, time, init_votes, question_id, message]

        image = request.files.get('a_image', None)
        if image and image.filename:
            # Allowing only certain extensions:
            if allowed_file(image.filename):
                # Making sure that filename is secure:
                filename = answer_id + "_" + secure_filename(image.filename)
                path_with_filename = "uploads/" + filename
                # Save file to Uploads folder:
                image.save(path_with_filename)
                # Append to new question to be added to CSV:
                new_answer.append(filename)
            else:
                new_answer.append('')
                flash("File was not uploaded. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")
        else:
            new_answer.append('')

        flash("Answer posted.", "success")
        answers.append(new_answer)
        write_csv('answer.csv', answers)

        return redirect(url_for('show_question_page', question_id=question_id))

    flash("Message must be filled and at least 10 characters long.", "error")

    return redirect(url_for('show_question_list'))


@app.route("/answer/<answer_id>/delete")
def delete_answer(answer_id):
    """Delete an answer based on its answer_id and return to the
    corresponding questions page.
    """
    answers = read_csv("answer.csv")
    for answer in answers:
        if answer[0] == answer_id:
            answers.remove(answer)
            question_id = answer[3]

    write_csv("answer.csv", answers)
    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/answer/<answer_id>/vote-<direction>")
@app.route("/question/<question_id>/vote-<direction>")
def vote(direction, question_id=None, answer_id=None):
    """Modifies number of votes of a given question or answer and
    returns to the corresponding question_page.
    """
    if question_id:
        questions = read_csv("question.csv")
        for i, question in enumerate(questions):
            if question[0] == question_id:
                if direction == "up":
                    questions[i][3] += 1
                elif direction == "down":
                    questions[i][3] -= 1

        write_csv("question.csv", questions)

    elif answer_id:
        answers = read_csv("answer.csv")
        for i, answer in enumerate(answers):
            if answer[0] == answer_id:
                question_id = answer[3]
                if direction == "up":
                    answers[i][2] += 1
                elif direction == "down":
                    answers[i][2] -= 1

        write_csv("answer.csv", answers)

    return redirect(url_for('show_question_page', question_id=question_id, valid_view=False))


@app.route("/answer/<answer_id>/del-img")
@app.route("/question/<question_id>/del-img")
def delete_image(question_id=None, answer_id=None):
    """Delete image of selected question OR answer."""
    if question_id:
        questions = read_csv("question.csv")
        for i, question in enumerate(questions):
            if question[0] == question_id:
                current_image = questions[i][6]
                questions[i][6] = ""
        write_csv("question.csv", questions)
        os.remove("/uploads/" + current_image)
        return redirect(url_for('show_edit_question_form', question_id=question_id))

    elif answer_id:
        answers = read_csv("answer.csv")
        for i, answer in enumerate(answers):
            if answer[0] == answer_id:
                question_id = answer[3]
                current_image = answers[i][5]
                answers[i][5] = ""
        write_csv("answer.csv", answers)
        os.remove("/uploads/" + current_image)
        return redirect(url_for('show_edit_answer_form', answer_id=answer_id))


@app.route("/answer/<answer_id>/edit")
def show_edit_answer_form(answer_id):
    """Show the edit answer form.
    Still has to be put into HTMLs.
    """
    return "Edit answer form - TO BE IMPLEMENTED"


@app.route("/answer/<answer_id>/edit", methods=['POST'])
def edit_answer(answer_id):
    """This will do the action, to edit the answer based on filled answer editing form.
    Still has to be put into HTMLs.
    """
    pass


def sort_questions():
    """To be broken down to different ones probably."""
    pass


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=2000)
