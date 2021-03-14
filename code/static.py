# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:04:27 2021

@author: yixiong YU

note: 
"""
# from numpy.random import RandomState
# import pandas as pd
# import numpy as np
# import time
# import openpyxl
# from ast import literal_eval
# import json
# import os
import math
from math import  cos,sin

def rad(d):
    # make the angle to radian
    return d * math.pi / 180.0

def getDistance(lat1, lng1, lat2, lng2):
    EARTH_REDIUS = 6378.137
    radLat1 = rad(lat1)
    radLat2 = rad(lat2)
    a = radLat1 - radLat2
    b = rad(lng1) - rad(lng2)
    s = 2 * math.asin(math.sqrt(math.pow(sin(a/2), 2) + cos(radLat1) * cos(radLat2) * math.pow(sin(b/2), 2)))
    s = s * EARTH_REDIUS
    return s#计算结果单位为千米(km)
# print(getDistance(28.55, 120, 29.4, 120))

