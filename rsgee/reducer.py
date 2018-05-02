# -*- coding: utf-8 -*-
import enum


class Reducer(enum.Enum):
    QMO = "qmo"
    MAX = "max"
    MIN = "min"
    MEDIAN = "median"
    STDV = "stdDev"
    COUNT = "count"
