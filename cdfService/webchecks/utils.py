from flask import jsonify
from cdfService.logging.cdfAPILogging import cdfApiLogger
import os
import subprocess
from getpass import getuser
from cdfService.email.email import send_general_error_email


def webCheck():
    """
    self built webcheck to serve in place of the elastic api monitoring module.
    Returns the current SVN versions, current memory useage.

    Returns:
        web_check (json): JSON object containing inforamtion about the current status of the app.
    """
    web_check = {}
    # server info
    tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
    info_server = {'Total Memory': f'{tot_m}', 'Used Memory': f'{used_m}', 'Free Memory': f'{free_m}'}
    web_check.update({'Info Server': info_server})
    info_gen = get_svn_info('EDI_GEN', './repository/cdfs/cdfs')
    cdfApiLogger.info(f'Info Gen {info_gen}')
    info_web = get_svn_info('EDI_WEB', './repository/prod/prod')
    cdfApiLogger.info(f'Info WEB {info_web}')
    info_webapp = get_app_info('gunicorn')
    info_worker = get_app_info('svnWorker')
    web_check.update({'Info EDI_GEN': info_gen})
    web_check.update({'Info EDI_Web': info_web})
    web_check.update({'info Webapp': info_webapp})
    web_check.update({'info Worker': info_worker})
    web_check = jsonify(web_check)
    return web_check


def get_app_info(app_name: str):
    """[summary]

    Args:
        app_name (str): [description]

    Returns:
        [type]: [description]
    """
    app_info = {}
    user = getuser()
    proc1 = subprocess.Popen(['ps', '-fu', f'{user}'], stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(['grep', f'{app_name}'], stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc3 = subprocess.Popen(['grep', '-v', 'grep'], stdin=proc2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_list = proc3.communicate()
    processes = process_list[0].decode('UTF-8').split('\n')
    for i in range(len(processes)):
        app_info[f'Process_id_{i}'] = processes[i]
    cdfApiLogger.info(f'{app_info}')
    return app_info

def get_svn_info(repo_name: str, repo_path: str):
    """[summary]

    Args:
        repo_name (str): [description]
        repo_path (str): [description]

    Returns:
        [type]: [description]
    """
    svn_procs = {}
    svn_info = subprocess.Popen(['svn', 'info', f'{repo_path}'], stdout=subprocess.PIPE).communicate()
    svn_info = svn_info[0].decode('UTF-8').split('\n')
    for i in range(len(svn_info)):
        svn_procs[f'{repo_name}_{i}'] = svn_info[i]
    return svn_procs


def get_app_status(app_name: str):
    """[summary]

    Args:
        app_name (str): [description]

    Returns:
        [type]: [description]
    """
    app_info = {}
    user = getuser()
    proc1 = subprocess.Popen(['ps', '-fu', f'{user}'], stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(['grep', f'{app_name}'], stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc3 = subprocess.Popen(['grep', '-v', 'grep'], stdin=proc2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_list = proc3.communicate()
    processes = process_list[0].decode('UTF-8').split('\n')
    for i in range(len(processes)):
        app_info[f'Process_id_{i}'] = processes[i]
    cdfApiLogger.info(f'{app_info}')
    if int(len(app_info)) <= 1:
        status_code = 'failed'
        return status_code
    else:
        status_code = 'ok'
        return status_code


def memory_status():
    """[summary]

    Returns:
        [type]: [description]
    """
    tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
    info_server = {'Total Memory': f'{tot_m}', 'Used Memory': f'{used_m}', 'Free Memory': f'{free_m}'}
    cdfApiLogger.info(f'Server memory poll: {info_server}')
    mem_limit = int(tot_m) * .8
    if int(used_m) >= mem_limit:
        status_code = 'failed'
        send_general_error_email('Memory over 90 percent used. Please check the application and/or restart the server.')
        cdfApiLogger.error('Memory over 90 percent used. Please check the application and/or restart the server.')
        return status_code
    else:
        status_code = 'ok'
        cdfApiLogger.info('Memory Status OK.')
        return status_code


def svn_status():
    """[summary]

    Returns:
        [type]: [description]
    """
    info_gen = subprocess.Popen(['svn', 'info', './repository/cdfs/cdfs'], stdout=subprocess.PIPE).communicate()
    info_gen = info_gen[0].decode('UTF-8').split('\n')
    if int(len(info_gen)) <= 1:
        status_code = 'failed'
        return status_code
    info_web = subprocess.Popen(['svn', 'info', './repository/prod/prod'], stdout=subprocess.PIPE).communicate()
    info_web = info_web[0].decode('UTF-8').split('\n')
    if int(len(info_web)) <= 1:
        status_code = 'failed'
        return status_code
    else:
        status_code = 'ok'
        return status_code