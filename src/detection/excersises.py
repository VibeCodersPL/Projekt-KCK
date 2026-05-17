import math
from typing import List
from time import time


class Condition:
    def __init__(self, landmarks: List[int] = [11,13,15], degree: int = 160, tolerance: int = 0.3):
        self.landmarks = landmarks # Lista 3 punktów, np. [11, 13, 15]
        self.degree = degree
        self.tolerance = tolerance    


class State:
    def __init__(self, conditionFront:List[Condition] = [Condition()], conditionSide:List[Condition] = [Condition()], messege:str = "DEFAULT"):
        self.conditonFront = conditionFront
        self.conditonSide = conditionSide
        self.messege = messege
        self.startTime = 0
        self.durationStats = []
        
    def start(self):
        self.startTime = time()
        
    def stop(self):
        timeOfStart = self.startTime        
        self.startTime = 0
        duration = time() - timeOfStart
        self.durationStats.append(duration) 
        return duration
    
class Exercise:
    __FRAMES_PER_SECOND = 30
    __CORRECT_FRAMES = math.ceil(__FRAMES_PER_SECOND / 4)

    def __init__(self, name: str):
        self._excersiseName = name
        self.__frameCounter = 0
        self.__lastFramesCorrectnessArray: list[int] = [0] * self.__CORRECT_FRAMES
        self._currentStateName = "DEFAULT"
        self._states: dict[str, State] = {}
        self._statesNames = ["DEFAULT"]
        self._stateIdx = 0
        self._timeOfStateStart = time()
        self._states["DEFAULT"] = State()
        self._maxStateIdx = len(self._states)
        
        

    def checkExcersise(self, landmarksFront = None, landmarksSide = None) -> bool:
    
        state:State = self.__getState()
        
        if landmarksFront:
            for cond in state.conditonFront:
                angle = self.__calculateThreePointAngle(landmarksFront[cond.landmarks[0]], landmarksFront[cond.landmarks[1]], landmarksFront[cond.landmarks[2]])
                if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                    self.__setLastFrameValue(0)
                    return False
        
                
        if landmarksSide:
            for cond in state.conditonSide:
                angle = self.__calculateThreePointAngle(landmarksSide[cond.landmarks[0]], landmarksSide[cond.landmarks[1]], landmarksSide[cond.landmarks[2]])
                if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                    self.__setLastFrameValue(0)
                    return False
        
        self.__setLastFrameValue(1)
                             
        return True, self.__isCompletedState()

    def __isCompletedState(self):
        if sum(self.__lastFramesCorrectnessArray) / len(self.__lastFramesCorrectnessArray) == 1:
            self.__lastFramesCorrectnessArray = [0] * self.__CORRECT_FRAMES
            return True
        return False

    def __setLastFrameValue(self, value:int):
        self.__lastFramesCorrectnessArray[self.__frameCounter] = value
        self.__frameCounter = (self.__frameCounter + 1) % self.__CORRECT_FRAMES
    
    def __getState(self) -> State:
        return self._states.get(self._currentStateName)
        
    def __calculateThreePointAngle(self,leftP, midP, rightP) -> int:
        '''returns angle in degrees'''
        dis = lambda p1, p2: math.sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2))                
        return int(math.degrees(math.acos((math.pow(dis(midP, leftP), 2) + math.pow(dis(midP, rightP), 2) - math.pow(dis(rightP, leftP), 2)) / (2 * dis(leftP, midP) * dis(rightP, midP)))))

    
    def setState(self, stateName: str | None = None):
        
        print(self._statesNames)
        print(self._stateIdx, self._maxStateIdx)
        
        if stateName == self._currentStateName:
            return self._currentStateName
        
        stateDuration = self._states[self._currentStateName].stop()

        if stateName is None:
            self._stateIdx = (self._stateIdx + 1) % self._maxStateIdx
            self._currentStateName = self._statesNames[self._stateIdx]
        else:
            if stateName in self._statesNames:
                self._stateIdx = self._statesNames.index(stateName)
                self._currentStateName = stateName
            else:
                raise ValueError(f"Stan {stateName} nie istnieje!")
        
        return self._currentStateName, (stateDuration - self.__CORRECT_FRAMES/self.__FRAMES_PER_SECOND)
    
    def getStateMessage(self):
        return ((self._states.get(self._currentStateName)).messege)
    
    def getEndStats(self):
        for key, state in self._states.items():
            print(key, state.durationStats)
    
class LowReady(Exercise):
    def __init__(self):
        super().__init__("LowReady")
        
        self._statesNames.append("START")
        self._statesNames.append("END")
        
        self._states["START"] = State(messege = "START")
        self._states["END"] = State(messege = "END")
        
        self._maxStateIdx = len(self._statesNames)
        
            
        


    
           
           