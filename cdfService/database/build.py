import sqlite3 as lite
import concurrent.futures
import subprocess
import time
from cdfService.services.appVariables import basedir
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.database.Definitions import om_def, transportation_def, billing_def, restricted_def, read_file
import sys
import re


"""cdfService.database.build\r\n
    This is a full table rebuild script. \r\n
    This python module to build or rebuild the CDF_DATA table. \r\n
    Only use this script when initializing a new DB or when rebuilding after a recovery/renewal of the DB. \r\n
"""


@cdfApiLogger.catch()
def cdf_names():
    """cdfService.database.build.cdf_names\r\n
    Gets a list of all cdfs in the repository.
    The finder.sh script is a simple built 'find' command that returns the full path of all cdf's contained on the server "find $(pwd) -name '*.cdf'"
    It is built as a callable script because using the subprocess module to run the find command could not return the needed data.

    Returns:
        tuple: tuple containing the full file path of all cdf files found in the repository directory.
    """
    if 'win' in sys.platform:
        files = subprocess.Popen('finder.bat', stdout=subprocess.PIPE).communicate()
    else:
        cdfApiLogger.info(f'starting finder script')
        files = subprocess.Popen(r'./cdfService/database/finder.sh', stdout=subprocess.PIPE).communicate()
    return files


@cdfApiLogger.catch()
def file_action(file: str, restricted: dict, transportation: dict, om: dict, billing: dict, billing_exception: dict, restricted_exception: dict):
    """cdfService.database.build.file_action\r\n
    Starts all sub actions on the given cdf.
    Returns the name of the cdf to the primary process as a result.

    Args:
        file (str): Full file path of a cdf file.
        restricted (dict): Dictionary containing all definitions for the "restricted" flag.
        transportation (dict): Dictionary containing all definitions for the "transportation" flag.
        om (dict): Dictionary containing all definitions for the "om" flag.
        billing (dict): Dictionary containing all definitions for the "billing" flag.

    Returns:
        cdf_array[0] (str): Name of the cdf.
    """
    t1 = time.perf_counter()
    itemPath = file
    data = itemPath.split(r'/')
    for i in range(len(data)):
        if data[i].endswith(".cdf"):
            item = data[i]
            cdfApiLogger.info(f'{item} split from path, adding to array.')
            cdf_array = ([item, itemPath])
            cdfApiLogger.info(f'starting flag identification for {cdf_array[0]}')
            cdf_array = cdf_restrictions(cdf_array, restricted, transportation, om, billing, billing_exception, restricted_exception)
    t2 = time.perf_counter()
    cdfApiLogger.info(f' this prcess took {t2 - t1} second(s)')
    return cdf_array[0]   



#<
# cdfService.database.build.insert_cdf_data
# This function uses the passed cdf array to build an sql insert statement, then executes the insert.
# >
@cdfApiLogger.catch()
def insert_cdf_data(cdf_array: dict):
    conn = lite.connect(basedir, timeout=10)
    try:
        cdf = cdf_array[0]
        path = cdf_array[1]
        is_transportation = cdf_array[2]
        is_om = cdf_array[3]
        is_billing = cdf_array[4]
        is_restricted = cdf_array[5]
        requires_approval = cdf_array[6]
        header = cdf_array[7]
        number = cdf_array[8]
        blob = cdf_array[9]
        last_upd_by = f'SYSTEM'
        ddl1 = """INSERT INTO 'CDF_DATA' (
        'CDF_NAME',
        'CDF_Path',
        'Transportation',
        'OM',
        'Billing',
        'Is_Restricted',
        'HEADER',
        'NUMBER_OF_COLUMNS',
        'FILE_CONTENTS',
        'LAST_UPD_BY',
        'Requires_Approval',
        'Date_Updated')
        values ( ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        CURRENT_TIMESTAMP)"""
        insert_tuple = ([cdf, path, is_transportation, is_om, is_billing, is_restricted, str(header), number, blob,
                         last_upd_by, requires_approval])
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(ddl1, insert_tuple)
                cdfApiLogger.info(f'ADDED {cdf} TO THE DATABASE')
                cur.close
        except (lite.Error, lite.Warning) as e:
            cdfApiLogger.error(e, exc_info=True)
    except Exception as e:
            cdfApiLogger.error(str(e) + " FOUND IN " + str(cdf), exc_info=True)
    conn.close()


@cdfApiLogger.catch()
def cdf_restrictions(cdf_array: dict, restricted: dict, transportation: dict, om: dict, billing: dict,
                     billing_exception: dict, restricted_exception: dict):
    """cdfService.database.build.cdf_restrictions\r\n
    This function tests the cdf name against the set of restion dictionaires and sets the corresponding flag value in an array.
    The array is then passed to the insert function.

    Args:
        cdf_array (dict): Contains full file path and file name.
        restricted (dict): Dictionary containing all definitions for the "restricted" flag.
        transportation (dict): Dictionary containing all definitions for the "transportation" flag.
        om (dict): Dictionary containing all definitions for the "om" flag.
        billing (dict): Dictionary containing all definitions for the "billing" flag.
        billing_exception(dict): Dictionary containing exceptions to remove the billing flag.
        restricted_exception(dict): Dictionary containing exceptions to remove the is_restricted flag.

    Returns:
        dict: Dictionary containing full dataset and flags for the cdf.
    """
    file = str(cdf_array[0])
    path = str(cdf_array[1])
    is_transportation = 'FALSE'
    is_om = 'FALSE'
    is_billing = 'FALSE'
    is_restricted = 'FALSE'
    Requires_Approval = 'FALSE'
    cdfApiLogger.info(f'Setting Transportation flag for {file}')
    for j in range(len(transportation)):
        test = str(transportation[j])
        if test in file:
            if re.search(f"{test}", file):
                is_transportation = 'TRUE'
    for k in range(len(om)):
        test = str(om[k])
        if test in file:
            if re.search(f"{test}", file):
                is_om = 'TRUE'
    for l in range(len(billing)):
        test = str(billing[l])
        if test in file:
            if re.search(f"{test}", file):
                is_billing = 'TRUE'
    for m in range(len(restricted)):
        test = str(restricted[m])
        if f'{test}' not in file:
            m += 1
        if re.search(f'{test}', file):
            is_restricted = 'TRUE'
    for o in range(len(restricted_exception)):
        test = restricted_exception[o]
        if test in file:
            is_restricted = 'FALSE'
    for n in range(len(billing_exception)):
        test = billing_exception[n]
        if test in file:
            is_billing = 'FALSE'
    if is_billing == 'TRUE':
        Requires_Approval = 'TRUE'
    cdfApiLogger.info(f'Restricted flag for {file}, is now is_restricted = {is_restricted}')
    cdfApiLogger.info(f'getting file contents for {file}')
    try:
        read = open(str(path), 'rb')
        header = read.readline()
        parsed_header = str(header).split(',')
        number = len(parsed_header)
        cdf_array = ([file, path, is_transportation, is_om, is_billing, is_restricted, Requires_Approval,
                      header, number, read_file(path)])
        cdfApiLogger.info(f'File contents set for {file}')
    except Exception as e:
        cdfApiLogger.error(f'Exception occurred when reading {file}\r\n{e}', exc_info=True)
    cdfApiLogger.info(f'Inserting {file} into the table.')
    insert_cdf_data(cdf_array)
    return cdf_array


@cdfApiLogger.catch()
def startTableBuild():
    """cdfService.database.build.startTableBuild
    Primary function. 
    Creates a list of cdfs
    Creates the restrictions dictionaries based on the functions called from cdfservice.database.Definitions
    Passes each cdf to a subthread along with all the restrictions dictionaires.
    Each thread executes all other actions on the cdf.
    This setup was used to curtail a memory consumption issue
    """
    t3 = time.perf_counter()
    pool = concurrent.futures.ThreadPoolExecutor(4)
    cdfs=[]
    restricted = restricted_def(basedir)
    transportation = transportation_def(basedir)
    om = om_def(basedir)
    billing = billing_def(basedir)
    billing_exception = billing_exception_def(basedir)
    restricted_exception = exception_def(basedir)
    files = cdf_names()
    files = str(files[0])
    files = files.split(r'\n')
    for file in files:
        if file.endswith('.cdf'):
            print(file)
            cdfs.append(file)
    cdfApiLogger.info(str(files))
    results = [pool.submit(file_action, cdf, restricted, transportation, om, billing, billing_exception, restricted_exception) for cdf in cdfs]
    t4 = time.perf_counter()
    print(f'this operation took {t4-t3} second(s)')
    return results


@cdfApiLogger.catch()
def exception_def(database_path: str):
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
            ddl = "Select restriction from 'CDF_UPDATE_FILTERS' WHERE SERVICE = 'EXCEPTION'"
            cur.execute(ddl)
            ddlarray = cur.fetchall()
            cur.close()
            for i in range(len(ddlarray)):
                exception[i] = str(ddlarray[i][0])
        conn.close()
        cdfApiLogger.info("CREATED EXCEPTIONS list.")
    except (lite.Error, lite.Warning) as e:
            cdfApiLogger.error(e, exc_info=True)
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
def cdf_exceptions(database_path: str):
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


def billing_exceptions(database_path: str):
    conn = lite.connect(database_path)
    exceptions = billing_exception_def(database_path)
    cdfApiLogger.info(str(exceptions))
    for i in range(len(exceptions)):
        cdf = str(exceptions[i])
        cdfApiLogger.info(str(cdf))
        ddl = f"UPDATE CDF_DATA SET Billing = 'FALSE', Date_Updated = CURRENT_TIMESTAMP WHERE CDF_NAME LIKE '%{cdf}%'"
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
    t8 = time.perf_counter()
    results = startTableBuild()
    print(results)
    t9 = time.perf_counter()
    cdfApiLogger.info(f'Rebuilding the database took {t9 - t8} seconds')
