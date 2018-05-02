import ee

from mapbiomas import processors
from rsgee.band import Band
from rsgee.db.models import TaskTypes
from rsgee.imagemaker import ImageMaker
from rsgee.provider import Provider
from rsgee.reducer import Reducer

YEARS = [1985]

# ********** COLLECTION SETTINGS ****************+
COLLECTION = 'LANDSAT/LT05/C01/T1_TOA'
COLLECTION_PREFIX = 'L5_T1_TOA'
COLLECTION_PROVIDER = Provider.LT05

# *********  FUSION TABLE SETTINGS
FEATURE_COLLECTION = 'ft:1KksfUWfqBvx78c533ixJCuJy0y8ORAuXOLKghHCy'
FEATURE_WRS = 'PATHROW'
FEATURE_WRS_SELECTED = {
    'AND': {'ACS_WRS':1},
    'OR' : {'MT': 1, 'MS': 1, 'GO': 1, 'MG': 1, 'ES': 1, 'SP': 1, 'PR': 1},
}

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
GENERATOR_CLASS = processors.SemiPereneGenerator
GENERATION_BANDS = [Band.GREEN, Band.RED, Band.NIR, Band.SWIR1, Band.SWIR2,
                    Band.NDVI, Band.NDWI]
GENERATION_EXTRA_BANDS = []
GENERATION_REDUCERS = [Reducer.MEDIAN]
GENERATION_VARIABLES = [
	'ACP_WET1_GREEN_median', 'ACP_WET1_RED_median', 'ACP_WET1_NIR_median', 'ACP_WET1_SWIR1_median', 'ACP_WET1_SWIR2_median', 'ACP_WET1_NDVI_median', 'ACP_WET1_NDWI_median', 
        'ACP_WET2_GREEN_median', 'ACP_WET2_RED_median', 'ACP_WET2_NIR_median', 'ACP_WET2_SWIR1_median', 'ACP_WET2_SWIR2_median', 'ACP_WET2_NDVI_median', 'ACP_WET2_NDWI_median',
        'ACP_DRY1_GREEN_median', 'ACP_DRY1_RED_median', 'ACP_DRY1_NIR_median', 'ACP_DRY1_SWIR1_median', 'ACP_DRY1_SWIR2_median', 'ACP_DRY1_NDVI_median', 'ACP_DRY1_NDWI_median', 
        'ACP_DRY2_GREEN_median', 'ACP_DRY2_RED_median', 'ACP_DRY2_NIR_median', 'ACP_DRY2_SWIR1_median', 'ACP_DRY2_SWIR2_median', 'ACP_DRY2_NDVI_median', 'ACP_DRY2_NDWI_median', 
        'ACP_DRY3_GREEN_median', 'ACP_DRY3_RED_median', 'ACP_DRY3_NIR_median', 'ACP_DRY3_SWIR1_median', 'ACP_DRY3_SWIR2_median', 'ACP_DRY3_NDVI_median', 'ACP_DRY3_NDWI_median', 
        'ACP_WET3_GREEN_median', 'ACP_WET3_RED_median', 'ACP_WET3_NIR_median', 'ACP_WET3_SWIR1_median', 'ACP_WET3_SWIR2_median', 'ACP_WET3_NDVI_median', 'ACP_WET3_NDWI_median']

GENERATION_EXTRA_VARIABLES = []
GENERATION_PERIODS = ['ACP_WET1', 'ACP_WET2', 'ACP_DRY1', 'ACP_DRY2', 'ACP_DRY3', 'ACP_WET3']
GENERATION_EXTRA_PERIODS = ['ACP_ALL']
GENERATION_OFFSET = 2
GENERATION_CLIP_GEOMETRY = True
GENERATION_APPLY_MASK = True

# ********** CLASSIFICATION SETTINGS ***************
CLASSIFIER_CLASS = processors.Classifier
CLASSIFICATION_TRAIN = 'users/marciano/mapbiomas/train/semiperene'
CLASSIFICATION_TREES = 100
CLASSIFICATION_POINTS = 10000
CLASSIFICATION_BUFFER = 50000

# ********** EXPORT SETTINGS **********************
EXPORT_CLASS = ee.batch.Export.image.toCloudStorage
EXPORT_TASKS = [TaskTypes.GENERATION, TaskTypes.CLASSIFICATION]
EXPORT_TYPES = [ImageMaker.IMAGE]
EXPORT_BUCKET = 'agrosatelite-mapbiomas'
EXPORT_ASSET = 'users/marciano'
EXPORT_DIRECTORY = 'classification/semiperene/1985'
EXPORT_MAX_TASKS = 3
EXPORT_INTERVAL = 30
EXPORT_MAX_ERRORS = 1
EXPORT_BUFFER = -4200
EXPORT_SCALE = 30
EXPORT_SCALES = {
    10000: [Band.GREEN, Band.RED, Band.NIR, Band.SWIR1, Band.SWIR2, Band.NDVI, Band.NDWI],
}
EXPORT_MAX_PIXELS = 1.0E13

# *********** EXTRA SETTINGS
QUALITY_MOSAIC = Band.NDVI
MAX_IMAGES = 5000
