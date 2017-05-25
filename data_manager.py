
import config
import psycopg2


def connect_db(func):
    def wrapper(*args, **kwargs):
        """Return connection object if established. Set autocommit to True."""
        DNS = "dbname='{}' host='{}' user='{}' password='{}'".format(config.DB, config.HOST, config.USER, config.PW)
        conn = None
        try:
            conn = psycopg2.connect(DNS)
            conn.autocommit = True
        except Exception as e:
            print("Cannot connect. Invalid credentials.")
            print(e, end='')
        else:
            print("Connected to database '{}' on '{}' as user '{}'.".format(config.DB, config.HOST, config.USER))
            result = func(conn, *args, **kwargs)
            return result
        finally:
            if conn:
                conn.close()
    return wrapper


@connect_db
def get_questions(conn, criterium, order):
    """Return questions list for list.html"""

    check_criterium = ("title", "submission_time", "view_number", "vote_number", "answer_count")
    check_order = ("asc", "desc")

    if criterium not in check_criterium or order not in check_order:
        criterium = "submission_time"
        order = "desc"

    SQL = """SELECT id, title, submission_time, view_number, vote_number, answer_count
             FROM question ORDER BY {} {};""".format(criterium, order)

    with conn.cursor() as cursor:
        cursor.execute(SQL)
        result = cursor.fetchall()
    return result


@connect_db
def get_question_details(conn, question_id):
    SQL = """SELECT title, message, image FROM question WHERE id = %s;"""
    data = (question_id,)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
        result = cursor.fetchone()
    return result


@connect_db
def get_all_for_question(conn, question_id):
    SQL_q = """ SELECT * FROM question WHERE id = %s;"""
    SQL_a = """ SELECT * FROM answer WHERE question_id = %s ORDER BY vote_number DESC, submission_time DESC;"""
    data = (question_id, )
    with conn.cursor() as cursor:
        cursor.execute(SQL_q, data)
        result_q = cursor.fetchone()
        cursor.execute(SQL_a, data)
        result_a = cursor.fetchall()
    return result_q, result_a


@connect_db
def update_view_count(conn, question_id):
    SQL = """UPDATE question SET view_number = view_number + 1 WHERE id = %s;"""
    data = (question_id, )
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)


@connect_db
def insert_question(conn, new_question):
    """Insert question."""
    SQL = """INSERT INTO question (submission_time, view_number, vote_number,
                                   title, message, image, answer_count)
             VALUES (%s, %s, %s, %s, %s, %s, %s)
             RETURNING id, image;"""
    data = (new_question[0], new_question[1], new_question[2], new_question[3],
            new_question[4], new_question[5], new_question[6])
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
        result = cursor.fetchone()
    return result


@connect_db
def rename_question_image(conn, filename, question_id):
    """"""
    SQL = """UPDATE question SET image = %s WHERE id = %s;"""
    data = (filename, question_id)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)


@connect_db
def update_answer_counter(conn, question_id, operation):
    """"""
    number = 1 if operation == "ADD" else 0
    if number:
        SQL = """UPDATE question SET answer_count = answer_count + 1 WHERE id = %s;"""
    else:
        SQL = """UPDATE question SET answer_count = answer_count - 1 WHERE id = %s;"""

    data = (question_id,)

    with conn.cursor() as cursor:
        cursor.execute(SQL, data)


@connect_db
def insert_answer(conn, new_answer):
    """Insert answer."""
    SQL = """INSERT INTO answer (submission_time, vote_number,
                                   question_id, message, image)
             VALUES (%s, %s, %s, %s, %s)
             RETURNING id, image;"""
    data = (new_answer[0], new_answer[1], new_answer[2], new_answer[3],
            new_answer[4])
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
        result = cursor.fetchone()
    return result


@connect_db
def rename_answer_image(conn, filename, answer_id):
    """"""
    SQL = """UPDATE answer SET image = %s WHERE id = %s;"""
    data = (filename, answer_id)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)


@connect_db
def delete_question(conn, question_id):
    """"""
    SQL = """DELETE FROM question WHERE id = %s;"""
    data = (question_id, )

    with conn.cursor() as cursor:
        cursor.execute(SQL, data)


@connect_db
def fetch_answer_images(conn, question_id):
    SQL = """SELECT image from answer WHERE question_id = %s;"""
    data = (question_id,)

    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
        result = cursor.fetchone()
    return result


@connect_db
def delete_answer_by_id(conn, answer_id):
    """Deletes answer by answer ID."""
    SQL = """DELETE FROM answer WHERE id = %s;"""
    data = (answer_id,)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)


@connect_db
def get_answer_image(conn, answer_id):
    """Deletes image of an answer."""
    SQL = """SELECT image, question_id FROM answer WHERE id = %s;"""
    data = (answer_id,)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
        result = cursor.fetchone()
    return result


@connect_db
def get_answer_details(conn, answer_id):
    SQL = """SELECT id FROM answer WHERE id = %s;"""
    data = (answer_id,)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
        result = cursor.fetchone()
    return result


@connect_db
def update_question(conn, q_form, question_id):
    """Insert question."""
    SQL = """UPDATE question SET title = %s, message = %s WHERE id = %s;"""
    data = (q_form['q_title'], q_form['q_desc'], question_id)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)


@connect_db
def get_image_for_update_question(conn, question_id):
    """Get image name for question with question_id."""
    SQL = """SELECT image FROM question WHERE id = %s;"""
    data = (question_id,)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
        result = cursor.fetchone()[0]
    return result


@connect_db
def change_vote_count(conn, direction, question_id=None, answer_id=None):
    """Change vote count in direction. 'up' as add one, 'down' as reduce by one."""
    if question_id:
        table = "question"
        the_id = question_id
    elif answer_id:
        table = "answer"
        the_id = answer_id
        SQL2 = """SELECT question_id FROM answer WHERE id = %s;"""
        data2 = (answer_id,)

    if direction == "up":
        SQL1 = """UPDATE {} SET vote_number = vote_number + 1 WHERE id = %s;""".format(table)
    elif direction == "down":
        SQL1 = """UPDATE {} SET vote_number = vote_number - 1 WHERE id = %s;""".format(table)
    data1 = (the_id,)

    with conn.cursor() as cursor:
        cursor.execute(SQL1, data1)
        if answer_id:
            cursor.execute(SQL2, data2)
            result = cursor.fetchone()[0]

    if answer_id:
        return result


@connect_db
def get_question_image(conn, question_id):
    """Deletes image of a question."""
    SQL1 = """SELECT image FROM question WHERE id = %s;"""
    SQL2 = """UPDATE question SET image = NULL WHERE id = %s;"""
    data = (question_id,)

    with conn.cursor() as cursor:
        cursor.execute(SQL1, data)
        result = cursor.fetchone()[0]
        cursor.execute(SQL2, data)
    return result


@connect_db
def get_5_questions(conn):
    """Return 5 most recent questions."""
    SQL = """SELECT id, title, submission_time, view_number, vote_number, answer_count
             FROM question ORDER BY submission_time DESC LIMIT 5;"""
    with conn.cursor() as cursor:
        cursor.execute(SQL)
        result = cursor.fetchall()
    return result


@connect_db
def get_search_results(conn, phrase):
    """Return search results based on search phrase as tuple: questions 2d list, answers 2d list.
    In question table [0] index as primary key is connected to [3] index as foreign key in answer table.
    """
    SQL1 = """SELECT id, title, submission_time, view_number, vote_number, answer_count FROM question
             WHERE title ILIKE %s ORDER BY vote_number;"""
    SQL2 = """SELECT id, submission_time, vote_number, question_id, message FROM answer
            WHERE message ILIKE %s ORDER BY vote_number DESC;"""
    data = ('%' + phrase + '%',)
    with conn.cursor() as cursor:
        cursor.execute(SQL1, data)
        result_questions = cursor.fetchall()
        cursor.execute(SQL2, data)
        result_answers = cursor.fetchall()
    return result_questions, result_answers


@connect_db
def get_additional_questions(conn, missing_question_ids):
    """Return those questions that are still missing to serve as parent question
    for answers found by phrase, even though these questions do not have the phrase in their title/description.
    """
    if not missing_question_ids:
        missing_question_ids = (None,)

    SQL = """SELECT id, title, submission_time, view_number, vote_number, answer_count FROM question
             WHERE id IN %s;"""
    data = (missing_question_ids,)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
        result = cursor.fetchall()
    return result
