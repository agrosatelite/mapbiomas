import ee

from mapbiomas import processors

from rsgee.processors import generic as rsgee_processors
from rsgee.band import Band
from rsgee.reducer import Reducer
from rsgee.db.models import TaskTypes
from rsgee.imagemaker import ImageMaker
from rsgee.provider import Provider

YEARS = [2017]

# ********** COLLECTION SETTINGS ****************+
COLLECTION = 'LANDSAT/LC08/C01/T1_TOA'
COLLECTION_PREFIX = 'L8_T1_TOA'
COLLECTION_PROVIDER = Provider.LC08

# *********  FUSION TABLE SETTINGS
FEATURE_COLLECTION = 'ft:1KksfUWfqBvx78c533ixJCuJy0y8ORAuXOLKghHCy'
FEATURE_WRS = 'PATHROW'
FEATURE_WRS_SELECTED = {
    'OR': {
        'AMAZONIA': 1,
        'CAATINGA': 1,
        'CERRADO': 1,
        'MATAATLANT': 1,
        'PAMPA': 1,
        'PANTANAL': 1,
    },
}

#FEATURE_WRS_FILTER = [220069]

# ********  Database

DATABASE = {
    'ENGINE': 'postgresql',
    'NAME': 'mapbiomas',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'localhost',
    'PORT': '5432',
}

# ********** GENERATION SETTINGS *******************
GENERATOR_CLASS = rsgee_processors.GeneratorProcessor
GENERATION_BANDS = [Band.BLUE, Band.GREEN, Band.RED, Band.NIR, Band.NDWI, Band.NDWI2, Band.MNDWI, Band.AWEI_NSH, Band.AWEI_SH]
GENERATION_REDUCERS = [Reducer.MEDIAN]
GENERATION_VARIABLES = ['ANNUAL_BLUE_median', 'ANNUAL_GREEN_median', 'ANNUAL_RED_median', 'ANNUAL_NIR_median', 'ANNUAL_NDWI_median', 'ANNUAL_NDWI2_median', 'ANNUAL_MNDWI_median', 'ANNUAL_AWEI_NSH_median', 'ANNUAL_AWEI_SH_median']
GENERATION_PERIODS = ['ANNUAL']
GENERATION_OFFSET = 0
GENERATION_APPLY_BRDF = True
GENERATION_CLIP_GEOMETRY = True
GENERATION_APPLY_MASK = True

# ********** EXPORT SETTINGS **********************
EXPORT_CLASS = ee.batch.Export.image.toAsset
EXPORT_TASKS = [TaskTypes.GENERATION]
EXPORT_TYPES = [ImageMaker.IMAGE]
EXPORT_BUCKET = 'agrosatelite-mapbiomas'
EXPORT_ASSET = 'users/mapbiomas1'
EXPORT_DIRECTORY = 'water'
EXPORT_MAX_TASKS = 10
EXPORT_INTERVAL = 30
EXPORT_BUFFER = -4000
EXPORT_SCALE = 30
EXPORT_SCALES = {
    10000: [Band.BLUE, Band.GREEN, Band.RED, Band.MNDWI, Band.AWEI_NSH, Band.AWEI_SH],
}
EXPORT_MAX_PIXELS = 1.0E13

# *********** EXTRA SETTINGS

MAX_IMAGES = 5000
