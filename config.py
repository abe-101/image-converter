# config.py

import os

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Define maximum image size
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB

# Define maximum image dimensions
MAX_IMAGE_DIMENSIONS = (3000, 3000)

# Define minimum image dimensions
MIN_IMAGE_DIMENSIONS = (1400, 1400)

# Define Flask secret key
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'my-secret-key')

UPLOAD_FOLDER = 'uploads'

