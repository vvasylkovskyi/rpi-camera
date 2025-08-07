from shared.logger.logger import Logger
from shared.models.camera_control_event import WebRTCOffer

class StubCamera:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = Logger("StubCamera")
        return cls._instance

    def start_video(self):
        self.logger.warning("start_video called, but camera not available.")
        return False

    def stop_video(self):
        self.logger.warning("stop_video called, but camera not available.")
        return None

    async def start_webrtc_stream(self, webrtc_offer: WebRTCOffer):
        self.logger.warning("start_webrtc_stream called, but camera not available.")
        return None

    async def stop_webrtc_stream(self):
        self.logger.warning("stop_webrtc_stream called, but camera not available.")
        return False
