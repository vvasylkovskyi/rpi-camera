from threading import Condition
from picamera2.outputs import Output

class StreamingOutput(Output):
    def __init__(self):
        super().__init__()
        self.frame = None
        self.condition = Condition()

    def outputframe(self, frame, keyframe=True, timestamp=None, packet=None, audio=None):
        with self.condition:
            self.frame = frame
            self.condition.notify_all()