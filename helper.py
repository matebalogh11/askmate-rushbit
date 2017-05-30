
from datetime import datetime


def create_timestamp():
    """Create timestamp."""
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    return timestamp


def allowed_extension(filename):
    """Takes a filename and validates by extension.
    @filename string: filename string.
    @return bool: True if file extension in allowed extensions, else False.
    """
    ALLOWED_EXTENSIONS = ['jpeg', 'jpg', 'png', 'gif']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
