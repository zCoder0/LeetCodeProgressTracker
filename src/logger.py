import logging
import os 
from src.config import Settings
from datetime import datetime


LOG_FILE_NAME = f"{datetime.now().strftime('%d-%m-%Y-%H-%M')}.log"

LOG_FULL_PATH = os.path.join(Settings.LOG_DIR, LOG_FILE_NAME)

os.makedirs(Settings.LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FULL_PATH,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)