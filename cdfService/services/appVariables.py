#< cdfService.services.appVariables
# collection of global app variables.
# the variable sets check for OS environment and OS setup.
# differentiates between QA and Dev environments. 
# Dev will match prod.
#>
import os
import sys
import getpass
from cdfService.logging.cdfAPILogging import cdfApiLogger


if 'linux' in sys.platform:
    """This variable set is for the linux environment.\r\n
    Checks the server config for username to determine QA/Dev/Prod
    """
    if 'qa' in getpass.getuser():
        basedir = os.path.abspath(r'/prod/svc/cdfsvcqa/cdfservice/cdfService/database/CDF_INFO.sqlite')
        appdir = os.path.abspath(r'/prod/svc/cdfsvcqa/cdfservice')
        repo_path = os.path.abspath(r'/prod/svc/cdfsvcqa/cdfservice/repository')
        ca_cert = os.path.abspath(r'/prod/svc/cdfsvcqa/cdfService/services/ca_certs.pem')
        svn_folders = [repo_path + '/cdfs/cdfs', repo_path + '/prod/prod']
        cdfApiLogger.info('USING QA VARIABLES')
    else:
        basedir = os.path.abspath(r'/prod/svc/cdfsvc/cdfservice/cdfService/database/CDF_INFO.sqlite')
        appdir = os.path.abspath(r'/prod/svc/cdfsvcqa/cdfservice')
        repo_path = os.path.abspath(r'/prod/svc/cdfsvc/cdfservice/repository')
        ca_cert = os.path.abspath(r'/prod/svc/cdfsvc/cdfService/services/ca_certs.pem')
        svn_folders = [repo_path + '/cdfs/cdfs', repo_path + '/prod/prod']
        cdfApiLogger.info('USING DEV/PROD VARIABLES')


if 'win' in sys.platform:
    """This variable set is for windows environment.\r\n
    Use these if on pc localhost for testing.
    """
    basedir = os.path.abspath(r'C:\Users\chq-davidwe\Documents\Projects\Python\CDFService\dev\With_Data\CDF_INFO.sqlite')
    repo_path = os.path.abspath(r'C:\Users\chq-davidwe\Documents\Projects\Python\CDFService\repository')
    ca_cert = os.path.abspath(r'C:\Users\chq-davidwe\Documents\Projects\Python\CDFService\cdfService\services\ca_certs.pem')
    svn_folders = [repo_path + '\cdfs', repo_path + '\prod']
    cdfApiLogger.info('USING WINDOWS VARIABLES')
    # test repo is a limited range of files to test specific problems.
    repo_path = os.path.abspath(r'C:\Users\chq-davidwe\Documents\Projects\Python\CDFService\testRepo')

