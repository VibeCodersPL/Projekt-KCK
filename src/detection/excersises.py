import math
from typing import List
from time import time


class Condition:
    def __init__(self, landmarks: List[int] = [11,13,15], degree: int = 160, tolerance: int = 0.3, conditionMet:bool = True):
        """Representation of one condition of excersise 

        Args:
            landmarks (List[int], optional): list of 3 points. Defaults to [11,13,15].
            degree (int, optional): angle between points. Defaults to 160.
            tolerance (int, optional): tolerance of angle. Defaults to 0.3.
        """         
        self.landmarks = landmarks
        self.degree = degree
        self.tolerance = tolerance
        self.conditionMet = conditionMet


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
        self.correctnessMetric = []
    
        
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

    def addToCorrectnessMetric(self,metric):
        self.correctnessMetric.append(metric)

    
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
        self.__lastFramesCorrectnessArray: list[bool] = [False] * self.__CORRECT_FRAMES
        self.__lastFramesCorrectnessMetricArray: list[bool] = [False] * self.__CORRECT_FRAMES
        self._currentStateName = "DEFAULT"
        self._states: dict[str, State] = {}
        self._timeOfStateStart = time()
        self._states["DEFAULT"] = State()
        self._currentState = self._states.get("DEFAULT")
        

    def checkExcersise(self, landmarksFront = None, landmarksSide = None):
        """check one frame for correctness

        Args:
            landmarksFront (List[Condition], optional): list of front landmarks. Defaults to None.
            landmarksSide (List[Condition], optional): list od side landmarks. Defaults to None.

        Returns:
            bool: flag for excersise being done correctly
        """        
                
        isAllConditionsMet = True
        
        if landmarksFront:
            for cond in self._currentState.conditonFront:
                angle = self.__calculateThreePointAngle(landmarksFront[cond.landmarks[0]], landmarksFront[cond.landmarks[1]], landmarksFront[cond.landmarks[2]])
                if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                    self.__setLastFrameValue(False)
                    cond.conditionMet, isAllConditionsMet = False, False
                else:
                    cond.conditionMet = True
        
        if landmarksSide:
            for cond in self._currentState.conditonSide:
                angle = self.__calculateThreePointAngle(landmarksSide[cond.landmarks[0]], landmarksSide[cond.landmarks[1]], landmarksSide[cond.landmarks[2]])
                if abs(angle - cond.degree) - (cond.degree * cond.tolerance) > 0:
                    self.__setLastFrameValue(False)
                    cond.conditionMet, isAllConditionsMet = False, False
                else:
                    cond.conditionMet = True
        
        if isAllConditionsMet == False:
            return False, False
        
        self.__setLastFrameValue(True)
        return True, self.__isCompletedState()

    def __isCompletedState(self):
        """checks if state of excersise is completed

        Returns:
            bool: flag for completion of step of excersise
        """        
        return (sum(self.__lastFramesCorrectnessArray) / len(self.__lastFramesCorrectnessArray) == 1)
   
    def __setLastFrameValue(self, value:bool):
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
            tuple: current step name and duration of previous step, or just current step name if we are trying to set the same step
        """

        currentStateName = next(k for k, v in self._states.items() if v == self._currentState)    

        if stateName == currentStateName:
            return currentStateName

        stateDuration = self._currentState.stop()
        self.__lastFramesCorrectnessArray = [0] * self.__CORRECT_FRAMES

        if stateName is None:
            statesNamesList = list(self._states.keys())
            currentIndex = statesNamesList.index(currentStateName)
            stateName = statesNamesList[(currentIndex + 1) % len(statesNamesList)]
                
        else:
            if stateName not in self._states:
                raise ValueError(f"Stan '{stateName}' nie istnieje!")

        self._currentState = self._states[stateName] 

        return stateName, (stateDuration - self.__CORRECT_FRAMES / self.__FRAMES_PER_SECOND)

        
    
    
    
    def getStateMessage(self):
        """returns state messege

        Returns:
            str: state messege
        """        
        return ((self._states.get(self._currentStateName)).messege)
    
    def getStateConditions(self):
        currentState = self._states.get(self._currentStateName)
        
        return currentState.conditonFront, currentState.conditonSide
    
    def getEndStats(self):
        #TODO Rozbudować
        """return end stats of each excersise
        """        
        for key, state in self._states.items():
            print(key, state.durationStats)
    
class LowReady(Exercise):
    def __init__(self):
        super().__init__("LowReady")
                
        conditionList = [Condition([23,25,27]),Condition([24,26,28]), Condition()]
        
        self._states["START"] = State(conditionFront=conditionList,conditionSide=conditionList, messege = "START")
        self._states["END"] = State(messege = "END")        
            
        


    
           
           