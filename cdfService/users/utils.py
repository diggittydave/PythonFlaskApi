from cdfService.users.schemas import User
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService import db
from flask import jsonify
import uuid
import datetime
from cdfService.email.email import send_general_error_email


@cdfApiLogger.catch()
def get_response(client, username: str, password: str, settingKeyPattern: str, permissionKeyPattern: str,
                 detailKeyPattern: str, version: str):
    """Uses zeep module to conduct a SOAP call to S&P. The call is to retrieve user permissions for the CDF API.

    Args:
        client (object): Destination for SOAP Call. Contains wsdl settings for zeep module parsing.
        username (str): Username passed in from login or token gen call.
        password (str): Passed in from login or token gen call. Not stored in any way.
        settingKeyPattern (str): Search pattern to limit return response results.
        permissionKeyPattern (str): Search pattern to limit return response results.
        detailKeyPattern (str): Search pattern to limit return response results.
        version (str): Version number.

    Returns:
        response[dict]: SOAP Response in dictionary format for use in outer function.
    """
    header = {'appID': 'CDFService', 'messageID': f'{uuid.uuid4()}'}
    credentials = {'username': f'{username}', 'password': f'{password}'}
    try:
        response = client.service.getSPInfo(header=header,
                                            credentials=credentials,
                                            settingKeyPattern=settingKeyPattern,
                                            permissionKeyPattern=permissionKeyPattern,
                                            detailKeyPattern=detailKeyPattern,
                                            version=version)
        cdfApiLogger.info(f"Fetching user permissions for {credentials['username']} for app {header['appID']}")
        cdfApiLogger.info(f"{response['status']}")
        return response
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'ERROR IN GETTING RESPONSE FROM IDM!\r\n {e}')
        return response


@cdfApiLogger.catch()
def user_perms_from_response(username: str, password: str, client):
    """Function to parse permissions from SOAP response.

    Args:
        username (str): Username passed in from login or token gen call.
        password (str): Passed in from login or token gen call. Not stored in any way.
        client (object): Destination for SOAP Call. Contains wsdl settings for zeep module parsing.

    Returns:
        user[dict]: Contains status and permissions for user attempting to log in or generate a token.
    """
    user = {'user_data': {}, 'permissions': {}}
    prod_response = get_response(client, username, password, '%', '%CDFServiceAPI%', '%', '1.0')
    status = str(prod_response['status'])
    if 'OK' in status:
        user['status'] = prod_response['status']
        if len(prod_response['permission']) > 0:
            cdfApiLogger.info("passed check 1")
            for i in range(len(prod_response['permission'])):
                appPerm = prod_response['permission'][i]['nameAction']
                permission = prod_response['permission'][i]['allowed']
                user['permissions'][f'{appPerm}'] = permission
            for i in range(len(prod_response['detail'])):
                user_detail = prod_response['detail'][i]['userDetailsKey']
                value = prod_response['detail'][i]['value']
                user['user_data'][f'{user_detail}'] = value
            user['appID'] = prod_response['header']['appID']
            user['messageID'] = prod_response['header']['messageID']
            return user
        else:
            return user
    else:
        user['status'] = str(prod_response['status'])
        return user


@cdfApiLogger.catch()
def update_user_perms(user, snp_user):
    """Updates locally stored permissions for user based on snp_response.

    Args:
        user (dict, class): User class, queried from local database. Only contains permissions and username. Always updated upon login for each user.
        snp_user (dict): S&P response dictionary containing current permissions according to S&P and IDM.

    Returns:
        user(dict, class): Updated user permissions.
    """
    # cdf data modification permissions
    try:
        if snp_user['permissions']['CDFServiceAPI.cdf_data.ACTION_UPDATE']:
            user.cdf_data = snp_user['permissions']['CDFServiceAPI.cdf_data.ACTION_UPDATE']
    except:
        user.cdf_data = False
    # cdf data view only permissions
    try:
        if snp_user['permissions']['CDFServiceAPI.cdf_data_view.ACTION_VIEW']:
            user.cdf_data_view = snp_user['permissions']['CDFServiceAPI.cdf_data_view.ACTION_VIEW']
    except:
        user.cdf_data_view = False
    # cdf filter modification Permissions
    try:
        if snp_user['permissions']['CDFServiceAPI.cdf_filter.ACTION_UPDATE']:
            user.cdf_filter = snp_user['permissions']['CDFServiceAPI.cdf_filter.ACTION_UPDATE']
    except:
        user.cdf_filter = False
    # cdf filter view only permissions
    try:
        if snp_user['permissions']['CDFServiceAPI.cdf_filter_view.ACTION_VIEW']:
            user.cdf_filter_view = snp_user['permissions']['CDFServiceAPI.cdf_filter_view.ACTION_VIEW']
    except:
        user.cdf_filter_view = False
    user.date_updated = datetime.datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'{e}', exc_info=True)
    return user


@cdfApiLogger.catch()
def insert_user(snp_user):
    """Function for inserting first time users into local DB. Only used for login and token gen functionality. No other user data is stored.

    Args:
        snp_user (dict): S&P response dictionary.

    Returns:
        inserted_user(dict, class): Queried user after insert, to ensure login process can occur.
    """
    current_date = datetime.datetime.now()
    username = snp_user['user_data']['USERNAME'] # in dev use 'USERNAME', in prod, use 'ITIM_EMPLOYEE_ID' #
    user = User(public_id=username,
                email=snp_user['user_data']['EMAIL_ADDRESS'],
                cdf_data=snp_user['permissions']['CDFServiceAPI.cdf_data.ACTION_UPDATE'],
                cdf_data_view=snp_user['permissions']['CDFServiceAPI.cdf_data_view.ACTION_VIEW'],
                cdf_filter=snp_user['permissions']['CDFServiceAPI.cdf_filter.ACTION_UPDATE'],
                cdf_filter_view=snp_user['permissions']['CDFServiceAPI.cdf_filter_view.ACTION_VIEW'],
                date_updated=current_date)
    try:
        db.session.add(user)
        db.session.commit()
        cdfApiLogger.info(f'Added user: {user.public_id}')
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'{e}', exc_info=True)
        return jsonify({'error': f"{e}"})
    inserted_user = User.query.filter_by(public_id=username).first()
    return inserted_user

@cdfApiLogger.catch()
def snp_validate(snp_user: dict):
    """Validates User already exists within local login data. If the user exists, the permissions are updated with current response from S&P.
    If the user does not exist, a local copy is created and then logged in.

    Args:
        snp_user (dict): S&P response dictionary.

    Returns:
        user[dict,class]: User data.
    """
    cdfApiLogger.info(f'validating {snp_user}')
    username = snp_user['user_data']['USERNAME']
    try:
        user = User.query.filter_by(public_id=username).first()
        if user:
            update_user = update_user_perms(user, snp_user)
            return update_user
        else:
            user = insert_user(snp_user)
            return user
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'{e}', exc_info=True)
        user = insert_user(snp_user)
        return user


# if __name__ == '__main__':
    # user_perms_from_response('chq-davidwe', '', prod_client)
    # user_perms_from_response('chq-davidwe', '', qa_client)
    # print(user_perms_from_response('chq-davidwe', 'st@rtup1', dev_client))
