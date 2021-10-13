from flask import (jsonify, request, Blueprint)
from cdfService.cdfApi.utils import (allCDF, getCDF, smallList, login_service, token_required)
from cdfService.cdfApi.patchUtils import post_change
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.email.email import send_general_error_email

cdfApi = Blueprint('cdfApi', '__name__')


@cdfApiLogger.catch()
@cdfApi.route('/api/cdf/list/<key>', methods=['GET'])
@token_required
def get_cdfs(current_user, key):
    """Gets a list of CDFs based on a search key in the GET request URL.

    Args:
        current_user (str): current user id, passed in from the @token_required wrapper.
        key (str): string used to search for a limited list of CDFs.

    Returns:
        smallList (json): json object containing all cdf names and id keys where the cdf matches the search string.
        message (json): json object containing respons message based on failure type.
    """
    if current_user.cdf_data_view:
        if key:
            return smallList(key)
        else:
            return jsonify({"message": "No search criteria submitted."})
    else:
        return jsonify({"message": "cannot perform this function"})


@cdfApiLogger.catch()
@cdfApi.route('/api/cdf/list', methods=['GET'])
@token_required
def get_ALL_cdfs(current_user):
    """Route returns comprehensive list of all cdf names paired with their ID key.

    Args:
        current_user (str): current user id, passed in from the @token_required wrapper.

    Returns:
        allCDF (json): json object containing all cdf names and their corresponding ID keys.
    """
    if current_user.cdf_data_view:
        return allCDF()
    else:
        return jsonify({"message":"cannot perform this function"})


@cdfApiLogger.catch()
@cdfApi.route('/api/cdf/ID_KEY/<ID_KEY>', methods=['GET'] )
@token_required
def get_cdf(current_user, ID_KEY):
    """Route returns all data on a single CDF based on the ID Key in the url.

    Args:
        current_user (str): current user id, passed in from the @token_required wrapper.
        ID_KEY (str): ID Key of the CDF being requested. Is passed into getCDF() function.

    Returns:
        getCDF json: Json object containing all relevent data on requested CDF.
    """
    if current_user.cdf_data_view:
        return getCDF(ID_KEY)
    else:
        return jsonify({"message": "You do not have access to view this data!"})


@cdfApiLogger.catch()
@cdfApi.route('/api/cdf/update/ID_KEY/<ID_KEY>', methods=['POST'])
@token_required
def post_cdf_change(current_user, ID_KEY):
    """Post a change to a CDF.

    Args:
        current_user (str): current user id, passed in from the @token_required wrapper.
        ID_KEY (str): ID Key of the CDF being updated. Is passed into post_change function.

    Returns:
        message (json): Message based on success/failure of changes to the cdf.
    """
    if current_user.cdf_data_view:
        data = request.get_json()
        cdfApiLogger.info(f'Post action to CDF {ID_KEY} :contents {data}', exc_info=True)
        try:
            return post_change(ID_KEY, data)
        except Exception as e:
            send_general_error_email(e)
            cdfApiLogger.error(f'error in posting data {data} to cdf {ID_KEY}\r\n {e}')


@cdfApiLogger.catch()
@cdfApi.route('/api/token_gen')
def token_gen():
    """Token Generation endpoint.

    Returns:
        login_service(): JWT Basic authorization object with public ID and jwt token.
    """
    auth = request.authorization
    try:
        return login_service(auth)
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'ERROR Logging in user! \r\n {e}')

