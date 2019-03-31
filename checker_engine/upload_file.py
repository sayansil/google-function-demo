import os

class uploadfile():
    def __init__(self, name, type=None, not_allowed_msg=''):
        self.name = name
        self.type = type
        self.not_allowed_msg = not_allowed_msg
        self.url = "data/%s" % name
        self.thumbnail_url = "thumbnail/%s" % name


    def is_image(self):
        fileName, fileExtension = os.path.splitext(self.name.lower())

        if fileExtension in ['.jpg', '.png', '.jpeg', '.bmp']:
            return True

        return False


    def get_file(self):
        if self.type != None:
            # POST an image
            if self.type.startswith('image'):
                return {"name": self.name,
                        "type": self.type,
                        "url": self.url,
                        "thumbnailUrl": self.thumbnail_url}

            # POST an normal file
            elif self.not_allowed_msg == '':
                return {"name": self.name,
                        "type": self.type,
                        "url": self.url}

            # File type is not allowed
            else:
                return {"error": self.not_allowed_msg,
                        "name": self.name,
                        "type": self.type}

        # GET image from disk
        elif self.is_image():
            return {"name": self.name,
                    "url": self.url,
                    "thumbnailUrl": self.thumbnail_url}

        # GET normal file from disk
        else:
            return {"name": self.name,
                    "url": self.url}
