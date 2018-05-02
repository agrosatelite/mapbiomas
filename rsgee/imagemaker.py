# -*- coding: utf-8 -*-

import re

import ee
import enum

from rsgee.conf import settings

class ImageMaker(object):
    IMAGE = 1
    IMAGE_BY_BAND = 2
    IMAGE_BY_REDUCER = 3
    IMAGE_BY_PERIOD = 4

    def __init__(self, task_manager, parameters={}):
        self.__task_manager = task_manager
        self.__parameters = parameters

    def make_image(self, filename, image, type, format='int16'):
        if type == self.IMAGE:
            return self.__make_image(filename, image, format)
        elif type == self.IMAGE_BY_BAND:
            return self.make_image_by_band(filename, image, format)
        elif type == self.IMAGE_BY_REDUCER:
            return self.make_image_by_reducer(filename, image, format)
        elif type == self.IMAGE_BY_PERIOD:
            return self.make_image_by_period(filename, image, format)

    def make_image_by_band(self, filename, image, format='int16'):
        band_names = settings.GENERATION_VARIABLES
        for band in band_names:
            new_filename = "{0}_{1}".format(filename, band)
            self.__make_image(image.select(band), new_filename, format)

    def make_image_by_reducer(self, filename, image, format='int16'):
        band_names = settings.GENERATION_VARIABLES
        dict_reducer_bands = {}
        for band_name in band_names:
            reg = re.match('^(?P<band>.*)_(?P<reducer>.*)$', band_name)
            try:
                band = reg.group('band')
                reducer = reg.group('reducer')
            except Exception, e:
                print e
                continue
            if not dict_reducer_bands.has_key(reducer):
                dict_reducer_bands[reducer] = [band]
            else:
                dict_reducer_bands[reducer].append(band)

        for reducer, bands in dict_reducer_bands.items():
            new_band_names = map(lambda x: "{0}_{1}".format(x, reducer), bands)
            new_filename = "{0}_{1}".format(filename, reducer)
            self.__make_image(image.select(new_band_names), new_filename, format)

    def make_image_by_period(self, filename, image, format='int16'):
        band_names = settings.GENERATION_VARIABLES
        dict_period_bands = {}
        for band_name in band_names:
            for p in settings.GENERATION_PERIODS + settings.GENERATION_EXTRA_PERIODS:
                if band_name.find(p) == 0:
                    try:
                        period = band_name[:len(p)]
                        band = band_name[len(p):]
                    except Exception:
                        continue
                    if not dict_period_bands.has_key(period):
                        dict_period_bands[period] = [band]
                    else:
                        dict_period_bands[period].append(band)

        for period, bands in dict_period_bands.items():
            new_band_names = map(lambda x: "{0}{1}".format(period, x), bands)
            new_filename = "{0}_{1}".format(filename, period)
            self.__make_image(image.select(new_band_names), new_filename, format)

    def __make_image(self, filename, image, format='int16'):
        formats = {
            'byte': image.byte(),
            'int16': image.int16(),
            'int32': image.int32(),
            'float': image.float()
        }

        image = formats[format]
        if not filename:
            filename = image.get('system:index').getInfo()
        image = image.set('system:index', filename)

        print filename

        specifications = {
            'image': image,
            'description': filename,
            'scale': settings.EXPORT_SCALE,
            'maxPixels': settings.EXPORT_MAX_PIXELS,
        }
        if self.__task_manager.get_export_class() == ee.batch.Export.image.toCloudStorage:
            bucket = self.__parameters['bucket']
            code = "{directory}/{filename}".format(directory=self.__parameters['directory'].strip("/"), filename=filename)
            specifications.update({
                'bucket': bucket,
                'fileNamePrefix': code,
            })
        elif self.__task_manager.get_export_class() == ee.batch.Export.image.toAsset:
            code = "{asset}/{directory}/{filename}".format(asset=self.__parameters['asset'].strip("/"), directory=self.__parameters['directory'].strip("/"), filename=filename)
            specifications.update({
                'assetId': code,
            })
        self.__task_manager.add_task(code, specifications)
