import math
import ee
import re

class BRDFCorrect(object):
	def __init__(self):
		self.image = None
		self.corners = None
		self.constants = {
			'pi' : math.pi
		}
		self.coefficientsByBand = {
			'blue': {'fiso': 0.0774, 'fgeo': 0.0079, 'fvol': 0.0372},
			'green': {'fiso': 0.1306, 'fgeo': 0.0178, 'fvol': 0.0580},
			'red': {'fiso': 0.1690, 'fgeo': 0.0227, 'fvol': 0.0574},
			'nir': {'fiso': 0.3093, 'fgeo': 0.0330, 'fvol': 0.1535},
			'swir1': {'fiso': 0.3430, 'fgeo': 0.0453, 'fvol': 0.1154},
			'swir2': {'fiso': 0.2658, 'fgeo': 0.0387, 'fvol': 0.0639}
		}

	def format(self, s, args):
		if not args:
			args = {}
		
		allArgs = self.merge(self.constants, args)

		def fun(keys):
			for b in keys.groups():
				replacement = allArgs[b]
				if (replacement == None):
					print('Undeclared argument: ' + b, 's: ' + s, args)
					return None
				return str(replacement)

		result = re.sub('{([^{}]*)}', fun, s)

		if (result.find('{') > -1):
			return self.format(result, args)
		return result

	def toImage(self, band, args={}):
		if type(band) == str:
			if (band.find('.') > -1 or band.find(' ') > -1 or band.find('{') > -1):
				band = self.image.expression(self.format(band, args), {'i': self.image})
			else:
				band = self.image.select(band)
		return ee.Image(band)

	def set(self, name, toAdd, args={}):
		toAdd = self.toImage(toAdd, args)
		toAdd = toAdd.rename([name])
		self.image = self.image.addBands(toAdd, None, True)

	def setIf(self, name, condition, trueValue, falseValue=0):
		def invertMask(mask):
			return mask.multiply(-1).add(1)

		condition = self.toImage(condition)
		trueMasked = self.toImage(trueValue).mask(self.toImage(condition))
		falseMasked = self.toImage(falseValue).mask(invertMask(condition))
		value = trueMasked.unmask(falseMasked)
		self.set(name, value)

	def merge(self, o1, o2):
		def addAll(target, toAdd):
			for key in toAdd:
				target[key] = toAdd[key]

		result = {}
		addAll(result, o1)
		addAll(result, o2)
		return result

	def x(self, point):
		return ee.Number(ee.List(point).get(0))

	def y(self, point):
		return ee.Number(ee.List(point).get(1))

	def pointBetween(self, pointA, pointB):
		return ee.Geometry.LineString([pointA, pointB]).centroid().coordinates()

	def slopeBetween(self, pointA, pointB):
		return ((self.y(pointA)).subtract(self.y(pointB))).divide((self.x(pointA)).subtract(self.x(pointB)))

	def toLine(self, pointA, pointB):
		return ee.Geometry.LineString([pointA, pointB])

	def findCorners(self):
		footprint = ee.Geometry(self.image.get('system:footprint'))
		bounds = ee.List(footprint.bounds().coordinates().get(0))
		coords = footprint.coordinates()

		xs = coords.map(lambda item:  self.x(item))
		ys = coords.map(lambda item: self.y(item))

		def findCorner(targetValue, values):
			diff = values.map(lambda value: ee.Number(value).subtract(targetValue).abs())
			minValue = diff.reduce(ee.Reducer.min())
			idx = diff.indexOf(minValue)
			return coords.get(idx)

		lowerLeft = findCorner(self.x(bounds.get(0)), xs)
		lowerRight = findCorner(self.y(bounds.get(1)), ys)
		upperRight = findCorner(self.x(bounds.get(2)), xs)
		upperLeft = findCorner(self.y(bounds.get(3)), ys)
		
		return {
			'upperLeft': upperLeft,
			'upperRight': upperRight,
			'lowerRight': lowerRight,
			'lowerLeft': lowerLeft
		}

	def viewAngles(self):
		maxDistanceToSceneEdge = 1000000
		maxSatelliteZenith = 7.5
		upperCenter = self.pointBetween(self.corners['upperLeft'], self.corners['upperRight'])
		lowerCenter = self.pointBetween(self.corners['lowerLeft'], self.corners['lowerRight'])

		slope = self.slopeBetween(lowerCenter, upperCenter)
		slopePerp = ee.Number(-1).divide(slope)

		self.set('viewAz', ee.Image(ee.Number(math.pi / 2).subtract((slopePerp).atan())))

		leftLine = self.toLine(self.corners['upperLeft'], self.corners['lowerLeft'])
		rightLine = self.toLine(self.corners['upperRight'], self.corners['lowerRight'])
		leftDistance = ee.FeatureCollection(leftLine).distance(maxDistanceToSceneEdge)
		rightDistance = ee.FeatureCollection(rightLine).distance(maxDistanceToSceneEdge)
		viewZenith = rightDistance.multiply(maxSatelliteZenith * 2) \
			.divide(rightDistance.add(leftDistance)) \
			.subtract(maxSatelliteZenith)
		self.set('viewZen', viewZenith.multiply(math.pi).divide(180))

	def solarPosition(self):
		#Ported from http://pythonfmask.org/en/latest/_modules/fmask/landsatangles.html
		date = ee.Date(ee.Number(self.image.get('system:time_start')))
		secondsInHour = 3600
		self.set('longDeg',
			ee.Image.pixelLonLat().select('longitude'))
		self.set('latRad', 
			ee.Image.pixelLonLat().select('latitude').multiply(math.pi).divide(180))
		self.set('hourGMT', 
			ee.Number(date.getRelative('second', 'day')).divide(secondsInHour))
		self.set('jdp', #Julian Date Proportion
			date.getFraction('year'))
		self.set('jdpr', #Julian Date Proportion in Radians
			'i.jdp * 2 * {pi}')
		self.set('meanSolarTime', 
			'i.hourGMT + i.longDeg / 15')
		self.set('localSolarDiff', 
			'(0.000075 + 0.001868 * cos(i.jdpr) - 0.032077 * sin(i.jdpr)' +
			'- 0.014615 * cos(2 * i.jdpr) - 0.040849 * sin(2 * i.jdpr))' +
			'* 12 * 60 / {pi}')
		self.set('trueSolarTime', 
			'i.meanSolarTime + i.localSolarDiff / 60 - 12')
		self.set('angleHour',
			'i.trueSolarTime * 15 * {pi} / 180')
		self.set('delta',
			'0.006918 - 0.399912 * cos(i.jdpr) + 0.070257 * sin(i.jdpr) - 0.006758 * cos(2 * i.jdpr)' +
			'+ 0.000907 * sin(2 * i.jdpr) - 0.002697 * cos(3 * i.jdpr) + 0.001480 * sin(3 * i.jdpr)')
		self.set('cosSunZen', 
			'sin(i.latRad) * sin(i.delta) ' +
			'+ cos(i.latRad) * cos(i.delta) * cos(i.angleHour)')
		self.set('sunZen', 
			'acos(i.cosSunZen)')
		self.set('sinSunAzSW', 
			self.toImage('cos(i.delta) * sin(i.angleHour) / sin(i.sunZen)').clamp(-1, 1))
		self.set('cosSunAzSW',
			'(-cos(i.latRad) * sin(i.delta)' +
			'+ sin(i.latRad) * cos(i.delta) * cos(i.angleHour)) / sin(i.sunZen)')
		self.set('sunAzSW',
			'asin(i.sinSunAzSW)')
		self.setIf('sunAzSW',
			'i.cosSunAzSW <= 0',
			'{pi} - i.sunAzSW',
			'sunAzSW')
		self.setIf('sunAzSW',
			'i.cosSunAzSW > 0 and i.sinSunAzSW <= 0',
			'2 * {pi} + i.sunAzSW',
			'sunAzSW')
		self.set('sunAz',
			'i.sunAzSW + {pi}')
		self.setIf('sunAz', 
			'i.sunAz > 2 * {pi}', 'i.sunAz - 2 * {pi}', 'sunAz')

	def sunZenOut(self):
		# https://nex.nasa.gov/nex/static/media/publication/HLS.v1.0.UserGuide.pdf
		self.set('centerLat',
			ee.Number(
				ee.Geometry(self.image.get('system:footprint'))
					.bounds().centroid(30).coordinates().get(0))
				.multiply(math.pi).divide(180))
		self.set('sunZenOut',
			'(31.0076' +
			'- 0.1272 * i.centerLat' +
			'+ 0.01187 * pow(i.centerLat, 2)' +
			'+ 2.40E-05 * pow(i.centerLat, 3)' +
			'- 9.48E-07 * pow(i.centerLat, 4)' +
			'- 1.95E-09 * pow(i.centerLat, 5)' +
			'+ 6.15E-11 * pow(i.centerLat, 6)) * {pi}/180')

	def cosPhaseAngle(self, name, sunZen, viewZen, relativeSunViewAz):
		args = {
			'sunZen': sunZen,
			'viewZen': viewZen,
			'relativeSunViewAz': relativeSunViewAz
		}
		self.set(name,
			self.toImage('cos({sunZen}) * cos({viewZen})' +
				'+ sin({sunZen}) * sin({viewZen}) * cos({relativeSunViewAz})', args)
				.clamp(-1, 1))

	def rossThick(self, bandName, sunZen, viewZen, relativeSunViewAz):
		args = {'sunZen': sunZen, 'viewZen': viewZen, 'relativeSunViewAz': relativeSunViewAz}
		self.cosPhaseAngle('cosPhaseAngle', sunZen, viewZen, relativeSunViewAz)
		self.set('phaseAngle',
			'acos(i.cosPhaseAngle)')
		self.set(bandName,
			'(({pi}/2 - i.phaseAngle) * i.cosPhaseAngle + sin(i.phaseAngle)) ' +
			'/ (cos({sunZen}) + cos({viewZen})) - {pi}/4', args)

	def anglePrime(self, name, angle):
		args = {'b/r': 1, 'angle': angle}
		self.set('tanAnglePrime', '{b/r} * tan({angle})', args)
		self.setIf('tanAnglePrime', 'i.tanAnglePrime < 0', 0)
		self.set(name, 'atan(i.tanAnglePrime)')

	def liThin(self, bandName, sunZen, viewZen, relativeSunViewAz):
		#From https://modis.gsfc.nasa.gov/data/atbd/atbd_mod09.pdf
		args = {
			'sunZen': sunZen,
			'viewZen': viewZen,
			'relativeSunViewAz': relativeSunViewAz,
			'h/b': 2,
		}

		self.anglePrime('sunZenPrime', sunZen)
		self.anglePrime('viewZenPrime', viewZen)
		self.cosPhaseAngle('cosPhaseAnglePrime', 'i.sunZenPrime', 'i.viewZenPrime', relativeSunViewAz)

		self.set('distance',
			'sqrt(pow(tan(i.sunZenPrime), 2) + pow(tan(i.viewZenPrime), 2)' +
			'- 2 * tan(i.sunZenPrime) * tan(i.viewZenPrime) * cos({relativeSunViewAz}))', args)
		self.set('temp',
			'1/cos(i.sunZenPrime) + 1/cos(i.viewZenPrime)')
		self.set('cosT',
			self.toImage('{h/b} * sqrt(pow(i.distance, 2) + pow(tan(i.sunZenPrime) * tan(i.viewZenPrime) * sin({relativeSunViewAz}), 2))' +
				'/ i.temp', args)
				.clamp(-1, 1))
		self.set('t', 'acos(i.cosT)')
		self.set('overlap',
			'(1/{pi}) * (i.t - sin(i.t) * i.cosT) * (i.temp)')
		self.setIf('overlap', 'i.overlap > 0', 0)
		self.set(bandName,
			'i.overlap - i.temp' +
			'+ (1/2) * (1 + i.cosPhaseAnglePrime) * (1/cos(i.sunZenPrime)) * (1/cos(i.viewZenPrime))')

	def brdf(self, bandName, kvolBand, kgeoBand, coefficients):
		args = self.merge(coefficients, {
			#kvol: 'i.' + kvolBand,
			'kvol': '3 * i.' + kvolBand, #check this multiplication factor.  Is there an 'optimal' value?  Without a factor here, there is not enough correction.
			'kgeo': 'i.' + kgeoBand
		})
		self.set(bandName, '{fiso} + {fvol} * {kvol} + {fgeo} * {kvol}', args)

	def applyCFactor(self, bandName, coefficients):
		self.brdf('brdf', 'kvol', 'kgeo', coefficients)
		self.brdf('brdf0', 'kvol0', 'kgeo0', coefficients)
		self.set('cFactor',
			'i.brdf0 / i.brdf', coefficients)
		self.set(bandName, '{bandName} * i.cFactor', {'bandName': 'i.' + bandName})

	def adjustBands(self):
		for bandName in self.coefficientsByBand:
			self.applyCFactor(bandName, self.coefficientsByBand[bandName])

	def correct(self, image):
		self.image = image
		bands = self.coefficientsByBand.keys()
		self.image = ee.Image(ee.Algorithms.If(
			ee.List(['LANDSAT_5', 'LANDSAT_7']).contains(self.image.get('SPACECRAFT_ID')),
          	self.image.select(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], bands),
			ee.Algorithms.If(
				ee.List(['LANDSAT_8']).contains(self.image.get('SPACECRAFT_ID')),
				self.image.select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7'], bands),
				ee.Image(0)
			)
		))

		self.corners = self.findCorners()

		self.viewAngles()
		self.solarPosition()
		self.sunZenOut()
		self.set('relativeSunViewAz', 'i.sunAz - i.viewAz')
		self.rossThick('kvol', 'i.sunZen', 'i.viewZen', 'i.relativeSunViewAz')
		self.rossThick('kvol0', 'i.sunZenOut', 0, 0)

		self.liThin('kgeo', 'i.sunZen', 'i.viewZen', 'i.relativeSunViewAz')
		self.liThin('kgeo0', 'i.sunZenOut', 0, 0)

		self.adjustBands()

		self.image = ee.Image(ee.Algorithms.If(
			ee.List(['LANDSAT_5', 'LANDSAT_7']).contains(self.image.get('SPACECRAFT_ID')),
          	self.image.select(bands, ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']),
			ee.Algorithms.If(
				ee.List(['LANDSAT_8']).contains(self.image.get('SPACECRAFT_ID')),
				self.image.select(bands, ['B2', 'B3', 'B4', 'B5', 'B6', 'B7']),
				ee.Image(0)
			)
		))

		return image.addBands(self.image, None, True)

BRDFCorrect = BRDFCorrect()
