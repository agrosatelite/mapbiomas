import ee
import ee.mapclient

from rsgee.conf import settings
from rsgee.processors.generic.base import BaseProcessor
from rsgee.imagecollection import ImageCollection


class Classifier(BaseProcessor):
    def __init__(self, mosaics, train, trees, points, years, buffer):
        BaseProcessor.__init__(self)
        self._mosaics = mosaics
        self._train = train
        self._trees = trees
        self._points = points
        self._years = years
        self._buffer = buffer

    def run(self):
        for year in self._years:
            train_asset = ImageCollection(self._train).filter(ee.Filter.eq('year', int(year))).mosaic()
            for image_name, image_data in self._mosaics.items():
                if year != image_data['year']:
                    continue
                image = image_data['image']
                path = image_data['path']
                row = image_data['row']
                geometry = image_data['geometry']
                geometry_neighbors = image_data['neighbors']

                roi = geometry
                roi_train = geometry_neighbors.intersection(geometry.buffer(self._buffer))

                neighbors = image.clip(roi_train).set('system:footprint', roi_train).unmask(None)
                center = neighbors.clip(roi).set('system:footprint', roi)

                train = train_asset.clip(roi_train).unmask(None)
                neighbors = neighbors.addBands(train.select([0], ['class']))

                training = ee.FeatureCollection(neighbors.sample(
                    region=roi_train,
                    numPixels=self._points,
                    scale=settings.EXPORT_SCALE)
                )

                classifier = ee.Classifier.randomForest(self._trees).train(
                    features=training,
                    classProperty='class',
                    inputProperties=list(settings.GENERATION_VARIABLES + settings.GENERATION_EXTRA_VARIABLES)
                )
                classified = center.classify(classifier)
                classified = classified.clip(roi).set('year', year).set('system:footprint', roi)

                final_image = classified
                final_name = image_name

                self.add_image_in_batch(final_name, {"image": final_image, "year": int(year), "path": int(path), "row": int(row), "geometry": roi})


class ClassifierFusionTable(BaseProcessor):
    def __init__(self, mosaics, train, trees, points, years, buffer):
        BaseProcessor.__init__(self)
        self._mosaics = mosaics
        self._train = train
        self._trees = trees
        self._points = points
        self._years = years
        self._buffer = buffer

    def run(self):
        for year in self._years:
            train_geometry = ee.FeatureCollection(self._train).union().geometry()
            for image_name, image_data in self._mosaics.items():
                if year != image_data['year']:
                    continue
                image = image_data['image']
                path = image_data['path']
                row = image_data['row']
                geometry = image_data['geometry']
                geometry_neighbors = image_data['neighbors']

                roi = geometry
                roi_train = geometry_neighbors.intersection(geometry.buffer(self._buffer))

                neighbors = image.clip(roi_train).set('system:footprint', roi_train).unmask(None)
                center = neighbors.clip(roi).set('system:footprint', roi)


                geo1 = train_geometry.intersection(roi_train)
                geo2 = train_geometry.difference(roi_train).union(roi_train.difference(train_geometry))

                image1 = ee.Image(1).clip(geo1).select([0], ['class']).byte()
                image2 = ee.Image(0).clip(geo2).select([0], ['class']).byte()


                training_roi = ee.FeatureCollection(neighbors.addBands(image1).sample(
                    region=geo1,
                    numPixels=self._points/2,
                    scale=settings.EXPORT_SCALE)
                )

                training_others = ee.FeatureCollection(neighbors.addBands(image2).sample(
                    region=geo2,
                    numPixels=self._points/2,
                    scale=settings.EXPORT_SCALE)
                )

                training = training_roi.merge(training_others)

                classifier = ee.Classifier.randomForest(self._trees).train(
                    features=training,
                    classProperty='class',
                    inputProperties=list(settings.GENERATION_VARIABLES + settings.GENERATION_EXTRA_VARIABLES)
                )
                classified = center.classify(classifier)
                classified = classified.clip(roi).set('year', year).set('system:footprint', roi)

                final_image = classified
                final_name = image_name

                self.add_image_in_batch(final_name, {"image": final_image, "year": int(year), "path": int(path), "row": int(row), "geometry": roi})


class ClassifierFixBounds(Classifier):
    def __init__(self, mosaics, train, trees, points, years, buffer):
        super(ClassifierFixBounds, self).__init__(mosaics, train, trees, points, years, buffer)

    def run(self):
        for year in self._years:
            annual_training = ImageCollection(self._train).filter(ee.Filter.eq('year', int(year))).mosaic()

            training = None
            for image_name, image_data in self._mosaics.items():
                image = image_data['image']
                path = image_data['path']
                row = image_data['row']
                if path == 215 and row == 67:
                    geometry = image_data['geometry']
                    geometry_neighbors = image_data['neighbors']

                    roi_train = geometry_neighbors.intersection(geometry.buffer(self._buffer))

                    neighbors = image.clip(roi_train).set('system:footprint', roi_train).unmask(None)

                    train = annual_training.clip(roi_train).unmask(None)
                    neighbors = neighbors.addBands(train.select([0], ['class']))

                    training = ee.FeatureCollection(neighbors.sample(
                        region=roi_train,
                        numPixels=self._points,
                        scale=settings.EXPORT_SCALE)
                    )

            for image_name, image_data in self._mosaics.items():
                if year != image_data['year']:
                    continue
                image = image_data['image']
                path = image_data['path']
                row = image_data['row']
                roi = image_data['geometry']

                center = image.clip(roi).set('system:footprint', roi)

                classifier = ee.Classifier.randomForest(self._trees).train(
                    features=training,
                    classProperty='class',
                    inputProperties=settings.GENERATION_VARIABLES
                )
                classified = center.classify(classifier)
                classified = classified.clip(roi).set('year', year).set('system:footprint', roi)

                final_image = classified
                final_name = image_name

                self.add_image_in_batch(final_name, {"image": final_image, "year": int(year), "path": int(path), "row": int(row), "geometry": roi})
