from flask import Flask, redirect, request, url_for, render_template
from data_manager import read_csv, write_csv

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
    """ Displays list of questions as a table and an 'Ask a question' button. """

    questions = data_manager.read_csv("question.csv")

    return render_template("list.html", questions=questions, title="Questions")


@app.route("/new-question/")
def show_new_question_form():  # REQUIRED
    title = "Ask a new question"
    return render_template("q_form.html", title=title)


@app.route("/question/<question_ID>")
def show_question_page(question_ID):  # REQUIRED
    q_data = read_csv("question.csv")
    a_data = read_csv("answer.csv")

    answers = [item for item in a_data if question_ID in item]
    answers = sorted(answers, key=lambda x: x[2], reverse=True)
    for question in q_data:
        if question[0] == question_ID:
            return render_template("question.html", question_ID=question_ID, answers=answers, question=question,
                                   title="AskMate - Question" + question_ID)
    return "There is no such question."


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
    """ Deletes question based on its question_id and corresponding answers
    upon hitting delete button on a question page and redirects to the root page. """

    questions = data_manager.read_csv("question.csv")
    answers = data_manager.read_csv("answer.csv")

    for question in questions:
        if question[0] == question_id:
            questions.remove(question)
            for answer in answers:
                if answer[3] == question_id:
                    answers.remove(answer)

    write_csv("question.csv", questions)
    write_csv("answer.csv", answers)

    return redirect(url_for("show_question_list"))


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def answer_question():
    if request.method == "POST":
        comment = request.form["answer"]
        answer = [a_id, time, 0, question_id, comment]
        if request.form["image"]:
            answer.append(request.form["image"])
        all_answers = read_csv("answer.csv")
        all_answers.append(answer)
        write_csv("answer.csv")
        return redirect(url_for("show_question_page"))
    else:
        return render_template("a_form.html")


@app.route("/answer/<answer_id>/delete")
def delete_answer(answer_id):
    """Deletes an answer based on its answer_id and returns to the 
    corresponding questions page. """

    answers = data_manager.read_csv("answer.csv")

    for answer in answer:
        if answer[0] == answer_id:
            answers.remove(answer)
            question_id = answer[3]

    write_csv("answer.csv", answers)

    return redirect(url_for('show_question_page(question_id)'))


@app.rout("/answer=<answer_id>/vote-<direction>")
@app.route("/question/<question-id>/vote-<direction>")
def vote(question_id=None, answer_id=None, direction):
    """ Modifies number of votes of a given question or answer and
    returns to the corresponding question_page. """

    if question_id:
        questions = data_manager.read_csv("question.csv")
        for question in questions:
            if question[0] == question_id:
                if direction == "up":
                    question[3] += 1
                elif direction == "down":
                    question[3] -= 1

        write_csv("question.csv", questions)

    elif answer_id:
        answers = data_manager.read_csv("answer.csv")
        for answer in answers:
            if answer[0] == answer_id:
                question_id = answer[3]
                if direction == "up":
                    answer[2] += 1
                elif direction == "down":
                    answer[2] -= 1

        write_csv("answer.csv", answers)

    return redirect(url_for("show_question_page(question_id"))


if __name__ == "__main__":
    app.run(debug=True)
