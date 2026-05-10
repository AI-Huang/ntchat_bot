"""
Daemon - Monitor main process status

Features:
1. Start and monitor main process (main.py)
2. Check if main process is running normally
3. Auto-restart if main process exits abnormally
4. Send email notification when main process stops
5. Log monitoring events
6. Support graceful shutdown
"""

import logging
import os
import signal
import smtplib
import subprocess
import sys
import threading
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import formataddr

# Configuration
MAIN_SCRIPT = "main.py"
CHECK_INTERVAL = 5  # Check interval in seconds
RESTART_DELAY = 3   # Delay before restart in seconds
MAX_RESTARTS = 10   # Maximum restart attempts
RESTART_WINDOW = 60 # Time window for restart limit in seconds

# Email notification configuration
# Set these environment variables or update the defaults below
EMAIL_ENABLED = os.environ.get('DAEMON_EMAIL_ENABLED', 'false').lower() == 'true'
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.example.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'your_email@example.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'your_password')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'your_email@example.com')
TO_EMAIL = os.environ.get('TO_EMAIL', 'recipient@example.com')
EMAIL_SUBJECT = os.environ.get('EMAIL_SUBJECT', '⚠️ WeChat Bot Service Alert')

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


def send_email_alert(subject: str, message: str):
    """
    Send email notification when main process stops
    
    Args:
        subject: Email subject
        message: Email content
    """
    if not EMAIL_ENABLED:
        logger.debug("Email notification is disabled")
        return
    
    try:
        # Create email message
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = formataddr(('WeChat Bot Daemon', FROM_EMAIL))
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        
        logger.info(f"Email notification sent to {TO_EMAIL}")
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")


class Daemon:
    def __init__(self):
        self.main_process = None
        self.restart_count = 0
        self.last_restart_time = 0
        self.running = True
        self.log_thread = None
        self.last_email_time = 0
        self.email_cooldown = 300  # 5 minutes cooldown between emails
    
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
            self._send_stop_alert(f"Failed to start main process: {e}")
            return False

    def _send_stop_alert(self, reason: str):
        """Send email alert when main process stops"""
        now = time.time()
        # Rate limiting: only send email once every 5 minutes
        if now - self.last_email_time < self.email_cooldown:
            logger.debug("Email cooldown period not exceeded, skipping notification")
            return
        
        self.last_email_time = now
        
        subject = f"{EMAIL_SUBJECT} - Main Process Stopped"
        message = f"""WeChat Bot service has stopped unexpectedly.
        
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Reason: {reason}
Restart attempts: {self.restart_count}
Max restarts allowed: {MAX_RESTARTS}
Restart window: {RESTART_WINDOW} seconds

{"="*50}
This is an automated notification from the daemon process.
{"="*50}"""
        
        send_email_alert(subject, message)

    def check_process(self):
        """Check if main process is running"""
        if self.main_process is None:
            return False

        return_code = self.main_process.poll()
        if return_code is None:
            return True

        # Process has exited
        reason = f"Main process exited with code: {return_code}"
        logger.warning(reason)
        self._send_stop_alert(reason)
        return False

    def monitor(self):
        """Monitor main process"""
        logger.info("Daemon started, monitoring main process...")
        
        if EMAIL_ENABLED:
            logger.info(f"Email notifications enabled, will send alerts to {TO_EMAIL}")
        else:
            logger.info("Email notifications disabled")

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
                        reason = f"Max restarts ({MAX_RESTARTS}) reached in {RESTART_WINDOW} seconds"
                        logger.error(reason)
                        self._send_stop_alert(f"{reason}, daemon stopping")
                        break

                    logger.info(f"Waiting {RESTART_DELAY} seconds before restart...")
                    time.sleep(RESTART_DELAY)

                    if not self.start_main_process():
                        reason = "Failed to restart main process"
                        logger.error(reason)
                        self._send_stop_alert(reason)
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