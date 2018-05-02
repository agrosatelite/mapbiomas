# -*- coding: utf-8 -*-
import ee

from rsgee.conf import settings
from rsgee.image import Image
from rsgee.imagecollection import ImageCollection
from rsgee.processors.generic import GeneratorProcessor
from rsgee.reducer import Reducer


class MapbiomasGenerator(GeneratorProcessor):
    def __init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf, apply_mask):
        GeneratorProcessor.__init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf,
                                    apply_mask)

    def get_neighbors(self, images, path, row):
        wrs = []
        for offset_path in range(-1, 2):
            for offset_row in range(-1, 2):
                for image in images:
                    local_path = path + offset_path
                    local_row = row + offset_row
                    local_geometry = image.get('GEOMETRY')
                    if int(image.get('PATH')) == local_path and int(image.get('ROW')) == local_row:
                        wrs.append((local_path, local_row, local_geometry))
        return wrs


class AnnualGenerator(MapbiomasGenerator):
    def __init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf, apply_mask):
        MapbiomasGenerator.__init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf,
                                    apply_mask)

    def run(self):
        features = self._feature_collection.get_features()
        for year in self._years:
            for feature in features:
                path = feature.get('PATH')
                row = feature.get('ROW')
                geometry = ee.Geometry.MultiPolygon(feature.get('GEOMETRY'))

                neighbors = self.get_neighbors(features, int(path), int(row))
                neighbors_paths = map(lambda x: x[0], neighbors)
                neighbors_rows = map(lambda x: x[1], neighbors)
                neighbors_geometry = ee.Geometry.MultiPolygon(map(lambda x: x[2], neighbors))

                image_collection = self._collection \
                    .filter(ee.Filter.inList('WRS_PATH', ee.List(neighbors_paths))) \
                    .filter(ee.Filter.inList('WRS_ROW', ee.List(neighbors_rows)))

                final_image = Image()
                for period in self._periods:
                    period_dates = feature.get(period)
                    images_by_period = ImageCollection(image_collection).filter_by_period(year, period_dates, self._offset)

                    if self._clip_geometry:
                        images_by_period = images_by_period.clip_geometry()

                    if self._apply_mask:
                        images_by_period = images_by_period.apply_qamask()

                    if self._bands:
                        images_by_period = images_by_period.apply_bands(self._bands)

                    image_reduced = Image(images_by_period.apply_reducers(self._reducers))

                    final_image = final_image.addBands(
                        image_reduced.rename(image_reduced.bandNames().map(lambda band: ee.String(period).cat('_').cat(band)))
                    )

                if settings.GENERATION_EXTRA_BANDS:
                    final_image = final_image.addBands(Image(final_image).get_bands(settings.GENERATION_EXTRA_BANDS))

                final_name = "{0}_{1}_{2}".format(settings.COLLECTION_PREFIX, "{0}{1}".format(path, row), str(year))
                final_image = final_image.select(settings.GENERATION_VARIABLES + settings.GENERATION_EXTRA_VARIABLES).set('year', year)

                self.add_image_in_batch(final_name,
                                        {"image": final_image, "year": int(year), "path": int(path), "row": int(row), "geometry": geometry,
                                         'neighbors': neighbors_geometry})


class SemiPereneGenerator(MapbiomasGenerator):
    def __init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf, apply_mask):
        MapbiomasGenerator.__init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf,
                                    apply_mask)

    def run(self):
        features = self._feature_collection.get_features()
        for year in self._years:
            for feature in features:
                path = feature.get('PATH')
                row = feature.get('ROW')
                geometry = ee.Geometry.MultiPolygon(feature.get('GEOMETRY'))

                neighbors = self.get_neighbors(features, int(path), int(row))
                neighbors_paths = map(lambda x: x[0], neighbors)
                neighbors_rows = map(lambda x: x[1], neighbors)
                neighbors_geometry = ee.Geometry.MultiPolygon(map(lambda x: x[2], neighbors))

                image_collection = self._collection \
                    .filter(ee.Filter.inList('WRS_PATH', ee.List(neighbors_paths))) \
                    .filter(ee.Filter.inList('WRS_ROW', ee.List(neighbors_rows)))

                images = []
                for period in self._periods:
                    period_dates = feature.get(period)
                    images_by_period = ImageCollection([])
                    for i in range(self._offset):
                        local_images_by_period = ImageCollection(image_collection).filter_by_period(year - i, period_dates, 1)

                        if self._clip_geometry:
                            local_images_by_period = local_images_by_period.clip_geometry()

                        if self._apply_mask:
                            local_images_by_period = local_images_by_period.apply_qamask()

                        if self._bands:
                            local_images_by_period = local_images_by_period.apply_bands(self._bands)

                        images_by_period = images_by_period.merge(local_images_by_period)

                    reduced_image = ImageCollection(images_by_period).apply_reducers(self._reducers)

                    reduced_image = reduced_image.rename(reduced_image.bandNames().map(
                        lambda band: ee.String(period).cat('_').cat(band))
                    )

                    images.append(reduced_image)

                final_image = Image.cat(images)

                final_name = "{0}_{1}_{2}".format(settings.COLLECTION_PREFIX, "{0}{1}".format(path, row), str(year))
                final_image = final_image.select(settings.GENERATION_VARIABLES + settings.GENERATION_EXTRA_VARIABLES).set('year', year)

                self.add_image_in_batch(final_name,
                                        {"image": final_image, "year": int(year), "path": int(path), "row": int(row), "geometry": geometry,
                                         'neighbors': neighbors_geometry})


class PlantedForestGenerator(MapbiomasGenerator):
    def __init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf, apply_mask):
        MapbiomasGenerator.__init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf,
                                    apply_mask)

    def run(self):
        features = self._feature_collection.get_features()
        for year in self._years:
            for feature in features:
                path = feature.get('PATH')
                row = feature.get('ROW')
                geometry = ee.Geometry.MultiPolygon(feature.get('GEOMETRY'))

                neighbors = self.get_neighbors(features, int(path), int(row))
                neighbors_paths = map(lambda x: x[0], neighbors)
                neighbors_rows = map(lambda x: x[1], neighbors)
                neighbors_geometry = ee.Geometry.MultiPolygon(map(lambda x: x[2], neighbors))

                image_collection = self._collection \
                    .filter(ee.Filter.inList('WRS_PATH', ee.List(neighbors_paths))) \
                    .filter(ee.Filter.inList('WRS_ROW', ee.List(neighbors_rows)))

                images = []
                for period in self._periods:
                    period_dates = feature.get(period)
                    images_by_period = ImageCollection([])
                    for i in range(self._offset):
                        local_images_by_period = ImageCollection(image_collection).filter_by_period(year - i, period_dates, 1)

                        if self._clip_geometry:
                            local_images_by_period = local_images_by_period.clip_geometry()

                        if self._apply_mask:
                            local_images_by_period = local_images_by_period.apply_qamask()

                        if self._bands:
                            local_images_by_period = local_images_by_period.apply_bands(self._bands)

                        images_by_period = images_by_period.merge(local_images_by_period)

                    reduced_image = ImageCollection(images_by_period).apply_reducers(self._reducers)

                    reduced_image = reduced_image.rename(reduced_image.bandNames().map(
                        lambda band: ee.String(period).cat('_').cat(band))
                    )

                    images.append(reduced_image)

                final_image = Image.cat(images)

                final_name = "{0}_{1}_{2}".format(settings.COLLECTION_PREFIX, "{0}{1}".format(path, row), str(year))
                final_image = final_image.select(settings.GENERATION_VARIABLES + settings.GENERATION_EXTRA_VARIABLES).set('year', year)

                self.add_image_in_batch(final_name,
                                        {"image": final_image, "year": int(year), "path": int(path), "row": int(row), "geometry": geometry,
                                         'neighbors': neighbors_geometry})


class PereneGenerator(MapbiomasGenerator):
    def __init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf, apply_mask):
        MapbiomasGenerator.__init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf,
                                    apply_mask)

    def run(self):
        features = self._feature_collection.get_features()
        for year in self._years:
            for feature in features:
                path = feature.get('PATH')
                row = feature.get('ROW')
                geometry = ee.Geometry.MultiPolygon(feature.get('GEOMETRY'))

                neighbors = self.get_neighbors(features, int(path), int(row))
                neighbors_paths = map(lambda x: x[0], neighbors)
                neighbors_rows = map(lambda x: x[1], neighbors)
                neighbors_geometry = ee.Geometry.MultiPolygon(map(lambda x: x[2], neighbors))

                image_collection = self._collection \
                    .filter(ee.Filter.inList('WRS_PATH', ee.List(neighbors_paths))) \
                    .filter(ee.Filter.inList('WRS_ROW', ee.List(neighbors_rows)))

                images = []
                for period in self._periods:
                    period_dates = feature.get(period)
                    images_by_period = ImageCollection([])
                    for i in range(self._offset):
                        local_images_by_period = ImageCollection(image_collection).filter_by_period(year - i, period_dates, 1)

                        if self._clip_geometry:
                            local_images_by_period = local_images_by_period.clip_geometry()

                        if self._apply_mask:
                            local_images_by_period = local_images_by_period.apply_qamask()

                        if self._bands:
                            local_images_by_period = local_images_by_period.apply_bands(self._bands)

                        images_by_period = images_by_period.merge(local_images_by_period)

                    reduced_image = ImageCollection(images_by_period).apply_reducers(self._reducers)

                    reduced_image = reduced_image.rename(reduced_image.bandNames().map(
                        lambda band: ee.String(period).cat('_').cat(band))
                    )

                    images.append(reduced_image)

                final_image = Image.cat(images)

                final_name = "{0}_{1}_{2}".format(settings.COLLECTION_PREFIX, "{0}{1}".format(path, row), str(year))
                final_image = final_image.select(settings.GENERATION_VARIABLES + settings.GENERATION_EXTRA_VARIABLES).set('year', year)

                self.add_image_in_batch(final_name,
                                        {"image": final_image, "year": int(year), "path": int(path), "row": int(row), "geometry": geometry,
                                         'neighbors': neighbors_geometry})



class ModisGenerator(GeneratorProcessor):
    def __init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf, apply_mask):
        GeneratorProcessor.__init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry, apply_brdf,
                                    apply_mask)

    def run(self):
        for year in self._years:
            for feature in self._feature_collection.get_features():
                path = feature.get('PATH')
                row = feature.get('ROW')
                geometry = ee.Geometry.MultiPolygon(feature.get('geometry'))

                image_collection = self._collection.map(lambda image: image.clip(geometry))

                images = []
                for period in self._periods:
                    period_dates = feature.get(period)

                    images_by_period = ImageCollection(image_collection).filter_by_period(year, period_dates, self._offset)

                    images_by_period = images_by_period.apply_smoothing()

                    if self._clip_geometry:
                        images_by_period = images_by_period.clip_geometry()

                    if self._apply_mask:
                        images_by_period = images_by_period.apply_qamask()

                    if self._bands:
                        images_by_period = images_by_period.apply_bands(self._bands)

                    image_reduced = Image(images_by_period.apply_reducers(self._reducers))
                    image_reduced = image_reduced.rename(image_reduced.bandNames().map(
                        lambda band: ee.String(period).cat('_').cat(band))
                    )
                    images.append(image_reduced)

                final_image = Image.cat(images)

                if settings.GENERATION_EXTRA_BANDS:
                    final_image = final_image.addBands(Image(final_image).get_bands(settings.GENERATION_EXTRA_BANDS))

                final_name = "{0}_{1}_{2}".format(settings.COLLECTION_PREFIX, "{0}{1}".format(path, row), str(year))
                final_image = final_image.clip(geometry).select(settings.GENERATION_VARIABLES + settings.GENERATION_EXTRA_VARIABLES).set('year',
                                                                                                                                         year).set(
                    'system:footprint', geometry)

                self.add_image_in_batch(final_name,
                                        {"image": final_image, "year": int(year), "path": int(path), "row": int(row), "geometry": geometry})
