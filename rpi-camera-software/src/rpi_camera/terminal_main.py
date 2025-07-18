import asyncio
from rpi_camera.logger.logger import Logger
from rpi_camera.terminal.terminal_controller import TerminalController  # your TerminalController class

logger = Logger("TerminalRunner")

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    terminal_controller = TerminalController(loop)
    terminal_controller.start()

    logger.info("Terminal Controller started. Press Ctrl+C to quit.")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping...")
    finally:
        terminal_controller.stop()
        loop.stop()
        loop.close()
        logger.info("Terminal Controller stopped.")

if __name__ == "__main__":
    main()
