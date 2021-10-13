from cdfService.email.email import send_general_error_email
from flask import flash, redirect, render_template, request, url_for, Blueprint, Response
from flask_login import current_user, login_required
from cdfService import db
from cdfService.cdfData.schemas import CDF_DATA
from cdfService.cdfFilters.utils import startRebuildProcs, download_filters
from cdfService.cdfFilters.schemas import CDF_UPDATE_FILTERS
from cdfService.users.schemas import User
from cdfService.cdfFilters.forms import FilterForm, ReloadForm, FilterSearchForm
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.users.utils import user_perms_from_response
from cdfService.config import ConfigClass
import concurrent.futures

cdfFilter = Blueprint('cdfFilter', '__name__')


@cdfApiLogger.catch()
@cdfFilter.route('/webapp/Filter/search/starts_with/<key>', methods=['GET','POST'])
@login_required
def webapp_filter_start_search_key(key):
    """A page containing Results of search. Also can search for new string on page.    
    Args:
        key ([int]): Id Key of CDF stored in database.

    Returns:
        Webpage: Rendes data in table containing ID key hyper link and CDF Name.
    """
    if current_user.is_authenticated and (current_user.cdf_filter or current_user.cdf_filter_view):
        form = FilterSearchForm()
        if key:
            page = request.args.get('page', 1, type=int )
            some_filters = CDF_UPDATE_FILTERS.query.filter(CDF_UPDATE_FILTERS.RESTRICTION.like(key + '%', escape='/')).order_by(CDF_UPDATE_FILTERS.RESTRICTION).paginate(page=page, per_page=25)
            if form.validate_on_submit():
                key = form.search.data
                cdfApiLogger.info(f'{current_user} searching for  {key}')
                if form.starts_with.data and not form.contains.data:
                    return redirect(url_for('cdfFilter.webapp_filter_start_search_key', key=key))
                if form.contains.data and not form.starts_with.data:
                    return redirect(url_for('cdfFilter.webapp_filter_contain_search_key', key=key))
                if form.contains.data and form.starts_with.data:
                    return redirect(url_for('cdfFilter.webapp_filter_contain_search_key', key=key))
            return render_template('filter_search_starts_results.html', title='FILTER SEARCH RESULTS', form=form, posts=some_filters, key=key)
        else:
            key = ''
            page = request.args.get('page', 1, type=int)
            some_filters = CDF_UPDATE_FILTERS.query.filter(CDF_UPDATE_FILTERS.RESTRICTION.like(key + '%', escape='/')).order_by(CDF_UPDATE_FILTERS.RESTRICTION).paginate(page=page, per_page=25)
            cdfApiLogger.info(f'{current_user} searching for  {key}')
            return render_template('filter_search_start_results.html', title='FILTER SEARCH RESULTS', form=form, posts=some_filters, key=key)
    else:
        return redirect(url_for('main.about'))


@cdfApiLogger.catch()
@cdfFilter.route('/webapp/Filter/search/contains/<key>', methods=['GET', 'POST'])
@login_required
def webapp_filter_contain_search_key(key):
    """A page containing Results of search. Also can search for new string on page.
    Args:
        key ([int]): Id Key of CDF stored in database.

    Returns:
        Webpage: Rendes data in table containing ID key hyper link and CDF Name.
    """
    if current_user.is_authenticated and (current_user.cdf_filter or current_user.cdf_filter_view):
        form = FilterSearchForm()
        if key:
            page = request.args.get('page', 1, type=int )
            some_filters = CDF_UPDATE_FILTERS.query.filter(CDF_UPDATE_FILTERS.RESTRICTION.like('%' + key + '%', escape='/')).order_by(CDF_UPDATE_FILTERS.RESTRICTION).paginate(page=page, per_page=25)
            if form.validate_on_submit():
                key = form.search.data
                cdfApiLogger.info(f'{current_user} searching for  {key}')
                if form.starts_with.data and not form.contains.data:
                    return redirect(url_for('cdfFilter.webapp_filter_start_search_key', key=key))
                if form.contains.data and not form.starts_with.data:
                    return redirect(url_for('cdfFilter.webapp_filter_contain_search_key', key=key))
                if form.contains.data and form.starts_with.data:
                    return redirect(url_for('cdfFilter.webapp_filter_contain_search_key', key=key))
            return render_template('filter_search_contain_results.html', title='FILTER SEARCH RESULTS', form=form, posts=some_filters, key=key)
        else:
            key = ''
            page = request.args.get('page', 1, type=int)
            some_filters = CDF_UPDATE_FILTERS.query.filter(CDF_UPDATE_FILTERS.RESTRICTION.like('%' + key + '%', escape='/')).order_by(CDF_UPDATE_FILTERS.RESTRICTION).paginate(page=page, per_page=25)
            cdfApiLogger.info(f'{current_user} searching for  {key}')
            return render_template('filter_search_contain_results.html', title='FILTER SEARCH RESULTS', form=form, posts=some_filters, key=key)
    else:
        return redirect(url_for('main.about'))


@cdfApiLogger.catch()
@cdfFilter.route('/webapp/filter/<RESTRICTION>', methods=['GET', 'POST'])
@login_required
def filter(RESTRICTION):
    """Route for viewing an individual filter flag. Can be used to remove a flag.

    Args:
        RESTRICTION (str): regex string of filter/flag.

    Returns:
        redirect: If filter is removed, the page will redirect to 'filters'.
        render_template: template for filter.html
        redirect: if user does not have access, user is redirected to 'HOME'.
    """
    form = FilterForm()
    filter1 = CDF_UPDATE_FILTERS.query.get_or_404(RESTRICTION)
    filter2 = str(filter1).split(' ')
    if current_user.is_authenticated and current_user.cdf_filter:
        try:
            if '^' in RESTRICTION:
                cdfApiLogger.info("selecting starting with '^'")
                testing = str(RESTRICTION).replace('^', '')
                affected_cdfs = CDF_DATA.query.filter(CDF_DATA.CDF_NAME.like(f'{testing}%', escape='/')).order_by(
                    CDF_DATA.CDF_NAME).all()
                if '_' in testing:
                    cdfApiLogger.info("selecting escape string with '_'")
                    testing = testing.replace('_', '/_')
                    cdfApiLogger.info(f'{testing}')
                    affected_cdfs = CDF_DATA.query.filter(CDF_DATA.CDF_NAME.like(f'{testing}%', escape='/')).order_by(CDF_DATA.CDF_NAME).all()
            else:
                affected_cdfs = CDF_DATA.query.filter(CDF_DATA.CDF_NAME.like(f'%{RESTRICTION}%', escape='/')).order_by(CDF_DATA.CDF_NAME).all()
            if form.validate_on_submit():
                remove = form.filter.data
                try:
                    if remove in filter2[1]:
                        flash('Filter removed', 'success')
                        db.session.delete(filter1)
                        db.session.commit()
                        cdfApiLogger.info(f'Filter {filter2}', exc_info=True)
                        return redirect(url_for('cdfFilter.filter_switch'))
                    else:
                        flash('FILTER NOT REMOVED', 'error')
                        return redirect(url_for('cdfFilter.filters'))
                except Exception as e:
                    send_general_error_email(e)
                    cdfApiLogger.error(f'ERROR UPDATING FILTERS! \r\n {e}')
            return render_template('filter.html', title='Restriction', form=FilterForm(),
                                   post=filter1, affected_cdfs=affected_cdfs)
        except Exception as e:
            send_general_error_email(e)
            cdfApiLogger.error(f'{e}', exc_info=True)
    else:
        return redirect(url_for('main.about'))


@cdfApiLogger.catch()
@cdfFilter.route('/webapp/filters/reload', methods=['GET', 'POST'])
@login_required
def filter_reload():
    """Route to the reload flags funtion.
    The function resets all flags based on entries added or removed from the filters list.

    Returns:
        render_template: html template for reload.html.
        redirect: upon successful form submit, redirects to 'about'.
        redirect: if user does not have access, user is redirected to 'about'.
    """
    form = ReloadForm()
    if current_user.is_authenticated and current_user.cdf_filter:
        if form.validate_on_submit():
            try:
                pool = concurrent.futures.ThreadPoolExecutor()
                snp_user = user_perms_from_response(form.id.data, form.password.data, ConfigClass.SNP_Client)
                user = User.query.filter_by(public_id=form.id.data).first()
                pool.submit(startRebuildProcs, user)
                return redirect(url_for('main.about')), flash(f'REBUILDING FLAGS FOR CDF TABLE. THIS MAY TAKE SOME TIME.')
            except Exception as e:
                send_general_error_email(e)
                cdfApiLogger.error(f'Error rebuilding flags. \r\n {e}')
        return render_template('reload.html', title='Reload_Filters', form=ReloadForm())
    else:
        return redirect(url_for('main.about'))


@cdfApiLogger.catch()
@cdfFilter.route('/webapp/filter_switch', methods=['GET', 'POST'])
@login_required
def filter_switch():
    """Filter selection switch.

    Returns:
        render_template: html template for filter_switch.html
        redirect: If user is not logged in, user is redirected to login page.
    """
    if current_user.is_authenticated and (current_user.cdf_filter_view or current_user.cdf_filter):
        form = FilterSearchForm()
        try:
            if form.validate_on_submit():
                key = form.search.data
                if form.starts_with.data and not form.contains.data:
                    return redirect(url_for('cdfFilter.webapp_filter_start_search_key', key=key))
                if form.contains.data and not form.starts_with.data:
                    return redirect(url_for('cdfFilter.webapp_filter_contain_search_key', key=key))
                if form.contains.data and form.starts_with.data:
                    return redirect(url_for('cdfFilter.webapp_filter_contain_search_key', key=key))
            cdfApiLogger.info(f'Redirected to filter_switch.html.')
            return render_template('filter_switch.html', title='filter_switch', form=form)
        except Exception as e:
            send_general_error_email(e)
            cdfApiLogger.error(f'Error in redirect. \r\n {e}')
    else:
        return redirect(url_for('main.about'))


@cdfApiLogger.catch()
@cdfFilter.route('/webapp/filter_switch/<RESTRICTION>', methods=['GET','POST'])
@login_required
def filter_list(RESTRICTION):
    """Route for accessing the filters list.

    Returns:
        render_template: html template for filters.html
        redirect: if user does not have access, will be redirected to 'about'
    """
    if current_user.is_authenticated and (current_user.cdf_filter_view or current_user.cdf_filter):
        form = FilterForm()
        page = request.args.get('page', 1, type=int)
        filters = CDF_UPDATE_FILTERS.query.filter(CDF_UPDATE_FILTERS.SERVICE.like(RESTRICTION)).order_by(CDF_UPDATE_FILTERS.RESTRICTION).paginate(page=page, per_page=25)
        if form.validate_on_submit():
            try:
                flash('New validation filter added.', 'success')
                post = CDF_UPDATE_FILTERS(SERVICE=form.service.data, RESTRICTION=form.filter.data, ADDED_BY=str(current_user.public_id))
                db.session.add(post)
                db.session.commit()
                cdfApiLogger.info(f'New filter added {post}', exc_info=True)
                return redirect(url_for('cdfFilter.filter_switch'))
            except Exception as e:
                send_general_error_email(e)
                cdfApiLogger.error(f'ERROR ADDING FILTER {post}. \r\n {e}')
        return render_template('filters.html', title='Filters', form=form, posts=filters, RESTRICTION=RESTRICTION)
    else:
        return redirect(url_for('main.about'))


@cdfApiLogger.catch()
@cdfFilter.route('/webapp/filter_download', methods=['GET'])
@login_required
def filter_download():
    if current_user.is_authenticated and (current_user.cdf_filter_view or current_user.cdf_filter):
        response = Response(download_filters(), mimetype='text/csv')
        response.headers.set("Content-Disposition", "attachment", filename='filters.csv')
        return response
    else:
        return redirect(url_for('main.about'))

