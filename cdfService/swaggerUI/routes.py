from flask_swagger_ui import get_swaggerui_blueprint


SWAGGER_URL = '/swagger'
API_URL_QA = '/static/swagger_qa.json'
API_URL_DEV = '/static/swagger_dev.json'

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL_DEV,
    config={
        'app_name': "CDF Service API"
    }
)


@SWAGGERUI_BLUEPRINT.route(SWAGGER_URL)
def swagger():
    return SWAGGERUI_BLUEPRINT
