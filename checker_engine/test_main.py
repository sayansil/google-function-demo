# -*- coding: utf-8 -*-
#
# jQuery File Upload Plugin GAE Python Example
# https://github.com/blueimp/jQuery-File-Upload
#
# Copyright 2011, Sebastian Tschan
# https://blueimp.net
#
# Licensed under the MIT license:
# https://opensource.org/licenses/MIT
#

from google.appengine.api import memcache, images
import json
import os
import re
import urllib
import webapp2
from werkzeug import secure_filename
import cloudstorage as gcs

DEBUG=os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
WEBSITE = 'https://imgchecker.000webhostapp.com/'
MIN_FILE_SIZE = 1  # bytes
# Max file size is memcache limit (1MB) minus key size minus overhead:
MAX_FILE_SIZE = 999000  # bytes
IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')
ACCEPT_FILE_TYPES = IMAGE_TYPES
THUMB_MAX_WIDTH = 80
THUMB_MAX_HEIGHT = 80
THUMB_SUFFIX = '.'+str(THUMB_MAX_WIDTH)+'x'+str(THUMB_MAX_HEIGHT)+'.png'
EXPIRATION_TIME = 300  # seconds
# If set to None, only allow redirects to the referer protocol+host.
# Set to a regexp for custom pattern matching against the redirect value:
REDIRECT_ALLOW_TARGET = None

class CORSHandler(webapp2.RequestHandler):
    def cors(self):
        headers = self.response.headers
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] =\
            'OPTIONS, HEAD, GET, POST, DELETE'
        headers['Access-Control-Allow-Headers'] =\
            'Content-Type, Content-Range, Content-Disposition'

    def initialize(self, request, response):
        super(CORSHandler, self).initialize(request, response)
        self.cors()

    def json_stringify(self, obj):
        return json.dumps(obj, separators=(',', ':'))

    def options(self, *args, **kwargs):
        pass

class UploadHandler(CORSHandler):
    def validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'File is too big'
        elif not ACCEPT_FILE_TYPES.match(file['type']):
            file['error'] = 'Filetype not allowed'
        else:
            return True
        return False

    def validate_redirect(self, redirect):
        if redirect:
            if REDIRECT_ALLOW_TARGET:
                return REDIRECT_ALLOW_TARGET.match(redirect)
            referer = self.request.headers['referer']
            if referer:
                from urlparse import urlparse
                parts = urlparse(referer)
                redirect_allow_target = '^' + re.escape(
                    parts.scheme + '://' + parts.netloc + '/'
                )
            return re.match(redirect_allow_target, redirect)
        return False

    def get_file_size(self, file):
        file.seek(0, 2)  # Seek to the end of the file
        size = file.tell()  # Get the position of EOF
        file.seek(0)  # Reset the file position to the beginning
        return size

    def write_blob(self, data, info):
        key = urllib.quote(info['type'].encode('utf-8'), '') +\
            '/' + str(hash(data)) +\
            '/' + urllib.quote(info['name'].encode('utf-8'), '')

        if IMAGE_TYPES.match(info['type']):
            try:
                thumbnail_key = key + THUMB_SUFFIX
                bucket = '/img_check_bucket/'
                file = urllib.quote(info['name'].encode('utf-8'), '')
                filename = bucket + file
                gcs_file = gcs.open(filename, 'w',
                                    content_type='image/jpeg',
                                    retry_params=gcs.RetryParams(initial_delay=0.2,
                                                    max_delay=5.0,
                                                    backoff_factor=2,
                                                    max_retry_period=15))
                gcs_file.write(data)
                gcs_file.close()


            except: #Failed to add image
                thumbnail_key = None
        return (key, thumbnail_key)

    def handle_upload(self):
        for name, fieldStorage in self.request.POST.items():
            if type(fieldStorage) is unicode:
                continue
            result = {}
            result['name'] = urllib.unquote(fieldStorage.filename)
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            if self.validate(result):
                key, thumbnail_key = self.write_blob(
                    fieldStorage.value,
                    result
                )

    def head(self):
        pass

    def get(self):
        self.redirect(WEBSITE)

    def post(self):
        if (self.request.get('_method') == 'DELETE'):
            return self.delete()
        result = {'files': self.handle_upload()}
        s = self.json_stringify(result)
        redirect = self.request.get('redirect')
        if self.validate_redirect(redirect):
            return self.redirect(str(
                redirect.replace('%s', urllib.quote(s, ''), 1)
            ))
        if 'application/json' in self.request.headers.get('Accept'):
            self.response.headers['Content-Type'] = 'application/json'
        self.response.write(s)

class FileHandler(CORSHandler):
    def get(self, content_type, data_hash, file_name):
        return self.error(404)

    def delete(self, content_type, data_hash, file_name):
        return self.error(404)

app = webapp2.WSGIApplication(
    [
        ('/', UploadHandler),
        ('/(.+)/([^/]+)/([^/]+)', FileHandler)
    ],
    debug=DEBUG
)
