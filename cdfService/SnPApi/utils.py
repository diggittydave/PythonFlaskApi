from zeep import Client
from zeep.transports import Transport
import uuid

from cdfService.email.email import send_general_error_email
from cdfService.logging.cdfAPILogging import cdfApiLogger


transport = Transport(timeout=10)

qa_client = Client('http://qaspcentral.chq.ei:8121/spsoap/services/SPWebService?wsdl', transport=transport)
dev_client = Client('http://devspcentral.chq.ei:8121/spsoap/services/SPWebService?wsdl', transport=transport)
prod_client = Client('http://spcentral.chq.ei:8121/spsoap/services/SPWebService?wsdl', transport=transport)


def get_response(client, username: str, password: str, settingKeyPattern:str, permissionKeyPattern: str,
                 detailKeyPattern: str, version: str):
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
        return response
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'ERROR IN GETTING RESPONSE FROM IDM!\r\n {e}')
        return response


def user_perms_from_response(username: str, password: str, client):
    user = {'user_data':{}, 'permissions': {}}
    prod_response = get_response(client, username, password, '%', '%', '%', '1.0')
    print(prod_response['status'])
    status = str(prod_response['status'])
    print(f'STATUS = {status}')
    if status == "['OK']":
        user['status'] = prod_response['status']
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
        print(user)
        return user
    else:
        user['status'] = prod_response['status']
        return user


if __name__ == '__main__':
    user_perms_from_response('chq-davidwe', '', prod_client)
    user_perms_from_response('chq-davidwe', '', qa_client)
    user_perms_from_response('chq-davidwe', '5ggD-tjWK', dev_client)
