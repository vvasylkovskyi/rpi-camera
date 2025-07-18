import asyncio
import signal
from rpi_camera.video_operations.rpi_camera import RpiCamera
from rpi_camera.logger.logger import Logger

logger = Logger("main")

async def main():
    logger.info("Starting RPI Camera...")
    rpi_camera = RpiCamera()
    ## TODO: Do camera things    
    try:

        # Run until stopped, e.g. by Ctrl+C
        logger.info("Running Camera Module... Press Ctrl+C to exit.")
        stop_event = asyncio.Event()

        def shutdown_handler():
            logger.info("Shutdown signal received, stopping...")
            stop_event.set()

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, shutdown_handler)
        loop.add_signal_handler(signal.SIGTERM, shutdown_handler)

        await stop_event.wait()

    except Exception as e:
        logger.error(f"Error in Camera Module: {e}")


if __name__ == "__main__":
    asyncio.run(main())
