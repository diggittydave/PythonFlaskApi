# cdfService.database.exceptions.py
import sqlite3 as lite
from cdfService.services.appVariables import basedir
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.database.Definitions import exception_def


@cdfApiLogger.catch()
def cdf_exceptions(database_path: str):
    """cdfService.database.exceptions.cdf_exceptions\r\n
    This function updates CDF's based on the EXCEPTION key.\r\n
    Each CDF name is listed in the databse. \r\n
    These cdf's generally flag for a restriction because of a pattern match in the file name.\r\n
    EDI has determined these files do not need to be restricted and allow users to update without approval process.\r\n

    Args:
        database_path (str): File path of SQLITE database.
    """
    conn = lite.connect(database_path)
    exceptions = exception_def(database_path)
    cdfApiLogger.info(str(exceptions))
    for i in range(len(exceptions)):
        cdf = str(exceptions[i])
        cdfApiLogger.info(str(cdf))
        ddl = f"UPDATE CDF_DATA SET Is_Restricted = 'FALSE', Date_Updated = CURRENT_TIMESTAMP WHERE CDF_NAME = '{cdf}'"
        cdfApiLogger.info(ddl)
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(ddl)
                conn.commit()
                cdfApiLogger.info(f'updated {cdf}')
                cur.close()
        except (lite.Error, lite.Warning, Exception) as e:
                cdfApiLogger.error(str(e) + ' has occured with ' + str(ddl) + str(cdf), exc_info=True)
        except Exception as e:
            cdfApiLogger.error(str(e) + " FOUND IN " + str(cdf), exc_info=True)
    conn.close()
    cdfApiLogger.info("TABLE updated")


if __name__ == '__main__':
    cdf_exceptions(basedir)