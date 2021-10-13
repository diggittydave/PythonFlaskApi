#<
# cdfService.database.Definitions
# provides definition dictionaries for the services and restrictions.
# Also provides the dictionary containing all CDFS when running the cdfService.database.build module
#>

import sqlite3 as lite
from cdfService.services.appVariables import basedir, repo_path
from cdfService.logging.cdfAPILogging import cdfApiLogger
import os

billing = {}
om = {}
transportation = {}
restricted = {}
exception = {}


@cdfApiLogger.catch()
def restricted_def(database_path: str):
    """cdfService.database.Definitions.restricted_def\r\n
    Defines the is_restricted criteria.
    Keys are stored in the CDF-UPDATE-FILTERS table
    Keys are strings used in pattern matching against the cdf name.
    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "restricted" flag.
    """
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
    except (lite.Error, lite.Warning) as e:
            cdfApiLogger.error(e, exc_info=True)
    return restricted


@cdfApiLogger.catch()
def billing_def(database_path: str):
    """cdfService.database.Definitions.billing_def\r\n
    defines the Billing affected services criteria.
    Keys are stored in CDF-UPDATE-FILTTERS table.
    Keys are strings used in pattern matching against the cdf name.

    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "billing" flag.
    """
    i = 0
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
    except (lite.Error, lite.Warning) as e:
            cdfApiLogger.error(e, exc_info=True)
    return billing


@cdfApiLogger.catch()
def transportation_def(database_path: str):  
    """cdfService.database.Definitions.transportation_def\r\n
    defines the Transportation affected services criteria.
    Keys are stored in CDF-UPDATE-FILTTERS table.
    Keys are strings used in pattern matching against the cdf name.

    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "transportation" flag.
    """
    i = 0
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
    except (lite.Error, lite.Warning) as e:
            cdfApiLogger.error(e, exc_info=True)
    return transportation 


@cdfApiLogger.catch()
def om_def(database_path: str):
    """cdfService.database.Definitions.om_def\r\n
    Defines the OM affected services criteria.\r\n
    Keys are stored in CDF-UPDATE-FILTTERS table.\r\n
    Keys are strings used in pattern matching against the cdf name.\r\n

    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "om" flag.
    """
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
    except (lite.Error, lite.Warning) as e:
            cdfApiLogger.error(e, exc_info=True)
    return om


@cdfApiLogger.catch()
def cdf_names(repo_path):
    """cdfService.database.Definitions.cdf_names\r\n
    Gets a list of all cdfs in the repository.\r\n
    This function was replaced by a callable bash script.\r\n

    Args:
        repo_path (str): String value of the full directory path to the local CDF repository.

    Returns:
        dict: dictionary containing a list of cdf files and their name.
    """
    cdf_array = {}
    i = 0
    filecounter = 0
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.cdf'):
                filecounter += 1
    cdfApiLogger.info(str(filecounter) + ' CDF Files found in the repository directory.')
    for dirpath, subdirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".cdf"):
                    item = file
                    itemPath = str(os.path.join(dirpath, file))
                    cdf_array[i] = ([item, itemPath])
                    i += 1
                    cdfApiLogger.info("found " + item, exc_info=True)
    return cdf_array


@cdfApiLogger.catch()
def exception_def(database_path: str):
    """cdfService.database.Definitions.exception_def\r\n
    Gets a list of all exception cdf names.\r\n
    Exception cdfs are defined as those that may contain strings which match other flags, but are not actually restricted.\r\n

    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing the unique strings used to identify the "Exceptions" to the "restricted" flag.
    """
    conn = lite.connect(database_path)
    with conn:
        cur = conn.cursor()
        ddl = "Select restriction from 'CDF_UPDATE_FILTERS' WHERE SERVICE = 'EXCEPTION'"
        cur.execute(ddl)
        ddlarray = cur.fetchall()
        cur.close()
        for i in range(len(ddlarray)):
            exception[i] = str(ddlarray[i][0])
    conn.close()
    return exception


@cdfApiLogger.catch()
def billing_exception_def(database_path: str):
    """cdfService.svnServices.svnUpdate.exception_def\r\n
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
        cdfApiLogger.info("CREATED EXCEPTIONS list.", exc_info=True)
    except (lite.Error, lite.Warning) as e:
            cdfApiLogger.error(e, exc_info=True)
    return exception


@cdfApiLogger.catch()
def cdf_array_def(database_path: str):
    """cdfService.database.Definitions.cdf_array_def\r\n
    defines the is_restricted criteria. \r\n
    Keys are stored in the CDF-UPDATE-FILTERS table.\r\n
    Keys are strings used in pattern matching against the cdf name.\r\n

    Args:
        database_path (str): Filepath to SQLITE database.

    Returns:
        dict: Dictionary containing all CDF names.
    """
    conn = lite.connect(database_path)
    cdfs = []
    with conn:
        cur = conn.cursor()
        ddl = "SELECT CDF_NAME FROM 'CDF_DATA'"
        cur.execute(ddl)
        ddlarray = cur.fetchall()
        for i in range(len(ddlarray)):
            cdfs[i] = str(ddlarray[i][0])
    conn.close()
    return cdfs


@cdfApiLogger.catch()
def read_file(filepath):
    """cdfService.database.Definitions.read_file
    Function to open and read a file as a binary object.
    Returns the entire contents of a file as a singular object.
    The object is stored in the database and is used in api responses.

    Args:
        filepath (str): Filepath to CDF to be read.

    Returns:
        blob: binary blob representative of the contents of the CDF.
    """
    try:
        with open(filepath, 'rb') as f:
            blob = f.read()
        return blob
    except Exception as e:
        cdfApiLogger.error("Exception occured when reading " + str(filepath), exc_info=True)
        return "Error in File"


if __name__ == "__main__":
    om = om_def(basedir)
    transportation = transportation_def(basedir)
    billing = billing_def(basedir)
    restricted = restricted_def(basedir)
    cdf_array = cdf_names(repo_path)
    print(om)
    print(transportation)
    print(billing)
    print(restricted)
