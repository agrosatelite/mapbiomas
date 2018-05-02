from rsgee.imagemaker import ImageMaker

class BaseProcessor(object):
    def __init__(self):
        self._batch = {}

    def add_image_in_batch(self, filename, data):
        self._batch[filename] = data

    def get_batch(self):
        return self._batch

    def export_batch(self, taskmanager, type=ImageMaker.IMAGE, format='int16', parameters={}):
        export = ImageMaker(taskmanager, parameters)
        for filename, data in self._batch.items():
            export.make_image(filename, data['image'], type, format)
