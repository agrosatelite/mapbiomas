# -*- coding: utf-8 -*-

import ee

from rsgee.conf import settings
from rsgee.imagecollection import ImageCollection

class FeatureCollection(ee.FeatureCollection):
    def __init__(self, *args, **kargs):
        ee.FeatureCollection.__init__(self, *args, **kargs)

    def filter_by_wrs(self, feature_wrs, feature_wrs_selected={}, feature_wrs_filter=[]):
        collection = ImageCollection([])

        if(feature_wrs_selected.has_key('OR') and feature_wrs_selected['OR']):
            for fs, value in feature_wrs_selected['OR'].items():
                collection = collection.merge(self.filter(ee.Filter.eq(fs, value)))
        else:
            collection = self

        if(feature_wrs_selected.has_key('AND') and feature_wrs_selected['AND']):
            for fs, value in feature_wrs_selected['AND'].items():
                collection = collection.filter(ee.Filter.eq(fs, value))

        if feature_wrs_filter:
            collection = collection.filter(ee.Filter.inList(feature_wrs, ee.List(feature_wrs_filter)))
        return FeatureCollection(collection)

    def get_features(self):
        data = self.getInfo()
        properties = []
        for feature in data['features']:
            d = {
                'PATH': '%03d' % feature['properties']['PATH'],
                'ROW': '%03d' % feature['properties']['ROW'],
                'GEOMETRY': feature['geometry']['coordinates']
            }
            for period in settings.GENERATION_PERIODS:
                d[period] = feature['properties'][period] if feature['properties'].has_key(period) else period
            properties.append(d)
        return properties
