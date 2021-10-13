from flask import render_template, Blueprint, make_response
from cdfService.webchecks.utils import webCheck, memory_status, svn_status, get_app_status
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.email.email import send_general_error_email

webchecks = Blueprint('webchecks', '__name__')


@webchecks.route('/webapp/webcheck/Full_Status')
def full_status():
    """Webcheck route. Returns json object with all statuses. For use with future monitoring applications.

    Returns:
        json: object containing multiple keypair dictionaries. 
    """
    return make_response(webCheck(), 200)


@webchecks.route('/webapp/webcheck/web_app', methods=['GET'])
def webapp():
    """Basic Webcheck route.

    Returns:
        json: Json object containing various stats and current status of app.
    """
    try:
        status_code = (get_app_status('gunicorn'))
        return render_template('bb_status_page.html', status_page_title='Webapp Status', status_code=status_code)
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'Error generating webcheck: \r\n {e}')
        return render_template('bb_status_page.html', status_page_title='Webapp Status', status_code='Failed')


@webchecks.route('/webapp/webcheck/svn_worker', methods=['GET'])
def svn_worker():
    """Basic Webcheck route.

    Returns:
        Webpage: Renders webpage with current SVN Worker status.
    """
    try:
        status_code = (get_app_status('svnWorker'))
        return render_template('bb_status_page.html', status_page_title='SVN Worker Status', status_code=status_code)
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'Error generating webcheck: \r\n {e}')
        return render_template('bb_status_page.html', status_page_title='SVN Worker Status', status_code='Failed')


@webchecks.route('/webapp/webcheck/memory_status', methods=['GET'])
def mem_status():
    """Basic Webcheck route.

    Returns:
        Webpage: Renders webpage with current Memory Use status.
    """
    try:
        status_code = memory_status()
        return render_template('bb_status_page.html', status_page_title='Memory Status', status_code=status_code)
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'Error generating webcheck: \r\n {e}')
        return render_template('bb_status_page.html', status_page_title='Memory Status', status_code='Failed')


@webchecks.route('/webapp/webcheck/SvnConnections', methods=['GET'])
def svn_connections():
    """Basic Webcheck route.

    Returns:
        Webpage: Renders webpage with current SVN connection status.
    """
    try:
        status_code = svn_status()
        return render_template('bb_status_page.html', status_page_title='SVN Connections', status_code=status_code)
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'Error generating webcheck: \r\n {e}')
        return render_template('bb_status_page.html', status_page_title='SVN Connections', status_code=status_code)