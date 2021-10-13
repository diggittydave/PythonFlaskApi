from flask import flash, redirect, url_for, Blueprint, render_template
from flask_login import current_user, login_user, logout_user
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.users.schemas import User
from cdfService.users.forms import LoginForm
from cdfService.users.utils import user_perms_from_response, snp_validate
from cdfService.config import ConfigClass

users = Blueprint('users', '__name__')


@users.route('/webapp/login', methods=['GET', 'POST'])
def login():
    """Login page for web interface.

    Returns:
        render_template: html template for login.html
        redirect: if user is already logged in, redirects to the 'about' page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.about'))
    form = LoginForm()
    try:
        if form.validate_on_submit():
            snp_user = user_perms_from_response(form.id.data, form.password.data, ConfigClass.SNP_Client)
            cdfApiLogger.info(str(snp_user['status']))
            cdfApiLogger.info(str(snp_user['user_data']))
            cdfApiLogger.info(len(snp_user['user_data']))
            cdfApiLogger.info(str(snp_user['permissions']))
            cdfApiLogger.info(len(snp_user['permissions']))
            if "OK" in snp_user['status'] and (snp_user['permissions']['CDFServiceAPI.cdf_data.ACTION_UPDATE']
                                                 or snp_user['permissions']['CDFServiceAPI.cdf_filter.ACTION_UPDATE']):
                snp_user_name = snp_user['user_data']['USERNAME']
                cdfApiLogger.info(f" fetching {snp_user_name}")
                snp_validate(snp_user)
                user = User.query.filter_by(public_id=snp_user_name).first()
                cdfApiLogger.info(f'login in {user.public_id}')
                login_user(user)
                return redirect(url_for('main.about'))
            elif "OK" in snp_user['status']:
                if (len(snp_user['permissions']) == 0) \
                        or (snp_user['permissions']['CDFServiceAPI.cdf_data.ACTION_UPDATE'] is False):
                    cdfApiLogger.info(f"No permissions for user {form.id.data}!")
                    flash(f"No Permissions for {form.id.data} Found!")
                    flash("If you continue to have issues, please contact support.")
                    return render_template('login.html', title='LOGIN', form=form)
            elif 'INVALID_PASSWORD' in snp_user['status']:
                cdfApiLogger.info(f"Invalid Password for user {form.id.data}")
                flash(f"Invalid Password: {form.id.data}")
                flash("If you continue to have issues, please contact support.")
                return render_template('login.html', title='LOGIN', form=form)
            elif 'INVALID_USERID' in snp_user['status']:
                cdfApiLogger.info("Invalid User, redirecting.")
                flash(f"Invalid User: {form.id.data}")
                flash("If you continue to have issues, please contact support.")
                return render_template('login.html', title='LOGIN', form=form)
            else:
                return 403
    except Exception as e:
        cdfApiLogger.error("error caught", e)
        flash("An error occured validating your user account.")
        flash("If you continue to have issues, please contact support.")
        return render_template('login.html', title='LOGIN', form=form)
    return render_template('login.html', title='LOGIN', form=form)


# Route to initiate a logout of the current user.
@users.route('/webapp/logout')
def logout():
    """Route to initiate a logout of the current user.

    Returns:
        redirect: Redirects user to login page.
    """
    logout_user()
    return redirect(url_for('users.login'))