# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 19:31:46 2021

@author: YU Yixiong
"""

import openpyxl  
import math  
import random  
# import matplotlib.pyplot as plt 
import static as st
import Heli
import City
import Mission


def findTheWaitHeli(heliList):#找一个现在作业时间最小的飞机，也就是实际仿真中，下一架要调度的飞机  
     lTime=100000000000000000  
     h=None  
     for heli in heliList:  
          if(heli.t<lTime):  
               lTime=heli.t  
               h=heli  
     return h

def findTheNearestCity(lat,lon,locationList):  
      #根据传入的城市列表和坐标点，输出离坐标点最近的城市  
      dmin=100000000000  
      loc=None  
      for location in locationList:  
          d=st.getDistance(lat, lon, location.para["PosY"], location.para["PosX"])  
          if(d<dmin):  
                dmin=d  
                loc=location  
      return loc 

def findAvailbleRefuelingCity(heli,cityList):
    # return the AvailbleRefuelingCity ,based on the heli name and citylist
    availbleCityList=[]
    if heli.para["IsHeli"]==True:
        for city in cityList:
            if city.para["hasGas"]==True:
                if city.heliNum>heli.para["HeliArea"]:
                    availbleCityList.append(city.para["Name"])
    else:
        for city in cityList:
            if city.para["hasGas"]==True:
                if city.trackNum>heli.para["TrackArea"]:
                    availbleCityList.append(city.para["Name"])
    return availbleCityList

def findAvailbleLandingCity(heli,cityList):
    availbleCityList=[]
    if heli.para["IsHeli"]==True:
        for city in cityList:
            if city.para["hasGas"]==False:
                if city.heliNum>heli.para["HeliArea"]:
                    availbleCityList.append(city.para["Name"])
    else:
        for city in cityList:
            if city.para["hasGas"]==False:
                if city.trackNum>heli.para["TrackArea"]:
                    availbleCityList.append(city.para["Name"])
    return availbleCityList

def calRouteOilForScout(heli,p1,p2):
    #this heli get P1 first and then p2, you should convert the place type first to get the coordinates
    # p1.p2 are city 
    d1=st.getDistance(heli.lat, heli.lon, p1.para["PosY"], p1.para["PosX"])
    d2=st.getDistance(p1.para["PosY"], p1.para["PosX"],p2.para["PosY"], p2.para["PosX"])
    distance=d1+d2
    
    return distance*heli.para["OilUseSpeed"]/heli.para["Speed"]

def calRouteOil(heli,p1,p2,p3):
    #if the plane can back to base after the mission, then we judge it OK to assign this mission; if not then just go back to the nearest base to refuel
    
    #this heli get P1 first and then p2, you should convert the place type first to get the coordinates
    # p1.p2 are city     #p3 is the nearest city that can refuel , you need to find it first
    veri=False
    
    d1=st.getDistance(heli.lat, heli.lon, p1.para["PosY"], p1.para["PosX"])
    d2=st.getDistance(p1.para["PosY"], p1.para["PosX"],p2.para["PosY"], p2.para["PosX"])
    d3=st.getDistance(p2.para["PosY"], p2.para["PosX"],p3.para["PosY"], p3.para["PosX"])
    distance=d1+d2+d3
    
    return distance*heli.para["OilUseSpeed"]/heli.para["Speed"]
    

def prospectTaskLoad(heli,m):
    # if the heli can do the mission, the function will return the taskload which != 0 
    
    missionNeed=["WuZiNeed","JiuYuanMemberNeed",  "ToTransZaiMin", "ToTransShangYuan", "FireNum",    "ZCArea"]
    taskCapa=[ "MaxWuZi",    "MaxHuman",           "MaxHuman",     "YH_Space",         "XF_Content", "YG_Speed"]
    
    # "WG_bool","SheBeiNeed",
    taskName=taskNameForMission(m)
    
    if taskName in missionNeed:
        if heli.para[taskCapa[missionNeed.index(taskName)]] > 0:
            return taskCapa[missionNeed.index(taskName)],min(heli.para[taskCapa[missionNeed.index(taskName)]],m.residue[taskName])
        else:
            return taskCapa[missionNeed.index(taskName)],0
    elif (taskName=="SheBeiNeed"):
        # get the max equipment that heli can swing
        if heli.para["WG_bool"]==2:#这里是后期要修改的bug，S76是不能够吊运设备的，这里需要加入设备重量信息判断
            return "WG_bool",1
        else:
            return "WG_bool",0
    else:
        # the only task name remained is "external load" which mean "WX_max" 
        if heli.para["Name"]=="BZK_005":
            return taskCapa[missionNeed.index(taskName)],0
        else: 
            return taskCapa[missionNeed.index(taskName)],(min(heli.para[taskCapa[missionNeed.index(taskName)]],m.residue[taskName]))
    
def missionToCity(m,cityList):
    # return the city object based on its ID infomation
    for c in cityList:
        if c.para["Id"]==m.para["From"]:
            return c

def taskNameForMission(m):
    # find out the mission's task Name 
    
    taskName=None
    for key in m.residue.keys():
        if m.residue[key]!=0:
            taskName=key
            return taskName
# def capaNeedForMission(m):
#     taskName=taskNameForMission(m)
    
    
def getRouteOrder(m,c):
    # According to the mission sort, judge the route order like "heli to m(city Class), to c"
    
    taskName=taskNameForMission(m)
        
    mc=["ToTransZaiMin", "ToTransShangYuan"]
    cm=["WuZiNeed", "JiuYuanMemberNeed", "SheBeiNeed", "FireNum"]
    if taskName in mc:
        return (missionToCity(m),c)
    elif taskName in cm:
        return (c,missionToCity(m))
    else:
        return missionToCity(m)

def findBase(cityList):
     baseList=[]
     for c in cityList:
          if c.para["hasGas"]==True:
               baseList.append(c)
     return baseList

def calTaskTime(heli,taskCapa,taskload):
     # calculate the working time for each class of task, based on the taskload and class, and the heli.performance 
     if taskCapa=="MaxWuZi":
          tasktime=2*taskload*heli.para["WuZiTime"]
     
     return tasktime

def missionEnforceInspect(heli,m,c,cityList):
     # if the heli can do the job, then return a list that contain the progress's infomation; if not return the null set
     # processInfo=[route,taskName,taskCapa,taskload,[heliLog1,helilog2,...],heli.oil,heli.t]
    processInfo=[]
    
# =============================================================================
## inspect the oil
# =============================================================================
    oilNeed=0
# inspect the oil  :  oil doing task
# calculate the taskload
    taskCapa,taskload=prospectTaskLoad(heli,m)
# check whether the heli can do the job
    if(taskload==0):
        return processInfo
    tasktime=calTaskTime(heli, taskCapa, taskload)
    oilNeed+=tasktime*heli.para["OilUseSpeed"]

# inspect the oil  :  oil on the road
# check distance
    route=getRouteOrder(m,c) #these are two cities
    nearestBase=findTheNearestCity(route[-1].para["PosY"], route[-1].para["PosX"], findBase(cityList))
    
    if len(route)==2:         
        oilNeed+=calRouteOil(heli, route[0], route[1], nearestBase)
    if len(route)==1:         
        oilNeed+=calRouteOilForScout(heli,route[0],nearestBase)
    
    if heli.oil<oilNeed:
        return processInfo
        
# =============================================================================
# # inspect the landing condition
# =============================================================================
    
    
    
    
    
    
    
    return processInfo








if __name__ =="__main__":
    cityList=City.getCityList()
    heli=Heli.addHeli("Bell429")
    ml=Mission.getMissionList()
    # print(missionToCity(ml[0], cityList).para)
    # print(prospectTaskLoad(heli,ml[2]))
    
    # (a,b)=getRouteOrder(ml[5], cityList[1])
    # print(a.para,"\n",b.para)
# print(findAvailbleLandingCity(heli, cityList))
# print(calRouteDistance(heli, cityList[1], cityList[1]))