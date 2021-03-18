# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 11:19:15 2021

@author: YU Yixiong
"""

import json
import Mission
import Heli
import matplotlib.pyplot as plt
import commander
import technician as th

missionSubPlot=330

def getLog(pathheliLog,pathMissionLog):
    with open(pathheliLog,"r") as f:
        heliLog=json.load(f)
        f.close()
    with open(pathMissionLog,"r") as f:
        mLog=json.load(f)
        f.close()
    
    return heliLog,mLog

def draw(a,x):#a是要画的列表，x是在图中的横坐标
    for i in range(len(a)):
         plt.bar(x,a[-i-1], bottom=0,width=0.5)

def flowChart(dic):
     plt.figure(figsize=(10,8),dpi=300)
     plt.rcParams['font.sans-serif'] = 'SimHei'#黑体
     plt.rcParams['axes.unicode_minus'] = False
     plt.title('各飞机流程图')
     
     for key in dic.keys():
          draw(dic[key],key)
          
     plt.grid(True)
     plt.xticks(rotation=60, horizontalalignment="center")
     plt.xlabel('飞机名称')
     plt.ylabel('time/s')
     plt.savefig('..\\data\\fleet1\\各飞机流程图.jpg')

def handleHeliLog(heliLog):
    dic={}
    for i in range(len(heliLog)):
        if heliLog[i][0] in dic.keys():
               dic[heliLog[i][0]].append(heliLog[i][-1])
        else:
               dic[heliLog[i][0]]=[heliLog[i][-1]]
    return dic

def handleHeliLogFullEdition(heliLog):
    dic={}
    for i in range(len(heliLog)):
        if heliLog[i][0] in dic.keys():
               dic[heliLog[i][0]].append(heliLog[i])
        else:
               dic[heliLog[i][0]]=[heliLog[i]]
    return dic

def drawHeliFlowChart(heliLog):
    heliLog=sorted(heliLog,key=(lambda x:[x[-1]]),reverse=False)
    dic=handleHeliLog(heliLog)
    flowChart(dic)
    # return dic

def fibonacci(l):
    for i in range(1,len(l)):
        l[i]+=l[i-1]
    return l
            
def handleMissionLog(MissionLog):
    dicTime={}
    for i in range(len(MissionLog)):
        if MissionLog[i][0] in dicTime.keys():
               dicTime[MissionLog[i][0]].append(MissionLog[i][3])
        else:
               dicTime[MissionLog[i][0]]=[0]
               dicTime[MissionLog[i][0]].append(MissionLog[i][3])
    
    dicTask={}
    for i in range(len(MissionLog)):
        if MissionLog[i][0] in dicTask.keys():
               dicTask[MissionLog[i][0]].append(MissionLog[i][2])
        else:
               dicTask[MissionLog[i][0]]=[0]
               dicTask[MissionLog[i][0]].append(MissionLog[i][2])
    return dicTime,dicTask
               
def drowMissionFlowChart(MissionLog):
    plt.figure(figsize=(10,8),dpi=300)
    plt.rcParams['font.sans-serif'] = 'SimHei'#黑体
    plt.rcParams['axes.unicode_minus'] = False
    # plt.title('任务执行进度图')
    plt.figure(1)
    
    MissionLog=sorted(MissionLog,key=(lambda x:[x[0],x[3]]),reverse=False)
    dicTime,dicTask=handleMissionLog(MissionLog)
    
    for key in dicTask.keys():
        dicTask[key]=fibonacci(dicTask[key])
        plt.subplot(missionSubPlot+key)
        plt.plot(dicTime[key], dicTask[key])
    plt.savefig('..\\data\\fleet1\\任务执行进度图.jpg')
    # return MissionLog


def calTimeScore(missionLog,missionList):
    dicTime,dicTask=handleMissionLog(missionLog)
    mTimeList=[]
    scoreList=[]
    for i in range(1,len(missionList)+1):
        for m in missionList:
            if m.seri==i:
                mTime=max(dicTime[i])
                mTimeList.append(mTime)
                scoreList.append(mTime*m.para["MissionHard"]/60)
    sumScore=sum(scoreList)
    return mTimeList,scoreList,sumScore

def calCost(heliLog,heliList):
    heliFlyTimedic={}
    heliRefuelTimedic={}
    heliLogDic=handleHeliLogFullEdition(heliLog)
    for key in heliLogDic.keys():
        refuelTime=0
        tl=[]
        for log in heliLogDic[key]:
            tl.append(log[-1])
            if log[1]=="基地保障":
                refuelTime+=0.33
        heliRefuelTimedic[key]=refuelTime
        heliFlyTimedic[key]=max(tl)/3600-refuelTime
    return heliRefuelTimedic,heliFlyTimedic
    

 
if __name__ =="__main__":
    el,ml=getLog("D:/labWork/CompetitionSystem/data/fleet1/HeliLog.json", "D:/labWork/CompetitionSystem/data/fleet1/MissionLog.json")
    drawHeliFlowChart(el)
    drowMissionFlowChart(ml)
    a,b,sumScore=calTimeScore(ml,Mission.getMissionList())
    
    # heliNameList=commander.getMyFleet()
    # cityList,missionList,heliList=th.fleetInitialize(heliNameList)
    # deployPlan=th.fleetDeploy(heliList,cityList)
    
    # heliRefuelTimedic,heliFlyTimedic=calCost(el,heliList)
    
