
from os import urandom

from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for, session)

import account_logic as account
import answers_logic
import comments_logic
import helper
import questions_logic
import search_logic
import tag_logic
import users_logic
import vote_logic


app = Flask(__name__)


@app.before_request
def check_before_request():
    """Before each request, check/do the following:
    1. Refresh session time, 2. Check for valid request method, 3. Check for valid id variable.
    """
    account.make_session_permanent(app)
    account.check_for_valid_request()
    account.check_for_valid_id_variable()


@app.route('/new-question/post', methods=['POST'])
@account.login_required('user')
def ask_question():
    """Post a new question with title, description and optional image.
    Redirect: to new question posted upon success, else to question list page.
    """
    if not questions_logic.valid_request(request.form):
        flash("✘ Title and description must be filled and at least 10 characters long.", "error")
        return redirect(url_for('show_question_list'))

    new_question = questions_logic.create_new_question_no_image(request.form, session['user_name'])
    question_id, previous_image = questions_logic.insert_question(new_question)

    image_status = questions_logic.update_question_image(question_id, previous_image, request.files)
    if image_status == "uploaded":
        flash("✓ File was uploaded successfully.", "success")
    elif image_status == "not_allowed_ext":
        flash("✘ File was not uploaded. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")

    flash("✓ Question posted.", "success")
    return redirect(url_for('show_question_page', question_id=question_id))


@app.route('/question/<question_id>/post-edit', methods=['POST'])
@account.login_required('author')
def edit_question(question_id):
    """Edit question with question_id, based on filled HTTP request form.
    Updates info in CSV file and manages filesystem.
    """
    if not questions_logic.valid_request(request.form):
        flash("✘ Title and description must be filled and at least 10 characters long.", "error")
        return redirect(url_for('show_question_list'))

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
    """View function of question list. Normally shows most recent on top,
    if requested from table headers (query string), orders accordingly.
    """
    for key in request.args:
        criterium = key
        order = request.args[key]

    questions = questions_logic.get_questions(criterium, order)
    return render_template("list.html", questions=questions, title="Questions")


@app.route("/new-question/")
@account.login_required('user')
def show_new_question_form():
    """View function of new question form."""
    title = "Ask New Question"
    return render_template("q_form.html", title=title)


@app.route("/question/<question_id>/new-answer")
@account.login_required('user')
def show_new_answer_form(question_id):
    """View function of new answer form."""
    title = "Add new answer to question: {}".format(question_id)
    return render_template("a_form.html", title=title, question_id=question_id)


@app.route("/question/<question_id>/edit")
@account.login_required('author')
def show_edit_question_form(question_id):
    """View function of edit question form"""
    selected_question = questions_logic.get_question_details(question_id)

    return render_template("q_form.html", title="Edit Question",
                           selected_question=selected_question, question_id=question_id)


@app.route("/question/<question_id>/")
def show_question_page(question_id):
    """View function of question page, with details, answers, comments, tags."""
    if request.args.get('view') == "counted":
        questions_logic.update_view_count(question_id)

    question, answers = questions_logic.get_all_for_question(question_id)
    q_comments, a_comments = comments_logic.retrieve_comments(question_id, answers)

    added_tags = tag_logic.get_added_tag_ids_and_names(question_id)
    title = "Question {}".format(question_id)

    return render_template("question.html", question=question, answers=answers, title=title,
                           q_comments=q_comments, a_comments=a_comments, added_tags=added_tags)


@app.route("/question/<question_id>/delete")
@account.login_required('author')
def delete_question(question_id):
    """Delete question, its answers and all comments, and all image files."""
    questions_logic.remove_answer_images_by_q_id(question_id)
    question_image = questions_logic.get_question_details(question_id)[2]
    questions_logic.delete_question_with_image(question_id, question_image)

    return redirect(url_for("show_question_list"))


@app.route("/question/<question_id>/new-answer", methods=["POST"])
@account.login_required('user')
def add_answer(question_id):
    """Add answer and redirect to its question page."""
    if not answers_logic.valid_answer_message(request.form):
        flash("✘ Message must be filled and at least 10 characters long.", "error")
        return redirect(url_for('show_new_answer_form', question_id=question_id))

    answers_logic.update_answer_counter(question_id, operation="ADD")

    new_answer = answers_logic.create_new_answer_no_image(request.form["message"], question_id, session['user_name'])
    answer_id, image = answers_logic.insert_answer(new_answer)
    image_status = answers_logic.update_answer_image(answer_id, None, request.files)

    if image_status == "uploaded":
        flash("✓ File was uploaded successfully.", "success")
    elif image_status == "not_allowed_ext":
        flash("✘ File was not uploaded. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")
    flash("✓ Answer posted.", "success")

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/answer/<answer_id>/edit", methods=["GET", "POST"])
@account.login_required('author')
def edit_answer(answer_id):
    """Delete answer with answer_id and redirect to its question page."""
    previous_image, question_id = answers_logic.get_answer_image_and_q_id(answer_id)

    if request.method == "POST":
        if not answers_logic.valid_answer_message(request.form):
            flash("✘ Message must be filled and at least 10 characters long.", "error")
            return redirect(url_for('edit_answer', answer_id=answer_id))

        answers_logic.update_answer_message(answer_id, request.form['message'])

        image_status = answers_logic.update_answer_image(answer_id, previous_image, request.files)
        if image_status == "uploaded":
            flash("✓ Answer image was uploaded successfully.", "success")
        elif image_status == "updated":
            flash("✓ Previous answer image was updated with new one successfully.", "success")
        elif image_status == "not_allowed_ext":
            flash("✘ Image was not updated. Allowed extensions: JPEG, JPG, PNG, GIF.", "error")

        return redirect(url_for('show_question_page', question_id=question_id))

    answer = answers_logic.get_answer_details(answer_id)
    title = "Add new answer to question: {}".format(question_id)
    return render_template("a_form.html", title=title, question_id=question_id, answer=answer)


@app.route("/answer/<answer_id>/delete")
@account.login_required('author')
def delete_answer(answer_id):
    """Delete answer with answer_id and redirect to its question page."""
    question_id = answers_logic.remove_answer_and_get_q_id(answer_id)
    answers_logic.update_answer_counter(question_id, operation="SUB")

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/answer/<answer_id>/del-img")
@app.route("/question/<question_id>/del-img")
@account.login_required('author')
def delete_image(question_id=None, answer_id=None):
    """Delete image of selected question."""
    if question_id:
        questions_logic.delete_q_image(question_id)
        return redirect(url_for('show_edit_question_form', question_id=question_id))

    elif answer_id:
        answers_logic.delete_a_image(answer_id)
        return redirect(url_for('edit_answer', answer_id=answer_id))


@app.route("/answer/<answer_id>/vote-<direction>")
@app.route("/question/<question_id>/vote-<direction>")
@account.login_required('user')
def vote(direction, question_id=None, answer_id=None):
    """Modify number of votes of a given question or answer,
    then redirect to corresponding question_page.
    """
    if direction not in ("up", "down"):
        return abort(404)

    if question_id:
        vote_logic.vote_question(direction, question_id=question_id)

        users_logic.change_reputation_q(question_id, direction)

    elif answer_id:
        vote_logic.vote_answer(direction, answer_id=answer_id)
        question_id = answers_logic.get_question_id(answer_id)

        users_logic.change_reputation_a(answer_id, direction)

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/question/<question_id>/new-comment", methods=["POST"])
@app.route("/answer/<answer_id>/new-comment", methods=["POST"])
@account.login_required('user')
def add_comment(question_id=None, answer_id=None):
    """Add comment. Works for question and answer as well."""
    if not question_id:
        question_id = request.args.get('q_id')

    if request.method == 'POST':
        if len(request.form.get('message', '')) >= 5:
            comments_logic.insert_comment(question_id, answer_id, request.form['message'],
                                          session['user_name'], request.args.get('only'))
            flash("Comment successfully added.", "success")
        else:
            flash("Comment was not added. It has to be at least 5 characters long.", "error")

    return redirect(url_for("show_question_page", question_id=question_id))


@app.route("/comment/<comment_id>/<question_id>/edit", methods=["POST"])
@account.login_required('author')
def edit_comment(comment_id, question_id):
    """Edit comment."""
    if request.method == 'POST':
        if len(request.form.get('message', '')) >= 5:
            comments_logic.edit_comment(request.form['message'], comment_id)
            flash("Comment successfully edited.", "success")
        else:
            flash("Comment was not edited. It has to be at least 5 characters long.", "error")

    return redirect(url_for("show_question_page", question_id=question_id))


@app.route("/comment/<comment_id>/<question_id>/edit")
@account.login_required('author')
def delete_comment(comment_id, question_id):
    """Delete comment from question."""
    comments_logic.delete_comment(comment_id)

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/question/<question_id>/manage-tags", methods=["GET", "POST"])
@account.login_required('author')
def manage_tags(question_id):
    """GET: view function of question tag addition page.
    POST: allows choosing from existing tags and adding new ones.
    """
    if request.method == "POST":
        error_message = tag_logic.manage_new_tag_relations(request.form, question_id)

        if error_message == "invalid_input":
            flash("Tag length must be between 2-20 characters and contain only \
            lowercase letters, digits and dashes.", "error")
            return redirect(url_for('show_question_page', question_id=question_id))

        return redirect(url_for('show_question_page', question_id=question_id))

    added_tag_ids_and_names = tag_logic.get_added_tag_ids_and_names(question_id)
    added_tag_names = tuple(id_and_name[1] for id_and_name in added_tag_ids_and_names)
    not_yet_added_tags = tag_logic.get_not_yet_added_tags(tuple(added_tag_names))

    return render_template("tag.html", added_tags=added_tag_ids_and_names,
                           not_yet_added_tags=not_yet_added_tags,
                           question_id=question_id, title="Manage Tags")


@app.route("/question/<question_id>/tag/<tag_id>/delete")
@account.login_required('author')
def delete_tag(question_id, tag_id):
    """Delete tag relation and reload page the link is requested from."""
    if not tag_logic.valid_tag_id(tag_id):
        return abort(404)

    tag_logic.delete_tag(question_id, tag_id)

    if request.args.get('direct') == 'tag_manager':
        return redirect(url_for('manage_tags', question_id=question_id))

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/answer/<answer_id>/<question_id>/accept")
@account.login_required('author')
def accept_answer(answer_id, question_id):
    """Mark answer accepted and de-select any other answers."""
    if (not answers_logic.valid_answer_id(answer_id) or
            not questions_logic.valid_question_id(question_id)):
        return abort(404)

    answers_logic.mark_accepted_exclusively(answer_id, question_id)
    users_logic.change_reputation_a(answer_id, direction="up", acc=True)

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/answer/<answer_id>/<question_id>/remove-accept")
@account.login_required('author')
def remove_accept_mark(answer_id, question_id):
    """Remove accept mark from answer."""
    if (not answers_logic.valid_answer_id(answer_id) or
            not questions_logic.valid_question_id(question_id)):
        return abort(404)

    answers_logic.remove_accept_mark(answer_id)
    users_logic.change_reputation_a(answer_id, direction="down", acc=True)

    return redirect(url_for('show_question_page', question_id=question_id))


@app.route("/user_list")
def show_user_list(criterium='role', order='asc'):
    for key in request.args:
        criterium = key
        order = request.args[key]

    users = users_logic.get_user_list(criterium, order)
    return render_template('user_list.html', users=users, title="Users")


@app.route("/tags/")
def show_tag_page(criterium='tag_name', order='asc'):
    """View function of tag page."""
    for key in request.args:
        criterium = key
        order = request.args[key]

    tags = tag_logic.get_tag_ids_names_question_count(criterium, order)
    return render_template("tag_page.html", tags=tags, title="Existing Tags")


@app.route("/tag/<tag_id>/del")
@account.login_required('admin')
def delete_tag_4ever(tag_id):
    """Delete tag from tag table, irreversibly."""
    if not tag_logic.valid_tag_id(tag_id):
        return abort(404)

    tag_logic.delete_tag_4ever(tag_id)
    tag_name = request.args.get('tag_name') if request.args.get('tag_name') else "Unknown"

    flash("Tag '{}' deleted from existing tags.".format(tag_name), "success")
    return redirect(url_for('show_tag_page'))


@app.route("/tag/<tag_id>/questions")
def show_questions_with_tag(tag_id):
    if not tag_logic.valid_tag_id(tag_id):
        return abort(404)

    questions = tag_logic.get_questions_with_tag(tag_id)
    tag_name = request.args.get('tag_name')
    title = "Questions with tag '{}'".format(tag_name)

    return render_template('list.html', questions=questions, title=title, tag_name=tag_name)


@app.route("/user/<user_id>/")
def show_user_page(user_id):
    """Show user page in detail."""
    user_name = request.args.get('user_name')
    if users_logic.valid_user_by_name(user_name):
        pass
    else:
        user_name = users_logic.valid_user(user_id)
        if not user_name:
            return abort(404)
    title = "AskMate User Page - {}".format(user_name)
    question, answer, comment = users_logic.fetch_user_detail(user_name)
    return render_template('user_page.html', user_name=user_name, title=title,
                           question=question, answer=answer, comment=comment)


@app.route('/register', methods=['GET', 'POST'])
@account.not_loggedin
def registration():
    if request.method == 'POST':
        return account.register_account()

    return render_template('registration.html', title='Registration Page')


@app.route('/login', methods=['GET', 'POST'])
@account.not_loggedin
def login():
    """Show login page upon GET, do login upon POST request."""
    if request.method == 'POST':
        return account.login_user()

    return render_template('login.html', title='Login Page')


@app.route('/logout')
@account.login_required('user')
def logout():
    """Logout user from page."""
    return account.logout_user()


@app.route('/user/<user_id>/del')
@account.login_required('admin')
def delete_user(user_id):
    """Delete user. Admin only function."""
    if not users_logic.valid_user(user_id):
        abort(404)

    user_name = users_logic.delete_user_and_get_name(user_id)

    flash("User '{}' deleted.".format(user_name), "success")

    return redirect(url_for('show_user_list'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(405)
def not_allowed_method(error):
    return render_template('404.html'), 405


if __name__ == "__main__":
    app.secret_key = urandom(12)
    app.run(debug=True, port=2003)
