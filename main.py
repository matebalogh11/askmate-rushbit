from flask import Flask, redirect, request, url_for, render_template

app = Flask(__name__)


# Common functions
def sort_questions():
    pass


def importdata(filename):
    pass


def exportdata(filename):
    pass


# Routing
@app.route("/")
@app.route("/list")
def show_question_list():  # REQUIRED
    questions = data_manager.read_csv("question.csv")
    return render_template("list.html", questions=questions, title="Questions")


@app.route("/new-question/")
def show_new_question_form():  # REQUIRED
    title = "Ask a new question"
    return render_template("q_form.html", title=title)


@app.route("/question/<question_id>")
def show_question_page(question_id):  # REQUIRED
    pass


@app.route("/question/<question_id>/edit")
def show_edit_question_form(question_id):
    title = "Edit question"
    questions = read_csv("questions.csv")
    question_needed = question[int(question_id) - 1]
    return render_template("q_form.html",
                           title=title,
                           question_needed=question_needed,
                           question_id=question_id)


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    pass


@app.route("/question/<question_id>/new-answer")
def answer_question(question_id):  # REQUIRED
    pass


@app.route("/answer/<answer_id>/delete")
def delete_answer(answer_id):
    pass


@app.route("/question/<question-id>/vote-<direction>")
def vote(direction):
    pass


if __name__ == "__main__":
    app.run(debug=True)
