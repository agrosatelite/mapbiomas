from datetime import datetime

import ee

from rsgee.conf import settings
from rsgee.processors.generic.base import BaseProcessor


class ClassifierProcessor(BaseProcessor):
    def __init__(self, mosaics, train, trees, points, years, buffer):
        BaseProcessor.__init__(self)
        self.__mosaics = mosaics
        self.__train = train
        self.__trees = trees
        self.__points = points
        self.__years = years
        self.__buffer = buffer

    def run(self):
        for year in self.__years:
            annual_training = self.__train.filter(ee.Filter.eq('year', int(year))).mosaic()
            for final_name, image_data in self.__mosaics.items():
                if year != image_data['year']:
                    continue
                image = image_data['image']
                path = image_data['path']
                row = image_data['row']
                geometry = image_data['geometry']

                train = annual_training.clip(geometry).unmask(None)

                image = image.addBands(train.select([0], ['class']))

                training = image.sample(
                    numPixels=self.__points,
                    scale=settings.EXPORT_SCALE,
                    seed=datetime.now().microsecond,
                )

                classifier = ee.Classifier.randomForest(self.__trees, seed=datetime.now().microsecond).train(training, 'class')
                classified = image.classify(classifier)

                final_image = classified.clip(geometry).set('year', year).set('system:footprint', geometry)

                self.add_image_in_batch(final_name, {"image": final_image,
                                                     "year": int(year),
                                                     "path": int(path),
                                                     "row": int(row),
                                                     "geometry": geometry})
