from skeletor import db
from skeletor.config import DATE_TIME_FORMAT
from werkzeug.security import generate_password_hash
from skeletor.databases_connections.postgress.base_model import BaseModel


class Identity(BaseModel):
    __tablename__ = "identities"

    identity = db.Column(db.String(255), nullable=False)
    feature_flag_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kwargs):
        super(Identity, self).__init__(*args, **kwargs)

    def asdict(self, *args, **kwargs):
        return {
            **{
                'identity': self.identity,
                'feature_flag_id': self.feature_flag_id,
                'value': self.value,
            },
            **self.get_base_dict()
        }

    def __repr__(self):
        return "<Identity(identity='%s')>" % self.identity
