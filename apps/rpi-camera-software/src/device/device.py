import time

import psutil
import subprocess
from shared.logger.logger import Logger


class Device:
    _instance = None

    def __new__(cls, device_id=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = Logger("Device")
            cls._instance.__init__(device_id)
        return cls._instance
    
    def __init__(self, device_id=None):
        if not hasattr(self, 'device_id'):
            self.device_id = device_id or "raspberry-pi"  # default device id
    
    def collect_metrics(self):
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        metrics = {
            'device_id': self.device_id,
            'cpu_percent': cpu_percent,
            'memory_percent': mem.percent,
            'disk_percent': disk.percent,
            'uptime_seconds': time.time() - psutil.boot_time(),
        }
        # Log the collected metrics
        self.logger.info(f"Collected health metrics: {metrics}")
        return metrics

    def reboot_device(self):
        self.logger.info("Rebooting device now...")
        subprocess.call(["sudo", "reboot"])

    def shutdown_device(self):
        self.logger.info("Shutting down device now...")
        subprocess.call(["sudo", "shutdown", "now"])