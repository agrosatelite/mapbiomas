"""
Invokes django-admin when the django module is run as a script.
Example: python -m django check
"""

# -*- coding: utf-8 -*-
import ee

from rsgee.imagemaker import ImageMaker
from rsgee.conf import settings
from rsgee.db import DatabaseManager
from rsgee.db.models import TaskTypes

from rsgee.imagecollection import ImageCollection
from rsgee.featurecollection import FeatureCollection
from rsgee.taskmanager import TaskManager

class Manage(object):
    def execute_commands(self, command):
        if command in ['-r', 'run']:
            self.run()
        elif command in ['-h', 'help']:
            self.help()
        else:
            self.help()

    def run(self):

        ee.Initialize()

        landsat_collection = ImageCollection(settings.COLLECTION)
        feature_collection = FeatureCollection(settings.FEATURE_COLLECTION).filter_by_wrs(settings.FEATURE_WRS,
                                                                                          settings.FEATURE_WRS_SELECTED,
                                                                                          settings.FEATURE_WRS_FILTER)

        session = DatabaseManager().get_session()

        taskmanager = TaskManager(settings.EXPORT_CLASS, settings.EXPORT_TASKS[-1], session, settings.EXPORT_MAX_TASKS,
                                  settings.EXPORT_INTERVAL, settings.EXPORT_MAX_ERRORS)

        if TaskTypes.GENERATION in settings.EXPORT_TASKS:
            generator = settings.GENERATOR_CLASS(landsat_collection, feature_collection, settings.GENERATION_BANDS,
                                                 settings.GENERATION_REDUCERS, settings.YEARS, settings.GENERATION_OFFSET,
                                                 settings.GENERATION_PERIODS, settings.GENERATION_CLIP_GEOMETRY, settings.GENERATION_APPLY_BRDF, settings.GENERATION_APPLY_MASK)
            generator.run()
            if not TaskTypes.CLASSIFICATION in settings.EXPORT_TASKS:
                for export_type in settings.EXPORT_TYPES:
                    generator.export_batch(taskmanager, export_type, settings.GENERATION_TYPE,
                                           {'bucket': settings.EXPORT_BUCKET, 'asset': settings.EXPORT_ASSET,
                                            'directory': settings.EXPORT_DIRECTORY})

        if TaskTypes.GENERATION and TaskTypes.CLASSIFICATION in settings.EXPORT_TASKS:
            mosaics = generator.get_batch()
            classifier = settings.CLASSIFIER_CLASS(mosaics, settings.CLASSIFICATION_TRAIN,
                                                   settings.CLASSIFICATION_TREES, settings.CLASSIFICATION_POINTS,
                                                   settings.YEARS, settings.CLASSIFICATION_BUFFER)
            classifier.run()
            classifier.export_batch(taskmanager, ImageMaker.IMAGE, settings.CLASSIFICATION_TYPE,
                                    {'bucket': settings.EXPORT_BUCKET, 'asset': settings.EXPORT_ASSET,
                                     'directory': settings.EXPORT_DIRECTORY})

        if TaskTypes.POSTPROCESSING in settings.EXPORT_TASKS:
            collection = ImageCollection(settings.POSTPROCESSING_COLLECTION)
            postprocessor = settings.POSTPROCESSOR_CLASS(collection, settings.COLLECTION_PREFIX,
                                                         settings.POSTPROCESSING_FILTERS, settings.YEARS, 1)
            postprocessor.run()
            postprocessor.export_batch(taskmanager, ImageMaker.IMAGE, settings.POSTPROCESSING_TYPE,
                                       {'bucket': settings.EXPORT_BUCKET, 'asset': settings.EXPORT_ASSET,
                                        'directory': settings.EXPORT_DIRECTORY})

        taskmanager.start()
        taskmanager.join()

        session.close()

    def help(self):
        print """Usage: manage.py [COMMAND]...
        -r, run                 COMMAND start the processing of tasks.
        -h, help                COMMAND show the help
        """
