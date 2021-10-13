import sqlite3 as lite
from flask import current_app, redirect, url_for
from cdfService.cdfData.schemas import CDF_DATA, CDFNamesSchema, CDFContentSchema
from cdfService.users.schemas import User
import jwt
import datetime
from flask import jsonify, request, make_response
from functools import wraps
from cdfService import basedir
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.users.utils import user_perms_from_response, snp_validate
from cdfService.email.email import send_cdf_error_email, send_general_error_email
from cdfService.config import ConfigClass


@cdfApiLogger.catch()
def smallList(key: str):
    """
    Function for 'searchable' endpoint.
    Returns a list cdf names and id keys matching the supplied search string.

    Args:
        key (str): search string submitted in url of GET request.

    Returns:
        results (json): {'CDF_NAME':'', 'ID_KEY':''}
    """
    cdfApiLogger.info(f'LIST REQUESTED VIA API WITH KEY {key}')
    search = f'{key}'
    conn = lite.connect(basedir)
    try:
        some_cdfs = CDF_DATA.query.filter(CDF_DATA.CDF_NAME.like('%' + search + '%')).all()
        result = CDFNamesSchema.dump(some_cdfs)
        cdfApiLogger.info(f'RETURNING VALUES VIA JSON RESPONSE: \r\n {result}')
        return jsonify(result)
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'error \r\n {e}', exc_info=True)
        return jsonify({'message':f'Error getting list for search criteria {key}'})


@cdfApiLogger.catch()
def allCDF():
    """
    Function to return a list of all cdf's with their id_key.\r\n
    Returns json object with all available cdfs.\r\n

    Returns:
        results (json): {'CDF_NAME':'', 'ID_KEY':''}
    """
    cdfApiLogger.info("FULL CDF LIST REQUESTED VIA API CALL.")
    files = {}
    try:
        all_cdfs = CDF_DATA.query.all()
        result = CDFNamesSchema.dump(all_cdfs)
        cdfApiLogger.info("RETURNING FULL LIST VIA JSON RESPONSE TO SERVICE CATALOG.")
        return jsonify(result)
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'Error \r\n {e}' + str(e), exc_info=True)
        return jsonify({'message': 'Error getting list'})


@cdfApiLogger.catch()
def getCDF(idKey):
    """
    Function to get a single cdf data-set\r\n
    Returns a json object with all required information about a CDF.\r\n

    Args:
        idKey (str): Id Key for cdf in GET request url.\r\n

    Returns:
        results0 json: {'ID_KEY':'', 'CDF_NAME':'', 'CDF_PATH':'',\r\n
        'Is_Restricted':'', 'Approvers':'', 'Date_Updated':'', 'HEADER':'',\r\n
        'NUMBER_OF_COLUMNS':'', 'FILE_CONTENTS':'', 'LAST_UPD_BY' :'',\r\n
        'Requires_Approval':'', 'SERVICE':''}\r\n
    """
    i = 0
    cdfApiLogger.info(f"Received request for key {idKey}")
    cdfApiLogger.info("trying " + str(idKey))
    try:
        cdf = CDF_DATA.query.filter_by(ID_KEY=idKey).first()
        contents = str(cdf.FILE_CONTENTS, encoding='ISO-8859-1')
        cdf.FILE_CONTENTS = contents
        result0 = CDFContentSchema.dump(cdf)
        if len(result0) > 1:
            result0.update({'SERVICE': 'NONE'})
            if 'TRUE' in result0['Is_Restricted']:
                result0.update({'FILE_CONTENTS': f"You can proceed with your CDF request, however, please note there may be a delay in your request as this is a ‘restricted CDF’ and will require Support to coordinate with the EDI Department"})
            if 'TRUE' in result0['Transportation']:
                result0.update({"SERVICE": "Transportation"})
            if 'TRUE' in result0['OM']:
                result0.update({"SERVICE": "OM"})
            if 'TRUE' in result0['Billing']:
                result0.update({"SERVICE": "Billing"})
            cdfApiLogger.info(f"Returning {result0['CDF_NAME']} via API Call")
            return jsonify(result0)
        else:
            return jsonify({"msg": f"A CDF with ID Key {idKey} does not exist."})
    except Exception as e:
        send_cdf_error_email(error=e, cdf_name=cdf.CDF_NAME)
        cdfApiLogger.error(f"A problem was found with idKey {cdf.CDF_NAME}\r\n {e}", exc_info=True)
        return jsonify({"msg": "Error finding your CDF. Please check the logs."})


@cdfApiLogger.catch()
def login_service(auth):
    """
    Uses basic authentication to return a jwt token.
    jwt tokens are used in GET/POST api calls.

    Args:
        auth (authentication): Basic Authentication request sent in the form of a get/post.

    Returns:
        token (json): Json object containing both the public id and the generated token. 
        message (json): response based on failures in login process.
    """
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify username or password', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    snp_check = user_perms_from_response(auth.username, auth.password, ConfigClass.SNP_Client)
    cdfApiLogger.info(f" Fetching {snp_check}")
    user = User.query.filter_by(public_id=auth.username).first()
    if not user:
        snp_validate(snp_check)
    if ("OK" in snp_check['status']) and snp_check['permissions']['CDFServiceAPI.cdf_data_view.ACTION_VIEW']:
        user = User.query.filter_by(public_id=auth.username).first()
        cdfApiLogger.info(f"generating token for {user.public_id}")
        token = jwt.encode({'public_id': user.public_id,
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                           current_app.config['SECRET_KEY'])
        return jsonify({'public_id': user.public_id, 'token': token.decode('UTF-8')})
    return make_response('Could not verify password', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@cdfApiLogger.catch()
def token_required(f):
    """
    jwt token requirement wrapper
    Token is placed in the header of the API call

    Args:
        f (object): all contents of GET/POST request and header containing token:
         {<header>'x-access-token':'<token>'</header><body></body>}

    Returns:
        decorated object: Decorated object.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        """decodes and checks jwt token for validity.

        Returns:
            f (object): current user args and keyword args returned to wrapper.
        """
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return redirect(url_for('errors.403'), 403)
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
            cdfApiLogger.info('successful token check')
        except Exception as e:
            send_general_error_email(e)
            cdfApiLogger.error('Token is invalid!' + str(e), exc_info=True)
            return jsonify({'message': 'Token is invalid!' + str(e)}), 401
        return f(current_user, *args, **kwargs)
    return decorated

