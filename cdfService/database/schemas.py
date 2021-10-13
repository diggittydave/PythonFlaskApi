#<
# cdfservice.database.schemas
# contains schema classes used to return the json objects back after the database queries.
#>
from flask import current_app
from cdfService import db, ma, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    """Login Manger

    Args:
        user_id (str): passed from user login page.

    Returns:
        int: user Id
    """
    return User.query.get(int(user_id))


class CDF_DATA(db.Model):
    """cdfService.database.schemas.CDF_DATA 
    CDF Data Class/Model used in the list and cdf pulls

    Args:
        db (object): Database object defined in __init__.py and imported.
    """
    ID_KEY = db.Column(db.Integer, primary_key=True)
    CDF_NAME = db.Column(db.CHAR(200))
    CDF_PATH = db.Column(db.CHAR(200))
    Transportation = db.Column(db.CHAR, nullable=False)
    OM = db.Column(db.CHAR, nullable=False)
    Billing = db.Column(db.CHAR, nullable=False)
    Is_Restricted = db.Column(db.CHAR, nullable=False)
    Approvers = db.Column(db.CHAR(200))
    Date_Updated = db.Column(db.TIMESTAMP(50))
    HEADER = db.Column(db.CHAR(500))
    NUMBER_OF_COLUMNS = db.Column(db.Integer)
    FILE_CONTENTS = db.Column(db.BLOB)
    LAST_UPD_BY = db.Column(db.CHAR(200))
    Requires_Approval = db.Column(db.CHAR, nullable=True)

    def __init__(self, CDF_NAME, CDF_PATH, Transportation, OM, Billing, Affected_Service, Is_Restricted, Approvers,
                 Date_Updated, HEADER, NUMBER_OF_COLUMNS, FILE_CONTENTS, LAST_UPD_BY, Requires_Approval):
        self.CDF_NAME = CDF_NAME
        self.CDF_PATH = CDF_PATH
        self.Transportation = Transportation
        self.OM = OM
        self.Billing = Billing
        self.Affected_Service = Affected_Service
        self.Is_Restricted = Is_Restricted
        self.Approvers = Approvers
        self.Date_Updated = Date_Updated
        self.CDF_HEADER = HEADER
        self.NUMBER_OF_COLUMNS = NUMBER_OF_COLUMNS
        self.FILE_CONTENTS = FILE_CONTENTS
        self.LAST_UPD_BY = LAST_UPD_BY
        self.Requires_Approval = Requires_Approval


class CDF_UPDATE_FILTERS(db.Model):
    """cdfService.database.schemas.CDF_UPDATE_FILTERS
    Filters schema allows users to modify the filters available.
    This class is mainly used in the web interface.
    Args:
        db (object): Database object defined in __init__.py and imported.
    """
    RESTRICTION = db.Column(db.String(200), primary_key=True, unique=True)
    SERVICE = db.Column(db.String(50))
    ADDED_BY = db.Column(db.String(200))

    def __init__(self, RESTRICTION, SERVICE, ADDED_BY):
        self.RESTRICTION = RESTRICTION
        self.SERVICE = SERVICE
        self.ADDED_BY = ADDED_BY


class User(db.Model, UserMixin):
    """cdfService.database.schemas.Current_Users
    User Table class/model.
    Used in user creation, authentication, and updating user permissions.

    Args:
        db (object): Database object defined in __init__.py and imported.
        UserMixin (Module): Allows user password reset functionality.

    Returns:
        s.dumps (str): Unique Token value based on username and secret key. Used to access password reset page.
        User.query.get (str): Returns username after decoding token.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    cdf_filter = db.Column(db.Boolean, nullable=False)
    cdf_data = db.Column(db.Boolean, nullable=False)
    User_Admin = db.Column(db.Boolean, nullable=False)
    cdf_filter_view = db.Column(db.Boolean, nullable=False)
    cdf_data_view = db.Column(db.Boolean, nullable=False)
    updated_by = db.Column(db.CHAR(200))
    date_updated = db.Column(db.String(50))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __init__(self, id, public_id, name, email, password, admin, cdf_filter, cdf_data, User_Admin, cdf_filter_view, cdf_data_view, updated_by, date_updated):
        self.public_id = public_id
        self.name = name
        self.email = email
        self.password = password
        self.admin = admin
        self.cdf_filter = cdf_filter
        self.cdf_data = cdf_data
        self.User_Admin = User_Admin
        self.cdf_filter_view = cdf_filter_view
        self.cdf_data_view = cdf_data_view
        self.updated_by = updated_by
        self.date_updated = date_updated
        

class Removed_Users(db.Model, UserMixin):
    """cdfService.database.schemas.Removed_Users
    Deleted User Table class/model.
    For tracking historical/removed users.

    Args:
        db (object): Database object defined in __init__.py and imported.
        UserMixin (Module): Allows user password reset functionality.

    Returns:
        s.dumps (str): Unique Token value based on username and secret key. Used to access password reset page.
        User.query.get (str): Returns username after decoding token.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    cdf_filter = db.Column(db.Boolean, nullable=False)
    cdf_data = db.Column(db.Boolean, nullable=False)
    User_Admin = db.Column(db.Boolean, nullable=False)
    cdf_filter_view = db.Column(db.Boolean, nullable=False)
    cdf_data_view = db.Column(db.Boolean, nullable=False)
    updated_by = db.Column(db.CHAR(200))
    date_updated = db.Column(db.TIMESTAMP(50))

    def __init__(self, id, public_id, name, email, admin, cdf_filter, cdf_data, User_Admin, cdf_filter_view, cdf_data_view, updated_by, date_updated):
        self.public_id = public_id
        self.name = name
        self.email = email
        self.admin = admin
        self.cdf_filter = cdf_filter
        self.cdf_data = cdf_data
        self.User_Admin = User_Admin
        self.cdf_filter_view = cdf_filter_view
        self.cdf_data_view = cdf_data_view
        self.updated_by = updated_by
        self.date_updated = date_updated
        

class CDFContentSchema(ma.Schema):
    """cdfService.database.schemas.CDFContentSchema\r\n
    cdf schema returns all data from CDF-INFO table.\r\n
    Args:
        ma (instance): Flask-Marshmallow object defined in __init__.py
    """
    class Meta:
        fields = ('ID_KEY', 'CDF_NAME', 'CDF_PATH', 'Transportation', 'OM', 'Billing', 'Is_Restricted', 'Approvers',
                  'Date_Updated', 'HEADER', 'NUMBER OF COLUMNS', 'FILE_CONTENTS', 'LAST_UPD_BY', 'Requires_Approval')


class CDFNamesSchema(ma.Schema):
    """cdfService.database.schemas.CDFNamesSchema\r\n
    list schema returns only the cdf name and id key from the CDF-INFO table.\r\n
    used by api service calls.\r\n

    Args:
        ma (instance): Flask-Marshmallow object defined in __init__.py
    """

    class Meta:
        fields = ('CDF_NAME', 'ID_KEY')


class UserSchema(ma.Schema):
    """cdfService.database.schemas.UserSchema\r\n
    User schema returning data from the User table.\r\n
    These are used in the web interface on the users pages.\rn

    Args:
        ma (instance): Flask-Marshmallow object defined in __init__.py
    """
    class Meta:
        fields = ('public_id', 'name', 'admin', 'email', 'cdf_filter', 'cdf_data', 'User_Admin', 'cdf_filter_view', 'cdf_data_view', 'updated_by', 'date_updated')


class FiltersSchema(ma.Schema):
    """cdfService.database.schemas.FiltersSchema\r\n
    Schema returning the filters data.\r\n
    Used in the web interface on the Filters pages.\r\n

    Args:
        ma (instance): Flask-Marshmallow object defined in __init__.py
    """
    class Meta:
        fields = ('RESTRICTION', 'SERVICE')


#<
# init schemas
# Each schema has a set number of items it can return.
#>
CDFNamesSchema = CDFNamesSchema(many=True)
CDFContentSchema = CDFContentSchema(many=False)
FiltersSchema = FiltersSchema(many=True)
UserSchema = UserSchema(many=True)