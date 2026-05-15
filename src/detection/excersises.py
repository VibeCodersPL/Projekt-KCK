import math
from typing import List

class Condition:
    def __init__(self, landmarks: List[int], degree: int, tolerance: int):
        self.landmarks = landmarks # Lista 3 punktów, np. [11, 13, 15]
        self.degree = degree
        self.tolerance = tolerance

class Exercise:
    
    name = None
    stateName = None
    _frontAngleConditions = None
    _sideAngleConditions = None
    
    def __init__(self, name: str):
        self.name = name
        self.stateName = "DEFAULT"
        
        self._frontAngleConditions = [
            Condition([11,13,15],160,0.3),
            Condition([12,14,16],160,0.3),
        ]
    
        self._sideAngleConditions = [
            Condition([11,13,15],160,0.3),
            Condition([12,14,16],160,0.3),
        ]

    def checkExcersise(self, landmarksFront = None, landmarksSide = None) -> bool:
    
        if landmarksFront:
            for cond in self._frontAngleConditions:
                angle = self.__calculateThreePointAngle(landmarksFront[cond.landmarks[0]], landmarksFront[cond.landmarks[1]], landmarksFront[cond.landmarks[2]])
                if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                    return False
                
        if landmarksSide:
            for cond in self._frontAngleConditions:
                angle = self.__calculateThreePointAngle(landmarksSide[cond.landmarks[0]], landmarksSide[cond.landmarks[1]], landmarksSide[cond.landmarks[2]])
                if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                    return False
            
        return True
    
    
    def __calculateThreePointAngle(self,leftP, midP, rightP) -> int:
        '''returns angle in degrees'''
        dis = lambda p1, p2: math.sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2))                
        return int(math.degrees(math.acos((math.pow(dis(midP, leftP), 2) + math.pow(dis(midP, rightP), 2) - math.pow(dis(rightP, leftP), 2)) / (2 * dis(leftP, midP) * dis(rightP, midP)))))

    
    
    
    
class LowReady(Exercise):
        
    states = ["START"]    
    stateIdx = 0
    maxStateIdx = len(states)
    
    def __init__(self):
        super().__init__("LowReady")
        self.state = self.states[0]

    def setState(self, stateName: str | bool = False):
        if(stateName == False or True):
            self.stateIdx = self.stateIdx % self.maxStateIdx
            self.state = self.states[self.stateIdx]
        
        self.state = stateName
        
        if(stateName == "START"):
            self._frontAngleConditions = [
                Condition([11,13,15],160,0.05),
                Condition([12,14,16],160,0.05),
            ]
        
            self._sideAngleConditions = [
                Condition([11,13,15],160,0.05),
                Condition([12,14,16],160,0.05),
            ]
        
        if(stateName == "END"):
            self._frontAngleConditions = [
                Condition([11,13,15],160,0.05),
                Condition([12,14,16],160,0.05),
            ]
        
            self._sideAngleConditions = [
                Condition([11,13,15],160,0.05),
                Condition([12,14,16],160,0.05),
            ]


    
           
           