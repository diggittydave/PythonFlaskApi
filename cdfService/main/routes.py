from flask import redirect, render_template, url_for, Blueprint, make_response
from flask_login import current_user, login_required
from cdfService.main.utils import webCheck, svn_Data_only
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.config import ConfigClass
from cdfService.email.email import send_general_error_email


main = Blueprint('main', '__name__')


@cdfApiLogger.catch()
@main.route('/', methods=['GET'])
@main.route('/index', methods=['GET'])
@login_required
def index():
    """Index page routes to login or about page if already logged in.

    Returns:
        url redirect: URL Redirect based on login status of current session.
    """
    if current_user.is_authenticated:
        return render_template(url_for('main.about'))
    else:
        return redirect(url_for('main.login'))


@cdfApiLogger.catch()
@main.route('/webapp/services/web_check_info', methods=['GET'])
def webcheck():
    """Basic Webcheck route.

    Returns:
        json: Json object containing various stats and current status of app.
    """
    try:
        return make_response(webCheck(), 200)
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'Error generating webcheck: \r\n {e}')


@cdfApiLogger.catch()
@main.route('/webapp/about')
@login_required
def about():
    """Homepage of the user interface.

    Returns:
        render_template: html template for about.html
        redirect: If user is not logged in, user is redirected to login page.
    """
    if not current_user.is_authenticated:
        try:
            cdfApiLogger.info(F'Redirected to login. Current user is not authenticated.')
            return redirect(url_for('main.login'))
        except Exception as e:
            send_general_error_email(e)
            cdfApiLogger.error(f'Error in redirect. \r\n {e}')
    if current_user.is_authenticated:
        try:
            cdfApiLogger.info(f'Redirected to about.html.')
            return render_template('about.html', title='ABOUT')
        except Exception as e:
            send_general_error_email(e)
            cdfApiLogger.error(f'Error in redirect. \r\n {e}')


@cdfApiLogger.catch()
@main.route('/webapp/svn_info')
@login_required
def svn_info():
    """Homepage of the user interface.

    Returns:
        render_template: html template for about.html
        redirect: If user is not logged in, user is redirected to login page.
    """
    if not current_user.is_authenticated:
        try:
            cdfApiLogger.info(F'Redirected to login. Current user is not authenticated.')
            return redirect(url_for('main.login'))
        except Exception as e:
            send_general_error_email(e)
            cdfApiLogger.error(f'Error in redirect. \r\n {e}')
    if current_user.is_authenticated:
        try:
            gen = svn_Data_only(str(ConfigClass.svn_folders[0]))
            web = svn_Data_only(str(ConfigClass.svn_folders[1]))
            svcp = svn_Data_only(str(ConfigClass.svn_folders[2]))
            cdfApiLogger.info(f'Redirected to about.html.')
            return render_template('svn_data.html', title='SVN Repository Information', gen=gen, web=web, svcp=svcp)
        except Exception as e:
            send_general_error_email(e)
            cdfApiLogger.error(f'Error in redirect. \r\n {e}')