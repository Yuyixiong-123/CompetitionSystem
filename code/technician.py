# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 19:31:46 2021

@author: YU Yixiong
"""

import random  
import copy
import json
import static as st
import Heli
import City
import Mission
import commander

class config():
    refuelTimeInBase=1200

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
def missionToCity(m,cityList):
    # return the city object based on its ID infomation
    for c in cityList:
        if c.para["Id"]==m.para["From"]:
            return c
       
def calRouteOilForScout(heli,p1,p2):
    #this heli get P1 first and then p2, you should convert the place type first to get the coordinates
    # p1.p2 are city 
    d1=st.getDistance(heli.lat, heli.lon, p1.para["PosY"], p1.para["PosX"])
    d2=st.getDistance(p1.para["PosY"], p1.para["PosX"],p2.para["PosY"], p2.para["PosX"])
    distance=d1+d2
    
    # all based on hour(h) unit 
    return distance*heli.para["OilUseSpeed"]/heli.para["Speed"]

def calRouteOil(heli,p1,p2,p3):
    #if the plane can back to base after the mission, then we judge it OK to assign this mission; if not then just go back to the nearest base to refuel
    
    #this heli get P1 first and then p2, you should convert the place type first to get the coordinates
    # p1.p2 are city     #p3 is the nearest city that can refuel , you need to find it first
    
    d1=st.getDistance(heli.lat, heli.lon, p1.para["PosY"], p1.para["PosX"])
    d2=st.getDistance(p1.para["PosY"], p1.para["PosX"],p2.para["PosY"], p2.para["PosX"])
    d3=st.getDistance(p2.para["PosY"], p2.para["PosX"],p3.para["PosY"], p3.para["PosX"])
    distance=d1+d2+d3
    
    # all based on hour(h) unit 
    return distance*heli.para["OilUseSpeed"]/heli.para["Speed"]

def taskNameForMission(m):
    # find out the mission's task Name 
    taskName=None
    for key in m.residue.keys():
        if m.residue[key]!=0:
            taskName=key
            return taskName
    return None
    
    
def getRouteOrder(m,c,cityList):
    # According to the mission sort, judge the route order like "heli to m(city Class), to c"
    
    taskName=taskNameForMission(m)
        
    mc=["ToTransZaiMin", "ToTransShangYuan"]
    cm=["WuZiNeed", "JiuYuanMemberNeed", "SheBeiNeed", "FireNum"]
    if taskName in mc:
        return (missionToCity(m,cityList),c)
    elif taskName in cm:
        return (c,missionToCity(m,cityList))
    else:
        return (missionToCity(m,cityList),)

def findBase(cityList):
     baseList=[]
     for c in cityList:
          if c.para["hasGas"]==True:
               baseList.append(c)
     return baseList
    
def calLoadForScout(heli,m,cityList):
    # print(len(cityList))
    c=missionToCity(m, cityList)
    baseList=findBase(cityList)
    nearBase=findTheNearestCity(c.para["PosY"], c.para["PosX"], baseList)
    oilForRoute=calRouteOilForScout(heli, c, nearBase)
    # print("oilForRoute=",oilForRoute," kg")
    
    oilForScoute=heli.oil-oilForRoute
    # print("oilForScoute=",oilForScoute," kg")
    scouteTime=oilForScoute/heli.para["OilUseSpeed"]*3600  #second unit
    # print("scouteTime=",scouteTime," s")
    return min(scouteTime/heli.para["YG_Speed"],m.para["ZCArea"]) # square kilo meter
    
def checkScouteStatus(m,cityList,missionList):
    c=missionToCity(m, cityList)  
    for mm in missionList:
        if mm.para["From"]==c.para["Id"]:
            if mm.para["ZCArea"]!=0:
                return False
    return True

def prospectTaskLoad(heli,m,cityList,missionList):
    # if the heli can do the mission, the function will return the taskload which != 0 
    
    missionNeed=["JiuYuanMemberNeed",  "ToTransZaiMin", "ToTransShangYuan"]
    taskCapa=[   "MaxHuman",           "MaxHuman",     "YH_Space"]
    
    # "WG_bool","SheBeiNeed",
    taskName=taskNameForMission(m)
    if taskName==None:
        return None,None,0
    else:
        if taskName in missionNeed:
            if heli.para[taskCapa[missionNeed.index(taskName)]] > 0:
                # print("prospectTaskLoad：  ",taskName,taskCapa[missionNeed.index(taskName)],heli.para[taskCapa[missionNeed.index(taskName)]],m.residue[taskName])
                return taskName,taskCapa[missionNeed.index(taskName)],min(heli.para[taskCapa[missionNeed.index(taskName)]],m.residue[taskName])
            else:
                return taskName,taskCapa[missionNeed.index(taskName)],0
            
        elif taskName ==  "FireNum" :
            # need to check whether the missionCity has been scouted
            if checkScouteStatus(m,cityList,missionList)==False:
                return taskName,"XF_Content",0
            else:
                # print("prospectTaskLoad：  ",taskName,"XF_Content",m.para["FireNum"],heli.para["XF_Content"])
                return taskName,"XF_Content",min(m.para["FireNum"],heli.para["XF_Content"])
        elif (taskName=="SheBeiNeed"):
            # get the max equipment that heli can swing
            if heli.para["WG_bool"]==2:#这里是后期要修改的bug，S76是不能够吊运设备的，这里需要加入设备重量信息判断
                # print("prospectTaskLoad：  ",taskName,"WG_bool",1)
                return taskName,"WG_bool",1
            else:
                return taskName,"WG_bool",0
        elif(taskName=="ZCArea"):
            if heli.para["YG_Speed"]==0:
                return taskName,"YG_Speed",0
            else:
                # print("prospectTaskLoad：  ",taskName,"YG_Speed",calLoadForScout(heli, m, cityList))
                return taskName,"YG_Speed",calLoadForScout(heli, m, cityList)
        
        elif(taskName=="WuZiNeed"):
            # the only task name remained is "external load" which mean "WX_max" 
            if heli.para["Name"]=="BZK_005":
                return None,None,0
            else: 
                # print("prospectTaskLoad：  ",taskName,"MaxWuZi",heli.para["MaxWuZi"],m.residue[taskName])
                return taskName,"MaxWuZi",(min(heli.para["MaxWuZi"],m.residue[taskName]))


def calTaskTime(heli,taskCapa,taskload):
    # give the tasktime by heli's task model! ! !
     # calculate the working time for each class of task, based on the taskload and class, and the heli.performance 
     tasktime1=0
     tasktime2=0 #the unit is second(s)
     
     if taskCapa=="MaxWuZi":
          tasktime1,tasktime2=taskload*heli.para["WuZiTime"],taskload*heli.para["WuZiTime"]
     if taskCapa=="MaxHuman":
         tasktime1,tasktime2=taskload*heli.para["HumanTime"],taskload*heli.para["HumanTime"]
     if taskCapa=="YG_Speed":
         tasktime1,tasktime2=taskload*heli.para["YG_Speed"],0
     if taskCapa=="WG_bool":
         tasktime1,tasktime2=taskload*(heli.para["WG_Time"]),taskload*(heli.para["WG_DownTime"])
     if taskCapa=="YH_Space":
         tasktime1,tasktime2=taskload*(heli.para["YH_DJTime"]),taskload*(heli.para["YH_JJTime"])
     if taskCapa=="XF_Content":
         tasktime1,tasktime2=taskload*(heli.para["XF_WaterTimeD"]),taskload*(heli.para["XF_WaterTime"])
         
     return tasktime1,tasktime2
 
def checklanding(heli,t1,t2,c):
    #check whether can or cannot if the heli land c at t, base on the classification of the heli
    if heli.para["IsHeli"]==True:
        return c.checkHeliNum(t1,t2,heli.para["HeliArea"])
    else:
        return c.checkTrackNum(t1,t2,heli.para["TrackArea"])
    
def getRouteTimeList(heli,tasktime1,tasktime2,route,nearestBase,t0=0,t1=0,t2=0,t3=0,t4=0,t5=0,t6=0):
    if len(route)==2:
        t0=t0+heli.t
        t1+=t0+(st.getDistance(heli.lat, heli.lon, route[0].para["PosY"], route[0].para["PosX"])/heli.para["Speed"]*3600)
        t2+=t1+tasktime1
        t3+=t2+(st.getDistance(route[0].para["PosY"], route[0].para["PosX"], route[1].para["PosY"], route[1].para["PosX"])/heli.para["Speed"]*3600)
        t4+=t3+tasktime2
        t5+=t4+(st.getDistance(route[1].para["PosY"], route[1].para["PosX"], nearestBase.para["PosY"], nearestBase.para["PosX"])/heli.para["Speed"]*3600)
        t6+=t5+config.refuelTimeInBase
        return [t0,t1,t2,t3,t4,t5,t6]
    else:
        t0+=heli.t
        t1+=t0+(st.getDistance(heli.lat, heli.lon, route[0].para["PosY"], route[0].para["PosX"])/heli.para["Speed"]*3600)
        t2+=t1+tasktime1
        t3+=t2+(st.getDistance(route[0].para["PosY"], route[0].para["PosX"], nearestBase.para["PosY"], nearestBase.para["PosX"])/heli.para["Speed"]*3600)
        t4+=t3+config.refuelTimeInBase
        return [t0,t1,t2,t3,t4]
    
def verifyTheHeliCapa(heli,cityList,missionList):
    for m in missionList:
        _1,_2,taskload=prospectTaskLoad(heli,m,cityList,missionList)
        if taskload>0:   
            return True
    return False

def findMiserHeliBase(heli,baseList2):
    # print("look for a back base.........")
    baseList=copy.deepcopy(baseList2)
    while(True):
        if len(baseList)==0:
            break
        rb=random.randint(1,len(baseList))
        b=baseList.pop(rb-1)
        dt=st.getDistance(heli.lat,heli.lon,b.para["PosY"],b.para["PosX"])/heli.para["Speed"]
        oilNeed=dt*heli.para["OilUseSpeed"]
         # print('back to ',b.para["Name"],'oilNeed:',oilNeed)
        if oilNeed<heli.oil:
            if checklanding(heli,heli.t,heli.t+dt,b)==True:
               # return the true origin base object
                for base in baseList2:
                    if base.para['Name']==b.para["Name"]:
                        # print("find a base to return")
                        return base
    # print("can't find a base")
    return None
            
def missionEnforceInspect(heli,m,c,cityList,missionList,heliList):
    # print("-------------missionEnforceInspect-----------\n")
     # if the heli can do the job, then return a list that contain the progress's infomation; if not return the null set
    processInfo=[]
    
# =============================================================================
## inspect the distance oil , add the taskTime below
# =============================================================================
    oilNeed=0
# inspect the oil  :  oil doing task
    taskName,taskCapa,taskload=prospectTaskLoad(heli,m,cityList,missionList)
    print(heli.name,"taskName",taskName,", taskload = ",taskload)
# check whether the heli can do the job
    if(taskload==0):
        return processInfo
    tasktime1,tasktime2=calTaskTime(heli, taskCapa, taskload) # 1 for upload, 2 for download
    tasktime=tasktime1+tasktime2
    oilNeed+=tasktime*heli.para["OilUseSpeed"]/3600
    # print("tasktime",tasktime,"oilNeed = ",oilNeed)

# inspect the oil  :  oil on the road
# check distance
    route=getRouteOrder(m,c,cityList) #these are two cities
    # print(route)
    nearestBase=findTheNearestCity(route[-1].para["PosY"], route[-1].para["PosX"], findBase(cityList))
    if len(route)==2:         
        oilNeed+=calRouteOil(heli, route[0], route[1], nearestBase)
    if len(route)==1:         
        oilNeed+=calRouteOilForScout(heli,route[0],nearestBase)
    
    if len(route)==2:
        print("route: ",route[0].para["Name"],route[1].para["Name"])
        # print("In this route I need ",oilNeed,'and I have ',heli.oil)
    else:
        print("route: ",route[0].para["Name"])
        # print("In this route I need ",oilNeed,'and I have ',heli.oil)
    if heli.oil<oilNeed:
        print("oil not enough")
        if verifyTheHeliCapa(heli,cityList,missionList)==True:
                base=findMiserHeliBase(heli,findBase(cityList))
                if base!=None:
                     # To check whether the heli fly around some bases and don't do anything
                    if heli.checkPositionForBackBase(base,findBase(cityList))==False:
                         heli.modifyLog()
                         Heli.writeHeliLog(heli,commander.config.logOutputPath)
                         heliList.remove(heli)
                         return processInfo
                    heli.backToBase(base)  
        return processInfo
    oilNeed-=st.getDistance(route[-1].para["PosY"], route[-1].para["PosX"],nearestBase.para["PosY"],nearestBase.para["PosX"])/heli.para["Speed"]*heli.para["OilUseSpeed"]
# =============================================================================
# # inspect the landing condition
# =============================================================================
    # =============================================================================
    #         checkLandC1,checkLandC2,checkLandC3=False,False,False
    #         wt1,wt3,wt5=0,0,0
    #           特别想解决这个直升机悬停的问题，不然真是一点都不智能。
    # =============================================================================
    routeTimeList=[]
    if taskName in ["WuZiNeed", "JiuYuanMemberNeed", "ToTransZaiMin", "ToTransShangYuan"]:
        if len(route)==2:
            routeTimeList=getRouteTimeList(heli,tasktime1,tasktime2,route,nearestBase)
            # t1 go to the c1; t2 done the task in c1 ; t3 go to the c2 ; t4 done the task in c2 ; t5 get the nearbase ; t6 done the refuel
            if checklanding(heli,routeTimeList[1],routeTimeList[2],route[0])==False:
                print("can not land in "+route[0].para["Name"])
                return processInfo
            if checklanding(heli,routeTimeList[3],routeTimeList[4],route[1])==False:
                print("can not land in "+route[1].para["Name"])
                return processInfo
            if checklanding(heli,routeTimeList[5],routeTimeList[6],nearestBase)==False:
                print("can not land in "+nearestBase.para["Name"])
                return processInfo
            
        else:
            routeTimeList=getRouteTimeList(heli,tasktime1,tasktime2,route,nearestBase)
            if checklanding(heli,routeTimeList[1],routeTimeList[2],route[0])==False:
                print("can not land in "+route[0].para["Name"])
                return processInfo
            if checklanding(heli,routeTimeList[3],routeTimeList[4],nearestBase)==False:
                print("can not land in "+nearestBase.para["Name"])
                return processInfo
    else:
        if len(route)==2:
        # in these situation, the heli do "scout", "fire extinguishment", "swing equipment" 
            routeTimeList=getRouteTimeList(heli,tasktime1,tasktime2,route,nearestBase)
            # t1 go to the c1; t2 done the task in c1 ; t3 go to the c2 ; t4 done the task in c2 ; t5 get the nearbase ; t6 done the refuel
            if checklanding(heli,routeTimeList[5],routeTimeList[6],nearestBase)==False:
                print("can not land in "+nearestBase.para["Name"])
                return processInfo
            
        else:
            routeTimeList=getRouteTimeList(heli,tasktime1,tasktime2,route,nearestBase)
            if checklanding(heli,routeTimeList[3],routeTimeList[4],nearestBase)==False:
                print("can not land in "+nearestBase.para["Name"])
                return processInfo
# =============================================================================
#     congratulate ! The ** heli finaly can do the ** job
#           give the processInfo to the list
# =============================================================================
# log.append(['返回基地', base.para["Name"],self.t])
# informBase(self,t1,t2,base):  [[t1,t2,route[0]],[t1,t2,route[1]]]
    if len(route)==2:
        if taskName in ["WuZiNeed", "JiuYuanMemberNeed", "ToTransZaiMin", "ToTransShangYuan"]:
            processInfo=[route,taskName,taskCapa,taskload,oilNeed,[[routeTimeList[1],routeTimeList[2],route[0]],[routeTimeList[3],routeTimeList[4],route[1]]],[["前往",route[0].para['Name'],'',routeTimeList[1]],[taskName,route[0].para['Name'],taskload,routeTimeList[2]],["前往",route[1].para['Name'],'',routeTimeList[3]],[taskName,route[1].para['Name'],taskload,routeTimeList[4]]]]
        else:
            processInfo=[route,taskName,taskCapa,taskload,oilNeed,[],[["前往",route[0].para['Name'],'',routeTimeList[1]],[taskName,route[0].para['Name'],taskload,routeTimeList[2]],["前往",route[1].para['Name'],'',routeTimeList[3]],[taskName,route[1].para['Name'],taskload,routeTimeList[4]]]]
    else:
        processInfo=[route,taskName,taskCapa,taskload,oilNeed,[],[["前往",route[0].para['Name'],'',routeTimeList[1]],[taskName,route[0].para['Name'],taskload,routeTimeList[2]]]]
    
    return processInfo

def findCapaCity(needName,cityList):
    clist=[]
    for c in cityList:
        if type(c.para[needName])!=bool:
            if c.para[needName]>0:
                clist.append(c)
        if type(c.para[needName])==bool:
            if c.para[needName]==True:
                clist.append(c)
    return clist
                
def theCityWhoCatchMission(m,cityList):
    taskName=taskNameForMission(m)
    if taskName == "WuZiNeed":
        return findCapaCity("WuZiNum", cityList)
        
    if taskName == "JiuYuanMemberNeed":
        return findCapaCity("JiuYuanNum", cityList)
        
    if taskName == "SheBeiNeed":
        return findCapaCity("SheBeiNum", cityList)
        
    if taskName == "ToTransZaiMin":
        return findCapaCity("canZM", cityList)
        
    if taskName == "ToTransShangYuan":
        return findCapaCity("canYH", cityList)
        
    if taskName == "FireNum":
        return findCapaCity("hasWater", cityList)
        
    if taskName == "ZCArea":
        return findCapaCity("FireNum", cityList)
    
def update(heli,c,m,processInfo):
    # print("-------------update-----------\n")
    route,taskName,taskCapa,taskload,oilNeed,heliInform,heliLog=processInfo
    
    # heli's information update
    heli.lon=route[-1].para["PosX"]
    heli.lat=route[-1].para["PosY"]
    heli.oil-=oilNeed
    heli.t=heliLog[-1][-1]
    if len(heliInform)!=0:
        for inform in  heliInform:
            t1, t2, base=inform
            heli.informBase(t1, t2, base)
    
    for l in heliLog:
        heli.log.append(l)
    
    # mission's information update
    m.residue[taskName]-=taskload
    m.log.append([heli.name,taskload,heli.t,taskName])
        
def fm(m,missionList):
    for i in range(len(missionList)):
        if taskNameForMission(m)==taskNameForMission(missionList[i]):
            return missionList[i]
def fc(c,cityList):
    for i in range(len(cityList)):
        if c.para["Name"]==cityList[i].para["Name"]:
            return cityList[i]
        
def assignWork(heli,cityList,missionList,heliList):
    # print("----------------------------------------assignWork--------------------------------------------------\n")
    # print('missionList',len(missionList))
    # print("cityList",len(cityList))
    ml=copy.deepcopy(missionList)
    find=False
    
    while(find!=True):
        if len(ml)==0:
            break
        rm=random.randint(1, len(ml))
        m=ml.pop(rm-1)
        
        cl2=theCityWhoCatchMission(m,cityList)
        cl=copy.deepcopy(cl2)
        while(True):
            if cl==None:
                break
            if len(cl)==0:
                break
            rc=random.randint(1, len(cl))
            c=cl.pop(rc-1)
            if heli in heliList:
                 processInfo=missionEnforceInspect(heli,fm(m,missionList),fc(c,cityList),cityList,missionList,heliList)
            
            if(len(processInfo)!=0):
                find=True
                #  在这个 bug卡了很久，一开始是因为 深浅拷贝，所以删除了我的元素；后来是因为深拷贝，所以不会改变原来的数据
                city=fc(c,cityList)
                mission=fm(m,missionList)
                update(heli,city,mission,processInfo)
                return 1
# =============================================================================
#     if len(heli.log)>0:
#         if heli.log[-1][0]=="基地保障":
#             heliList.remove(heli)
#             return None
# =============================================================================
    if heli in heliList:
         if verifyTheHeliCapa(heli,cityList,missionList)==True:
             base=findMiserHeliBase(heli,findBase(cityList))
             if base!=None:
                   # To check whether the heli fly around some bases and don't do anything
                 if heli.checkPositionForBackBase(base,findBase(cityList))==False:
                    heli.modifyLog()
                    Heli.writeHeliLog(heli,commander.config.logOutputPath)
                    heliList.remove(heli)
                    return None
                 heli.backToBase(base)
         else:
             heli.modifyLog()
             Heli.writeHeliLog(heli,commander.config.logOutputPath)
             heliList.remove(heli)
             return None
    else:
        return None
            # never back to base how poor you are
        # no value at all. how pathetic you
def parkHeli(h,b):
    if h.para["IsHeli"]==True:
        if b.heliNum-h.para["HeliArea"]>0:
            b.heliNum-=h.para["HeliArea"]
            h.lon=b.para["PosX"]
            h.lat=b.para["PosY"]
            return True
    if h.para["IsHeli"]==False:
        if b.trackNum-h.para["TrackArea"]>0:
            b.trackNum-=h.para["TrackArea"]
            h.lon=b.para["PosX"]
            h.lat=b.para["PosY"]
            return True
    return False
        
def fleetInitialize(heliNameList):
    with open(commander.config.logOutputPath,"w") as hlog:
         json.dump([],hlog)
         hlog.close()
    with open(commander.config.missionLogPath,"w") as mlog:
         json.dump([],mlog)
         mlog.close()
    cityList=City.getCityList()
    missionList=Mission.getMissionList()
    
    heliList=[]
    for i in range(len(heliNameList)):
        heli=Heli.addHeli(heliNameList[i])
        heli.name=str(i+1)+'-'+heli.para["Name"]
        heliList.append(heli)
    return [cityList,missionList,heliList]

def fleetDeploy(heliList,cityList):
    deployPlan=[]
    baseList=findBase(cityList)
    for h in heliList:
        i=1
        
        while (i<20):
            b=random.choice(baseList)
            a=parkHeli(h, b)
            if a==True:
                deployPlan.append(h.name+' : '+b.para["Name"])
                break
            i+=1
            if i==19:
                return []
    return deployPlan

def checkAllMissionResidue(missionList,heliList):
    residue=False
    ml=[]
    for m in missionList:
        if m.residueCheck()!=None:
            residue=True
        else:
            ml.append(m)
    for m in ml:
        Mission.writeMissionLog(m)
        missionList.remove(m)
    if residue==False:
         for h in heliList:
              Heli.writeHeliLog(h,commander.config.logOutputPath)
    return residue

def getMyFleet():
    with open("../data/fleet1/fleet.txt") as f:
        heliNameList=f.readlines()
        f.close()
    for i in range(len(heliNameList)):
        heliNameList[i]=heliNameList[i][:-1]
    return(heliNameList)

if __name__ =="__main__":
    # cityList=City.getCityList()
    # heli=Heli.addHeli("M-26")
    # missionList=Mission.getMissionList()
# =============================================================================
#     processInfo=missionEnforceInspect(heli,missionList[4],cityList[2],cityList,missionList)
#     if(len(processInfo)!=0):
#         route,taskName,taskCapa,taskload,oilNeed,heliInform,heliLog=processInfo
#         print(route,"\n",taskName,"\n",taskCapa,"\n",taskload,"\n",oilNeed,"\n",heliLog)
# =============================================================================
    
    # print("-----------------------------------------------\n\n")
    # print(assignWork(heli, cityList, missionList))
    # print(missionToCity(ml[0], cityList).para)
    # print(prospectTaskLoad(heli,ml[2]))
    # assignWork(heli,cityList,missionList)
    # (a,b)=getRouteOrder(ml[5], cityList[1])
    # print(a.para,"\n",b.para)
# print(findAvailbleLandingCity(heli, cityList))
# print(calRouteDistance(heli, cityList[1], cityList[1]))
    # pass
    heliNameList=getMyFleet()
    cityList,missionList,heliList=fleetInitialize(heliNameList)
    deployPlan=fleetDeploy(heliList,cityList)
    # for m in missionList:
    #      print(taskNameForMission(m))
    # print(prospectTaskLoad(heliList[0], missionList[-1], cityList, missionList))
    # heliList[0].log.append([0,1,2,3])
    # Heli.writeHeliLog(heliList[0])