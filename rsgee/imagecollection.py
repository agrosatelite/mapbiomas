# -*- coding: utf-8 -*-

import ee, re

from rsgee.conf import settings

from rsgee.band import Band
from rsgee.image import Image
from rsgee.reducer import Reducer


class ImageCollection(ee.ImageCollection):
    def filter_by_period(self, year, period, offset):
        def parse_period(date_format, year):
            year_format = re.match('^\((?P<year>.*)\)-(.*)$', date_format).group('year')
            year = eval(year_format.replace('Y', str(year)))
            date = re.sub('\((.*)\)', str(year), date_format)
            return date

        initial_period, final_period = period.split(',')
        collection = ImageCollection([])
        for i in xrange(offset + 1):
            local_initial_period = parse_period(initial_period, year - i)
            local_final_period = parse_period(final_period, year - i)
            local_collection = self.filterDate(local_initial_period, local_final_period)
            collection = ImageCollection(ee.Algorithms.If(
                ee.Number(local_collection.size()).eq(0),
                collection,
                collection.merge(local_collection)
            ))

        collection = ImageCollection(ee.Algorithms.If(
            ee.Number(collection.size()).eq(0),
            self.filterDate(parse_period("(Y)-01-01", year), parse_period("(Y)-12-31", year)),
            collection
        ))
        return ImageCollection(collection)

    def apply_brdf(self):
        return self.map(lambda image: Image(image).apply_brdf())

    def apply_qamask(self):
        return self.map(lambda image: image.updateMask(Image(image).get_qamask()))

    def clip_geometry(self):
        return self.map(lambda image: Image(image).clip(image.geometry().buffer(settings.EXPORT_BUFFER)))

    def apply_smoothing(self):
        collection = self
        time_field = 'system:time_start'
        join = ee.Join.saveAll(matchesKey='images')
        diff_filter = ee.Filter.maxDifference(difference=1000 * 60 * 60 * 24 * 17, leftField=time_field, rightField=time_field)
        three_neighbor_join = join.apply(primary=collection, secondary=collection, condition=diff_filter)
        smoothed = ImageCollection(
            three_neighbor_join.map(lambda image: Image(image).addBands(ImageCollection.fromImages(image.get('images')).mean(), None, True)))
        return smoothed

    def apply_bands(self, bands):
        return self.map(lambda image: Band.rescale(Image(image).get_bands(bands)))

    def apply_reducers(self, reducers):
        collection = self
        reducer = []
        for r in reducers:
            if r == Reducer.MAX:
                reducer.append(ee.Reducer.max())
            if r == Reducer.MIN:
                reducer.append(ee.Reducer.min())
            if r == Reducer.MEDIAN:
                reducer.append(ee.Reducer.median())
            if r == Reducer.STDV:
                reducer.append(ee.Reducer.stdDev())
            if r == Reducer.COUNT:
                reducer.append(ee.Reducer.count())

        qmo = collection.get_max_by_band(settings.QUALITY_MOSAIC.value, 'qmo') if Reducer.QMO in reducers else None

        image = None
        if reducer:
            reducer = ee.List(reducer)
            image = collection.reduce(
                ee.Algorithms.If(
                    ee.Number(reducer.size()).gte(2),
                    reducer.slice(1).iterate(lambda r, list: ee.Reducer(list).combine(r, sharedInputs=True), reducer.get(0)),
                    reducer.get(0)
                )
            )

        result = None
        if qmo and image:
            result = image.addBands(qmo)
        elif qmo:
            result = qmo
        elif image:
            result = image

        return result.set('system:footprint', ee.Image(collection.first()).geometry())

    def get_max_by_band(self, band, prefix):
        image = self.qualityMosaic(band)
        return image.select(image.bandNames(), Band.apply_prefix(image.bandNames(), prefix))
