
from datetime import datetime


def create_timestamp():
    """Create timestamp, suitable for database timestamp format."""
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    return timestamp


def allowed_extension(filename):
    """Takes a filename string and validates extension, returning boolean."""
    ALLOWED_EXTENSIONS = ['jpeg', 'jpg', 'png', 'gif']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def valid_request(q_form):
    """Return True if HTTP request was sent with at least 10
    characters long title and description, else False"""
    title_length = len(q_form.get('q_title', ''))
    desc_length = len(q_form.get('q_desc', ''))
    if title_length >= 10 and desc_length >= 10:
        return True
    return False
