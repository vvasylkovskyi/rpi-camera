import asyncio
import av
import fractions
import time
from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from picamera2 import Picamera2
from rpi_camera.logger.logger import Logger 

class PicameraVideoTrack(VideoStreamTrack):
    def __init__(self, picam):
        super().__init__()
        self.picam = picam
        self.logger = Logger("PicameraVideoTrack")
        self.start_time = time.time()
    
    async def recv(self):
        await asyncio.sleep(1 / 30)  # Simulate 30fps pacing

        self.logger.debug("Capturing frame from Picamera2...")
        frame = self.picam.capture_array()
        self.logger.debug("Captured frame from Picamera2...")
        self.logger.debug(f"Frame dtype: {frame.dtype}, shape: {frame.shape}, type: {type(frame)}")

        video_frame = av.VideoFrame.from_ndarray(frame, format="rgb24")
        self.logger.debug(f"Captured frame: {video_frame}")
        video_frame.pts = int((time.time() - self.start_time) * 90000)  # 90kHz clock for video
        self.logger.debug(f"Video frame PTS: {video_frame.pts}")
        video_frame.time_base = fractions.Fraction(1, 90000)
        self.logger.debug(f"Video frame PTS: {video_frame.pts}, time_base: {video_frame.time_base}")
        return video_frame

ICE_SERVERS = [
    RTCIceServer(urls="stun:stun.l.google.com:19302"),
    # Optional: Add TURN server if needed
    RTCIceServer(
        urls="turn:standard.relay.metered.ca:80",
        username="267a8ddc0b92539bebd0229e",
        credential="Inh/lf0T5gQR7i77"
    ),
    RTCIceServer(
        urls="turn:standard.relay.metered.ca:80?transport=tcp",
        username="267a8ddc0b92539bebd0229e",
        credential="Inh/lf0T5gQR7i77"
    ),
    RTCIceServer(
        urls="turn:standard.relay.metered.ca:443",
        username="267a8ddc0b92539bebd0229e",
        credential="Inh/lf0T5gQR7i77"
    ),
    RTCIceServer(
        urls="turns:standard.relay.metered.ca:443?transport=tcp",
        username="267a8ddc0b92539bebd0229e",
        credential="Inh/lf0T5gQR7i77"
    )
]

class WebRTCStreamer:
    def __init__(self):
        self.pc = None
        self.logger = Logger("WebRTCStreamer")

    async def start(self, offer_sdp, video_track):
        rtc_config = RTCConfiguration(ICE_SERVERS)
        self.pc = RTCPeerConnection(configuration=rtc_config)
        self.pc.addTrack(video_track)

        await self.pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type="offer"))
        answer = await self.pc.createAnswer()
        self.logger.info(f"Generated answer SDP: {answer}")
        
        await self.pc.setLocalDescription(answer)

        return self.pc.localDescription.sdp

    async def stop(self):
        if self.pc:
            await self.pc.close()
            self.pc = None
