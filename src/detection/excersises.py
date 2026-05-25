import math
from typing import List
from time import time


class Condition:
    def __init__(self, landmarks: List[int] = [11,13,15], degree: int = 160, tolerance: int = 0.3):
        """Representation of one condition of excersise 

        Args:
            landmarks (List[int], optional): list of 3 points. Defaults to [11,13,15].
            degree (int, optional): angle between points. Defaults to 160.
            tolerance (int, optional): tolerance of angle. Defaults to 0.3.
        """         
        self.landmarks = landmarks
        self.degree = degree
        self.tolerance = tolerance    


class State:
    
    def __init__(self, conditionFront:List[Condition] = [Condition()], conditionSide:List[Condition] = [Condition()], messege:str = "DEFAULT"):
        """Representation of one state of excersise

        Args:
            conditionFront (List[Condition], optional): List of front conditions. Defaults to [Condition()].
            conditionSide (List[Condition], optional): List of side conditions. Defaults to [Condition()].
            messege (str, optional): state messege. Defaults to "DEFAULT".
        """        ''''''
        self.conditonFront = conditionFront
        self.conditonSide = conditionSide
        self.messege = messege
        self.startTime = 0
        self.durationStats = []
        
    def start(self):
        """Sets start time for the excersise
        """        ''''''
        self.startTime = time()
        
    def stop(self):
        """Clens start time for excersie

        Returns:
            time in second: return duration time of excersise
        """
        timeOfStart = self.startTime        
        self.startTime = 0
        duration = time() - timeOfStart
        self.durationStats.append(duration) 
        return duration
    
class Exercise:
    __FRAMES_PER_SECOND = 30
    __CORRECT_FRAMES = math.ceil(__FRAMES_PER_SECOND / 4)

    def __init__(self, name: str):
        """Represent excersise 

        Args:
            name (str): name of excersise
        """
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

    def checkExcersise(self, landmarksFront = None, landmarksSide = None):
        """check one frame for correctness

        Args:
            landmarksFront (List[Condition], optional): list of front landmarks. Defaults to None.
            landmarksSide (List[Condition], optional): list od side landmarks. Defaults to None.

        Returns:
            bool: flag for excersise being done correctly
        """        
        state:State = self._states.get(self._currentStateName)
        
        invalidConditions:List[Condition] = []
        
        
        if landmarksFront:
            for cond in state.conditonFront:
                angle = self.__calculateThreePointAngle(landmarksFront[cond.landmarks[0]], landmarksFront[cond.landmarks[1]], landmarksFront[cond.landmarks[2]])
                if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                    self.__setLastFrameValue(0)
                    invalidConditions.append(cond)
        
                
        if landmarksSide:
            for cond in state.conditonSide:
                angle = self.__calculateThreePointAngle(landmarksSide[cond.landmarks[0]], landmarksSide[cond.landmarks[1]], landmarksSide[cond.landmarks[2]])
                if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                    self.__setLastFrameValue(0)
                    invalidConditions.append(cond)
        
        if(len(invalidConditions) > 0):
            return False,False,invalidConditions
        
        self.__setLastFrameValue(1)
        return True, self.__isCompletedState(), []

    def __isCompletedState(self):
        """checks if state of excersise is completed

        Returns:
            bool: flag for completion of step of excersise
        """        
        if sum(self.__lastFramesCorrectnessArray) / len(self.__lastFramesCorrectnessArray) == 1:
            return True
        return False

    def __setLastFrameValue(self, value:int):
        """sets last frame value

        Args:
            value (int): value of last frame correctness
        """        
        self.__lastFramesCorrectnessArray[self.__frameCounter] = value
        self.__frameCounter = (self.__frameCounter + 1) % self.__CORRECT_FRAMES
    
    def __calculateThreePointAngle(self,leftP, midP, rightP) -> int:
        """calculates angle of three points

        Args:
            leftP (_type_): left point coords
            midP (_type_): mid point coords
            rightP (_type_): right point coords

        Returns:
            int: angle of three points in degrees
        """        
        dis = lambda p1, p2: math.sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2))                
        return int(math.degrees(math.acos((math.pow(dis(midP, leftP), 2) + math.pow(dis(midP, rightP), 2) - math.pow(dis(rightP, leftP), 2)) / (2 * dis(leftP, midP) * dis(rightP, midP)))))

    
    def setState(self, stateName: str | None = None):
        """sets state of excersise to next or to named like stateName arg

        Args:
            stateName (str | None, optional): next step name. Defaults to None.


        Returns:
            _type_: current step name + duration of previous step or current step name if we are trying to set the same step
        """
        print(self._statesNames)
        print(self._stateIdx, self._maxStateIdx)
        
        if stateName == self._currentStateName:
            return self._currentStateName
        
        stateDuration = self._states[self._currentStateName].stop()
        self.__lastFramesCorrectnessArray = [0] * self.__CORRECT_FRAMES

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
        """returns state messege

        Returns:
            str: state messege
        """        
        return ((self._states.get(self._currentStateName)).messege)
    
    def getEndStats(self):
        #TODO Rozbudować
        """return end stats of each excersise
        """        
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
        
            
        


    
           
           