
from os import urandom

from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)

import questions_logic
import search_logic
from data_manager import *
from logic import *
import helper

app = Flask(__name__)


@app.route('/new-question/post', methods=['POST'])
def ask_question():
    """Post a new question with title, description and optional image.
    Redirect: to new question posted upon success, else to question list page.
    """
    if not helper.valid_request(request.form):
        flash("✘ Title and description must be filled and at least 10 characters long.", "error")
        return redirect(url_for('show_question_list'))

    new_question = questions_logic.create_new_question_no_image(request.form)
    question_id, previous_image = questions_logic.insert_question(new_question)

    image_status = questions_logic.update_question_image(question_id, previous_image, request.files)
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
    if not helper.valid_request(request.form):
        flash("✘ Title and description must be filled and at least 10 characters long.", "error")
        return redirect(url_for('show_question_list'))
    try:
        selected_question = questions_logic.get_question_details(question_id)
        if not selected_question:
            raise IndexError
    except (psycopg2.DatabaseError, IndexError):
        return abort(404)

    questions_logic.update_question(request.form, question_id)

    previous_image = questions_logic.get_image_for_update_question(question_id)

    image_status = questions_logic.update_question_image(question_id, previous_image, request.files)
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
    questions = questions_logic.get_5_questions()

    return render_template("index.html", questions=questions, title="Index")


@app.route("/contact/")
def show_contact():
    """View function of contact page."""

    return render_template("contact.html", title="Contact")


@app.route("/search/")
def show_search_results():
    """View function of the results page."""
    if not request.args.get("q"):
        flash("Empty search field. No results retrieved.", "error")
        return redirect(url_for('show_index'))

    phrase = request.args["q"]
    questions = search_logic.get_questions_with_answers(phrase)
    if not questions:
        flash("No search results for phrase '{}'.".format(phrase), "error")

    return render_template("search.html", questions=questions, phrase=phrase, title="Search Results")


@app.route("/list/")
def show_question_list(criterium='submission_time', order='desc'):
    """View function of question list, shown as a table, plus button to add new question.
    If URL requested with query string (through ordering buttons),
    then selects the ordering accoringly before rendering list.html.
    """
    for key in request.args:
        criterium = key
        order = request.args[key]

    questions = questions_logic.get_questions(criterium, order)

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
        selected_question = questions_logic.get_question_details(question_id)
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

    added_ids_tags = get_added_tags(question_id)

    return render_template("question.html", question_id=question_id, answers=answers,
                           question=selected_question, title=("Question " + question_id),
                           q_comments=q_comments, a_comments=a_comments, added_ids_tags=added_ids_tags)


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
    """Add comment. Works for question and answer as well."""
    answer_id = request.args.get("answer_id")
    new_com = new_comment(question_id, answer_id, request.form.get("get_comment"))
    insert_comment(new_com)

    return redirect(url_for("show_question_page", question_id=question_id))


@app.route("/comment/edit/<question_id>/<comment_id>", methods=["POST"])
def fetch_comment_for_edit(question_id, comment_id):
    """Fetch comment for edit."""
    new_comment = request.form.get("get_comment")
    submission_time = create_timestamp()
    edit_comment(new_comment, comment_id, submission_time)
    return redirect(url_for("show_question_page", question_id=question_id))


@app.route("/comment/<question_id>/<comment_id>/delete")
def remove_comment(question_id, comment_id):
    """Remove comment from question."""
    delete_comment(comment_id)
    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/question/<question_id>/new-tag", methods=["GET", "POST"])
def show_add_tag(question_id):
    """View function of question tag addition page."""
    if request.method == "POST":

        status_message = do_inserts(request.form, question_id)

        if status_message == "contains_space":
            flash("The tag cannot contain spaces!", "error")
            return redirect(url_for('show_question_page', question_id=question_id))

        return redirect(url_for('show_question_page', question_id=question_id))

    else:
        ids_tags = get_added_tags(question_id)
        added_tags = [item[1] for item in ids_tags]
        existing_tags = get_existing_tags(tuple(added_tags))

        return render_template("tag.html", added_tags=added_tags, existing_tags=existing_tags,
                               question_id=question_id, title="Add Tag")


@app.route("/question/<question_id>/tag/<tag_id>/delete")
def delete_tag(question_id, tag_id):
    """Delete tag."""
    do_delete_tag(question_id, tag_id)

    return redirect(url_for('show_question_page', question_id=question_id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.secret_key = urandom(12)
    app.run(debug=True, port=2003)
