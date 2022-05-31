import logging
from logger.logger import *

logging.basicConfig(
    filename="./logging.txt",
    level=logging.DEBUG,
    format="[%(levelname)s] %(asctime)s : %(filename)s:%(lineno)d >> %(message)s"
)
