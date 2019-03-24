from flask import Flask, render_template, request
from werkzeug import secure_filename
import cloudstorage as gcs

app = Flask(__name__)

bucket = '/img_check_bucket/'

# Home pagetext
@app.route('/')
def home():
    names = get_filenames()
    images = []
    print names
    for name in names:
        gcs_file = gcs.open(name)
        image_raw = gcs_file.read()
        gcs_file.close()

        image = {
            'image':"data:image/png;base64, "+str(image_raw).encode('base64'),
            'name':name[18:]
            }
        images.append(image)

    return render_template('home.html',images=images)

def get_filenames():
    page_size = 1
    stats = gcs.listbucket(bucket , max_keys=page_size)
    names = []
    while True:
        count = 0
        for stat in stats:
            count += 1
            names.append(repr(stat.filename)[1:-1])
        if count != page_size or count == 0:
                break
        stats = gcs.listbucket(bucket , max_keys=page_size,
                            marker=stat.filename)
    return names
