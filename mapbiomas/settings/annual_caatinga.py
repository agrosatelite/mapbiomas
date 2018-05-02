import ee

from rsgee.band import Band
from rsgee.db.models import TaskTypes
from rsgee.imagemaker import ImageMaker
from rsgee.provider import Provider
from rsgee.reducer import Reducer

from mapbiomas import processors

YEARS = [2017]

# ********** COLLECTION SETTINGS ****************
COLLECTION = 'LANDSAT/LC08/C01/T1_TOA'
COLLECTION_PREFIX = 'L8_T1_TOA'
COLLECTION_PROVIDER = Provider.LC08

# *********  FUSION TABLE SETTINGS
FEATURE_COLLECTION = 'ft:1KksfUWfqBvx78c533ixJCuJy0y8ORAuXOLKghHCy'
FEATURE_WRS = 'PATHROW'
FEATURE_WRS_SELECTED = {
    'AND': {'AC_WRS': 1},
    #'OR': {'CERRADO': 1, 'AMAZONIA': 1, 'PR': 1, 'SC': 1, 'RS': 1}
    'OR': {'CAATINGA': 1, 'MG': 1, 'ES': 1, 'RJ': 1},
}

# ********  DATABASE SETTINGS

DATABASE = {
    'ENGINE': 'postgresql',
    'NAME': 'mapbiomas',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'localhost',
    'PORT': '5432',
}


# ********** GENERATION SETTINGS *******************
GENERATOR_CLASS = processors.AnnualGenerator
GENERATION_BANDS = [Band.GREEN, Band.RED, Band.NIR, Band.SWIR1, Band.SWIR2, Band.TIR1, Band.EVI2, Band.NDWI, Band.CAI]
GENERATION_EXTRA_BANDS = [Band.CEI]
GENERATION_REDUCERS = [Reducer.QMO, Reducer.MAX, Reducer.MIN, Reducer.MEDIAN, Reducer.STDV]
GENERATION_VARIABLES = [
    'AC_WET_NIR_qmo', 'AC_WET_SWIR1_qmo', 'AC_WET_EVI2_qmo',
    'AC_WET_RED_max', 'AC_WET_SWIR1_max', 'AC_WET_SWIR2_max', 'AC_WET_TIR1_max', 'AC_WET_EVI2_max', 'AC_WET_NDWI_max', 'AC_WET_CAI_max',
    'AC_WET_GREEN_min', 'AC_WET_SWIR1_min', 'AC_WET_EVI2_min', 'AC_WET_NDWI_min', 'AC_WET_CAI_min',
    'AC_WET_GREEN_median', 'AC_WET_RED_median', 'AC_WET_SWIR1_median', 'AC_WET_SWIR2_median', 'AC_WET_NDWI_median', 'AC_WET_CAI_median',
    'AC_WET_RED_stdDev', 'AC_WET_SWIR1_stdDev', 'AC_WET_SWIR2_stdDev', 'AC_WET_TIR1_stdDev', 'AC_WET_EVI2_stdDev', 'AC_WET_NDWI_stdDev', 'AC_WET_CAI_stdDev',

    'AC_DRY_NDWI_qmo', 'AC_DRY_CAI_qmo',
    'AC_DRY_RED_max', 'AC_DRY_SWIR1_max', 'AC_DRY_SWIR2_max', 'AC_DRY_NDWI_max', 'AC_DRY_CAI_max',
    'AC_DRY_RED_min', 'AC_DRY_SWIR2_min', 'AC_DRY_EVI2_min', 'AC_DRY_NDWI_min', 'AC_DRY_CAI_min',
    'AC_DRY_GREEN_median', 'AC_DRY_RED_median', 'AC_DRY_SWIR1_median', 'AC_DRY_SWIR2_median', 'AC_DRY_EVI2_median', 'AC_DRY_NDWI_median',
    'AC_DRY_SWIR1_stdDev', 'AC_DRY_NDWI_stdDev']
GENERATION_EXTRA_VARIABLES = ['ANNUAL_NIR_cei', 'ANNUAL_EVI2_cei', 'ANNUAL_NDWI_cei']
GENERATION_PERIODS = ['AC_WET', 'AC_DRY']
GENERATION_EXTRA_PERIODS = ['ANNUAL']
GENERATION_OFFSET = 4
GENERATION_CLIP_GEOMETRY = True
GENERATION_APPLY_MASK = True


# ********** CLASSIFICATION SETTINGS **************
CLASSIFIER_CLASS = processors.Classifier
CLASSIFICATION_TRAIN = 'users/marciano/mapbiomas/train/annual'
CLASSIFICATION_TREES = 100
CLASSIFICATION_POINTS = 10000
CLASSIFICATION_BUFFER = 50000

# ********** EXPORT SETTINGS **********************

EXPORT_CLASS = ee.batch.Export.image.toCloudStorage
EXPORT_TASKS = [TaskTypes.GENERATION, TaskTypes.CLASSIFICATION]
EXPORT_TYPES = [ImageMaker.IMAGE]
EXPORT_BUCKET = 'agrosatelite-mapbiomas'
EXPORT_ASSET = 'users/marciano'
EXPORT_DIRECTORY = 'classification/annual/caatinga/2017'
EXPORT_MAX_TASKS = 3
EXPORT_INTERVAL = 30
EXPORT_MAX_ERRORS = 1
EXPORT_BUFFER = -4200
EXPORT_SCALE = 30
EXPORT_SCALES = {
    100: [Band.TIR1],
    10000: [Band.GREEN, Band.RED, Band.NIR, Band.SWIR1, Band.SWIR2, Band.EVI2, Band.NDWI, Band.CAI],
}
EXPORT_MAX_PIXELS = 1.0E13

# *********** EXTRA SETTINGS *********************

QUALITY_MOSAIC = Band.EVI2
MAX_IMAGES = 5000
