from shared.logger.logger import Logger

class CameraFactory:
    _instance = None
    logger = Logger("CameraFactory")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.camera = cls._get_camera_instance()
        return cls._instance.camera

    @staticmethod
    def _get_camera_instance():
        """Returns an instance of the camera, either RaspberrypiCamera or StubCamera."""
        try:
            from camera.raspberrypi_camera import RaspberrypiCamera
            return RaspberrypiCamera()
        except ModuleNotFoundError:
            from camera.stub_camera import StubCamera
            CameraFactory.logger.warning("Picamera2 not found, using StubCamera instead.")
            return StubCamera()
