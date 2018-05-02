import ee

from rsgee.band import Band
from rsgee.db.models import TaskTypes
from rsgee.imagemaker import ImageMaker
from rsgee.provider import Provider
from rsgee.reducer import Reducer

from mapbiomas import processors

# ********** COLLECTION SETTINGS ****************
COLLECTION = 'MODIS/006/MOD13Q1'
COLLECTION_PREFIX = 'MOD13Q1'
COLLECTION_PROVIDER = Provider.MOD13Q1

# *********  FUSION TABLE SETTINGS
FEATURE_COLLECTION = 'ft:1KksfUWfqBvx78c533ixJCuJy0y8ORAuXOLKghHCy'
FEATURE_WRS = 'PATHROW'
FEATURE_WRS_SELECTED = {
    'AND': {'AC_WRS':1},
}
FEATURE_WRS_FILTER = [220069, 220066, 227069, 223080, 219075]

# ********  Database

DATABASE = {
    'ENGINE': 'postgresql',
    'NAME': 'mapbiomas',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'localhost',
    'PORT': '5432',
}


YEARS = [2010]

# ********** GENERATION SETTINGS *******************
GENERATOR_CLASS = processors.ModisGenerator
GENERATION_BANDS = [Band.BLUE, Band.RED, Band.NIR, Band.EVI2, Band.NDVI]
GENERATION_EXTRA_BANDS = [Band.CEI]
GENERATION_REDUCERS = [Reducer.MAX, Reducer.MIN]
GENERATION_VARIABLES = ['AC_WET_RED_max', 'AC_WET_NIR_max', 'AC_WET_EVI2_max', 'AC_DRY_RED_min', 'AC_DRY_NIR_min', 'AC_DRY_EVI2_min']
GENERATION_EXTRA_VARIABLES = ['ANNUAL_EVI2_cei']
GENERATION_PERIODS = ['AC_WET', 'AC_DRY']
GENERATION_EXTRA_PERIODS = ['ANNUAL']
GENERATION_OFFSET = 4
GENERATION_CLIP_GEOMETRY = True
GENERATION_APPLY_MASK = False

# ********** CLASSIFICATION SETTINGS **************
CLASSIFIER_CLASS = processors.Classifier
CLASSIFICATION_TRAIN = 'users/moisessalgado/mapbiomas/agricultura_anual'
CLASSIFICATION_TREES = 50
CLASSIFICATION_POINTS = 10000

# *********** POST PROCESSING SETTINGS ************
POSTPROCESSING_COLLECTION = 'users/mapbiomas6/classification'
POSTPROCESSING_FILTERS = []  # [Filter.TEMPORAL]

# ********** EXPORT SETTINGS **********************
EXPORT_CLASS = ee.batch.Export.image.toCloudStorage
EXPORT_TASKS = [TaskTypes.GENERATION]  # , TaskTypes.GENERATION, TaskTypes.CLASSIFICATION]#, [TaskTypes.POSTPROCESSING]
EXPORT_TYPES = [ImageMaker.IMAGE]
EXPORT_BUCKET = 'agrosatelite-mapbiomas'
EXPORT_ASSET = 'users/marciano'
EXPORT_DIRECTORY = 'classification/annual/modis_mosaics'
EXPORT_MAX_TASKS = 15
EXPORT_INTERVAL = 10
EXPORT_BUFFER = -4200
EXPORT_SCALE = 30
EXPORT_SCALES = {
    1: [Band.BLUE, Band.RED, Band.NIR, Band.NDVI],
    10000: [Band.EVI2],
}
EXPORT_MAX_PIXELS = 1.0E13

# *********** EXTRA SETTINGS *********************

QUALITY_MOSAIC = Band.EVI2
MAX_IMAGES = 5000
