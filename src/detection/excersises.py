import math
from typing import List
from time import time
import json
from tts.tts import TTS
from pathlib import Path

def load_json():
    JSON_PATH = Path(__file__).resolve().parents[1] / "tts" / "phrases.json"
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

tts_messages = load_json()

class Condition:
    def __init__(self, landmarks: List[int] = [11,13,15], degree: int = 160, tolerance: int = 0.3, conditionMet:bool = True, message:str = "Skoryguj postawę"):
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
        self.message = message


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
        
    def stop(self, metric):
        """Clens start time for excersie

        Returns:
            time in second: return duration time of excersise
        """
        timeOfStart = self.startTime        
        self.startTime = 0
        duration = time() - timeOfStart
        
        self.durationStats.append(duration) 
        self.correctnessMetric.append(metric)
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
        self.__lastFramesCorrectnessArray: list[bool] = [False] * self.__CORRECT_FRAMES
        self.__lastFramesCorrectnessMetricArray: list[bool] = [False] * self.__CORRECT_FRAMES
        self._states: dict[str, State] = {}
        self._states["DEFAULT"] = State()
        self._currentState = self._states.get("DEFAULT")
        self._timeOfExcersiseStart = 0
        self.is_running = False
        self.has_run = False
        self.is_saved = False
        self._currentState.start()

    def start_excersise(self):
        self.is_running = True
        self.has_run = False
        self.is_saved = False
        self._currentState.start()
        self._timeOfExcersiseStart = time()
        
    def stop_excersise(self):
        self.is_running = False
        self.has_run = True
        return time() - self._timeOfExcersiseStart
        
    def toggle_running(self) -> bool:
        """Przełącza stan ćwiczenia. Zwraca True jeśli wystartowało, False jeśli zatrzymano."""
        if self.is_running:
            self.stop_excersise()
        else:
            self.start_excersise()
        return self.is_running
        
    def mark_as_saved(self):
        self.is_saved = True

    def checkExcersise(self, landmarksFront = None, landmarksSide = None):
        """check one frame for correctness

        Args:
            landmarksFront (List[Condition], optional): list of front landmarks. Defaults to None.
            landmarksSide (List[Condition], optional): list od side landmarks. Defaults to None.

        Returns:
            bool: flag for excersise being done correctly
        """        
        # ZABEZPIECZENIE: Jeśli nie ma jakichkolwiek punktów (np. kamera odłączona lub brak sylwetki)
        if not landmarksFront or not landmarksSide:
            self.__setLastFrameValue(False, 0.0)
            return False, False
                
        isAllConditionsMet = True
        total_score = 0.0
        conditions_count = 0
        
        def evaluate_conditions(landmarks, conditions):
            nonlocal isAllConditionsMet, total_score, conditions_count
            
            # ZABEZPIECZENIE przed pustą listą landmarków
            if not landmarks or len(landmarks) == 0:
                isAllConditionsMet = False
                return

            for cond in conditions:
                # ZABEZPIECZENIE: Upewnij się, że tablica ma wystarczająco elementów
                if len(landmarks) <= max(cond.landmarks):
                    cond.conditionMet = False
                    isAllConditionsMet = False
                    continue

                angle = self.calculateThreePointAngle(
                    landmarks[cond.landmarks[0]], 
                    landmarks[cond.landmarks[1]], 
                    landmarks[cond.landmarks[2]]
                )
                
                error = abs(angle - cond.degree)
                max_error = cond.degree * cond.tolerance
                
                if max_error == 0:
                    max_error = 1.0 
                
                condition_score = max(0.0, 100.0 * (1.0 - (error / max_error)))
                
                total_score += condition_score
                conditions_count += 1
                
                if error > max_error:
                    cond.conditionMet = False
                    isAllConditionsMet = False
                else:
                    cond.conditionMet = True
        
        if landmarksFront:
            evaluate_conditions(landmarksFront, self._currentState.conditonFront)
        
        if landmarksSide:
            evaluate_conditions(landmarksSide, self._currentState.conditonSide)
        
        frame_score = (total_score / conditions_count) if conditions_count > 0 else 0.0
        
        if not isAllConditionsMet:
            self.__setLastFrameValue(False, frame_score)
            return False, False
        
        self.__setLastFrameValue(True, frame_score)
        return True, self.__isCompletedState()

    def __isCompletedState(self):
        """checks if state of excersise is completed

        Returns:
            bool: flag for completion of step of excersise
        """        
        return (sum(self.__lastFramesCorrectnessArray) / len(self.__lastFramesCorrectnessArray) == 1)
   
    def __setLastFrameValue(self, value:bool, metric:bool | None = None):
        """sets last frame value

        Args:
            value (int): value of last frame correctness
        """        
        self.__lastFramesCorrectnessArray[self.__frameCounter] = value
        if metric is not None:
            self.__lastFramesCorrectnessMetricArray[self.__frameCounter] = metric
        self.__frameCounter = (self.__frameCounter + 1) % self.__CORRECT_FRAMES
    
    def calculateThreePointAngle(self,leftP, midP, rightP) -> int:
        """calculates angle of three points

        Args:
            leftP (_type_): left point coords
            midP (_type_): mid point coords
            rightP (_type_): right point coords

        Returns:
            int: angle of three points in degrees
        """        
        dis = lambda p1, p2: math.sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2))                
        try:
            val = (math.pow(dis(midP, leftP), 2) + math.pow(dis(midP, rightP), 2) - math.pow(dis(rightP, leftP), 2)) / (2 * dis(leftP, midP) * dis(rightP, midP))
            val = max(-1.0, min(1.0, val))
            return int(math.degrees(math.acos(val)))
        except ZeroDivisionError:
            return 0
    
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

        avg_metric_of_correct_frames = sum(self.__lastFramesCorrectnessMetricArray) / len(self.__lastFramesCorrectnessMetricArray)
        stateDuration = self._currentState.stop(avg_metric_of_correct_frames)
        
        self.__lastFramesCorrectnessArray = [False] * self.__CORRECT_FRAMES
        self.__lastFramesCorrectnessMetricArray = [0.0] * self.__CORRECT_FRAMES

        if stateName is None:
            statesNamesList = list(self._states.keys())
            currentIndex = statesNamesList.index(currentStateName)
            stateName = statesNamesList[(currentIndex + 1) % len(statesNamesList)]
        else:
            if stateName not in self._states:
                raise ValueError(f"Stan '{stateName}' nie istnieje!")

        self._currentState = self._states[stateName] 
        self._currentState.start()

        return stateName, (stateDuration - self.__CORRECT_FRAMES / self.__FRAMES_PER_SECOND)

    def getStateMessage(self):
        """returns state messege

        Returns:
            str: state messege
        """        
        return (self._currentState.messege)
    
    def getStateConditions(self):
        return self._currentState.conditonFront, self._currentState.conditonSide
    
    def getEndStats(self):
        """return end stats of each excersise
        """ 
        output = {}   
        for k, v in self._states.items():
            v:State
            output[k] = (v.durationStats,v.correctnessMetric)
            
        return output
    
    
    
class LowReady(Exercise):
    def __init__(self):
        super().__init__("LowReady")
                
        conditionList = [Condition([23,25,27]),Condition([24,26,28]), Condition()]
        
        self._states["START"] = State(conditionFront=conditionList,conditionSide=conditionList, messege = "START")
        self._states["END"] = State(conditionFront=conditionList,conditionSide=conditionList, messege = "END")     
            

class StandingStance(Exercise):
    def __init__(self):
        super().__init__("StandingStance")
        messages = tts_messages.get("CwiczenieStojaca", [])

        def get_message(message_number, default="Skoryguj postawę"):
            if message_number < len(messages):
                return messages[message_number]
            return default

        legs_front = [
            Condition([24, 26, 28], degree=165, tolerance=0.15, message=get_message(0)),
            Condition([23, 25, 27], degree=165, tolerance=0.15, message=get_message(0)) 
        ]
        legs_side = [
            Condition([23, 25, 27], degree=165, tolerance=0.15, message="Zegnij mocniej kolana (widok z boku)")
        ]

        torso_front = [
            Condition([12, 24, 26], degree=170, tolerance=0.1, message="Ustaw tułów frontalnie"), 
            Condition([11, 23, 25], degree=170, tolerance=0.1, message="Ustaw tułów frontalnie")
        ]
        torso_side = [
            Condition([25, 23, 1], degree=170, tolerance=0.1, message="Ustaw tułów frontalnie"), 

        ]

        arms_front = [
            Condition([23, 11, 13], degree=20, tolerance=0.5, message=get_message(1))    
        ]
        arms_side = [
            Condition([11, 13, 15], degree=130, tolerance=0.2, message="Skoryguj wysokość uniesienia broni")
        ]

        self._states["Legs"] = State(
            conditionFront=legs_front,
            conditionSide=legs_side,
            messege="Skoncentruj się na nogach i ugięciu kolan."
        )

        self._states["LegsTorso"] = State(
            conditionFront=legs_front + torso_front,
            conditionSide=legs_side + torso_side,
            messege="Dobrze, teraz wyprostuj i pochyl lekko tułów."
        )

        self._states["LegsTorsoArms"] = State(
            conditionFront=legs_front + torso_front + arms_front,
            conditionSide=legs_side + torso_side + arms_side,
            messege="Złóż się do strzału. Zablokuj ramiona w ramie."
        )

        self._currentState = self._states.get("LegsTorsoArms")


        #self._currentState = self._states.get("Legs")
        self._currentState.start()
        self._timeOfStateStart = self._currentState.startTime
           
           