import os
from loguru import logger
import sys


#  logging setup
SVN_Worker = logger.bind()
SVN_Worker.add(r'./logs/SVN_Worker.log', backtrace=True, diagnose=True,
           rotation='20 MB', retention="45 days", compression="gz", enqueue=True)
SVN_Worker.add(sys.stdout, colorize=True, format="{time} {level} {message} ", level="INFO")