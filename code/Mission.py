# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 16:35:31 2021

@author: YU Yixiong
"""

import openpyxl
import commander

class Mission:
    def __init__(self,para,residue):
        self.para=para
        self.residue=residue
    t=0
        
    def residueCheck(self):
        '''
        return the need of mission name

        '''
        for key in self.residue.keys():
            if self.residue[key]>0:
                return key
        return None                
            
def getMissionList():
    wb=openpyxl.load_workbook("../data/SystemParameter.xlsx")
    sheet=wb['任务']
    missionList=[]
    
    for i in range(3,12):
        m=Mission({},{})
        for j in range(1,sheet.max_column+1):    
            m.para[sheet.cell(1,j).value]=sheet.cell(i,j).value
            if(1<j and j<9):
                m.residue[sheet.cell(1,j).value]=sheet.cell(i,j).value
            
        missionList.append(m)
        
    return missionList

def writeMissionLog(m):
     with open(commander.config.logOutputPath,'a+') as f:
          for item in m.residue.items():
              if item[-1]!=0:
                  f.write(str(item[0])+' '+str(item[1])+'\n')
          f.close()
          
if __name__ =="__main__":
    # p=getMissionList()
    pass