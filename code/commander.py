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
# import Heli
# import City
# import Mission
import technician as th

def getMyFleet():
    with open("../data/fleet1/fleet.txt") as f:
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
    while(th.checkAllMissionResidue(missionList)):
        heli=th.findTheWaitHeli(heliList)
        th.assignWork(heli, cityList, missionList,heliList)
        i+=1
        if(i>1000):
            break
        # print("done",done)
    with open("../data/fleet1/fleetLog.txt",'w') as f:
        for h in heliList:
            for l in h.log:
                f.write(h.name+':'+' '+str(l[0])+' '+str(l[1])+' '+str(l[2])+'   t='+str(l[3])+'\n')
            f.write('\n\n')
        for m in missionList:
            for item in m.residue.items():
                if item[-1]!=0:
                    f.write(str(item[0])+' '+str(item[1])+'\n')
        f.close()
    for m in missionList:
            for item in m.residue.items():
                if item[-1]!=0:
                    print(str(item[0])+' '+str(item[1])+'\n')    