import math
from typing import List

class Condition:
    def __init__(self, landmarks: List[int], degree: int, tolerance: int):
        self.landmarks = landmarks # Lista 3 punktów, np. [11, 13, 15]
        self.degree = degree
        self.tolerance = tolerance    

class Exercise:
    
    __MAX_FRAMES = 60
    __frameCounter = 0 
    __lastFramesCorrectnessArray: list[int] = [0] * 60    
    _excersiseName = None    
    
    
    
    _currentStateName = None
    _states: dict[str, tuple[list[Condition], list[Condition], str]] | None = None    
    _statesNames = ["DEFAULT"]    
    _stateIdx = 0
    _maxStateIdx = 0
    
        
    def __init__(self, name: str):
        self._excersiseName = name
        self._currentStateName = "DEFAULT"
        self._states = {}
        self._states["DEFAULT"] = ([
            Condition([11,13,15],160,0.3),
            Condition([12,14,16],160,0.3)
        ],
        [
            Condition([11,13,15],160,0.3),
            Condition([12,14,16],160,0.3)
        ], "START")
        
        

    def checkExcersise(self, landmarksFront = None, landmarksSide = None) -> bool:
    
        conditions = self.getConditions()
    
        if landmarksFront:
            for cond in conditions[0]:
                angle = self.__calculateThreePointAngle(landmarksFront[cond.landmarks[0]], landmarksFront[cond.landmarks[1]], landmarksFront[cond.landmarks[2]])
                if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                    self.__lastFramesCorrectnessArray[self.__frameCounter] = 0
                    self.__frameCounter = (self.__frameCounter + 1) % self.__MAX_FRAMES
                    return False
                
        if landmarksSide:
            for cond in conditions[1]:
                angle = self.__calculateThreePointAngle(landmarksSide[cond.landmarks[0]], landmarksSide[cond.landmarks[1]], landmarksSide[cond.landmarks[2]])
                if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                    self.__lastFramesCorrectnessArray[self.__frameCounter] = 0
                    self.__frameCounter = (self.__frameCounter + 1) % self.__MAX_FRAMES
                    return False
        
        self.__lastFramesCorrectnessArray[self.__frameCounter] = 1
        self.__frameCounter = (self.__frameCounter + 1) % self.__MAX_FRAMES
                
        if sum(self.__lastFramesCorrectnessArray) / len(self.__lastFramesCorrectnessArray)>= 0.6:
            self.setState()
            self.__lastFramesCorrectnessArray = [0] * 60
             
        return True
    
    def getConditions(self):
        return self._states.get(self._currentStateName)
        
    def __calculateThreePointAngle(self,leftP, midP, rightP) -> int:
        '''returns angle in degrees'''
        dis = lambda p1, p2: math.sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2))                
        return int(math.degrees(math.acos((math.pow(dis(midP, leftP), 2) + math.pow(dis(midP, rightP), 2) - math.pow(dis(rightP, leftP), 2)) / (2 * dis(leftP, midP) * dis(rightP, midP)))))

    
    def setState(self, stateName: str | None = None):
        
        if(stateName == None):
            self._stateIdx = (self._stateIdx + 1) % self._maxStateIdx
            self._currentStateName = self._statesNames[self._stateIdx]
        else:
            self._currentStateName = stateName

        return self._currentStateName
    
    def getMessage(self):
        return (self._states.get(self._currentStateName))[2]
    
    
class LowReady(Exercise):
    def __init__(self):
        super().__init__("LowReady")
        
        self._statesNames.append("START")
        self._statesNames.append("END")
        
        self._states["START"] = ([
            Condition([11,13,15],160,0.3),
            Condition([12,14,16],160,0.3)
        ],
        [
            Condition([11,13,15],160,0.3),
            Condition([12,14,16],160,0.3)
        ], "Rozpocznij ćwiczenie")
        
        self._states["END"] = ([
            Condition([11,13,15],160,0.3),
            Condition([12,14,16],160,0.3)
        ],
        [
            Condition([11,13,15],160,0.3),
            Condition([12,14,16],160,0.3)
        ], "Zakończ ćwiczenie")
        
        self._maxStateIdx = len(self._statesNames)
        
            
        


    
           
           