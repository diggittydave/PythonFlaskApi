from loguru import logger
import sys




cdfApiLogger = logger.bind()
#  separate different log modules to respective files.
#  cdf api logs
# cdfApiLogger.add(r'./logs/CDF_API_Calls.log', backtrace=True, diagnose=True,
#                 rotation='20 MB', retention="45 days", compression="gz", enqueue=True)

def user_filter(record):
    if (str(record['name']) == 'cdfService.users.utils') or (str(record['name']) == 'cdfService.users.routes'):
        return record


def api_filter(record):
    if (str(record['name']) == 'cdfService.cdfApi.utils') or (str(record['name']) == 'cdfService.cdfApi.routes'):
        return record


def webapp_filters(record):
    if (str(record['name']) == 'cdfService.cdfData.utils') or (str(record['name']) == 'cdfService.cdfData.routes') or \
            (str(record['name']) == 'cdfService.cdfFilters.utils') or \
            (str(record['name']) == 'cdfService.cdfFilters.routes') or (str(record['name']) == 'cdfService.main.utils')\
            or (str(record['name']) == 'cdfService.main.routes'):
        return record


def database_filters(record):
    if (str(record['name']) == 'cdfService.database.build') or (str(record['name']) == 'cdfService.database.rebuild_flags'):
        return record


#  cdf webapp logs
cdfApiLogger.add(r'./logs/Cdf_Webapp.log', backtrace=True, diagnose=True, filter=webapp_filters,
                 rotation='20 MB', retention="45 days", compression="gz", enqueue=True)

cdfApiLogger.add(r'./logs/Cdf_Api.log', backtrace=True, diagnose=True, filter=api_filter,
                 rotation='20 MB', retention="45 days", compression="gz", enqueue=True)

cdfApiLogger.add(r'./logs/Cdf_user.log', backtrace=True, diagnose=True, filter=user_filter,
                 rotation='20 MB', retention="45 days", compression="gz", enqueue=True)

cdfApiLogger.add(r'./logs/Cdf_Database_Update.log', backtrace=True, diagnose=True, filter=database_filters,
                 rotation='20 MB', retention="45 days", compression="gz", enqueue=True)

cdfApiLogger.add(sys.stdout, colorize=True, format="{time} {level} {name} {process} {message} ", level="TRACE")
cdfApiLogger.add(sys.stdout, colorize=True, format="{time} {level} {name} {process} {message} ", level="DEBUG")
cdfApiLogger.add(sys.stdout, colorize=True, format="{time} {level} {name} {process} {message} ", level="INFO")
cdfApiLogger.add(sys.stdout, colorize=True, format="{time} {level} {name} {process} {message} ", level="SUCCESS")
cdfApiLogger.add(sys.stdout, colorize=True, format="{time} {level} {name} {process} {message} ", level="WARNING")
cdfApiLogger.add(sys.stdout, colorize=True, format="{time} {level} {name} {process} {message} ", level="ERROR")
cdfApiLogger.add(sys.stdout, colorize=True, format="{time} {level} {name} {process} {message} ", level="CRITICAL")
