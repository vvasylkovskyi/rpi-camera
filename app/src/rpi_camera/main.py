import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from picamera2 import Picamera2
from picamera2.devices.imx500 import IMX500
from threading import Condition
from picamera2.encoders import JpegEncoder
from picamera2.outputs import Output

model = "/usr/share/imx500-models/imx500_network_mobilenet_v2.rpk"

app = FastAPI(title="RPI Camera API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StreamingOutput(Output):
    def __init__(self):
        super().__init__()
        self.frame = None
        self.condition = Condition()

    def outputframe(self, frame, keyframe=True, timestamp=None, packet=None, audio=None):
        with self.condition:
            self.frame = frame
            self.condition.notify_all()

# imx500 = IMX500(model)
picam2 = Picamera2()
output = StreamingOutput()
encoder = JpegEncoder()

picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()
picam2.start_encoder(encoder, output)

@app.get("/health-check")
async def health_check():
    # device_id = imx500.get_device_id()
    
    return {"status": "healthy"}

def generate_frames():
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )
        time.sleep(1 / 30)  # 30 FPS

@app.get("/video")
def video():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
