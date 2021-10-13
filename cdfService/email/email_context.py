from cdfService.config import ConfigClass
from flask_mail import Mail, Message
from cdfService.logging.cdfAPILogging import cdfApiLogger
from flask import current_app


def send_rebuild_start_message(user):
    mail = Mail(current_app)
    msg = Message('CDF API Flag Rebuild Start', sender='noreply@cdfserviceapi.chq.ei',
                  recipients=[f'{ConfigClass.dev_error_email_address}', f'{user}'])
    msg.body = ''' The Flag Rebuild process has been started. 
    You will receive an email when the process is completed.
    '''
    try:
        mail.send(msg)
    except Exception as e:
        cdfApiLogger.error(f'{e}', exc_info=True)


def send_rebuild_finish_message(user):
    mail = Mail(current_app)
    msg = Message('CDF API Flag Rebuild Finish', sender='noreply@cdfserviceapi.chq.ei',
                  recipients=[f'{ConfigClass.dev_error_email_address}', f'{user}'])
    msg.body = '''The rebuild process has been completed.
    '''
    try:
        mail.send(msg)
    except Exception as e:
        cdfApiLogger.error(f'{e}', exc_info=True)


