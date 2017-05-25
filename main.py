
import os
import re

from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)
from werkzeug.utils import secure_filename

from data_manager import *
from logic import *

app = Flask(__name__)


@app.route('/new-question/post', methods=['POST'])
def ask_question():
    """Post a new question with title, description and optional image.
    Redirect: to new question posted upon success, else to question list page.
    """
    if not valid_request(request.form):
        flash("✘ Title and description must be filled and at least 10 characters long.", "error")
        return redirect(url_for('show_question_list'))

    new_question = create_new_question_no_image(request.form)
    question_id, previous_image = insert_question(new_question)

    image_status = update_question_image(question_id, previous_image, request.files)
    if image_status == "uploaded":
        flash("✓ File was uploaded successfully.", "success")
    elif image_status == "not_allowed_ext":
        flash("✘ File was not uploaded. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")

    flash("✓ Question posted.", "success")
    return redirect(url_for('show_question_page', question_id=question_id))


@app.route('/question/<question_id>/post-edit', methods=['POST'])
def edit_question(question_id):
    """Edit question with question_id, based on filled HTTP request form.
    Updates info in CSV file and manages filesystem.
    """
    if not valid_request(request.form):
        flash("✘ Title and description must be filled and at least 10 characters long.", "error")
        return redirect(url_for('show_question_list'))

    try:
        selected_question = get_question_details(question_id)
        if not selected_question:
            raise IndexError
    except (psycopg2.DatabaseError, IndexError):
        return abort(404)

    update_question(request.form, question_id)

    previous_image = get_image_for_update_question(question_id)

    image_status = update_question_image(question_id, previous_image, request.files)
    if image_status == "uploaded":
        flash("✓ File was uploaded successfully.", "success")
    elif image_status == "updated":
        flash("✓ Previous image was updated with new one successfully.", "success")
    elif image_status == "not_allowed_ext":
        flash("✘ File was not updated. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")

    flash("✓ Question successfully edited.", "success")

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/")
def show_index():
    """View function of index page."""
    questions = get_5_questions()
    return render_template("index.html", questions=questions, title="Index")


@app.route("/contact/")
def show_contact():
    """View function of contact page."""
    return render_template("contact.html", title="Contact")


@app.route("/search/")
def show_search_results():
    """View function of the results page."""
    search_results = None

    if request.args.get("q"):
        phrase = request.args["q"]
        insensitive_phrase = re.compile(re.escape(phrase), re.IGNORECASE)

        questions, answers = get_search_results(phrase)

        for i in range(len(questions)):
            questions[i] = list(questions[i])
            questions[i].append([])

        missing_question_ids = []
        question_ids = [question[0] for question in questions]
        for i, answer in enumerate(answers):
            answers[i] = list(answers[i])
            answers[i][4] = answers[i][4].replace('<', '')
            answers[i][4] = answers[i][4].replace('>', '')
            answers[i][4] = insensitive_phrase.sub('<span class="highlight">{}</span>'.format(phrase), answers[i][4])
            if answer[3] not in question_ids:
                missing_question_ids.append(answer[3])

        additional_questions = get_additional_questions(tuple(missing_question_ids))
        for i in range(len(additional_questions)):
            additional_questions[i] = list(additional_questions[i])
            additional_questions[i].append([])

        for i, question in enumerate(additional_questions):
            for j, answer in enumerate(answers):
                if question[0] == answer[3]:
                    additional_questions[i][6].append(answer)

        for i, question in enumerate(questions):
            questions[i][1] = questions[i][1].replace('<', '')
            questions[i][1] = questions[i][1].replace('>', '')
            questions[i][1] = insensitive_phrase.sub('<span class="highlight">{}</span>'.format(phrase), questions[i][1])
            for j, answer in enumerate(answers):
                if question[0] == answer[3]:
                    questions[i][6].append(answer)

        questions.extend(additional_questions)
        flash("Showing search results for phrase '{}'.".format(phrase), "success")
        return render_template("search.html", questions=questions, title="Search Results")
    else:
        flash("Empty search field. No results retrieved.", "error")
        return redirect(url_for('show_index'))


@app.route("/list/")
def show_question_list(criterium='submission_time', order='desc'):
    """View function of question list, shown as a table, plus button to add new question.
    If URL requested with query string (through ordering buttons),
    then selects the ordering accoringly before rendering list.html.
    """
    for key in request.args:
        criterium = key
        order = request.args[key]

    questions = get_questions(criterium, order)
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


@app.route("/question/<question_id>/edit")
def show_edit_question_form(question_id):
    """View function of edit question form"""
    try:
        selected_question = get_question_details(question_id)
        if not selected_question:
            raise IndexError
    except (psycopg2.DatabaseError, IndexError):
        return abort(404)

    return render_template("q_form.html", title="Edit Question",
                           selected_question=selected_question, question_id=question_id)


@app.route("/question/<question_id>")
def show_question_page(question_id):
    """View function of question page, with details and answers."""
    if request.args.get('view') == "counted":
        update_view_count(question_id)

    try:
        selected_question, answers = get_all_for_question(question_id)
        answer_ids = tuple(collect_answer_ids(answers))
        q_comments, a_comments = retrieve_comments(question_id, answer_ids)
    except (IndexError, FileNotFoundError):
        return abort(404)

    return render_template("question.html", question_id=question_id, answers=answers,
                           question=selected_question, title=("Question " + question_id),
                           q_comments=q_comments, a_comments=a_comments)


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    """Delete question (and its image) based on its question_id
    furthermore delete corresponding answers and their images.
    """
    try:
        selected_question = get_question_details(question_id)
        if not selected_question:
            raise IndexError
    except (psycopg2.DatabaseError, IndexError):
        return abort(404)

    remove_answer_images_by_q_id(question_id)
    image = selected_question[2]
    filter_questions(question_id, image)

    return redirect(url_for("show_question_list"))


@app.route("/question/<question_id>/new-answer", methods=["POST"])
def add_answer(question_id):
    """Add answer and redirect to its question page."""
    try:
        selected_question = get_question_details(question_id)
        if not selected_question:
            raise IndexError
    except (psycopg2.DatabaseError, IndexError):
        return abort(404)

    if not valid_answer_message(request.form):
        flash("✘ Message must be filled and at least 10 characters long.", "error")
        return redirect(url_for('show_question_list'))

    update_answer_counter(question_id, operation="ADD")

    new_answer = create_new_answer_no_image(request.form["message"], question_id)
    answer_id, image = insert_answer(new_answer)
    image_status = update_answer_image(answer_id, request.files)

    if image_status == "uploaded":
        flash("✓ File was uploaded successfully.", "success")
    elif image_status == "not_allowed_ext":
        flash("✘ File was not uploaded. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")
    flash("✓ Answer posted.", "success")

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/answer/<answer_id>/delete")
def delete_answer(answer_id):
    """Delete answer with answer_id and redirect to its question page."""
    try:
        selected_answer_id = get_answer_details(answer_id)
        if not selected_answer_id:
            raise IndexError
    except (psycopg2.DatabaseError, IndexError):
        return abort(404)

    question_id = remove_answer(answer_id)
    update_answer_counter(question_id, operation="SUB")

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/answer/<answer_id>/vote-<direction>")
@app.route("/question/<question_id>/vote-<direction>")
def vote(direction, question_id=None, answer_id=None):
    """Modify number of votes of a given question or answer,
    then redirect to corresponding question_page.
    """
    if question_id:
        do_vote(direction, question_id=question_id)
    elif answer_id:
        question_id = do_vote(direction, answer_id=answer_id)

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/question/<question_id>/del-img")
def delete_image(question_id):
    """Delete image of selected question."""
    do_delete_image(question_id)

    return redirect(url_for('show_edit_question_form', question_id=question_id))


@app.route("/comment/<question_id>", methods=["POST"])
def add_comment(question_id):
    """This is ok for questions and answers as well"""
    answer_id = request.args.get("answer_id")
    new_com = new_comment(question_id, answer_id, request.form.get("get_comment"))
    insert_comment(new_com)
    return redirect(url_for("show_question_page", question_id=question_id))


@app.route("/comment/edit/<question_id>/<comment_id>", methods=["POST"])
def fetch_comment_for_edit(question_id, comment_id):
    new_comment = request.form.get("get_comment")
    submission_time = create_timestamp()
    edit_comment(new_comment, comment_id, submission_time)
    return redirect(url_for("show_question_page", question_id=question_id))


@app.route("/comment/<question_id>/<comment_id>/delete")
def remove_comment(question_id, comment_id):
    delete_comment(comment_id)
    return redirect(url_for('show_question_page', question_id=question_id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=2002)
