# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 19:45:39 2021

@author: YU Yixiong
"""

# import openpyxl  
# import math  
# import random  
# # import matplotlib.pyplot as plt 
# import static as st
import Heli
# import City
import Mission
import technician as th
import time

class config():
     getFleetTxtPath="../data/fleet1/fleet.txt"
     logOutputPath="../data/fleet1/fleetLog"+str(time.time())+".txt"

def getMyFleet():
    with open(config.getFleetTxtPath) as f:
        heliNameList=f.readlines()
        f.close()
    for i in range(len(heliNameList)):
        heliNameList[i]=heliNameList[i][:-1]
    return(heliNameList)

if __name__ =="__main__":
    
     heliNameList=getMyFleet()
     cityList,missionList,heliList=th.fleetInitialize(heliNameList)
     deployPlan=th.fleetDeploy(heliList,cityList)
     
     i=0
     while(th.checkAllMissionResidue(missionList,heliList)):
           heli=th.findTheWaitHeli(heliList)
           th.assignWork(heli, cityList, missionList,heliList)
           i+=1
           if(i>50):
               break
          
     
        
     # for m in missionList:
     #       Mission.writeMissionLog(m)
             
     # Mission.writeMissionLog(missionList[0])    
     # time.sleep(2)        
     # Mission.writeMissionLog(missionList[2])            
                  
                  
                  