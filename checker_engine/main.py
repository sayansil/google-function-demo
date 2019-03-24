from flask import Flask, render_template, request
from werkzeug import secure_filename
import cloudstorage as gcs
import json
import re
import urllib

app = Flask(__name__)

bucket = '/img_check_bucket/'
MIN_FILE_SIZE = 1  # bytes
MAX_FILE_SIZE = 999000  # bytes
IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')
ACCEPT_FILE_TYPES = IMAGE_TYPES

# Home page
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/', methods=['POST'])
def addFiles():
    for file in request.files.getlist("files[]"):
        result = {}
        result['name'] = secure_filename(file.filename)
        result['type'] = file.content_type
        result['size'] = get_file_size(file)
        if validate(result):
            write_blob(
                file.read(),
                result
            )
    return render_template('home.html')

def json_stringify(obj):
    return json.dumps(obj, separators=(',', ':'))

def validate(file):
    if file['size'] < MIN_FILE_SIZE:
        file['error'] = 'File is too small'
    elif file['size'] > MAX_FILE_SIZE:
        file['error'] = 'File is too big'
    elif not ACCEPT_FILE_TYPES.match(file['type']):
        file['error'] = 'Filetype not allowed'
    else:
        return True
    return False

def get_file_size(file):
    file.seek(0, 2)  # Seek to the end of the file
    size = file.tell()  # Get the position of EOF
    file.seek(0)  # Reset the file position to the beginning
    return size

def write_blob(data, info):
    key = urllib.quote(info['type'].encode('utf-8'), '') +\
        '/' + str(hash(data)) +\
        '/' + urllib.quote(info['name'].encode('utf-8'), '')

    if IMAGE_TYPES.match(info['type']):
        try:
            file = urllib.quote(info['name'].encode('utf-8'), '')
            filename = bucket + file
            print filename
            gcs_file = gcs.open(filename, 'w',
                                content_type='image/jpeg',
                                retry_params=gcs.RetryParams(initial_delay=0.2,
                                                max_delay=5.0,
                                                backoff_factor=2,
                                                max_retry_period=15))
            gcs_file.write(data)
            gcs_file.close()
        except: #Failed to add image
            print "GCloud Error"