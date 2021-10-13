from cdfService import db, ma, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    """Login Manger

    Args:
        user_id (str): passed from user login page.

    Returns:
        int: user Id
    """
    return User.query.get(user_id)


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
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cdf_filter = db.Column(db.Boolean, nullable=False)
    cdf_data = db.Column(db.Boolean, nullable=False)
    cdf_filter_view = db.Column(db.Boolean, nullable=False)
    cdf_data_view = db.Column(db.Boolean, nullable=False)
    date_updated = db.Column(db.String(50))

    def __init__(self, public_id, email, cdf_filter, cdf_data, cdf_filter_view, cdf_data_view, date_updated):
        self.public_id = public_id
        self.email = email
        self.cdf_filter = cdf_filter
        self.cdf_data = cdf_data
        self.cdf_filter_view = cdf_filter_view
        self.cdf_data_view = cdf_data_view
        self.date_updated = date_updated


class UserSchema(ma.Schema):
    """cdfService.database.schemas.UserSchema\r\n
    User schema returning data from the User table.\r\n
    These are used in the web interface on the users pages.\rn

    Args:
        ma (instance): Flask-Marshmallow object defined in __init__.py
    """
    class Meta:
        fields = ('public_id', 'cdf_filter', 'cdf_data', 'cdf_filter_view', 'cdf_data_view')


UserSchema = UserSchema(many=True)
