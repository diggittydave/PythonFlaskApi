import sqlite3 as lite
from cdfService.svnWorker.svnProcesses.SvnWorkerLogging import SVN_Worker


@SVN_Worker.catch()
def restricted_def(database_path: str):
    """
    Defines the is_restricted criteria.
    Keys are stored in the CDF-UPDATE-FILTERS table
    Keys are strings used in pattern matching against the cdf name.
    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "restricted" flag.
    """
    restricted = {}
    conn = lite.connect(database_path)
    restrictions = []
    try:
            with conn:
                cur = conn.cursor()
                ddl = "SELECT restriction, SERVICE FROM 'CDF_UPDATE_FILTERS' WHERE SERVICE = 'RESTRICTED'"
                cur.execute(ddl)
                ddlarray = cur.fetchall()
                cur.close()
                for i in range(len(ddlarray)):
                    restricted[i] = str(ddlarray[i][0])
            conn.close()
            SVN_Worker.info("CREATED RESTRICTED DEFINITIONS DICTIONARY.")
    except (lite.Error, lite.Warning) as e:
        SVN_Worker.error(e, exc_info=True)
    return restricted


@SVN_Worker.catch()
def billing_def(database_path: str):
    """
    defines the Billing affected services criteria.
    Keys are stored in CDF-UPDATE-FILTTERS table.
    Keys are strings used in pattern matching against the cdf name.

    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "billing" flag.
    """
    billing = {}
    conn = lite.connect(database_path)
    try:
        with conn:
            cur = conn.cursor()
            ddl = "SELECT restriction, SERVICE FROM 'CDF_UPDATE_FILTERS' WHERE SERVICE = 'BILLING'"
            cur.execute(ddl)
            ddlarray = cur.fetchall()
            cur.close()
            for i in range(len(ddlarray)):
                billing[i] = str(ddlarray[i][0])
        conn.close()
        SVN_Worker.info("CREATED BILLING DEFINITIONS DICTIONARY.")
    except (lite.Error, lite.Warning) as e:
        SVN_Worker.error(e, exc_info=True)
    return billing


@SVN_Worker.catch()
def transportation_def(database_path: str):
    """
    defines the Transportation affected services criteria.
    Keys are stored in CDF-UPDATE-FILTTERS table.
    Keys are strings used in pattern matching against the cdf name.

    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "transportation" flag.
    """
    transportation = {}
    conn = lite.connect(database_path)
    try:
        with conn:
            cur = conn.cursor()
            ddl = "SELECT restriction, SERVICE FROM 'CDF_UPDATE_FILTERS' WHERE SERVICE = 'TRANSPORTATION'"
            cur.execute(ddl)
            ddlarray = cur.fetchall()
            cur.close()
            for i in range(len(ddlarray)):
                transportation[i] = str(ddlarray[i][0])
        conn.close()
        SVN_Worker.info("CREATED TRANSPORTATION DEFINITIONS DICTIONARY.")
    except (lite.Error, lite.Warning) as e:
        SVN_Worker.error(e, exc_info=True)
    return transportation 


@SVN_Worker.catch()
def om_def(database_path: str):
    """
    Defines the OM affected services criteria.\r\n
    Keys are stored in CDF-UPDATE-FILTTERS table.\r\n
    Keys are strings used in pattern matching against the cdf name.\r\n

    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "om" flag.
    """
    om = {}
    conn = lite.connect(database_path)
    try:
        with conn:
            cur = conn.cursor()
            ddl = "Select restriction, SERVICE from 'CDF_UPDATE_FILTERS' WHERE SERVICE = 'OM'"
            cur.execute(ddl)
            ddlarray = cur.fetchall()
            cur.close()
            for i in range(len(ddlarray)):
                om[i] = str(ddlarray[i][0])
        conn.close()
        SVN_Worker.info("CREATED ORDER MANAGEMENT DEFINITIONS DICTIONARY.")
    except (lite.Error, lite.Warning) as e:
        SVN_Worker.error(e, exc_info=True)
    return om


@SVN_Worker.catch()
def exception_def(database_path: str):
    """
    Gets a list of all exception cdf names.\r\n
    Exception cdfs are defined as those that may contain strings which match other flags, but are not actually restricted.\r\n

    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "Exceptions" to the "restricted" flag.
    """
    exception = {}
    conn = lite.connect(database_path)
    try:
        with conn:
            cur = conn.cursor()
            ddl = "Select restriction from 'CDF_UPDATE_FILTERS' WHERE SERVICE = 'EXCEPTION'"
            cur.execute(ddl)
            ddlarray = cur.fetchall()
            cur.close()
            for i in range(len(ddlarray)):
                exception[i] = str(ddlarray[i][0])
        conn.close()
        SVN_Worker.info("CREATED EXCEPTIONS list.")
    except (lite.Error, lite.Warning) as e:
        SVN_Worker.error(e, exc_info=True)
    return exception


@SVN_Worker.catch()
def billing_exception_def(database_path: str):
    """
    Gets a list of all exception cdf names.\r\n
    Exception cdfs are defined as those that may contain strings which match other flags, but are not actually restricted.\r\n

    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "Exceptions" to the "restricted" flag.
    """
    exception = {}
    conn = lite.connect(database_path)
    try:
        with conn:
            cur = conn.cursor()
            ddl = "Select restriction from 'CDF_UPDATE_FILTERS' WHERE SERVICE = 'BILLING_EXCEPTION'"
            cur.execute(ddl)
            ddlarray = cur.fetchall()
            cur.close()
            for i in range(len(ddlarray)):
                exception[i] = str(ddlarray[i][0])
        conn.close()
        SVN_Worker.info("CREATED BILLING EXCEPTIONS list.")
    except (lite.Error, lite.Warning) as e:
        SVN_Worker.error(e, exc_info=True)
    return exception


@SVN_Worker.catch()
# change the is_restricted flag for files matching the exceptions list.
def cdf_exceptions(database_path: str):
    """change the is_restricted flag for files matching the exceptions list.

    Args:
        database_path (str): [description]
    """
    conn = lite.connect(database_path)
    exceptions = exception_def(database_path)
    SVN_Worker.info(str(exceptions))
    for i in range(len(exceptions)):
        cdf = str(exceptions[i])
        SVN_Worker.info(str(cdf))
        ddl = f"UPDATE CDF_DATA SET Is_Restricted = 'FALSE', Date_Updated = CURRENT_TIMESTAMP WHERE CDF_NAME = '{cdf}'"
        SVN_Worker.info(ddl)
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(ddl)
                conn.commit()
                SVN_Worker.info(f'updated {cdf}')
                cur.close()
        except (lite.Error, lite.Warning, Exception) as e:
                SVN_Worker.error(str(e) + ' has occured with ' + str(ddl) + str(cdf), exc_info=True)
        except Exception as e:
            SVN_Worker.error(str(e) + " FOUND IN " + str(cdf), exc_info=True)
    conn.close()
    SVN_Worker.info("TABLE updated")