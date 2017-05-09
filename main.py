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
def show_questions():  # REQUIRED
    pass


@app.route("/new-question/")
def new_question():  # REQUIRED
    pass


@app.route("/question/<question_id>")
def show_single_question(question_id):  # REQUIRED
    pass


@app.route("/question/<question_id>/edit")
def edit_question(question_id):
    pass


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