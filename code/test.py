# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 08:16:29 2021

@author: YU Yixiong
"""

import static as st
import Heli
import City
import Mission

citylist=City.getCityList()
heliList=["AC313_YL","Bell429"]
hl=[]
# *************************test the enforceablite of heli and city's instantation
for name in heliList:
    hl.append(Heli.addHeli(name))    

# =============================================================================
# '''
# test the mission check progress
# '''
# a=Mission.getMissionList()
# 
# print(a[1].residueCheck())
# =============================================================================

# c=citylist[0]
# c.occupyTimeForTrack.append([10,20,40])
# c.occupyTimeForTrack.append([15,20,40])
# print(c.checkTrackNum(16,90))


hl[0].backToBase(citylist[0])

