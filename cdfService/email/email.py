from cdfService.config import ConfigClass
from flask_mail import Message
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService import mail


def send_cdf_error_email(error: str, cdf_name: str):
    msg = Message('CDF API ERROR!', sender='noreply@cdfserviceapi.chq.ei',
                  recipients=[f'{ConfigClass.dev_error_email_address}', f'{ConfigClass.error_email_address}'])
    msg.body = f''' An error has occurred on a CDF:
{cdf_name}
{error}'''
    cdfApiLogger.info(f'{msg.body}')
    try:
        mail.send(msg)
    except Exception as e:
        cdfApiLogger.error(f'{e}', exc_info=True)


def send_general_error_email(error: str):
    msg = Message('CDF API ERROR!', sender='noreply@cdfserviceapi.chq.ei',
                  recipients=[f'{ConfigClass.dev_error_email_address}', f'{ConfigClass.error_email_address}'])
    msg.body = f''' An error has occured in the CDF Service API:
{error}'''
    cdfApiLogger.info(f'{msg.body}')
    try:
        mail.send(msg)
    except Exception as e:
        cdfApiLogger.error(f'{e}', exc_info=True)


def send_rebuild_start_message(user):
    msg = Message('CDF API Flag Rebuild Start', sender='noreply@cdfserviceapi.chq.ei',
                  recipients=[f'{ConfigClass.dev_error_email_address}', f'{user.email}'])
    msg.body = ''' The Flag Rebuild process has been started. 
    You will receive an email when the process is completed.
    '''
    try:
        mail.send(msg)
    except Exception as e:
        cdfApiLogger.error(f'{e}', exc_info=True)


def send_rebuild_finish_message(user):
    msg = Message('CDF API Flag Rebuild Finish', sender='noreply@cdfserviceapi.chq.ei',
                  recipients=[f'{ConfigClass.dev_error_email_address}', f'{user}'])
    msg.body = '''The rebuild process has been completed.
    '''
    try:
        mail.send(msg)
    except Exception as e:
        cdfApiLogger.error(f'{e}', exc_info=True)
