# -*- coding: utf-8 -*-

import math
import ee

from rsgee.band import Band
from rsgee.provider import Provider
from rsgee.conf import settings
from rsgee.utils.brdf import BRDFCorrect


class Image(ee.Image):
    def get_bands(self, bands=[]):
        images = []
        for band in bands:
            if band == Band.BLUE:
                images.append(self.get_blue())
            elif band == Band.GREEN:
                images.append(self.get_green())
            elif band == Band.RED:
                images.append(self.get_red())
            elif band == Band.NIR:
                images.append(self.get_nir())
            elif band == Band.SWIR1:
                images.append(self.get_swir(1))
            elif band == Band.SWIR2:
                images.append(self.get_swir(2))
            elif band == Band.TIR1:
                images.append(self.get_tir(1))
            elif band == Band.TIR2:
                images.append(self.get_tir(2))
            elif band == Band.BQA:
                images.append(self.get_bqa())
            elif band == Band.QAMASK:
                images.append(self.get_qamask())
            elif band == Band.EVI2:
                images.append(self.get_evi2())
            elif band == Band.NDVI:
                images.append(self.get_ndvi())
            elif band == Band.CAI:
                images.append(self.get_cai())
            elif band == Band.CEI:
                images.append(self.get_cei())
            elif band == Band.LAI:
                images.append(self.get_lai())
            elif band == Band.SAFER:
                images.append(self.get_safer())
            elif band == Band.MNDWI:
                images.append(self.get_mndwi())
            elif band == Band.NDWI:
                images.append(self.get_ndwi(1))
            elif band == Band.NDWI2:
                images.append(self.get_ndwi(2))
            elif band == Band.AWEI_NSH:
                images.append(self.get_awei_nsh())
            elif band == Band.AWEI_SH:
                images.append(self.get_awei_sh())
        return ee.Image.cat(images)

    def get_blue(self):
        blue = Image(0).rename([Band.BLUE.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07]:
            blue = self.select(['B1'], [Band.BLUE.value])
        elif settings.COLLECTION_PROVIDER in [Provider.LC08, Provider.S2]:
            blue = self.select(['B2'], [Band.BLUE.value])
        elif settings.COLLECTION_PROVIDER in [Provider.MOD13Q1]:
            blue = self.select(['sur_refl_b03'], [Band.BLUE.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.BLUE.value), self.select(Band.BLUE.value), blue)

    def get_green(self):
        green = Image(0).rename([Band.GREEN.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07]:
            green = self.select(['B2'], [Band.GREEN.value])
        elif settings.COLLECTION_PROVIDER in [Provider.LC08, Provider.S2]:
            green = self.select(['B3'], [Band.GREEN.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.GREEN.value), self.select(Band.GREEN.value), green)

    def get_red(self):
        red = Image(0).rename([Band.RED.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07]:
            red = self.select(['B3'], [Band.RED.value])
        elif settings.COLLECTION_PROVIDER in [Provider.LC08, Provider.S2]:
            red = self.select(['B4'], [Band.RED.value])
        elif settings.COLLECTION_PROVIDER in [Provider.MOD13Q1]:
            red = self.select(['sur_refl_b01'], [Band.RED.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.RED.value), self.select(Band.RED.value), red)

    def get_nir(self):
        nir = Image(0).rename([Band.NIR.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07]:
            nir = self.select(['B4'], [Band.NIR.value])
        elif settings.COLLECTION_PROVIDER in [Provider.LC08]:
            nir = self.select(['B5'], [Band.NIR.value])
        elif settings.COLLECTION_PROVIDER in [Provider.MOD13Q1]:
            nir = self.select(['sur_refl_b02'], [Band.NIR.value])
        elif settings.COLLECTION_PROVIDER in [Provider.S2]:
            nir = self.select(['B8'], [Band.NIR.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.NIR.value), self.select(Band.NIR.value), nir)

    def get_swir(self, version):
        """
            'version' in [1, 2]
        """
        if version == 1:
            swir1 = Image(0).rename([Band.SWIR1.value])
            if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07]:
                swir1 = self.select(['B5'], [Band.SWIR1.value])
            elif settings.COLLECTION_PROVIDER in [Provider.LC08]:
                swir1 = self.select(['B6'], [Band.SWIR1.value])
            elif settings.COLLECTION_PROVIDER in [Provider.S2]:
                swir1 = self.select(['B11'], [Band.SWIR1.value])

            return ee.Algorithms.If(self.bandNames().contains(Band.SWIR1.value), self.select(Band.SWIR1.value), swir1)

        elif version == 2:
            swir2 = Image(0).rename([Band.SWIR2.value])
            if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08]:
                swir2 = self.select(['B7'], [Band.SWIR2.value])
            elif settings.COLLECTION_PROVIDER in [Provider.S2]:
                swir2 = self.select(['B12'], [Band.SWIR2.value])

            return ee.Algorithms.If(self.bandNames().contains(Band.SWIR2.value), self.select(Band.SWIR2.value), swir2)

    def get_tir(self, version):
        """
            'version' in [1, 2]
        """
        if version == 1:
            tir1 = Image(0).rename([Band.TIR1.value])
            if settings.COLLECTION_PROVIDER in [Provider.LT05]:
                tir1 = self.select(['B6'], [Band.TIR1.value])
            elif settings.COLLECTION_PROVIDER in [Provider.LE07]:
                tir1 = self.select(['B6_VCID_2'], [Band.TIR1.value])
            elif settings.COLLECTION_PROVIDER in [Provider.LC08]:
                tir1 = self.select(['B10'], [Band.TIR1.value])

            return ee.Algorithms.If(self.bandNames().contains(Band.TIR1.value), self.select(Band.TIR1.value), tir1)

        elif version == 2:
            tir2 = Image(0).rename([Band.TIR2.value])
            if settings.COLLECTION_PROVIDER in [Provider.LC08]:
                tir2 = self.select(['B11'], [Band.TIR2.value])

            return ee.Algorithms.If(self.bandNames().contains(Band.TIR2.value), self.select(Band.TIR2.value), tir2)

    def get_bqa(self):
        bqa = Image(0).rename([Band.BQA.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08]:
            bqa = self.select(['BQA'], [Band.BQA.value])
        if settings.COLLECTION_PROVIDER in [Provider.MOD13Q1]:
            bqa = self.select(['DetailedQA'], [Band.BQA.value])
        if settings.COLLECTION_PROVIDER in [Provider.S2]:
            bqa = self.select(['QA60'], [Band.BQA.value])
        return ee.Algorithms.If(self.bandNames().contains(Band.BQA.value), self.select(Band.BQA.value), bqa)

    def get_qamask(self):
        mask = Image(0).rename([Band.QAMASK.value])
        bqa = Image(self.get_bqa())

        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08]:
            cloud_mask_image = Image(1).rename([Band.QAMASK.value])
            for start, end, desired in settings.QA_BITS.get(settings.COLLECTION_PROVIDER.value):
                pattern = 0
                for i in xrange(start, end + 1):
                    pattern = int(pattern + math.pow(2, i))
                blueprint = bqa.bitwiseAnd(pattern)
                blueprint = blueprint.rightShift(start)
                blueprint = blueprint.eq(desired)
                cloud_mask_image = cloud_mask_image.updateMask(blueprint)
            mask = cloud_mask_image

        if settings.COLLECTION_PROVIDER in [Provider.S2]:
            cloudBitMask = math.pow(2, 10)
            cirrusBitMask = math.pow(2, 11)
            cloud = ee.Image(bqa.bitwiseAnd(cloudBitMask).eq(0))
            cirrus = ee.Image(bqa.bitwiseAnd(cirrusBitMask).eq(0))
            mask = cloud.And(cirrus)

        return ee.Algorithms.If(self.bandNames().contains(Band.QAMASK.value), self.select(Band.QAMASK.value), mask)

    def get_evi2(self):
        """
            Reference: Jiang, Z., Huete, A. R., Didan, K., & Miura, T. (2008). Development of a two-band enhanced vegetation index without a blue band.
            Remote sensing of Environment, 112(10), 3833-3845.
        """
        evi2 = Image(0).rename([Band.EVI2.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08, Provider.MOD13Q1, Provider.S2]:
            evi2 = self.expression('2.5 * ((NIR - RED) / (NIR + 2.4*RED + 1))', {
                'NIR': self.get_nir(),
                'RED': self.get_red()
            }).select([0], [Band.EVI2.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.EVI2.value), self.select(Band.EVI2.value), evi2)

    def get_ndvi(self):
        ndvi = Image(0).rename([Band.NDVI.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08, Provider.S2]:
            ndvi = self.expression('(NIR - RED) / (NIR + RED)', {
                'RED': self.get_red(),
                'NIR': self.get_nir()
            }).select([0], [Band.NDVI.value])
        elif settings.COLLECTION_PROVIDER in [Provider.MOD13Q1]:
            ndvi = self.select(['NDVI'], [Band.NDVI.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.NDVI.value), self.select(Band.NDVI.value), ndvi)

    def get_cai(self):
        cai = Image(0).rename([Band.CAI.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08, Provider.S2]:
            cai = self.expression('SWIR2 / SWIR1', {
                'SWIR1': self.get_swir(1),
                'SWIR2': self.get_swir(2),
            }).select([0], [Band.CAI.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.CAI.value), self.select(Band.CAI.value), cai)

    def get_cei(self):
        """
            Reference: Rizzi, R., Risso, J., Epiphanio, R. D. V., Rudorff, B. F. T., Formaggio, A. R., Shimabukuro, Y. E., & Fernandes, S. L. (2009).
            Estimativa da área de soja no Mato Grosso por meio de imagens MODIS. Simpósio Brasileiro de Sensoriamento Remoto, 14, 387-394.
        """
        wet_name = settings.GENERATION_PERIODS[0]
        dry_name = settings.GENERATION_PERIODS[1]
        extra_name = settings.GENERATION_EXTRA_PERIODS[0]
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08, Provider.S2]:
            wet = map(lambda x: "{0}_{1}".format(wet_name, x), ['NIR_qmo', 'EVI2_qmo', 'NDWI_qmo'])
            dry = map(lambda x: "{0}_{1}".format(dry_name, x), ['NIR_min', 'EVI2_min', 'NDWI_min'])
            extra = map(lambda x: "{0}_{1}".format(extra_name, x), ['NIR_cei', 'EVI2_cei', 'NDWI_cei'])
        elif settings.COLLECTION_PROVIDER in [Provider.MOD13Q1]:
            wet = "{0}_{1}".format(wet_name, 'EVI2_max')
            dry = "{0}_{1}".format(dry_name, 'EVI2_min')
            extra = ["{0}_{1}".format(extra_name, 'EVI2_cei')]

        return self.expression('1000000*(WET_max - DRY_min) / (1000000+WET_max + 1000000+DRY_min)', {
            'WET_max': self.select(wet),
            'DRY_min': self.select(dry),
        }).rename(extra)

    def get_lai(self):
        """
            Reference: Chen, J.M.; Black, T.A. (1992). "Defining leaf area index for non-flat leaves".
            Agricultural and Forest Meteorology.
        """
        lai = Image(0).rename([Band.LAI.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08, Provider.S2]:
            lai = self.expression('0.3977 * (2.5556 * (NIR - RED)/(NIR + RED))', {
                'RED': self.get_red(),
                'NIR': self.get_nir(),
            }).select([0], [Band.LAI.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.LAI.value), self.select(Band.LAI.value), lai)

    def get_safer(self):
        """
            Reference: Teixeira, A.H.C. Determining regional actual evapotranspiration of irrigated crops and natural
            vegetation in the São Francisco River Basin (Brazil) using remote sensing and Penman-Monteith Equation.
            Remote Sens 2010, 2, 1287–1319.
        """
        safer = Image(0).rename([Band.SAFER.value])

        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08]:
            coefficients = settings.SAFER.get(settings.COLLECTION_PROVIDER.value)
            temperature_kelvin = Image(self.get_tir(1))
            temperature_celsius = Image(temperature_kelvin.add(-273.15))
            ndvi = Image(self.get_ndvi())

            planetary_albedo = Image(
                self.expression('(BLUE * BLUE_CV) + (GREEN * GREEN_CV) + (RED * RED_CV) + (NIR * NIR_CV) + (SWIR1 * SWIR1_CV) + (SWIR2 * SWIR2_CV)', {
                    'BLUE': self.get_blue(), 'BLUE_CV': coefficients.get('BLUE'),
                    'GREEN': self.get_green(), 'GREEN_CV': coefficients.get('GREEN'),
                    'RED': self.get_red(), 'RED_CV': coefficients.get('RED'),
                    'NIR': self.get_nir(), 'NIR_CV': coefficients.get('NIR'),
                    'SWIR1': self.get_swir(1), 'SWIR1_CV': coefficients.get('SWIR1'),
                    'SWIR2': self.get_swir(2), 'SWIR2_CV': coefficients.get('SWIR2'),
                }))
            surface_albedo = Image(planetary_albedo.multiply(coefficients.get('A_ALBEDO')).add(coefficients.get('B_ALBEDO')))
            safer = temperature_celsius.multiply(coefficients.get('B_ET_ET0')).divide(ndvi.multiply(surface_albedo)).add(
                coefficients.get('A_ET_ET0')).exp()
            safer = ndvi.expression('b(0) < 0 ? 0 : SAFER', {
                'SAFER': safer
            }).select([0], [Band.SAFER.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.SAFER.value), self.select(Band.SAFER.value), safer)

    def get_ndwi(self, version=1):
        """
            Reference:
                1: Gao, B. C. (1996). NDWI—A normalized difference water index for remote sensing of vegetation liquid water from space.
                Remote sensing of environment, 58(3), 257-266.

                2: McFeeters, S. K. (1996). The use of the Normalized Difference Water Index (NDWI) in the delineation of open water features.
                International journal of remote sensing, 17(7), 1425-1432.
        """
        ndwi = Image(0).rename([Band.NDWI.value])
        ndwi_band_name = None
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08, Provider.S2]:
            if version == 1:
                ndwi_band_name = Band.NDWI.value
                ndwi = self.expression('(NIR - SWIR1) / (NIR + SWIR1)', {
                    'NIR': self.get_nir(),
                    'SWIR1': self.get_swir(1)
                }).select([0], [ndwi_band_name])
            elif version == 2:
                ndwi_band_name = Band.NDWI2.value
                ndwi = self.expression('(GREEN - NIR) / (GREEN + NIR)', {
                    'GREEN': self.get_green(),
                    'NIR': self.get_nir(),
                }).select([0], [ndwi_band_name])
            else:
                raise AttributeError("Version {version} not exists.".format(version=version))
        return ee.Algorithms.If(self.bandNames().contains(ndwi_band_name), self.select(ndwi_band_name), ndwi)

    def get_mndwi(self):
        """
            Reference: Xu, Hanqiu. "Modification of normalised difference water index (NDWI) to enhance open water features in remotely sensed imagery."
            International journal of remote sensing 27.14 (2006): 3025-3033.
        """
        mndwi = Image(0).rename([Band.MNDWI.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08, Provider.S2]:
            mndwi = self.expression('(GREEN - SWIR1) / (GREEN + SWIR1)', {
                'GREEN': self.get_green(),
                'SWIR1': self.get_swir(1),
            }).select([0], [Band.MNDWI.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.MNDWI.value), self.select(Band.MNDWI.value), mndwi)

    def get_awei_nsh(self):
        """
            Reference: Feyisa, G.L.; Meilby, H.; Fensholt, R.; Proud, S.R. Automated water extraction index: A new technique for surface water mapping using Landsat imagery.
            Remote Sens. Environ. 2014, 140, 23–35.
        """
        awei_nsh = Image(0).rename([Band.AWEI_NSH.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08, Provider.S2]:
            awei_nsh = self.expression('4 * (GREEN - SWIR1) -  0.25 * NIR + 2.75 * SWIR2', {
                'GREEN': self.get_green(),
                'NIR': self.get_nir(),
                'SWIR1': self.get_swir(1),
                'SWIR2': self.get_swir(2),
            }).select([0], [Band.AWEI_NSH.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.AWEI_NSH.value), self.select(Band.AWEI_NSH.value), awei_nsh)

    def get_awei_sh(self):
        """
            Reference: Feyisa, G.L.; Meilby, H.; Fensholt, R.; Proud, S.R. Automated water extraction index: A new technique for surface water mapping using Landsat imagery.
            Remote Sens. Environ. 2014, 140, 23–35.
        """
        awei_sh = Image(0).rename([Band.AWEI_SH.value])
        if settings.COLLECTION_PROVIDER in [Provider.LT05, Provider.LE07, Provider.LC08, Provider.S2]:
            awei_sh = self.expression('BLUE + 2.5 * GREEN - 1.5 * (NIR + SWIR1) - 0.25 * SWIR2', {
                'BLUE': self.get_blue(),
                'GREEN': self.get_green(),
                'NIR': self.get_nir(),
                'SWIR1': self.get_swir(1),
                'SWIR2': self.get_swir(2),
            }).select([0], [Band.AWEI_SH.value])

        return ee.Algorithms.If(self.bandNames().contains(Band.AWEI_SH.value), self.select(Band.AWEI_SH.value), awei_sh)

    def apply_brdf(self):
        return BRDFCorrect.correct(self)
