from flask import Flask, request, jsonify, send_from_directory
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename
import threading

import os

# Create the Flask application
app = Flask(__name__)
app.config.from_pyfile("config.py")

# Ensure the upload directory exists
if not os.path.isdir(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Define a function to check if a file is an allowed image type
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route("/convert", methods=["POST"])
def convert_image():
    # Check if an image file was uploaded
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files["image"]

    # Check if the uploaded file has an allowed extension
    if not allowed_file(image.filename):
        return jsonify({"error": "Invalid file type"}), 400

    # Generate a secure filename for the uploaded image
    filename = secure_filename(image.filename)

    # Save the uploaded image to the UPLOAD_FOLDER directory
    image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    # Open the uploaded image and check its size
    with Image.open(os.path.join(app.config["UPLOAD_FOLDER"], filename)) as img:
        # Check if the image is square
        if img.width != img.height:
            # Crop the image to make it square
            size = min(img.width, img.height)
            left = (img.width - size) // 2
            upper = (img.height - size) // 2
            right = left + size
            lower = upper + size
            img = img.crop((left, upper, right, lower))

        # Check if the image is within the size limit
        if img.width > 3000 or img.height > 3000:
            # Resize the image to fit within the size limit
            img.thumbnail((3000, 3000), Image.ANTIALIAS)

        # Check if the image meets the minimum size requirement
        if img.width < 1400 or img.height < 1400:
            # Resize the image to meet the minimum size requirement
            img = img.resize((1400, 1400), Image.ANTIALIAS)

        # Check if the image meets the maximum file size requirement
        file_size = os.path.getsize(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        if file_size > 2 * 1024 * 1024:
            # Compress the image to reduce file size
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename), optimize=True, quality=80)
            file_size = os.path.getsize(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    # Generate a URL to the converted image
    converted_url = f"http://localhost:5000/uploads/{filename}"

    # Delete the uploaded image after 5 minutes
    threading.Timer(60, lambda: os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))).start()

    # Return the URL to the converted image
    return jsonify({"url": converted_url}), 200


@app.route('/uploads/<filename>')
def serve_converted_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
