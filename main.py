
import os

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from data_manager import *

app = Flask(__name__)


@app.route('/new-question/post', methods=['POST'])
def ask_question():
    """Post a new question and add to question.csv.
    Server-side validation: title and description field's minimum length validated.
    Uploading image: not required, but handled inside this question.
    Redirect: to new question posted upon success, else to question list page.
    """
    if len(request.form.get('q_title', 0)) >= 10 and len(request.form.get('q_desc', 0)) >= 10:
        questions = read_csv('question.csv')
        intial_views = 0
        initial_votes = 0
        empty_image = ''
        initial_answer_count = 0
        new_question = [generate_id(questions, 'q'), get_unix_timestamp(),
                        intial_views, initial_votes,
                        request.form['q_title'], request.form['q_desc'],
                        empty_image, initial_answer_count]

        question_id = new_question[0]
        image = request.files.get('q_image', None)
        if image and image.filename:
            if allowed_extension(image.filename):
                filename = question_id + "_" + secure_filename(image.filename)
                image.save("static/uploads/" + filename)
                new_question[6] = filename
            else:
                flash("✘ File was not uploaded. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")

        flash("✓ Question posted.", "success")
        questions.append(new_question)
        write_csv('question.csv', questions)
        return redirect(url_for('show_question_page', question_id=question_id, valid_view=False))

    flash("✘ Title and description must be filled and at least 10 characters long.", "error")
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
                current_image = question[6]
                current_answer_count = question[7]
                break
        else:
            flash("✘ Question ID does not exist. Please use the GUI to navigate.", "error")
            return redirect(url_for('show_question_list'))

        edited_question = [current_id, current_timestamp,
                           current_views, current_votes,
                           request.form['q_title'], request.form['q_desc'],
                           current_image, current_answer_count]

        image = request.files.get('q_image', None)
        if image and image.filename:
            if allowed_extension(image.filename):
                filename = current_id + "_" + secure_filename(image.filename)
                image.save("static/uploads/" + filename)
                edited_question[6] = filename
                if current_image:
                    os.remove("static/uploads/" + current_image)

            else:
                flash("✘ File was not updated. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")

        flash("✓ Question edited.", "success")
        questions[selected_question_index] = edited_question
        write_csv('question.csv', questions)
        return redirect(url_for('show_question_page', question_id=question_id, valid_view=False))

    flash("✘ Title and description must be filled and at least 10 characters long.", "error")
    return redirect(url_for('show_question_list'))


@app.route("/")
@app.route("/list/")
def show_question_list(criterium=None, order=None):
    """Display list of questions as a table and an 'Ask a question' button."""
    questions = read_csv("question.csv")
    for key in request.args:
        criterium = key
        order = request.args[key]

    questions = select_ordering(questions, order, criterium)

    for i in range(len(questions)):
        questions[i][1] = convert_unix(questions[i][1])
    return render_template("list.html", questions=questions, title="Questions")


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
    for i in range(len(answers)):
        answers[i][1] = convert_unix(answers[i][1])

    # Filter answers that belong to question:
    answers = [item for item in answers if question_id == item[3]]
    # Ordering: primary - most votes on top, secondary - most recent on top:
    answers = sorted(answers, key=lambda x: x[1], reverse=True)
    answers = sorted(answers, key=lambda x: x[2], reverse=True)

    if_valid_view = request.args.get('valid_view')
    question = add_to_view_count(questions, question_id, if_valid_view)

    return render_template("question.html", question_id=question_id, answers=answers,
                           question=question, title=("Question" + question_id))


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
                    filename = answer[5]
                    if filename:
                        os.remove('static/uploads/' + filename)
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
        init_time = get_unix_timestamp()
        init_votes = 0
        message = request.form["message"]
        empty_image = ''
        new_answer = [answer_id, init_time, init_votes, question_id, message, empty_image]

        image = request.files.get('a_image', None)
        if image and image.filename:
            if allowed_extension(image.filename):
                filename = answer_id + "_" + secure_filename(image.filename)
                image.save("static/uploads/" + filename)
                new_answer[5] = filename
            else:
                flash("✘ File was not uploaded. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")

        # Update number of answers for selected question:
        for i, question in enumerate(questions):
            if question[0] == question_id:
                questions[i][7] += 1
                break

        write_csv('question.csv', questions)
        flash("✓ Answer posted.", "success")
        answers.append(new_answer)
        write_csv('answer.csv', answers)
        return redirect(url_for('show_question_page', question_id=question_id))

    flash("✘ Message must be filled and at least 10 characters long.", "error")
    return redirect(url_for('show_question_list'))


@app.route("/answer/<answer_id>/delete")
def delete_answer(answer_id):
    """Delete an answer based on its answer_id and return to the
    corresponding questions page.
    """
    answers = read_csv("answer.csv")
    for answer in answers:
        if answer[0] == answer_id:
            question_id = answer[3]
            current_image = answer[5]
            answers.remove(answer)
            break
    if current_image:
        os.remove("static/uploads/" + current_image)

    # Update number of answers for this question:
    questions = read_csv('question.csv')
    for i, question in enumerate(questions):
        if question[0] == question_id:
            questions[i][7] -= 1
            break

    write_csv("question.csv", questions)
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
        os.remove("static/uploads/" + current_image)
        return redirect(url_for('show_edit_question_form', question_id=question_id))

    elif answer_id:
        answers = read_csv("answer.csv")
        for i, answer in enumerate(answers):
            if answer[0] == answer_id:
                question_id = answer[3]
                current_image = answers[i][5]
                answers[i][5] = ""
        write_csv("answer.csv", answers)
        os.remove("static/uploads/" + current_image)
        return redirect(url_for('show_edit_answer_form', answer_id=answer_id))


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=2000)
