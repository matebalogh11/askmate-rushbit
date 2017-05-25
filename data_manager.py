
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
    SQL = """ SELECT title, message, image FROM question WHERE id = %s """
    data = (question_id,)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
        result = cursor.fetchone()
    return result


@connect_db
def get_all_for_question(conn, question_id):
    SQL_q = """ SELECT * FROM question WHERE id = %s """
    SQL_a = """ SELECT * FROM answer WHERE question_id = %s ORDER BY vote_number DESC, submission_time DESC"""
    data = (question_id, )
    with conn.cursor() as cursor:
        cursor.execute(SQL_q, data)
        result_q = cursor.fetchone()
        cursor.execute(SQL_a, data)
        result_a = cursor.fetchall()
    return result_q, result_a


@connect_db
def update_view_count(conn, question_id):
    SQL = """ UPDATE question SET view_number = view_number + 1 WHERE id = %s """
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
        SQL = """UPDATE question SET answer_count = answer_count + 1 WHERE id = %s"""
    else:
        SQL = """UPDATE question SET answer_count = answer_count - 1 WHERE id = %s"""

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
    SQL = """DELETE FROM question WHERE id = %s"""
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
    SQL = """DELETE FROM answer WHERE id = %s"""
    data = (answer_id,)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)


@connect_db
def get_answer_image(conn, answer_id):
    """Deletes image of an answer."""
    SQL = """SELECT image, question_id FROM answer WHERE id = %s"""
    data = (answer_id,)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
        result = cursor.fetchone()
    return result


@connect_db
def get_answer_details(conn, answer_id):
    SQL = """ SELECT id FROM answer WHERE id = %s """
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
    SQL1 = """SELECT image FROM question WHERE id = %s"""
    SQL2 = """UPDATE question SET image = NULL WHERE id = %s"""
    data = (question_id,)

    with conn.cursor() as cursor:
        cursor.execute(SQL1, data)
        result = cursor.fetchone()[0]
        cursor.execute(SQL2, data)
    return result


@connect_db
def insert_comment(conn, new_comment):
    SQL = """INSERT INTO comment (question_id, answer_id,
                                    message, submission_time, edited_count)
            VALUES (%s, %s, %s, %s, %s)"""
    data = (new_comment[2], new_comment[0], new_comment[1], new_comment[3], new_comment[4])
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)


@connect_db
def retrieve_comments(conn, question_id, answer_ids=None):
    SQL_q = """ SELECT * FROM comment WHERE question_id = question_id ORDER BY submission_time """
    SQL_a = """ SELECT * FROM comment WHERE answer_id IN %s ORDER BY submission_time """
    data = (answer_ids,)
    with conn.cursor() as cursor:
        cursor.execute(SQL_q)
        result_q = cursor.fetchall()
        if answer_ids:
            cursor.execute(SQL_a, data)
            result_a = cursor.fetchall()
        else:
            result_a = None
    return result_q, result_a


@connect_db
def edit_comment(conn, new_comment, comment_id, submission_time):
    SQL = """UPDATE comment SET message = %s, edited_count = edited_count + 1, submission_time = %s
             WHERE id = %s;"""
    data = (new_comment, submission_time, comment_id)
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)


@connect_db
def delete_comment(conn, comment_id):
    SQL = """DELETE FROM comment WHERE id = %s"""
    data = (comment_id, )
    with conn.cursor() as cursor:
        cursor.execute(SQL, data)
