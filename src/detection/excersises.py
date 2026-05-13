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