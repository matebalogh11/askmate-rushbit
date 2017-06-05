
from datetime import datetime


def create_timestamp():
    """Create timestamp, suitable for database timestamp format."""
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    return timestamp


def allowed_extension(filename):
    """Takes a filename string and validates extension, returning boolean."""
    ALLOWED_EXTENSIONS = ['jpeg', 'jpg', 'png', 'gif']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
