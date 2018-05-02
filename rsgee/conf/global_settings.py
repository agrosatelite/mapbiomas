# -*- coding: utf-8 -*-
from rsgee.provider import Provider

YEARS  = []

#********** COLLECTION SETTINGS ******************

COLLECTION  = ''

COLLECTION_PREFIX = ''

COLLECTION_PROVIDER = None

#********* FUSION TABLE SETTINGS

FEATURE_COLLECTION = ''

FEATURE_WRS  = ''

FEATURE_WRS_SELECTED  = {
    'AND': {},
    'OR':{},
}

FEATURE_WRS_FILTER = []

#********** DATABASE SETTINGS **********************

DATABASE = {
    'ENGINE': '',
    'NAME': '',
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
}

#********** GENERATION SETTINGS *******************

GENERATOR_CLASS = 'rsgee.core.processors.Generator'

GENERATION_BANDS = []

GENERATION_EXTRA_BANDS = []

GENERATION_REDUCERS = []

GENERATION_VARIABLES  = []

GENERATION_EXTRA_VARIABLES = []

GENERATION_PERIODS = []

GENERATION_EXTRA_PERIODS = []

GENERATION_OFFSET = 0

GENERATION_CLIP_GEOMETRY = False

GENERATION_APPLY_BRDF = False

GENERATION_APPLY_MASK = False

GENERATION_TYPE = 'int16'

#********** CLASSIFICATION SETTINGS **************

CLASSIFIER_CLASS = 'rsgee.core.processors.Classifier'

CLASSIFICATION_TRAIN = ''

CLASSIFICATION_TREES = 100

CLASSIFICATION_POINTS = 1000

CLASSIFICATION_BUFFER = 30000

CLASSIFICATION_TYPE = 'byte'

#*********** POST PROCESSING SETTINGS ************

POSTPROCESSOR_CLASS  = 'rsgee.core.processors.PostProcessor'

POSTPROCESSING_COLLECTION = ''

POSTPROCESSING_FILTERS = []

POSTPROCESSING_TYPE = 'byte'

POSTPROCESSING_TEMPORAL_FILTER_THRESHOLD = 2

POSTPROCESSING_TEMPORAL_FILTER_OFFSET = 2

POSTPROCESSING_SPATIAL_FILTER_THRESHOLD = 15

POSTPROCESSING_SPATIAL_FILTER_KERNEL = [
                                            [1, 1, 1, 1, 1],
                                            [1, 2, 2, 2, 1],
                                            [1, 2, 2, 2, 1],
                                            [1, 2, 2, 2, 1],
                                            [1, 1, 1, 1, 1]
                                        ]

#********** EXPORT SETTINGS **********************

EXPORT_CLASS = 'ee.batch.Export.image.toCloudStorage'

EXPORT_TASKS  = []

EXPORT_TYPES = []

EXPORT_BUCKET = ''

EXPORT_ASSET = ''

EXPORT_DIRECTORY = ''

EXPORT_MAX_TASKS = 5

EXPORT_INTERVAL = 10

EXPORT_MAX_ERRORS = 0

EXPORT_BUFFER = -4200

EXPORT_SCALE  = 30

EXPORT_SCALES = {}

EXPORT_MAX_PIXELS = 1.0E13

#*********** EXTRA SETTINGS *********************

QUALITY_MOSAIC  = None

MAX_IMAGES  = 5000

DATE_FORMAT = "%Y-%m-%d"

#*********** INDEX SETTINGS *********************

# -*- coding: utf-8 -*-

QA_BITS = {
    Provider.LT05.value: [[0, 0, 0], [1, 1, 0], [4, 4, 0], [5, 6, 1], [7, 8, 1]],
    Provider.LE07.value: [[0, 0, 0], [1, 1, 0], [4, 4, 0], [5, 6, 1], [7, 8, 1]],
    Provider.LC08.value: [[0, 0, 0], [1, 1, 0], [4, 4, 0], [5, 6, 1], [7, 8, 1], [11, 12, 1]],
}

SAFER = {
    #Teixeira, Antônio et.al
    Provider.LT05.value: {
        'BLUE': 0.293,
        'GREEN': 0.274,
        'RED': 0.233,
        'NIR': 0.157,
        'SWIR1': 0.033,
        'SWIR2': 0.011,
        'A_ALBEDO': 0.7,
        'B_ALBEDO': 0.6,
        'A_ET_ET0': 0.315,
        'B_ET_ET0': -0.0015,
    },
    #Teixeira, Antônio et.al
    Provider.LE07.value: {
        'BLUE': 0.293,
        'GREEN': 0.274,
        'RED': 0.231,
        'NIR': 0.156,
        'SWIR1': 0.034,
        'SWIR2': 0.012,
        'A_ALBEDO': 0.7,
        'B_ALBEDO': 0.6,
        'A_ET_ET0': 0.315,
        'B_ET_ET0': -0.0015,
    },
    #Salgado, Moisés et.al
    Provider.LC08.value: {
        'BLUE': 0.301,
        'GREEN': 0.273,
        'RED': 0.233,
        'NIR': 0.143,
        'SWIR1': 0.037,
        'SWIR2': 0.013,
        'A_ALBEDO': 0.7,
        'B_ALBEDO': 0.6,
        'A_ET_ET0': 0.315,
        'B_ET_ET0': -0.0015,
    },
}
