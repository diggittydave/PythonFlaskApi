#<
# cdfService.svnServices.svnUpdate
# This function serves as a worker process.
# The process will loop every 30 seconds checking svn for a new version and updates.
# Pulls all svn updates and updates the database with the new information.
# The function runs a manual garbage collection in order to keep the memory useage as low as possible.
# >
import time
import sqlite3 as lite
import subprocess
from cdfService.services.appVariables import basedir
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.config import ConfigClass
import gc
from cdfService.svnWorker.svnProcesses.dbActions import check_files, update_cdf_data, insert_cdf_data, remove_file
from cdfService.svnWorker.svnProcesses.fileActions import find, get_updated_file, read_file
from cdfService.svnWorker.svnProcesses.flagDefinitions import restricted_def, transportation_def, om_def, billing_def, \
    billing_exception_def, exception_def
from cdfService.email.email import send_general_error_email


svn_folders = ConfigClass.svn_folders


@cdfApiLogger.catch()
def update(svn_folders: dict):
    """
    initiates the update function from svn.\r\n
    parses the current local revision, returns the local revision number and the global revision number.\r\n
    also provides the list of files being updated, added or removed.\r\n

    Args:
        svn_folders (dict): file path dictionary for the svn repositories on the server.

    Returns:
        content (dict): A dictionary containing file names being updated, added, or deleted.
    """
    content = []
    # update the GEN repo
    for i in range(len(svn_folders)):
        update_data = subprocess.Popen(['svn', 'update', str(svn_folders[i])], stdout=subprocess.PIPE).communicate()
        update_data = str(update_data[0]).split('\\n')
        for j in range(len(update_data)):
            content.append(update_data[j])
    return content  # return the list to update back to the parseUpdate function

@cdfApiLogger.catch()
def parseUpdate(svn_folders: dict):
    """
    parses the updated, added or removed files from the update.\r\n
    runs the updates, or inserts, or delete/copy actions as needed.\r\n

    Args:
        svn_folders (dict): [description]

    Returns:
        [type]: [description]
    """
    i = 0
    j = 0
    l = 0
    m = 0
    update_files = {}  # create empty dictionary with files to add/update each run.
    new_files = {}
    removed = {}  # create empty dictionary with files to remove each run.
    content = update(svn_folders)  # dictionary returned from update function above.
    for i in range(len(content)):
        item = str(content[i])
        action_tag = item[0]
        if action_tag == 'A':
            file = content[i]
            file = str(file).split("/")  # split dictionary entry based on return of file path
            for k in range(len(file)):
                if '.cdf' in file[k]:  # searches specifically for .cdf files
                    new_files[j] = str(file[k])  # adds the cdf name to the files dictionary.
                    i = i + 1  # upward to the next entry in the content dictionary.
                    j = j + 1  # increases the key count in the files dictionary.
        if action_tag == 'U':
            file = content[i]
            file = str(file).split("/")  # split dictionary entry based on return of file path
            for k in range(len(file)):
                if '.cdf' in file[k]:  # searches specifically for .cdf files
                    update_files[m] = str(file[k])  # adds the cdf name to the files dictionary.
                    i = i + 1  # upward to the next entry in the content dictionary.
                    m = m + 1  # increases the key count in the files dictionary.
        if action_tag == 'R':
            delete_file = content[i]
            delete_file = str(delete_file).split("/")  # split dictionary entry.
            for k in range(len(delete_file)):
                if '.cdf' in delete_file[k]:  # searches for the cdf file name.
                    removed[l] = str(delete_file[k])  # ads the file to the removed dictionary.
                    i = i + 1
                    l = l + 1
        if action_tag == 'D':
            delete_file = content[i]
            delete_file = str(delete_file).split("/")  # split dictionary entry.
            for k in range(len(delete_file)):
                if '.cdf' in delete_file[k]:  # searches for the cdf file name.
                    removed[l] = str(delete_file[k])  # ads the file to the removed dictionary.
                    i = i + 1
                    l = l + 1
    cdfApiLogger.info(f'Files to Add {new_files}')
    cdfApiLogger.info(f'Files to Updated {update_files}')  # log files to be updated or added
    cdfApiLogger.info(f'Files to be removed {removed}')  # log files to be removed
    for i in range(len(new_files)):
        new_file_dict = {'CDF_NAME': f'{new_files[i]}', 'CDF_PATH': f'{find(str(new_files[i]))}',
                         'Transportation': 'FALSE', 'OM': 'FALSE', 'Billing': 'FALSE', 'Is_Restricted': 'FALSE',
                         'HEADER': '', 'NUMBER_OF_COLUMNS': '', 'FILE_CONTENTS': '',
                         'LAST_UPD_BY': 'EDI Analyst or Support'}
        run_insert(new_file_dict)
    for i in range(len(update_files)):  # run update function for each file in the add/update file dictionary.
        file = update_files[i]
        run_update(file)
    for i in range(len(removed)):
        file = removed[i]
        remove_file(file)  # run the remove function for the files in the removed dictionary.


@cdfApiLogger.catch()
def run_update(file):
    """
    Update database contents for files found in svn update function.\r\n

    Args:
        file (str): [description]
    """
    cdfApiLogger.info(f'checking {file}')
    cdf_array = check_files(file)
    if cdf_array == '1':
        return
    update_dict = {'CDF_NAME': cdf_array[1], 'CDF_PATH': cdf_array[2], 'HEADER': cdf_array[9],
                   'NUMBER_OF_COLUMNS': cdf_array[10], 'FILE_CONTENTS': cdf_array[11],
                   'LAST_UPD_BY': 'EDI Analyst or Support'}
    cdfApiLogger.info(f'getting new contents {file}')
    update_array = get_updated_file(update_dict)
    cdfApiLogger.info(f'updating {file} in database')
    update_cdf_data(update_array)
    cdfApiLogger.info(f'Checking exceptions for {file}')
    cdf_exceptions(basedir)
    cdfApiLogger.info(f'{file} UPDATED!')


@cdfApiLogger.catch()
def run_insert(new_file_dict: dict):
    """
    Insert function handling the new files.\r\n
    Runs sub function to gather data about cdf.\r\n
    runs the databse insert function.\r\n
    logs the result.\r\n

    Args:
        new_file_dict ([dict]): [description]
    """
    restricted = restricted_def(basedir)
    transportation = transportation_def(basedir)
    om = om_def(basedir)
    billing = billing_def(basedir)
    billing_exception = billing_exception_def(basedir)
    restricted_exception = exception_def(basedir)
    file = str(new_file_dict['CDF_NAME'])
    for i in range(len(transportation)):
        if transportation[i] in file:
            new_file_dict['Transportation'] = 'TRUE'
    for i in range(len(om)):
        if om[i] in file:
            new_file_dict['OM'] = 'TRUE'
    for i in range(len(billing)):
        if billing[i] in file:
            new_file_dict['Billing'] = 'TRUE'
    for i in range(len(restricted)):
        if restricted[i] in file:
            new_file_dict['Is_Restricted'] = 'TRUE'
    for i in range(len(billing_exception)):
        if billing_exception[i] in file:
            new_file_dict['Billing'] = 'FALSE'
    for i in range(len(restricted_exception)):
        if restricted_exception[i] in file:
            new_file_dict['Is_Restricted'] = 'FALSE'
    if new_file_dict['Is_Restricted'] == 'TRUE':
        new_file_dict['Requires_Approval'] = 'TRUE'
    else:
        new_file_dict['Requires_Approval'] = 'FALSE'
    if new_file_dict['Billing'] == 'TRUE':
        new_file_dict['Requires_Approval'] = 'TRUE'
    try:
        read = open(str(new_file_dict['CDF_PATH']), 'rb')
        header = read.readline()
        parsed_header = str(header).split(',')
        number = len(parsed_header)
        new_file_dict['HEADER'] = header
        new_file_dict['NUMBER_OF_COLUMNS'] = number
        new_file_dict['FILE_CONTENTS'] = read_file(new_file_dict['CDF_PATH'])
        cdfApiLogger.info(f'Flags set for {file}')
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'Exception occurred when reading {file}\r\n {e}', exc_info=True)
        return
    insert_cdf_data(new_file_dict)  # insert the new cdf into the table.
    cdf_exceptions(ConfigClass.basedir)  # run cdf_exceptions to check if the new file is part of an exceptions list.
    cdfApiLogger.info(f'FILE ADDED {new_file_dict}')


# change the is_restricted flag for files matching the exceptions list.
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
            send_general_error_email(e)
            cdfApiLogger.error(str(e) + ' has occured with ' + str(ddl) + str(cdf), exc_info=True)
        except Exception as e:
            send_general_error_email(e)
            cdfApiLogger.error(str(e) + " FOUND IN " + str(cdf), exc_info=True)
    conn.close()
    cdfApiLogger.info("TABLE updated")


if __name__ == '__main__':
    cdfApiLogger.info('STARTING SVN UPDATE WORKER', )
    # reset gc counter
    gc_count = 0
    while True:
        try:
            cdfApiLogger.info('SVN WORKER STARTING UPDATE')
            parseUpdate(svn_folders)
            gc_count = gc_count + 1
            if gc_count > 5:
                cdfApiLogger.info('RUNNING GARBAGE COLLECTION, PLEASE WAIT')
                gc.collect()
                gc_count = 0
            cdfApiLogger.info('SVN WORKER SLEEPING')
            subprocess.Popen(['/home/cdfsvc/logrotate.sh',], stdout=subprocess.PIPE).communicate()
            time.sleep(30)
        except Exception as e:
            send_general_error_email(e)
            cdfApiLogger.error(e, exc_info=True)
            pass