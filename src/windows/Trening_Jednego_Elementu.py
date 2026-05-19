import detection.excersises as ex
from TwoCameraFrameWindow import TwoCameraFrameWindow as TCFW


class Trening_Jednego_Elementu(TCFW):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screenExcersise = ex.LowReady()

        
        