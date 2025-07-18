import asyncio
import threading
from rpi_camera.logger.logger import Logger  

class TerminalController:
    def __init__(self, loop):
        """
        :param loop: asyncio event loop
        :param video_controller: object with async start_video() and stop_video() methods
        """
        self.logger = Logger("Terminal")
        self.loop = loop
        self._stop_thread = threading.Event()

    def start(self):
        thread = threading.Thread(target=self._run_menu_loop, daemon=True)
        thread.start()

    def _run_menu_loop(self):
        self.logger.info("Terminal controller started. Waiting for user input...")
        menu_text = (
            "\nPlease choose an option:\n"
            "1) Start Video\n"
            "2) Stop Video\n"
            "Press Ctrl+C to quit. \n"
            "Enter choice [1-2]: "
        )
        while not self._stop_thread.is_set():
            try:
                choice = input(menu_text).strip()
            except EOFError:
                self.logger.info("Input closed. Exiting terminal controller.")
                break

            if choice == "1":
                self.logger.info("User selected: Start Video")
            elif choice == "2":
                self.logger.info("User selected: Stop Video")
            else:
                self.logger.info(f"Invalid option '{choice}'. Please enter 1, 2, or 3.")

    def stop(self):
        self._stop_thread.set()
