import subprocess
from cdfService.services.appVariables import svn_folders
from cdfService.cdfData.schemas import CDF_DATA, CDFContentSchema
import concurrent.futures
from flask import jsonify
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService import db
from cdfService.email.email import send_general_error_email


@cdfApiLogger.catch()
def post_change(ID_KEY: str, data: dict):
    """
    Initial function called from api POST request route.\r\n
    Pulls data from db based on ID key.\r\n
    Splits post request into mulitple lines to enter and check.\r\n
    Returns success or failure messages based on each line submitted in the post.\r\n
    
    Args:
        ID_KEY (str): ID_KEY from post request. Used to identify which CDF to check and update.
        data (dict): passed from post request. Each new line added by a user will be in this dictionary.
                    Also contains any approvers of the request and the name of the requestor.

    Returns:
        results_dict (dict): Dictionary containing success/failures for each individual line being added.
    """
    pool = concurrent.futures.ThreadPoolExecutor(4)
    results_dict = {}
    lines = str(data['line_data']).split(f'\r\n')  # split the input into multiple lines. This should function to allow multiple lines to be added per instance.
    cdfApiLogger.info(f'{lines}')
    approvers = data['Approvers']
    updated_by = data['LAST_UPD_BY']
    svn_commit = False
    try:
        file_data = CDF_DATA.query.filter_by(ID_KEY=ID_KEY).first()  # retrieve file data from the db.
        file_data = CDFContentSchema.dump(file_data)
        cdfApiLogger.info(f'{file_data}')
        svn_locked = svn_lock(file_data['CDF_PATH'])
        if svn_locked:
            results = [pool.submit(update_file, line, file_data) for line in
                        lines]  # creates a thread for each line in the post action
            i = 0
            for f in concurrent.futures.as_completed(results):  # evaluate the resuts from the treads run.
                results_dict[i] = f.result()
                cdfApiLogger.info(f'{f.result()}')
                i = i + 1
            for i in range(len(results_dict)):
                if results_dict[i]['added_lines']:
                    svn_commit = True
            if svn_commit:
                cdfApiLogger.info('Running SVN Commit. Updating database with new file contents.')
                #run_svn_commit(file_data['CDF_NAME'], updated_by, approvers)
                file_data['Approvers'] = approvers
                file_data['LAST_UPD_BY'] = updated_by
                new_data = open(file_data['CDF_PATH'], 'rb')
                new_data = new_data.read()
                file_data['FILE_CONTENTS'] = new_data
                db.session.commit()
                pass
            return jsonify(results_dict)  # return response messages.
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'{e}', exc_info=True)
        results_dict['error'] = e
        return jsonify(results_dict)


@cdfApiLogger.catch()
def update_file(line, file_data):
    """
    Runs a check against the passed in number of columns versus the acceptable number.\r\n
    Calls verify_line to ensure the line doesn't already exist in the file.\r\n
    Passes line to add_line function.\r\n

    Args:
        line (str): [description]
        file_data (dict): Dictionary containing file data as exctracted from the database.

    Returns:
        json: json message with success or failure with reasons.
    """
    file_name = file_data['CDF_NAME']
    cdfApiLogger.info(file_name)
    path = file_data['CDF_PATH']
    cdfApiLogger.info(path)
    columns = str(line).split(',')
    cdfApiLogger.info(f'{columns}')
    column_count = len(columns)
    check = file_data['NUMBER_OF_COLUMNS']
    if check == column_count:
        pass
    else:
        send_general_error_email(e)
        cdfApiLogger.error(f'Incorrect number of columns in line {line}. Should contain {check}, has {column_count}',
                           exc_info=True)
        return {
            'ERROR': f'INCORRECT NUMBER OF COLUMNS IN LINE {line}. Should contain {check}, has {column_count}'}  # return error caused by wrong number of columns.try:
    if not verify_line(path, line):
        added_line = add_line(path, line)
        return {'msg': f'{line} added to {file_name}', 'added_lines': added_line}
    else:
        return {'ERROR': f'{line} ALREADY IN {file_name}'}


@cdfApiLogger.catch()
def verify_line(path, line):
    """
    gets the current contents of the file by reading the file.
    Compares the new line to the file and returns True/False dependent on if the line already exists.

    Args:
        path ([type]): [description]
        line ([type]): [description]

    Returns:
        True [value]: True value after comparing "line" to the file contents. If line doesnt exist, returns True.
        False [value]: False value after comparing "line" to the file contents. If line exists, returns False.
        e [str]: error string if contents cannot be parsed against line.
    """
    try:
        contents = read_file(path)
        cdfApiLogger.info(f'{contents}')
        contents = contents.split('\r\n')
        cdfApiLogger.info(f'{line}')
        for i in range(len(contents)):
            cdfApiLogger.info(f'{contents[i], line}')
            if line in contents[i]:
                return True
            else:
                pass
        return False
    except Exception as e:
        return e


@cdfApiLogger.catch()
def read_file(filepath):
    """
    Function to open and read a file as a binary object.
    Returns the entire contents of a file as a singular object.
    The object is stored in the database and is used in api responses.

    Args:
        filepath (str): Filepath to CDF to be read.

    Returns:
        blob: binary blob representative of the contents of the CDF.
    """
    try:
        with open(filepath, 'r') as f:
            blob = f.read()
        return blob
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error("Exception occured when reading " + str(filepath), exc_info=True)
        return "Error in File"


@cdfApiLogger.catch()
def add_line(file_path, line):
    """
    Adds new line information to cdf file.
    Args:
        file_path ([type]): [description]
        line ([type]): [description]

    Returns:
        [type]: [description]
    """
    try:
        cdf = open(file_path, 'w')
        cdf.write(line)
        cdf.close()
        return True
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'{e}', exc_info=True)
        return False


@cdfApiLogger.catch()
def svn_lock(file: str):
    """
    Uses subprocesses to lock a file within SVN system. Locked files cannot be updated by other sources until the lock is cleared.
    Args:
        file (str): [description]

    Returns:
        [type]: [description]
    """
    try:
        lock_message = f'Locking {file} for service catalog requested update.'
        svn_file_lock = subprocess.Popen(['svn', 'lock', '-m', f'{lock_message}', f'{file}'], stdout=subprocess.PIPE).communicate()
        svn_file_lock = svn_file_lock[0].split('\r\n')
        cdfApiLogger.info(f'{svn_file_lock}')
        return True
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.info(f'{e}', exc_info=True)
        return False


@cdfApiLogger.catch()
def svn_unlock(file: str):
    """
    Uses subprocesses to unlock a currently locked SVN Repo cdf.

    Args:
        file (str): CDF Filename string.
    """
    lock_message = f'Locking {file} for service catalog update.'
    svn_file_unlock = subprocess.Popen(['svn', 'unlock', f'{file}'], stdout=subprocess.PIPE).communicate()
    cdfApiLogger.info(f'{file}')
    pass


@cdfApiLogger.catch()
def run_svn_commit(cdf_name, updated_by, approvers):
    """
    Commit changes made to CDF into SVN repository.

    Args:
        cdf_name (str): CDF Filename in string format.
        updated_by (str): Username of operator or requestor for update.
        approvers (str): Username of operator, support, or management approving change to cdf.
    """
    update_message = f'"{cdf_name} updated via service catalog. Request by: {updated_by}, Approvers: {approvers}"'
    update_cdf = subprocess.Popen(['svn', 'commit', '-m', f'{update_message}', str(svn_folders[0])], stdout=subprocess.PIPE).communicate()
    update_cdf = update_cdf[0].split('\r\n')
    cdfApiLogger.info(f'{update_cdf}')
    update_web = subprocess.Popen(['svn', 'commit', '-m', f'{update_message}', str(svn_folders[1])], stdout=subprocess.PIPE).communicate()
    update_web = update_web[0].split('\r\n')
    cdfApiLogger.info(f'{update_web}')
    pass
