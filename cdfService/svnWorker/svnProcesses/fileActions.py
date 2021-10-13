import os
import subprocess
from cdfService.svnWorker.svnProcesses.SvnWorkerLogging import SVN_Worker


@SVN_Worker.catch()
def get_updated_file(update_dict: dict):
    """
    Reads new file data from updated file. Tiggered on SVN update.

    Args:
        cdf_array (dict): Initial dict containing CDF Path and NAME.

    Returns:
        update_dict: Contains new data pulled from updated file. For use in outer function.
    """
    try:
        read = open(str(update_dict['CDF_PATH']), 'rb')
        header = read.readline()
        parsed_header = str(header).split(',')
        number = len(parsed_header)
        update_dict['FILE_CONTENTS'] = read_file(update_dict['CDF_PATH'])
        update_dict['NUMBER_OF_COLUMNS'] = number
        update_dict['HEADER'] = header
        SVN_Worker.info(f"Updated CDF data for {update_dict['CDF_NAME']} Found")
        return update_dict
    except Exception as e:
        SVN_Worker.error(f"Exception occurred when reading {update_dict['CDF_NAME']}", exc_info=True)


@SVN_Worker.catch()
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
        with open(filepath, 'rb') as f:
            blob = f.read()
        return blob
    except Exception as e:
        SVN_Worker.error("Exception occured when reading " + str(filepath), exc_info=True)
        return "Error in File"


@SVN_Worker.catch()
# find the full file path for the new files.
def find(name: str):
    """Finds the working directory path of the CDF name.

    Args:
        name (str): file name of CDF being searched for.

    Returns:
       item_path(str): Full file path of cdf.
    """
    for root, dirs, files, in os.walk('/prod/svc/cdfsvc/cdfservice/repository'):
        for file in files:
            if name in file:
                item_path = str(os.path.join(root, name))
                return item_path

