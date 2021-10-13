#<
# cdfService.database.rebuild_flags
# !!!! LONG RUNNING MODULE !!!!!
# Rebuilds flags for all files in database.
# This function can be kicked off from the /filters/rebuild page.
# Requires users with the proper permissions as well as password verification.
# This module can also be run as a standalone module.
# Can be run on the server from inside python terminal.
# to run, navigate to the app folder, then invoke the venv.
# next run the command 'python -m cdfService.database.rebuild_flags'
# Will update all files with a 'SYSTEM' update user.
# Runs as a multi-threaded process, but still takes about 5 minutes due to number of updates being made.
# >
import sqlite3 as lite
import concurrent.futures
from cdfService.services.appVariables import basedir
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.database.Definitions import restricted_def, transportation_def, billing_def, om_def,\
                                            billing_exception_def, exception_def
from cdfService.email.email import send_rebuild_finish_message, send_rebuild_start_message


@cdfApiLogger.catch()
def rebuildFlags(cdf: str, billing: dict, om: dict, transportation: dict, restricted: dict, billing_Exception: dict,
                 exception_list: dict, current_user: str):
    """# cdfService.database.rebuild_flags.rebuildFlags\r\n
    Each thread tests only one cdf against the billing, om, trans. and restricted dictionaires.\r\n
    Updates the flags as needed.\r\n

    Args:
        cdf (str): Full file path of a cdf file.\r\n
        restricted (dict): Dictionary containing all definitions for the "restricted" flag.\r\n
        transportation (dict): Dictionary containing all definitions for the "transportation" flag.\r\n
        om (dict): Dictionary containing all definitions for the "om" flag.\r\n
        billing (dict): Dictionary containing all definitions for the "billing" flag.\r\n
        exception_list (dict):
        current_user (str):

    Returns:
        String of name completed to the log file.
    """
    is_transportation = 'FALSE'
    is_om = 'FALSE'
    is_billing = 'FALSE'
    is_restricted = 'FALSE'
    Requires_Approval = 'FALSE'
    cdfApiLogger.info(f'Setting Transportation flag for {cdf}')
    for j in range(len(transportation)):
        if transportation[j] in cdf:
            is_transportation = 'TRUE'
    cdfApiLogger.info(f'Setting OM flag for {cdf}')
    for k in range(len(om)):
        if om[k] in cdf:
            is_om = 'TRUE'
    cdfApiLogger.info(f'Setting Billing flag for {cdf}')
    for l in range(len(billing)):
        if billing[l] in cdf:
            is_billing = 'TRUE'
    cdfApiLogger.info(f'Setting Restriction flag for {cdf}')
    for m in range(len(restricted)):
        if restricted[m] in cdf:
            is_restricted = 'TRUE'
    cdfApiLogger.info(f'Checking {cdf} for exceptions')
    for n in range(len(billing_Exception)):
        if billing_Exception[n] in cdf:
            is_billing = 'FALSE'
    for o in range(len(exception_list)):
        if exception_list[o] in cdf:
            is_restricted = 'FALSE'
    if is_billing == 'TRUE':
        Requires_Approval = 'TRUE'
    cdfApiLogger.info(f'getting cdf contents for {cdf}')
    try:
        update_tuple = [is_transportation, is_om, is_billing, is_restricted, Requires_Approval, str(current_user), cdf]
        ddl = """UPDATE CDF_DATA
        SET Transportation = ?
        , OM = ?
        , Billing = ?
        , Is_Restricted = ?
        , Requires_Approval = ?
        , Date_Updated = CURRENT_TIMESTAMP
        , LAST_UPD_BY = ?
        WHERE CDF_NAME = ? """
        conn = lite.connect(basedir, timeout=10000)
        with conn:
            cdfApiLogger.info(f'{ddl, update_tuple}')
            cur = conn.cursor()
            cur.execute(ddl, update_tuple)
            cur.close()
            cdfApiLogger.info(f'REBUILD FLAGS ON {cdf}', exc_info=True)
    except Exception as e:
        cdfApiLogger.error(f'Exception occurred when updating {cdf}\r\n{e}', exc_info=True)
    conn.close
    return f'finished with {cdf}'
    

@cdfApiLogger.catch()
def get_cdfs(database_path: str):
    """cdfService.database.rebuild_flags.get_cdfs 
    Builds a dictionary with all cdf names.

    Args:
        database_path (str): Filepath of SQLITE Database.

    Returns:
        [type]: [description]
    """
    cdfs = {}
    conn = lite.connect(database_path)
    with conn:
        cur = conn.cursor()
        ddl = "Select CDF_NAME from 'CDF_DATA'"
        cur.execute(ddl)
        ddlarray = cur.fetchall()
        for i in range(len(ddlarray)):
            cdfs[i] = str(ddlarray[i][0])
    conn.close()
    cdfApiLogger.info("CREATED rebuild list.", exc_info=True)
    return cdfs


@cdfApiLogger.catch()
def startRebuildProcs(current_user: dict):
    """cdfService.database.rebuild_flags.startRebuildProcs 
    Handles building of thread pool and definition dictionaries.
    One thread is created for each cdf name found in the get_cdf's function.

    Args:
        current_user (str): Username passed in from the webapp. Used to update the cdf_data table.
    """
    cdf_array = []
    cdfs = get_cdfs(basedir)
    billingDef = billing_def(basedir)
    omDef = om_def(basedir)
    transportationDef = transportation_def(basedir)
    restrictedDef = restricted_def(basedir)
    billing_Exception = billing_exception_def(basedir)
    exception_list = exception_def(basedir)
    for i in cdfs:
        cdf_array.append(cdfs[i])
        print(cdfs[i])
    pool = concurrent.futures.ThreadPoolExecutor(4)
    print('starting threads')
    results = [pool.submit(rebuildFlags, cdf, billingDef, omDef, transportationDef, restrictedDef, billing_Exception,
                           exception_list, current_user['user_data']['USERNAME']) for cdf in cdf_array]
    concurrent.futures.wait(results, timeout=None, return_when=results.ALL_COMPLETED)

    
#<
# This module can be run as a standalone module.
# Will update all files with a 'SYSTEM' update user.
#>
if __name__ == '__main__':
    current_user = {"user_data": {"Username": "SYSTEM"}}
    startRebuildProcs(current_user)
