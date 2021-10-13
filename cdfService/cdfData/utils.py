from flask import jsonify, request
from cdfService.cdfData.schemas import CDF_DATA, CDFNamesSchema
from cdfService.logging.cdfAPILogging import cdfApiLogger
from cdfService.email.email import send_general_error_email


@cdfApiLogger.catch()
def webappSmallList(key: str):
    """
    Function for 'searchable' endpoint.
    Returns a list cdf names and id keys matching the supplied search string.

    Args:
        key (str): search string submitted in url of GET request.

    Returns:
        results (json): {'CDF_NAME':'', 'ID_KEY':''}
    """
    cdfApiLogger.info(f'LIST REQUESTED WITH KEY {key}', exc_info=True)
    search = f'{key}'
    try:
        page = request.args.get('page', 1, type=int )
        some_cdfs = CDF_DATA.query.filter(CDF_DATA.CDF_NAME.like('%' + search + '%')).paginate(page=page, per_page=50)
        result = CDFNamesSchema.dump(some_cdfs)
        cdfApiLogger.info(f'{result}')
        return result
    except Exception as e:
        send_general_error_email(e)
        cdfApiLogger.error(f'error \r\n {e}', exc_info=True)
        return jsonify({'message':f'Error getting list for search criteria {key}'})