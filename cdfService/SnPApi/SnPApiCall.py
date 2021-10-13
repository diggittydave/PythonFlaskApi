import requests
import uuid

def snp_soap_request(username, password, url):
    #url = "http://devspcentral.chq.ei:8121/spsaop/services/SPWebService?wsdl"
    #headers = {'content-type': 'application/soap+xml'}
    headers = {'content-type': 'text/xml'}

    body = f"""<?xml version="1.0" encoding="UTF-8"?>
                    <SOAP-ENV:Envelope
                    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                    xmlns:sp="http://www.expeditors.com/ns/SPWebService"
                    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> 
                        <SOAP-ENV:Body> 
                            <sp:getSPInfo version="1.0"
                                xmlns="http://www.expd.com/ns/securityandprofiles/v1"
                                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                                <header
                                xmlns="http://www.expd.com/ns/securityandprofiles/v1"
                                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                                    <appID>CDF Service</appID>  
                                    <messageID>Request ID{ uuid.uuid4() }</messageID>  
                                </header>
                                <credentials 
                                xmlns="http://www.expd.com/ns/securityandprofiles/v1"
                                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> 
                                    <username>{username}</username>  
                                    <password>{password}</password>  
                                </credentials> 
                                <settingKeyPattern>%</settingKeyPattern>  
                                <permissionKeyPattern>%</permissionKeyPattern>  
                                <detailKeyPattern>%</detailKeyPattern>  
                            </sp:getSPInfo> 
                        </SOAP-ENV:Body> 
                    </SOAP-ENV:Envelope> 
            """

    response = requests.post(url,data=body,headers=headers)

    print(response.content)
    
    return response


def parse_response(response):
    pass


def update_user(response):
    pass

