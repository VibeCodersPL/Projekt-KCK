import math
from typing import List

class Condition:
    def __init__(self, landmarks: List[int], degree: int, tolerance: int):
        self.landmarks = landmarks # Lista 3 punktów, np. [11, 13, 15]
        self.degree = degree
        self.tolerance = tolerance

class Exercise:
    def __init__(self, name: str):
        self.name = name
        
        
    def getFrontAngleConditions(self) -> List[Condition]:
        raise NotImplementedError
    
    def getSideAngleConditions(self) -> List[Condition]:
        raise NotImplementedError
    
    def checkExcersise(self, landmarks, isSide:bool = False) -> bool:
    
        if(isSide):
            conditions = self.getSideAngleConditions();
        else: 
            conditions = self.getFrontAngleConditions()
            
        for cond in conditions:
            angle = self.__calculateThreePointAngle(landmarks[cond.landmarks[0]], landmarks[cond.landmarks[1]], landmarks[cond.landmarks[2]])
            if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                return False
         
        return True
    
    
    def __calculateThreePointAngle(self,leftP, midP, rightP) -> int:
        '''returns angle in degrees'''
        dis = lambda p1, p2: math.sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2))                
        return int(math.degrees(math.acos((math.pow(dis(midP, leftP), 2) + math.pow(dis(midP, rightP), 2) - math.pow(dis(rightP, leftP), 2)) / (2 * dis(leftP, midP) * dis(rightP, midP)))))


    
    
    
class LowReady(Exercise):
    
    
    
    def __init__(self):
        super().__init__("LowReady")
        
        self.__frontAngleConditions = [
            Condition([11,13,15],160,0.05),
            Condition([12,14,16],160,0.05),
        ]
    
        self.__sideAngleConditions = [
            Condition([11,13,15],160,0.05),
            Condition([12,14,16],160,0.05),
        ]
        
        
        
        
    def getFrontAngleConditions(self):
        return self.__frontAngleConditions
        
    def getSideAngleConditions(self):
        return self.__sideAngleConditions
    
    def setState(self, stateName):
        self.state = stateName