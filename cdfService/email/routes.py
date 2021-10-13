from flask import Blueprint
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.email.email import send_general_error_email, send_rebuild_start_message, send_rebuild_finish_message,\
    send_cdf_error_email


emailApi = Blueprint('emailApi', '__name__')


@cdfApiLogger.catch()
@emailApi.route('/api/email/error_email', methods=['POST'])
def send_error_email(content: str):
    try:
        send_general_error_email(content)
    except Exception as e:
        cdfApiLogger.error(e)


@cdfApiLogger.catch()
@emailApi.route('/api/email/flag_start', methods=['POST'])
def send_flag_start_email(user: object):
    try:
        send_rebuild_start_message(user)
    except Exception as e:
        cdfApiLogger.error(e)


@cdfApiLogger.catch()
@emailApi.route('/api/email/flag_finish', methods=['POST'])
def send_flag_end_email(user: object):
    try:
        send_rebuild_finish_message(user)
    except Exception as e:
        cdfApiLogger.error(e)


@cdfApiLogger.catch()
@emailApi.route('/api/email/cdf_error', methods=['POST'])
def send_cdf_error(user: object):
    try:
        send_cdf_error_email(user)
    except Exception as e:
        cdfApiLogger.error(e)
