"""
Daemon - Monitor main process status

Features:
1. Start and monitor main process (main.py)
2. Check if main process is running normally
3. Auto-restart if main process exits abnormally
4. Log monitoring events
5. Support graceful shutdown
"""

import logging
import os
import signal
import subprocess
import sys
import threading
import time

# Configuration
MAIN_SCRIPT = "main.py"
CHECK_INTERVAL = 5  # Check interval in seconds
RESTART_DELAY = 3   # Delay before restart in seconds
MAX_RESTARTS = 10   # Maximum restart attempts
RESTART_WINDOW = 60 # Time window for restart limit in seconds

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Daemon:
    def __init__(self):
        self.main_process = None
        self.restart_count = 0
        self.last_restart_time = 0
        self.running = True
        self.log_thread = None

    def _read_process_output(self):
        """Read main process output in a separate thread"""
        if self.main_process is None:
            return

        try:
            for line in iter(self.main_process.stdout.readline, ''):
                if line:
                    print(line.rstrip())
        except Exception as e:
            logger.debug(f"Error reading process output: {e}")

    def start_main_process(self):
        """Start main process"""
        try:
            logger.info(f"Starting main process: {MAIN_SCRIPT}")
            self.main_process = subprocess.Popen(
                [sys.executable, MAIN_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Start log reading thread
            self.log_thread = threading.Thread(
                target=self._read_process_output,
                daemon=True
            )
            self.log_thread.start()

            logger.info(f"Main process started, PID: {self.main_process.pid}")
            self.restart_count = 0
            return True
        except Exception as e:
            logger.error(f"Failed to start main process: {e}")
            return False

    def check_process(self):
        """Check if main process is running"""
        if self.main_process is None:
            return False

        return_code = self.main_process.poll()
        if return_code is None:
            return True

        logger.warning(f"Main process exited with code: {return_code}")
        return False

    def monitor(self):
        """Monitor main process"""
        logger.info("Daemon started, monitoring main process...")

        if not self.start_main_process():
            logger.error("Cannot start main process, daemon exiting")
            return

        while self.running:
            try:
                if not self.check_process():
                    now = time.time()
                    if now - self.last_restart_time < RESTART_WINDOW:
                        self.restart_count += 1
                    else:
                        self.restart_count = 1
                    self.last_restart_time = now

                    if self.restart_count >= MAX_RESTARTS:
                        logger.error(
                            f"Max restarts ({MAX_RESTARTS}) reached in {RESTART_WINDOW} seconds, daemon stopping"
                        )
                        break

                    logger.info(f"Waiting {RESTART_DELAY} seconds before restart...")
                    time.sleep(RESTART_DELAY)

                    if not self.start_main_process():
                        logger.error("Failed to restart main process, daemon exiting")
                        break

                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                logger.info("Received stop signal, stopping daemon...")
                self.running = False
            except Exception as e:
                logger.error(f"Daemon error: {e}")
                time.sleep(CHECK_INTERVAL)

    def stop(self):
        """Stop daemon and main process"""
        logger.info("Stopping daemon...")
        self.running = False

        if self.main_process and self.main_process.poll() is None:
            logger.info(f"Stopping main process (PID: {self.main_process.pid})...")
            try:
                self.main_process.terminate()
                self.main_process.wait(timeout=5)
                logger.info("Main process stopped")
            except subprocess.TimeoutExpired:
                logger.warning("Main process timeout, force killing")
                self.main_process.kill()
            except Exception as e:
                logger.error(f"Failed to stop main process: {e}")


def signal_handler(signum, frame):
    """Signal handler"""
    logger.info(f"Received signal {signum}, stopping daemon")
    daemon.stop()


if __name__ == "__main__":
    os.makedirs('logs', exist_ok=True)

    daemon = Daemon()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        daemon.monitor()
    except Exception as e:
        logger.error(f"Daemon exited with error: {e}")
        daemon.stop()