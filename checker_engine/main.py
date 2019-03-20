from flask import Flask, render_template, request
from werkzeug import secure_filename
import cloudstorage as gcs

app = Flask(__name__)

bucket = '/img_check_bucket/'

FEEDBACK_POSITIVE = 'Done'
FEEDBACK_NEGATIVE = 'Could not complete upload'

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Submission
@app.route('/', methods=['POST'])
def upload_image():
    try:
        file = request.files['file']
        filename = bucket + secure_filename(file.filename)
        gcs_file = gcs.open(filename, 'w',
                            content_type='image/jpeg',
                            retry_params=gcs.RetryParams(initial_delay=0.2,
                                            max_delay=5.0,
                                            backoff_factor=2,
                                            max_retry_period=15))
        gcs_file.write(file.read())
        gcs_file.close()
        return render_template('home.html',
            submit_feedback=FEEDBACK_POSITIVE)
    except:
        return render_template('home.html',
            submit_feedback=FEEDBACK_NEGATIVE)
