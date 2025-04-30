import logging
import os
from datetime import datetime

from src.constants import LOG_FILE

class TruncateFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', max_length=500):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.max_length = max_length

    def format(self, record):
        msg = super().format(record)
        if len(msg) > self.max_length:
            msg = msg[:self.max_length - 3] + ".."
        return msg

def setup_logging():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'a'):
            pass

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"{' NEW EXECUTION ':=^80}\n")
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S'): ^80}\n")
        f.write("=" * 80 + "\n\n")

    log_format = f"[%(levelname)s] <%(filename)s> (%(asctime)s) %(message)s"
    date_format = "%H:%M:%S"

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(TruncateFormatter(fmt=log_format, datefmt=date_format, max_length=200))

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler]
    )

    logging.getLogger("requests").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("selenium").setLevel(logging.CRITICAL)
    logging.getLogger("webdriver_manager").setLevel(logging.CRITICAL)
    logging.getLogger("connectionpool").setLevel(logging.CRITICAL)
    logging.getLogger("driver_finder").setLevel(logging.CRITICAL)
    logging.getLogger("service").setLevel(logging.CRITICAL)
    logging.getLogger("remote_connection").setLevel(logging.CRITICAL)