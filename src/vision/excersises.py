import math
from typing import List
from time import time
import json
from pathlib import Path

def load_json():
    JSON_PATH = Path(__file__).resolve().parents[1] / "core" / "phrases.json"
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

tts_messages = load_json()

class Condition:
    def __init__(self, landmarks: List[int] = [11,13,15], degree: int = 160, tolerance: int = 0.3, condition_met:bool = True, message:str = "Skoryguj postawę"):
        """Representation of one condition of excersise 

        Args:
            landmarks (List[int], optional): list of 3 points. Defaults to [11,13,15].
            degree (int, optional): angle between points. Defaults to 160.
            tolerance (int, optional): tolerance of angle. Defaults to 0.3.
        """         
        self.landmarks = landmarks
        self.degree = degree
        self.tolerance = tolerance
        self.condition_met = condition_met
        self.message = message


class State:
    
    def __init__(self, condition_front:List[Condition] = [Condition()], condition_side:List[Condition] = [Condition()], messege:str = "DEFAULT"):
        """Representation of one state of excersise

        Args:
            condition_front (List[Condition], optional): List of front conditions. Defaults to [Condition()].
            condition_side (List[Condition], optional): List of side conditions. Defaults to [Condition()].
            messege (str, optional): state messege. Defaults to "DEFAULT".
        """        ''''''
        self.condition_front = condition_front
        self.conditon_side = condition_side
        self.messege = messege
        self.start_time = 0
        self.duration_stats = []
        self.correctness_metric = []
    
        
    def start(self):
        """Sets start time for the excersise
        """        ''''''
        self.start_time = time()
        
    def stop(self, metric):
        """Clens start time for excersie

        Returns:
            time in second: return duration time of excersise
        """
        timeOfStart = self.start_time
        self.start_time = 0
        duration = time() - timeOfStart
        
        self.duration_stats.append(duration)
        self.correctness_metric.append(metric)
        return duration


class Exercise:
    __FRAMES_PER_SECOND = 30
    __CORRECT_FRAMES = math.ceil(__FRAMES_PER_SECOND / 4)

    def __init__(self, name: str):
        """Represent excersise 

        Args:
            name (str): name of excersise
        """
        self._excersise_name = name
        self.__frame_counter = 0
        self.__last_frames_correctness_array: list[bool] = [False] * self.__CORRECT_FRAMES
        self.__last_frames_correctness_metric_array: list[bool] = [False] * self.__CORRECT_FRAMES
        self._states: dict[str, State] = {}
        self._current_state = None
        self._time_of_excersise_start = 0
        self.is_running = False
        self.has_run = False
        self.is_saved = False
        self.messages = None
    def start_excersise(self):
        self.is_running = True
        self.has_run = False
        self.is_saved = False
        self._current_state.start()
        self._time_of_excersise_start = time()
        
    def stop_excersise(self):
        self.is_running = False
        self.has_run = True
        return time() - self._time_of_excersise_start
        
    def toggle_running(self) -> bool:
        """Przełącza stan ćwiczenia. Zwraca True jeśli wystartowało, False jeśli zatrzymano."""
        if self.is_running:
            self.stop_excersise()
        else:
            self.start_excersise()
        return self.is_running
        
    def mark_as_saved(self):
        self.is_saved = True

    def check_excersise(self, landmarks_front = None, landmarks_side = None):
        """check one frame for correctness

        Args:
            landmarks_front (List[Condition], optional): list of front landmarks. Defaults to None.
            landmarks_side (List[Condition], optional): list od side landmarks. Defaults to None.

        Returns:
            bool: flag for excersise being done correctly
        """        
        # ZABEZPIECZENIE: Jeśli nie ma jakichkolwiek punktów (np. kamera odłączona lub brak sylwetki)
        if not landmarks_front or not landmarks_side:
            self.__set_last_frame_value(False, 0.0)
            return False, False
                
        is_all_conditions_met = True
        total_score = 0.0
        conditions_count = 0
        
        def evaluate_conditions(landmarks, conditions):
            nonlocal is_all_conditions_met, total_score, conditions_count
            
            # ZABEZPIECZENIE przed pustą listą landmarków
            if not landmarks or len(landmarks) == 0:
                is_all_conditions_met = False
                return

            for cond in conditions:
                # ZABEZPIECZENIE: Upewnij się, że tablica ma wystarczająco elementów
                if len(landmarks) <= max(cond.landmarks):
                    cond.condition_met = False
                    is_all_conditions_met = False
                    continue

                angle = self.calculate_three_point_angle(
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
                    cond.condition_met = False
                    is_all_conditions_met = False
                else:
                    cond.condition_met = True
        
        if landmarks_front:
            evaluate_conditions(landmarks_front, self._current_state.condition_front)
        
        if landmarks_side:
            evaluate_conditions(landmarks_side, self._current_state.conditon_side)
        
        frame_score = (total_score / conditions_count) if conditions_count > 0 else 0.0
        
        if not is_all_conditions_met:
            self.__set_last_frame_value(False, frame_score)
            return False, False
        
        self.__set_last_frame_value(True, frame_score)
        return True, self.__is_completed_state()

    def __is_completed_state(self):
        """checks if state of excersise is completed

        Returns:
            bool: flag for completion of step of excersise
        """        
        return (sum(self.__last_frames_correctness_array) / len(self.__last_frames_correctness_array) == 1)
   
    def __set_last_frame_value(self, value:bool, metric: bool | None = None):
        """sets last frame value

        Args:
            value (int): value of last frame correctness
        """        
        self.__last_frames_correctness_array[self.__frame_counter] = value
        if metric is not None:
            self.__last_frames_correctness_metric_array[self.__frame_counter] = metric
        self.__frame_counter = (self.__frame_counter + 1) % self.__CORRECT_FRAMES
    
    def calculate_three_point_angle(self, leftP, midP, rightP) -> int:
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
    
    def set_state(self, state_name: str | None = None):
        """sets state of excersise to next or to named like stateName arg

        Args:
            state_name (str | None, optional): next step name. Defaults to None.
        Returns:
            tuple: current step name and duration of previous step, or just current step name if we are trying to set the same step
        """
        current_state_name = next(k for k, v in self._states.items() if v == self._current_state)

        if state_name == current_state_name:
            return current_state_name

        avg_metric_of_correct_frames = sum(self.__last_frames_correctness_metric_array) / len(self.__last_frames_correctness_metric_array)
        state_duration = self._current_state.stop(avg_metric_of_correct_frames)
        
        self.__last_frames_correctness_array = [False] * self.__CORRECT_FRAMES
        self.__last_frames_correctness_metric_array = [0.0] * self.__CORRECT_FRAMES

        if state_name is None:
            states_names_list = list(self._states.keys())
            current_index = states_names_list.index(current_state_name)
            state_name = states_names_list[(current_index + 1) % len(states_names_list)]
        else:
            if state_name not in self._states:
                raise ValueError(f"Stan '{state_name}' nie istnieje!")

        self._current_state = self._states[state_name]
        self._current_state.start()

        return state_name, (state_duration - self.__CORRECT_FRAMES / self.__FRAMES_PER_SECOND)

    def get_state_message(self):
        """returns state messege

        Returns:
            str: state messege
        """        
        return (self._current_state.messege)
    
    def get_state_conditions(self):
        return self._current_state.condition_front, self._current_state.conditon_side
    
    def get_end_stats(self):
        """return end stats of each excersise
        """ 
        output = {}   
        for k, v in self._states.items():
            v:State
            output[k] = (v.duration_stats, v.correctness_metric)
            
        return output
    
    def get_message(self, message_number, default="Skoryguj postawę"):
        if message_number < len(self.messages):
            return self.messages[message_number]
        return default

    
    
    
class LowReady(Exercise):
    def __init__(self):
        super().__init__("LowReady")
                
        condition_list = [Condition([23,25,27]),Condition([24,26,28]), Condition()]
        
        self._states["START"] = State(condition_front=condition_list, condition_side=condition_list, messege ="START")
        self._states["END"] = State(condition_front=condition_list, condition_side=condition_list, messege ="END")
            

class StandingStance(Exercise):
    def __init__(self):
        super().__init__("StandingStance")
        self.messages = tts_messages.get("CwiczenieStojaca", [])
        
        legs_front = [
            Condition([24, 26, 28], degree=165, tolerance=0.15, message=self.get_message(0)),
            Condition([23, 25, 27], degree=165, tolerance=0.15, message=self.get_message(0)) 
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
            Condition([23, 11, 13], degree=20, tolerance=0.5, message=self.get_message(1))    
        ]
        arms_side = [
            Condition([11, 13, 15], degree=130, tolerance=0.2, message="Skoryguj wysokość uniesienia broni")
        ]
        
        self._states["LowReady"] = get_low_ready_state()

        self._states["Legs"] = State(
            condition_front=legs_front,
            condition_side=legs_side,
            messege="Skoncentruj się na nogach i ugięciu kolan."
        )

        self._states["LegsTorso"] = State(
            condition_front=legs_front + torso_front,
            condition_side=legs_side + torso_side,
            messege="Dobrze, teraz wyprostuj i pochyl lekko tułów."
        )

        self._states["LegsTorsoArms"] = State(
            condition_front=legs_front + torso_front + arms_front,
            condition_side=legs_side + torso_side + arms_side,
            messege="Złóż się do strzału. Zablokuj ramiona w ramie."
        )
        self._current_state = self._states.get("LowReady")
        self._current_state.start()
        self._time_of_state_start = self._current_state.start_time

class KneelingStance(Exercise):
    def __init__(self):
        super().__init__("KneelingStance")
        self.messages = tts_messages.get("CwiczenieStojaca", [])
        
        legs_front = [
        ]
        legs_side = [
            Condition([24, 26, 28], degree=100, tolerance=0.15, message=self.get_message(0)),#lewa noga
            Condition([23, 25, 27], degree=85, tolerance=0.15, message="Zegnij mocniej kolana (widok z boku)")
        ]

        torso_front = [
            Condition([12, 24, 26], degree=170, tolerance=0.1, message="Ustaw tułów frontalnie"), 
            Condition([11, 23, 25], degree=170, tolerance=0.1, message="Ustaw tułów frontalnie")
        ]
        torso_side = [
            Condition([25, 23, 11], degree=170, tolerance=0.1, message="Ustaw tułów frontalnie"), 

        ]

        arms_front = [
            Condition([23, 11, 13], degree=20, tolerance=0.5, message=self.get_message(1))    
        ]
        arms_side = [
            Condition([11, 13, 15], degree=130, tolerance=0.2, message="Skoryguj wysokość uniesienia broni")
        ]


        self._states["LowReady"] = get_low_ready_state()


        self._states["Legs"] = State(
            condition_front=legs_front,
            condition_side=legs_side,
            messege="Skoncentruj się na nogach i ugięciu kolan."
        )

        self._states["LegsTorso"] = State(
            condition_front=legs_front + torso_front,
            condition_side=legs_side + torso_side,
            messege="Dobrze, teraz wyprostuj i pochyl lekko tułów."
        )

        self._states["LegsTorsoArms"] = State(
            condition_front=legs_front + torso_front + arms_front,
            condition_side=legs_side + torso_side + arms_side,
            messege="Złóż się do strzału. Zablokuj ramiona w ramie."
        )
        
        self._current_state = self._states.get("LowReady")
        self._current_state.start()
        self._time_of_state_start = self._current_state.start_time

        
        
        
def get_low_ready_state() -> State:
    
    legs_front = [
        Condition([24, 26, 28], degree=175, tolerance=0.1, message="Wyprostuj prawą nogę"),
        Condition([23, 25, 27], degree=175, tolerance=0.1, message="Wyprostuj lewą nogę")
    ]
    legs_side = [
        Condition([23, 25, 27], degree=175, tolerance=0.1, message="Nie uginaj kolan")
    ]

    torso_front = [
        Condition([12, 24, 26], degree=175, tolerance=0.1, message="Wyprostuj się"), 
        Condition([11, 23, 25], degree=175, tolerance=0.1, message="Wyprostuj się")
    ]
    torso_side = [
        Condition([11, 23, 25], degree=175, tolerance=0.1, message="Wyprostuj plecy"), 
    ]

    arms_front = [
        Condition([11, 13, 15], degree=125, tolerance=0.5, message="Trzymajbroń przy ciele"),   
        Condition([23, 11, 13], degree=15, tolerance=0.5, message="Trzymaj łokcie bliżej ciała")    
    ]
    arms_side = [
        Condition([12, 14, 16], degree=170, tolerance=0.15, message="Opuść lufę broni w dół")
    ]

    return State(
        condition_front=legs_front + torso_front + arms_front,
        condition_side=legs_side + torso_side + arms_side,
        messege="Przyjmij postawę swobodną. Wyprostuj się i opuść broń."
    )