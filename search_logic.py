
import re
import db


def get_questions_with_answers(phrase):
    """Get questions with answers, where phrase is found.
    Does hightlighting by adding HTML code.
    Does original input HTML basic escaping.
    """
    i_phrase = re.compile(re.escape(phrase), re.IGNORECASE)
    questions, answers = get_search_results(phrase)
    missing_question_ids = tuple(get_missing_q_ids_and_do_ans_highlight(questions, answers, i_phrase, phrase))
    questions_hightlight_and_append_answers(questions, answers, i_phrase, phrase)
    additional_questions = get_additional_questions(missing_question_ids)

    for i in range(len(additional_questions)):
        for answer in answers:
            if questions[i][0] == answer[3]:
                additional_questions[i][6].append(answer)

    questions.extend(additional_questions)
    return questions


def questions_hightlight_and_append_answers(questions, answers, i_phrase, phrase):
    """Transform each question into list and append an empty list,
    which will store answers.
    """
    for i in range(len(questions)):
        questions[i] = list(questions[i])
        questions[i].append([])
        questions[i][1] = questions[i][1].replace('<', '')
        questions[i][1] = questions[i][1].replace('>', '')
        questions[i][1] = i_phrase.sub('<span class="highlight">{}</span>'.format(phrase), questions[i][1])
        for answer in answers:
            if questions[i][0] == answer[3]:
                questions[i][6].append(answer)


def get_missing_q_ids_and_do_ans_highlight(questions, answers, i_phrase, phrase):
    """Return missing_question_ids and do hightlighting in the meanwhile"""
    missing_question_ids = []
    question_ids = [question[0] for question in questions]

    for i, answer in enumerate(answers):
        answers[i] = list(answers[i])

        answers[i][4] = answers[i][4].replace('<', '')
        answers[i][4] = answers[i][4].replace('>', '')
        answers[i][4] = i_phrase.sub('<span class="highlight">{}</span>'.format(phrase), answers[i][4])

        if answer[3] not in question_ids:
            missing_question_ids.append(answer[3])

    return missing_question_ids


def get_search_results(phrase):
    """Return search results based on search phrase as tuple: questions 2d list, answers 2d list."""
    SQL1 = """SELECT id, title, submission_time, view_number, vote_number, answer_count FROM question
             WHERE title ILIKE %s ORDER BY vote_number;"""
    SQL2 = """SELECT id, submission_time, vote_number, question_id, message FROM answer
            WHERE message ILIKE %s ORDER BY vote_number DESC;"""
    data = ('%' + phrase + '%',)
    fetch = "all"

    questions_and_answers = db.run_statements(((SQL1, data, fetch), (SQL2, data, fetch)))
    return questions_and_answers


def get_additional_questions(missing_question_ids):
    """Return those questions that are still missing to serve as parent questions
    for answers found by phrase, even though these questions do not have the phrase in title.
    """
    if not missing_question_ids:
        missing_question_ids = (None,)

    SQL = """SELECT id, title, submission_time, view_number, vote_number, answer_count FROM question
             WHERE id IN %s;"""
    data = (missing_question_ids,)
    fetch = "all"

    missing_questions = db.run_statements(((SQL, data, fetch),))[0]

    for i in range(len(missing_questions)):
        missing_questions[i] = list(missing_questions[i])
        missing_questions[i].append([])

    return missing_questions
