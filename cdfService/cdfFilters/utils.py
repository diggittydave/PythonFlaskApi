import concurrent.futures
from cdfService.database.Definitions import (restricted_def, transportation_def, billing_def, om_def,\
    billing_exception_def, exception_def)
import sqlite3 as lite
from cdfService.cdfFilters.schemas import CDF_UPDATE_FILTERS, FiltersSchema
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.services.appVariables import basedir
from cdfService.email.email import send_general_error_email, send_rebuild_finish_message, send_rebuild_start_message
import re
import io
import csv
import requests


@cdfApiLogger.catch()
def returnFilters():
    """
    Pulls all filters stored in database.\r\n
    The list is only accessible via the web interface\r\n
    The return object is formatted by the cdfService.templates.filters.htlm template.\r\n

    Returns:
        filters (dict): Dictionary containing the regex strings and their associated flag.
    """
    cdfApiLogger.info("Filters requested")
    try:
        filters = CDF_UPDATE_FILTERS.query.all()
        filters = FiltersSchema.dump(filters)
        return filters
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'Error querying filters. \r\n {e}')


@cdfApiLogger.catch()
def download_filters():
    conn = lite.connect(basedir)
    si = io.StringIO()
    cw = csv.writer(si)
    try:
        with conn:
            curr = conn.cursor()
            ddl = """SELECT * FROM CDF_UPDATE_FILTERS ORDER BY RESTRICTION"""
            curr.execute(ddl)
            filters = curr.fetchall()
            cdfApiLogger.info(f'{filters}')
            cw.writerow(('RESTRICTION', 'SERVICE', 'ID_KEY', 'ADDED_BY', 'DATE_ADDED'))
            for row in filters:
                cw.writerow(row)
            cdfApiLogger.info(f'{cw}')
            yield si.getvalue()
            si.seek(0)
            si.truncate(0)
    except Exception as e:
        send_general_error_email(e)


@cdfApiLogger.catch()
def returnFiltersrRestriction(restriction:str):
    """
    Pulls a list of filters based on their restriction flag stored in database.\r\n
    The list is only accessible via the web interface.\r\n
    The return object is formatted by the cdfService.templates.filters.htlm template.\r\n

    Returns:
        filters (dict): Dictionary containing the regex strings and their associated flag.
    """
    cdfApiLogger.info("Filters requested")
    try:
        filters = CDF_UPDATE_FILTERS.query.filter(CDF_UPDATE_FILTERS.SERVICE.like('%' + restriction + '%')).all()
        filter_list = FiltersSchema.dump(filters)
        return filter_list
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'Error querying filters. \r\n {e}')


@cdfApiLogger.catch()
def rebuildFlags(cdf: str, billing: dict, om: dict, transportation: dict, restricted: dict, restricted_exception: dict,
                 billing_Exception: dict, current_user):
    """
    Each thread tests only one cdf against the billing, om, trans. and restricted dictionaires.\r\n
    Updates the flags as needed.\r\n

    Args:
        cdf (str): Full file path of a cdf file.\r\n
        restricted (dict): Dictionary containing all definitions for the "restricted" flag.\r\n
        transportation (dict): Dictionary containing all definitions for the "transportation" flag.\r\n
        om (dict): Dictionary containing all definitions for the "om" flag.\r\n
        billing (dict): Dictionary containing all definitions for the "billing" flag.\r\n
        billing_exception(dict): Dictionary containing all Billing exceptions.
    Returns:
        String of name completed to the log file.
    """
    is_transportation = 'FALSE'
    is_om = 'FALSE'
    is_billing = 'FALSE'
    is_restricted = 'FALSE'
    requires_approval = 'FALSE'
    for j in range(len(transportation)):
        test = str(transportation[j])
        if test in cdf:
            if re.search(f"{test}", cdf):
                is_transportation = 'TRUE'
    for k in range(len(om)):
        test = om[k]
        if test in cdf:
            if re.search(f"{test}", cdf):
                is_om = 'TRUE'
    for l in range(len(billing)):
        test = str(billing[l])
        if test in cdf:
            if re.search(f"{test}", cdf):
                is_billing = 'TRUE'
    for m in range(len(restricted)):
        test = str(restricted[m])
        if f'{test}' not in cdf:
            m += 1
        if re.search(f"{test}", cdf):
            is_restricted = 'TRUE'
    for o in range(len(restricted_exception)):
        test = restricted_exception[o]
        if test in cdf:
            is_restricted = 'FALSE'
    for n in range(len(billing_Exception)):
        if billing_Exception[n] in cdf:
            is_billing = 'FALSE'
    if is_billing == 'TRUE':
        requires_approval = 'TRUE'
    try:
        update_tuple = [is_transportation, is_om, is_billing, is_restricted, requires_approval, str(current_user), cdf]
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
        send_general_error_email(e)
        cdfApiLogger.error(f'Exception occurred when updating {cdf}\r\n{e}', exc_info=True)
    conn.close
    return f'finished with {cdf}'


@cdfApiLogger.catch()
def get_cdfs(database_path: str):
    """
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
def startRebuildProcs(current_user):
    """
    Handles building of thread pool and definition dictionaries.
    One thread is created for each cdf name found in the get_cdf's function.

    Args:
        current_user (str): Username passed in from the webapp. Used to update the cdf_data table.
        current_app (app object)
    """
    user_email = current_user.email
    send_rebuild_start_message(user=user_email)
    cdf_array = []
    cdfs = get_cdfs(basedir)
    billingDef = billing_def(basedir)
    omDef = om_def(basedir)
    transportationDef = transportation_def(basedir)
    restrictedDef = restricted_def(basedir)
    restricted_exception = exception_def(basedir)
    billing_exception = billing_exception_def(basedir)
    for i in cdfs:
        cdf_array.append(cdfs[i])
        print(cdfs[i])
    pool = concurrent.futures.ThreadPoolExecutor(4)
    print('starting threads')
    results = [pool.submit(rebuildFlags, cdf, billingDef, omDef, transportationDef, restrictedDef,
                           restricted_exception, billing_exception,
                           current_user['user_data']['USERNAME']) for cdf in cdf_array]
    for result in concurrent.futures.as_completed(results):
        cdfApiLogger.info(result.result())


# <
# This module can be run as a standalone module.
# Will update all files with a 'SYSTEM' update user.
# >
if __name__ == '__main__':
    cdf = "customzone_7512_configuration.cdf"
    billingDef = billing_def(basedir)
    omDef = om_def(basedir)
    transportationDef = transportation_def(basedir)
    restrictedDef = restricted_def(basedir)
    billing_exception = billing_exception_def(basedir)
    rebuildFlags(cdf, billingDef, omDef, transportationDef, restrictedDef, billing_exception, 'chq-davidwe')