import ee

from rsgee.processors import generic as rsgee_processors
from rsgee.db.models import TaskTypes
from rsgee.imagemaker import ImageMaker

COLLECTION_PREFIX = 'AGRICULTURE'

YEARS = list(range(1985, 2018))

DATABASE = {
    'ENGINE': 'postgresql',
    'NAME': 'mapbiomas',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'localhost',
    'PORT': '5432',
}

# *********** POST PROCESSING SETTINGS ************
POSTPROCESSOR_CLASS = rsgee_processors.PostProcessor
POSTPROCESSING_COLLECTION = 'users/marciano/mapbiomas/classification/c3/raw/agriculture'
POSTPROCESSING_FILTERS = [rsgee_processors.Filter.SPATIAL]


# ********** EXPORT SETTINGS **********************
EXPORT_CLASS = ee.batch.Export.image.toAsset
EXPORT_TASKS = [TaskTypes.POSTPROCESSING]
EXPORT_TYPES = [ImageMaker.IMAGE]
EXPORT_BUCKET = 'agrosatelite-mapbiomas'
EXPORT_ASSET = 'users/mapbiomas1'
EXPORT_DIRECTORY = 'mapbiomas/classification/c3/filtered/agriculture'
EXPORT_MAX_TASKS = 5
EXPORT_INTERVAL = 20
EXPORT_BUFFER = 1
EXPORT_SCALE = 30
EXPORT_MAX_PIXELS = 1.0E13
