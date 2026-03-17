import os
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
if not os.path.exists('logs'):
    os.mkdir('logs')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
