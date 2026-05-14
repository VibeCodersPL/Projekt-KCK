import detection.excersises as ex
from TwoCameraFrameWindow import TwoCameraFrameWindow as TCFW

class TreningWspierany(TCFW):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screenExcersise = ex.LowReady()
