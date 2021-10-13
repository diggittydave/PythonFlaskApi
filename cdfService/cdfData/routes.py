import concurrent

from cdfService import ConfigClass
from cdfService.cdfFilters.forms import ReloadForm
from cdfService.database.build import startTableBuild
from cdfService.email.email import send_general_error_email
from cdfService.logging.cdfAPILogging import cdfApiLogger
from flask import redirect, render_template, request, url_for, Blueprint, flash
from flask_login import current_user, login_required
from cdfService.cdfData.schemas import CDF_DATA
from cdfService.cdfData.forms import CDFSearchForm, RebuildForm
from cdfService.users.schemas import User
from cdfService.users.utils import user_perms_from_response

cdfData = Blueprint('cdfData', '__name__')


@cdfApiLogger.catch()
@cdfData.route('/webapp/cdf/search', methods=['GET','POST'])
@login_required
def webapp_cdf_search():
    """CDF search page. Allows searching for specific CDF's based on a search string entered. 

    Returns:
        redirct: Redirctes to /webapp/cdf/search/<key>, which contains results and search form.
    """
    if current_user.is_authenticated and (current_user.cdf_data or current_user.cdf_data_view):
        form = CDFSearchForm()
        if form.validate_on_submit():
            key = form.search.data
            cdfApiLogger.info(f'{current_user} searching for  {key}')
            return redirect(url_for('cdfData.webapp_cdf_search_key', key=key))
        return render_template('cdf_search.html', title='CDF SEARCH', form=form)
    else:
        return redirect(url_for('main.about'))


@cdfApiLogger.catch()
@cdfData.route('/webapp/cdf/search/<key>', methods=['GET','POST'])
@login_required
def webapp_cdf_search_key(key):
    """A page containing Results of search. Also can search for new string on page.    
    Args:
        key ([int]): Id Key of CDF stored in database.

    Returns:
        Webpage: Rendes data in table containing ID key hyper link and CDF Name.
    """
    if current_user.is_authenticated and (current_user.cdf_data or current_user.cdf_data_view):
        form = CDFSearchForm()
        if key:
            page = request.args.get('page', 1, type=int )
            some_cdfs = CDF_DATA.query.filter(CDF_DATA.CDF_NAME.like('%' + key + '%')).order_by(CDF_DATA.CDF_NAME).paginate(page=page, per_page=25)
            if form.validate_on_submit():
                key = form.search.data
                page = request.args.get('page', 1, type=int )
                some_cdfs = CDF_DATA.query.filter(CDF_DATA.CDF_NAME.like('%' + key + '%')).order_by(CDF_DATA.CDF_NAME).paginate(page=page, per_page=25)
                cdfApiLogger.info(f'{current_user} searching for  {key}')
                return redirect(url_for('cdfData.webapp_cdf_search_key', key=key))
            return render_template('cdf_search_results.html', title='CDF SEARCH RESULTS', form=form, posts=some_cdfs, key=key)
        else:
            key = ''
            page = request.args.get('page', 1, type=int)
            some_cdfs = CDF_DATA.query.filter(CDF_DATA.CDF_NAME.like('%' + key + '%')).order_by(CDF_DATA.CDF_NAME).paginate(page=page, per_page=25)
            cdfApiLogger.info(f'{current_user} searching for  {key}')
            return render_template('cdf_search_results.html', title='CDF SEARCH RESULTS', form=form, posts=some_cdfs, key=key)
    else:
        return redirect(url_for('main.about'))


@cdfApiLogger.catch()
@cdfData.route('/webapp/cdf/ID_KEY/<ID_KEY>', methods=['GET'])
@login_required
def webapp_get_cdf(ID_KEY):
    """
    Contains relevant locally stored API data about a single CDF. Shows all relevant flags, update time, approvers and header data.

    Returns:
        Webpage: Data is in a table format.
    """
    if current_user.is_authenticated and (current_user.cdf_data or current_user.cdf_data_view):
        if ID_KEY:
            post = CDF_DATA.query.get_or_404(ID_KEY)
            header = post.HEADER
            content = post.FILE_CONTENTS
            cdfApiLogger.info(f'{current_user} Looking at {ID_KEY}')
            return render_template('webapp_cdf_data.html', title=f'CDF DATA FOR {post.CDF_NAME}', post=post, header=header)
        else:
            return redirect(url_for('cdfData.webapp_cdf_search'))
    else:
        return redirect(url_for('main.about'))


@cdfApiLogger.catch()
@cdfData.route('/webapp/cdf/rebuild', methods=['GET', 'POST'])
@login_required
def build_rerun():
    """Route to the reload flags funtion.
    The function resets all flags based on entries added or removed from the filters list.

    Returns:
        render_template: html template for reload.html.
        redirect: upon successful form submit, redirects to 'about'.
        redirect: if user does not have access, user is redirected to 'about'.
    """
    form = RebuildForm()
    if current_user.is_authenticated and current_user.cdf_filter:
        if form.validate_on_submit():
            try:
                pool = concurrent.futures.ThreadPoolExecutor()
                snp_user = user_perms_from_response(form.id.data, form.password.data, ConfigClass.SNP_Client)
                user = User.query.filter_by(public_id=form.id.data).first()
                cdfApiLogger.info('STARTING REBUILD OF DATABASE TABLE')
                pool.submit(startTableBuild)
                return redirect(url_for('main.about')), flash(f'REBUILDING CDF TABLE DATA.\r\n'
                                                              f'MISSING CDFS WILL BE ADDED.\r\n'
                                                              f' THIS MAY TAKE SOME TIME.\r\n')
            except Exception as e:
                send_general_error_email(e)
                cdfApiLogger.error(f'Error rebuilding flags. \r\n {e}')
        return render_template('rebuild_cdfs.html', title='Rebuild CDF Data', form=RebuildForm())
    else:
        return redirect(url_for('main.about'))