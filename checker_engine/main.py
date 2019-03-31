import os
import PIL
import simplejson
import traceback

from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug import secure_filename
import cloudstorage as gcs

from upload_file import uploadfile


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['UPLOAD_FOLDER'] = '/data/'
app.config['THUMBNAIL_FOLDER'] = 'data/thumbnail/'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['gif', 'png', 'jpg', 'jpeg', 'bmp'])
IGNORED_FILES = set(['.gitignore'])
BUCKET = '/img_check_bucket/'

bootstrap = Bootstrap(app)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    files = request.files['file']

    if files:
        filename = secure_filename(files.filename)
        mime_type = files.content_type

        if not allowed_file(files.filename):
            result = uploadfile(name=filename, type=mime_type, not_allowed_msg="File type not allowed")

        else:
            bucket_filename = BUCKET + secure_filename(filename)
            gcs_file = gcs.open(bucket_filename, 'w',
                                content_type='image/jpeg',
                                retry_params=gcs.RetryParams(initial_delay=0.2,
                                                max_delay=5.0,
                                                backoff_factor=2,
                                                max_retry_period=15))
            gcs_file.write(files.read())
            gcs_file.close()
            print bucket_filename

            # return json for js call back
            result = uploadfile(name=filename, type=mime_type)

        return simplejson.dumps({"files": [result.get_file()]})


# serve static files
@app.route("/thumbnail/<string:filename>", methods=['GET'])
def get_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename=filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
