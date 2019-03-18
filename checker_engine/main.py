from flask import Flask, render_template
from google.cloud import storage

app = Flask(__name__)

# Home page
@app.route('/')
def home():
    upload_blob('img_check_bucket','tty.jpg' , 'test_456')
    return render_template('demo_home.html')

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    print '1'
    bucket = storage_client.get_bucket(bucket_name)
    print '2'
    blob = bucket.blob(destination_blob_name)
    print '3'

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))