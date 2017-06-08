
from string import ascii_lowercase, digits

import db


def manage_new_tag_relations(form, question_id):
    """Manage new tag relations: add new valid tags,
    build new relations between question and tag entities as requested.
    """
    new_tag_ids, error_message = process_new_tags(form)

    if error_message:
        return error_message

    selected_tag_ids = process_selected_tags(form)

    tag_ids = []
    if new_tag_ids:
        tag_ids.extend(list(new_tag_ids))
    if selected_tag_ids:
        tag_ids.extend(list(selected_tag_ids))

    if tag_ids:
        insert_tag_relations(question_id, tag_ids)


def process_new_tags(form):
    """Process new tag inputs and build list of tag ids that were allowed to be added.
    In case any of the new input tags were invalid, cancel the whole process.
    """
    existing_tags = get_all_existing_tags()
    error_message = None
    new_tag_ids = None

    tags = (form.get("new_tag1", ''), form.get("new_tag2", ''), form.get("new_tag3", ''))

    new_tags = []
    for tag in tags:
        if len(tag) != 0:
            if not valid_tag_length(tag) or not valid_tag_characters(tag):
                error_message = "invalid_input"
            elif tag not in existing_tags:
                new_tags.append(tag)

    if new_tags:
        new_tag_ids = insert_new_tags(new_tags)

    return new_tag_ids, error_message


def valid_tag_length(tag):
    """Check if request has inputs with the expected keys and value length."""
    if len(tag) <= 20 and len(tag) >= 2:
        return True
    return False


def valid_tag_characters(tag):
    """Check if tag has all the allowed characters only.
    Allowed characters: ascii lowercase, digits, dash.
    """
    allowed_chars = (ascii_lowercase + digits + '-')
    if len(tag) != 0:
        for char in tag:
            if char not in allowed_chars:
                return False
    return True


def process_selected_tags(form):
    """Process selected tags and build list of tag ids.
    Duplicate selections are cancelled.
    """
    selected_tag_ids = None
    selected_tags = []

    if form.get("select_tag1"):
        selected_tags.append(form["select_tag1"])
    if form.get("select_tag2") and form.get("select_tag2") not in selected_tags:
        selected_tags.append(form["select_tag2"])
    if form.get("select_tag3") and form.get("select_tag3") not in selected_tags:
        selected_tags.append(form["select_tag3"])

    if selected_tags:
        selected_tag_ids = get_selected_tag_ids(tuple(selected_tags))

    return selected_tag_ids


def get_all_existing_tags():
    """Return all existing tags as list."""
    SQL = """SELECT name FROM tag;"""
    data = None
    fetch = "col"
    tag_names = db.run_statements(((SQL, data, fetch),))[0]
    return tag_names


def insert_new_tags(new_tags):
    """Insert new tags into tag table and return new tag ids."""
    inserted_tag_ids = []
    for new_tag in new_tags:
        SQL = """INSERT INTO tag (name) VALUES (%s) RETURNING id;"""
        data = (new_tag,)
        fetch = "one"
        inserted_tag_id = db.run_statements(((SQL, data, fetch),))[0][0]
        inserted_tag_ids.append(inserted_tag_id)

    return inserted_tag_ids


def insert_tag_relations(question_id, tag_ids):
    """Insert tag relations."""
    for tag_id in tag_ids:
        SQL = """INSERT INTO question_tag (question_id, tag_id) VALUES (%s, %s);"""
        data = (question_id, tag_id)
        fetch = None
        db.run_statements(((SQL, data, fetch),))


def get_selected_tag_ids(selected_tags):
    """Return selected tag ids."""
    SQL = """SELECT id FROM tag WHERE name in %s;"""
    data = (selected_tags,)
    fetch = "col"
    selected_tag_ids = db.run_statements(((SQL, data, fetch),))[0]
    return selected_tag_ids


def get_added_tag_ids_and_names(question_id):
    """Return tag ids and names, already added to certain question."""
    SQL = """SELECT tag.id, tag.name FROM question_tag AS qt
             JOIN tag ON
                qt.tag_id = tag.id
             WHERE qt.question_id = %s;"""
    data = (question_id,)
    fetch = "all"
    added_tag_ids_names = db.run_statements(((SQL, data, fetch),))[0]
    return added_tag_ids_names


def get_not_yet_added_tags(added_tags):
    """Return tags, not yet added to certain question, which is
    the difference between existing tags and previously added tags.
    """
    fetch = "col"
    if not added_tags:
        SQL = """SELECT name FROM tag;"""
        data = None
    else:
        SQL = """SELECT name FROM tag WHERE name NOT IN %s;"""
        data = (added_tags,)

    not_yet_added_tags = db.run_statements(((SQL, data, fetch),))[0]
    return not_yet_added_tags


def delete_tag(question_id, tag_id):
    """Delete tag relation from question_tag table."""
    SQL = """DELETE FROM question_tag WHERE question_id = %s AND tag_id = %s;"""
    data = (question_id, tag_id)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def valid_tag_id(tag_id):
    """Return True if tag_id found in tag table."""
    SQL = """SELECT id FROM tag WHERE id = %s;"""
    data = (tag_id,)
    fetch = "one"
    try:
        found_id = db.run_statements(((SQL, data, fetch),))[0][0]
    except (DatabaseError, TypeError):
        return False
    return True


def get_tag_ids_names_question_count(criterium, order):
    """Return all existing tag ids, names and number of questions."""
    check_criterium = ("tag_name", "question_count")
    check_order = ("asc", "desc")

    if criterium not in check_criterium or order not in check_order:
        criterium = "tag_name"
        order = "asc"

    SQL = """SELECT t.id, t.name AS tag_name, COUNT(q.id) AS question_count
             FROM tag t
             LEFT JOIN question_tag qt ON qt.tag_id = t.id
             LEFT JOIN question q ON q.id = qt.question_id
             GROUP BY t.id
             ORDER BY {} {};""".format(criterium, order)
    data = None
    fetch = "all"
    tag_ids_names_q_count = db.run_statements(((SQL, data, fetch),))[0]

    return tag_ids_names_q_count


def delete_tag_4ever(tag_id):
    """Delete tag from tag table, irreversibly."""
    SQL = """DELETE FROM tag WHERE id = %s;"""
    data = (tag_id,)
    fetch = None
    db.run_statements(((SQL, data, fetch),))


def get_questions_with_tag(tag_id):
    """Get all questions that have the tag with tag_id."""
    SQL = """SELECT q.id, q.title, q.submission_time, q.view_number, q.vote_number, q.answer_count, q.user_name
             FROM question q
             JOIN question_tag qt ON qt.question_id = q.id
             WHERE qt.tag_id = %s
             ORDER BY q.submission_time DESC;"""
    data = (tag_id,)
    fetch = "all"
    questions_with_tag = db.run_statements(((SQL, data, fetch),))[0]
    return questions_with_tag
