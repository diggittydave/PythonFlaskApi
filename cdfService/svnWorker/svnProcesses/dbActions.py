import sqlite3 as lite
from cdfService.svnWorker.svnProcesses.SvnWorkerLogging import SVN_Worker
from cdfService.config import ConfigClass
from cdfService.email.email import send_general_error_email


@SVN_Worker.catch()
def check_files(file: str,):
    """
    Check to ensure files exist in database.\r\n
    Passes off new files to another function for logging into the database.\r\n

    Args:
        file (str): [description]\r\n
        database_path ([type], optional): [description]. Defaults to str.\r\n

    Returns:
        cdf_return (dict): [description]
    """
    conn = lite.connect(ConfigClass.basedir)
    with conn:
        try:
            ddl = """SELECT * FROM CDF_DATA WHERE CDF_NAME = ?"""
            curr = conn.cursor()
            curr.execute(ddl, [file,])
            item = curr.fetchone()
            if not item:
                return 1
            else:
                SVN_Worker.info(f'{file} found in database.')
                return item
        except Exception as e:
            send_general_error_email(e)
            SVN_Worker.error(f"{e}", exc_info=True)

@SVN_Worker.catch()
def update_cdf_data(cdf_array: dict):
    """
    Updates API data with new file contents.\r\n

    Args:
        cdf_array(dict): New CDF data from SVN update.

    """
    conn = lite.connect(ConfigClass.basedir)
    with conn:
        try:
            curr = conn.cursor()
            ddl1 = """UPDATE CDF_DATA 
                        SET HEADER = ?, NUMBER_OF_COLUMNS = ?, FILE_CONTENTS = ?, LAST_UPD_BY = ?, Date_Updated = CURRENT_TIMESTAMP
                        WHERE CDF_NAME = ? """
            insert_tuple = ([
                cdf_array['HEADER'],
                cdf_array['NUMBER_OF_COLUMNS'],
                cdf_array['FILE_CONTENTS'],
                cdf_array['LAST_UPD_BY'],
                cdf_array['CDF_NAME']
            ])
            try:
                curr.execute(ddl1, insert_tuple)
                curr.close()
                SVN_Worker.info(f"CDF - {cdf_array['CDF_NAME']} updated with new content: \r\n"
                                       f" {cdf_array['FILE_CONTENTS']}")
                conn.commit()
            except Exception as e:
                send_general_error_email(e)
                SVN_Worker.error(f'{e}', exc_info=True)
        except Exception as e:
            send_general_error_email(e)
            SVN_Worker.error(f'{e}', exc_info=True)


@SVN_Worker.catch()
def insert_cdf_data(new_file_dict: dict):
    """
    Inserts new CDF into API database\r\n

    Args:
        new_file_dict(dict): New CDF data from SVN update.

    """
    conn = lite.connect(ConfigClass.basedir)
    try:
        ddl1 = """INSERT INTO 'CDF_DATA' ('CDF_NAME', 'CDF_PATH', 'Transportation', 'OM', 'Billing',
                    'Is_Restricted', 'HEADER', 'NUMBER_OF_COLUMNS', 'FILE_CONTENTS', 'LAST_UPD_BY', 'Requires_Approval',
                    'Date_Updated')\
                    values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)"""
        insert_tuple = ([
            new_file_dict['CDF_NAME'],
            new_file_dict['CDF_PATH'],
            new_file_dict['Transportation'],
            new_file_dict['OM'],
            new_file_dict['Billing'],
            new_file_dict['Is_Restricted'],
            new_file_dict['HEADER'],
            new_file_dict['NUMBER_OF_COLUMNS'],
            new_file_dict['FILE_CONTENTS'],
            new_file_dict['LAST_UPD_BY'],
            new_file_dict['Requires_Approval']
        ])
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(ddl1, insert_tuple)
                SVN_Worker.info(f"ADDED {new_file_dict['CDF_NAME']} TO THE DATABASE")
                cur.close()
                conn.commit()
                return
        except (lite.Error, lite.Warning) as e:
            send_general_error_email(e)
            SVN_Worker.error(f'{e}', exc_info=True)
        SVN_Worker.info(f"New CDF added {new_file_dict['CDF_NAME']}")
    except Exception as e:
        send_general_error_email(e)
        SVN_Worker.error(f'{e}', exc_info=True)


@SVN_Worker.catch()
def remove_file(file: str):
    """
    Queries CDF_DATA table for current CDF info based on file name. Passes the data to a serate function.
    Removes CDF from CDF_DATA table \r\n
    This table is meant to be a historical record of items deleted from SVN.

    Args:
        file(str): File name of CDF to be removed from CDF_DATA.

    """
    SVN_Worker.info(f'Preparing to remove {file} from the Database')
    conn = lite.connect(ConfigClass.basedir)
    with conn:
        try:
            ddl_select = f"""SELECT * FROM CDF_DATA WHERE CDF_NAME = ? """
            ddl_delete = f"""DELETE FROM CDF_DATA WHERE CDF_NAME = ? """
            curr = conn.cursor()
            try:
                curr.execute(ddl_select, [file,])
                removed_cdf = curr.fetchone()
                removed_cdf = {
                    'CDF_NAME': removed_cdf[1],
                    'CDF_PATH': removed_cdf[2],
                    'Transportation': removed_cdf[3],
                    'OM': removed_cdf[4],
                    'Billing': removed_cdf[5],
                    'Is_Restricted': removed_cdf[6],
                    'Approvers': removed_cdf[7],
                    'HEADER': removed_cdf[9],
                    'NUMBER_OF_COLUMNS': removed_cdf[10],
                    'FILE_CONTENTS': removed_cdf[11]
                }
                try:
                    insert_removed_cdf_data(removed_cdf)
                except Exception as e:
                    send_general_error_email(e)
                    SVN_Worker.error(f'Failed to add {file} to removed data.', exc_info=True)
                    SVN_Worker.error(f'{e}')
                    pass
                curr.execute(ddl_delete, [file,])
                curr.close()
                conn.commit()
            except Exception as e:
                send_general_error_email(e)
                SVN_Worker.error(f'{e}', exc_info=True)
        except Exception as e:
            send_general_error_email(e)
            SVN_Worker.error(f'{e}', exc_info=True)


@SVN_Worker.catch()
def insert_removed_cdf_data(removed_file: dict):
    """
    Inserts CDF informtion into the REMOVED_CDF_DATA table. \r\n
    This table is meant to be a historical record of items deleted from SVN.

    Args:
        file(str): File name of CDF to be removed from CDF_DATA.

    """
    conn = lite.connect(ConfigClass.basedir)
    try:
        ddl1 = """INSERT INTO 'REMOVED_CDF_DATA' ('CDF_NAME', 'CDF_PATH', 'Transportation', 'OM', 'Billing',
                    'Is_Restricted', 'Approvers', 'HEADER', 'NUMBER_OF_COLUMNS', 'FILE_CONTENTS', 'Date_Removed')\
                    values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP )"""
        insert_tuple = ([
            removed_file['CDF_NAME'],
            removed_file['CDF_PATH'],
            removed_file['Transportation'],
            removed_file['OM'],
            removed_file['Billing'],
            removed_file['Is_Restricted'],
            removed_file['Approvers'],
            removed_file['HEADER'],
            removed_file['NUMBER_OF_COLUMNS'],
            removed_file['FILE_CONTENTS']
        ])
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(ddl1, insert_tuple)
                SVN_Worker.info(f"ADDED {removed_file['CDF_NAME']} TO THE REMOVED_CDFS DATABASE TABLE")
                cur.close()
                conn.commit()
                return
        except (lite.Error, lite.Warning) as e:
            send_general_error_email(e)
            SVN_Worker.error(f'{e}', exc_info=True)
    except Exception as e:
        send_general_error_email(e)
        SVN_Worker.error(f'{e}', exc_info=True)
