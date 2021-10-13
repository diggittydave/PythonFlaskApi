from flask import jsonify
from cdfService.logging.cdfAPILogging import cdfApiLogger
import subprocess
import os
from getpass import getuser

from cdfService.email.email import send_general_error_email


@cdfApiLogger.catch()
def webCheck():
    """cdfService.routes.approutes.webCheck
    self built webcheck to serve in place of the elastic api monitoring module.
    Returns the current SVN versions, current memory useage.

    Returns:
        web_check (json): JSON object containing inforamtion about the current status of the app.
    """
    j = 10
    web_check = {}
    # server info
    tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
    info_server = {'Total Memory': f'{tot_m}', 'Used Memory': f'{used_m}', 'Free Memory': f'{free_m}'}
    web_check.update(info_server)
    # info stats for svn 'GEN' repo
    info_gen = subprocess.Popen(['svn', 'info', './repository/cdfs/cdfs'], stdout=subprocess.PIPE).communicate()
    info_gen = info_gen[0].decode('UTF-8').split('\n')
    cdfApiLogger.info(f'Info Gen {info_gen}')
    # info stats for svn 'WEB' repo
    info_web = subprocess.Popen(['svn', 'info', './repository/prod/prod'], stdout=subprocess.PIPE).communicate()
    info_web = info_web[0].decode('UTF-8').split('\n')
    cdfApiLogger.info(f'Info WEB {info_web}')
    # get info for all running services
    info_webapp = get_app_info('gunicorn')
    info_worker = get_app_info('svnUpdate')
    for i in range(len(info_gen)):
        web_check.update({f'info_gen{j}': f'{info_gen[i]}'})
        j = j + 1
    for i in range(len(info_web)):
        web_check.update({f'info_web{j}': f'{info_web[i]}'})
        j = j + 1
    web_check.update({'info Webapp': info_webapp})
    web_check.update({'info Worker': info_worker})
    web_check = jsonify(web_check)
    return web_check


@cdfApiLogger.catch()
def get_app_info(app_name: str):
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


@cdfApiLogger.catch()
def svn_Data_only(svn_folder: str):
    svn_data = {"URL": "", "Repository_Root": "", "Repository_UUID": "", "Revision": "", "Last_Changed_Author": "",
                "Last_Changed_Rev": "", "Last_Changed_Date": ""}
    try:
        svn_info = subprocess.Popen(['svn', 'info', str(svn_folder)], stdout=subprocess.PIPE).communicate()
        svn_info = svn_info[0].decode('UTF-8').split('\n')
        for i in range(len(svn_info)):
            if "URL" in svn_info[i]:
                url = []
                url = str(svn_info[i]).split(':')
                svn_data.update({"URL": f"{str(url[1])}:{str(url[2])}:{str(url[3])}"})
            if "Repository Root" in svn_info[i]:
                root = []
                root = str(svn_info[i]).split(':')
                svn_data.update({"Repository_Root": f"{str(root[1])}:{str(root[2])}:{str(root[3])}"})
            if "Repository UUID" in svn_info[i]:
                repo_uuid = []
                repo_uuid = str(svn_info[i]).split(':')
                svn_data.update({"Repository_UUID": f"{str(repo_uuid[1])}"})
            if "Revision:" in svn_info[i]:
                revision = []
                revision = str(svn_info[i]).split(':')
                svn_data.update({"Revision": f"{str(revision[1])}"})
            if "Author" in svn_info[i]:
                author = []
                author = svn_info[i].split(':')
                svn_data.update({"Last_Changed_Author": f"{str(author[1])}"})
            if "Last Changed Rev" in svn_info[i]:
                last_change = []
                last_change = str(svn_info[i]).split(':')
                svn_data.update({"Last_Changed_Rev": f"{str(last_change[1])}"})
            if "Last Changed Date" in svn_info[i]:
                changed_date = []
                changed_date = str(svn_info[i]).split(':')
                svn_data.update({"Last_Changed_Date": f"{str(changed_date[1])}:{str(changed_date[2])}:{str(changed_date[3])}"})
        return svn_data
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'{e}')