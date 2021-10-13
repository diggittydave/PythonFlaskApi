from cdfService import db, ma

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


class CDFContentSchema(ma.Schema):
    """
    cdf schema returns all data from CDF-INFO table.\r\n
    Args:
        ma (instance): Flask-Marshmallow object defined in __init__.py
    """
    class Meta:
        fields = ('ID_KEY', 'CDF_NAME', 'CDF_PATH', 'Transportation', 'OM', 'Billing', 'Is_Restricted', 'Approvers',
                  'Date_Updated', 'HEADER', 'NUMBER_OF_COLUMNS', 'FILE_CONTENTS', 'LAST_UPD_BY', 'Requires_Approval')


class CDFNamesSchema(ma.Schema):
    """
    list schema returns only the cdf name and id key from the CDF-INFO table.\r\n
    used by api service calls.\r\n

    Args:
        ma (instance): Flask-Marshmallow object defined in __init__.py
    """

    class Meta:
        fields = ('CDF_NAME', 'ID_KEY')


CDFNamesSchema = CDFNamesSchema(many=True)
CDFContentSchema = CDFContentSchema(many=False)
