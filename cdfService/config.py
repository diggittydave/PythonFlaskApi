import os
from flask_swagger_ui import get_swaggerui_blueprint
from zeep import Client
from zeep.transports import Transport

transport = Transport(timeout=10)


class SnPClients:
    qa_client = Client('http://qaspcentral.chq.ei:8121/spsoap/services/SPWebService?wsdl', transport=transport)
    dev_client = Client('http://devspcentral.chq.ei:8121/spsoap/services/SPWebService?wsdl', transport=transport)
    prod_client = Client('http://spcentral.chq.ei:8121/spsoap/services/SPWebService?wsdl', transport=transport)



class ConfigClass:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = 'exch-smtp.expeditors.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # elastic configurations
    ELASTIC_APM = {
        'SERVICE_NAME': 'CDF_Service',
        'SECRET_TOKEN': os.environ.get('SECRET_TOKEN'),
        'SEVER_URL': os.environ.get('SERVER_URL'),
        'SERVER_CERT': os.environ.get('SERVER_CERT'),
        'CA_CERTS': os.environ.get('CA_CERTS'),
        'DEBUG': True
        }
    basedir = os.path.abspath(r'/prod/svc/cdfsvc/cdfservice/cdfService/database/CDF_INFO.sqlite')
    appdir = os.path.abspath(r'/prod/svc/cdfsvcqa/cdfservice')  # applicaiton direcorty location.
    repo_path = os.path.abspath(r'/prod/svc/cdfsvc/cdfservice/repository')  # primary repository paths.
    svn_folders = [repo_path + '/cdfs/cdfs', repo_path + '/prod/prod', repo_path + '/svcp_prod/svcp_prod']  # separated repository paths.
    error_email_address = 'christopher.sharratt@expeditors.com'  # support email group
    dev_error_email_address = 'david.weber@expeditors.com'  # dev email group
    SNP_Client = SnPClients.prod_client  # set for prod/qa/dev sn


class Config_QA:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = 'exch-smtp.expeditors.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # elastic configurations
    ELASTIC_APM = {
        'SERVICE_NAME': 'CDF_Service',
        'SECRET_TOKEN': os.environ.get('SECRET_TOKEN'),
        'SEVER_URL': os.environ.get('SERVER_URL'),
        'SERVER_CERT': os.environ.get('SERVER_CERT'),
        'CA_CERTS': os.environ.get('CA_CERTS'),
        'DEBUG': True
        }
    basedir = os.path.abspath(r'/prod/svc/cdfsvcqa/cdfservice/cdfService/database/CDF_INFO.sqlite')
    appdir = os.path.abspath(r'/prod/svc/cdfsvcqa/cdfservice/')
    repo_path = os.path.abspath(r'/prod/svc/cdfsvcqa/cdfservice/repository')
    svn_folders = [repo_path + '/cdfs/cdfs', repo_path + '/prod/prod']


class Config_Swagger_UI:
    SWAGGER_URL = '/swagger'
    API_URL_QA = '/static/swagger_qa.json'
    API_URL_DEV = '/static/swagger_dev.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL_DEV,
        config={
            'app_name': "CDF Service API"
        }
    )
