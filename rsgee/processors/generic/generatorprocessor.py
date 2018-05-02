# -*- coding: utf-8 -*-
import ee

from rsgee.conf import settings
from rsgee.image import Image
from rsgee.imagecollection import ImageCollection
from rsgee.processors.generic.base import BaseProcessor

class GeneratorProcessor(BaseProcessor):
	def __init__(self, collection, feature_collection, bands, reducers, years, offset, periods, clip_geometry=False, apply_brdf=False, apply_mask=False):
		BaseProcessor.__init__(self)
		self._collection = collection
		self._feature_collection = feature_collection
		self._bands = bands
		self._reducers = reducers
		self._years = years
		self._offset = offset
		self._periods = periods
		self._clip_geometry = clip_geometry
		self._apply_brdf = apply_brdf
		self._apply_mask = apply_mask

	def run(self):
		for year in self._years:
			for feature in self._feature_collection.get_features():
				path = feature.get('PATH')
				row = feature.get('ROW')
				geometry = ee.Geometry.MultiPolygon(feature.get('GEOMETRY'))

				image_collection = self._collection.filter(ee.Filter.eq('WRS_PATH', int(path))).filter(ee.Filter.eq('WRS_ROW', int(row)))

				for period in self._periods:
					images_by_period = ImageCollection(image_collection).filter_by_period(year, feature.get(period), self._offset)

					if self._apply_brdf:
						images_by_period = images_by_period.apply_brdf()

					if self._clip_geometry:
						images_by_period = images_by_period.clip_geometry()

					if self._apply_mask:
						images_by_period = images_by_period.apply_qamask()

					if self._bands:
						images_by_period = images_by_period.apply_bands(self._bands)

					if self._reducers:
						image_reduced = Image(ImageCollection(images_by_period).apply_reducers(self._reducers))
						image_reduced = image_reduced.rename(image_reduced.bandNames().map(
							lambda band: ee.String(period).cat('_').cat(band))
						)
						final_name = "{0}_{1}_{2}".format(settings.COLLECTION_PREFIX, "{0}{1}".format(path, row), str(year))
						final_image = image_reduced.clip(geometry).select(settings.GENERATION_VARIABLES + settings.GENERATION_EXTRA_VARIABLES).set('year', year).set('system:footprint', geometry)

						self.add_image_in_batch(final_name, {"image": final_image,
															 "year": int(year),
															 "path": int(path),
															 "row": int(row),
															 "geometry": geometry})
					else:
						images_by_period = images_by_period.map(
							lambda image: Image(image).rename(Image(image).bandNames().map(
								lambda band: ee.String(period).cat('_').cat(band))
							)
						)
						images_by_period = images_by_period.toList(settings.MAX_IMAGES)
						for i in xrange(images_by_period.size().getInfo()):
							image = Image(images_by_period.get(i))
							date = image.date().format('yyyyMMdd').getInfo()
							final_name = "{0}_{1}_{2}".format(settings.COLLECTION_PREFIX, "{0}{1}".format(path, row), str(date))
							final_image = Image(image).clip(geometry).select(settings.GENERATION_VARIABLES + settings.GENERATION_EXTRA_VARIABLES).set('year', year).set('system:footprint', geometry)

							self.add_image_in_batch(final_name, {"image": final_image,
																 "year": int(year),
																 "path": int(path),
																 "row": int(row),
																 "geometry": geometry})
