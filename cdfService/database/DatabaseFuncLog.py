import os
from loguru import logger
import sys


#  logging setup
Cdf_Database = logger.bind()
Cdf_Database.add(r'./logs/Cdf_Database.log', backtrace=True, diagnose=True,
           rotation='20 MB', retention="45 days", compression="gz", enqueue=True)
Cdf_Database.add(sys.stdout, colorize=True, format="{time} {level} {message} ", level="INFO")
