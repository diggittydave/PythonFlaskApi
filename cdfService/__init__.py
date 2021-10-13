#<
# cdfService.__init__.py
# Primary app initializations.
# Primary app packages are imported and primary app settings are set.
#>
from flask import Flask, jsonify, request, Blueprint
from cdfService.services.appVariables import basedir, ca_cert
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_restplus import Api
from flask_mail import Mail
from cdfService.config import ConfigClass, Config_QA


# init bootstrap
Bootstrap()
# init db suite
db = SQLAlchemy()
# init marshmallow
ma = Marshmallow()
# init encryption suite
bcrypt = Bcrypt()
# init login management and retention suite.
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()
# init flask-RESTPlus
api = Api()


def create_app(config_class=ConfigClass):
    app = Flask(__name__)
    app.config.from_object(ConfigClass)
    # init bootstrap
    # init db suite
    db.init_app(app)
    # init marshmallow
    ma.init_app(app)
    # init encryption suite
    bcrypt.init_app(app)
    # init login management and retention suite.
    login_manager.init_app(app)
    # mail
    mail.init_app(app)
    # init flask-RESTPlus
    api.init_app(app)
    # import webapp blueprints
    from cdfService.cdfData.routes import cdfData
    from cdfService.cdfFilters.routes import cdfFilter
    from cdfService.users.routes import users
    from cdfService.main.routes import main
    from cdfService.webchecks.routes import webchecks
    # register webapp blueprints
    app.register_blueprint(cdfData)
    app.register_blueprint(cdfFilter)
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(webchecks)
    # import api blueprint used by service catalog:
    from cdfService.cdfApi.routes import cdfApi
    # register api blueprint
    app.register_blueprint(cdfApi)
    # swaggerui creation
    from cdfService.swaggerUI.routes import SWAGGERUI_BLUEPRINT
    app.register_blueprint(SWAGGERUI_BLUEPRINT)
    #email sender api
    #from cdfService.email.routes import emailApi
    #app.register_blueprint(emailApi)

    return app
