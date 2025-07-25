import asyncio
from aiortc.contrib.media import MediaRecorder
from picamera2 import Picamera2
from rpi_camera.webrtc.webrtc_streamer import PicameraVideoTrack

async def run():
    picam = Picamera2()
    video_config = picam.create_video_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
    picam.configure(video_config)
    picam.start()

    track = PicameraVideoTrack(picam)
    recorder = MediaRecorder("./output.mp4")  # output file
    await recorder.start()
    recorder.addTrack(track)

    print("Recording 5 seconds of video...")
    await asyncio.sleep(5)

    await recorder.stop()
    print("Recording complete. Output saved to output.mp4")

if __name__ == "__main__":
    asyncio.run(run())
