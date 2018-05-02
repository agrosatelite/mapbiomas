# -*- coding: utf-8 -*-
import ee
import enum


class Band(enum.Enum):
    BLUE = "BLUE"
    GREEN = "GREEN"
    RED = "RED"
    NIR = "NIR"
    SWIR1 = "SWIR1"
    SWIR2 = "SWIR2"
    TIR1 = "TIR1"
    TIR2 = "TIR2"

    #index
    BQA = "BQA"
    QAMASK = "QAMASK"
    EVI2 = "EVI2"
    NDVI = "NDVI"
    CAI = "CAI"
    CEI = "CEI"
    LAI = "LAI"
    SAFER = "SAFER"
    NDWI = "NDWI"
    NDWI2 = "NDWI2"
    MNDWI = "MNDWI"
    AWEI_NSH = "AWEI_NSH"
    AWEI_SH = "AWEI_SH"

    @classmethod
    def apply_prefix(self, bands, prefix):
        def add_prefix(band):
            return ee.String(band).cat("_").cat(prefix)

        return ee.List(bands).map(add_prefix)

    @classmethod
    def rescale(self, image):
        from rsgee.conf import settings
        for mult, bands in settings.EXPORT_SCALES.items():
            for band in bands:
                image = image.addBands(image.select(band.value).multiply(mult), overwrite=True)
        return image.int16()
