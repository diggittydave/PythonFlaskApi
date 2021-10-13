from cdfService import db, ma


class CDF_UPDATE_FILTERS(db.Model):
    """
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


class FiltersSchema(ma.Schema):
    """
    Schema returning the filters data.\r\n
    Used in the web interface on the Filters pages.\r\n

    Args:
        ma (instance): Flask-Marshmallow object defined in __init__.py
    """
    class Meta:
        fields = ('RESTRICTION', 'SERVICE')


FiltersSchema = FiltersSchema(many=True)
