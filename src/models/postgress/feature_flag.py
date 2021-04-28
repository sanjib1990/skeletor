from skeletor import db
from skeletor.config import DATE_TIME_FORMAT
from werkzeug.security import generate_password_hash
from skeletor.databases_connections.postgress.base_model import BaseModel


class FeatureFlag(BaseModel):
    __tablename__ = "feature_flags"

    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kwargs):
        super(FeatureFlag, self).__init__(*args, **kwargs)

    def asdict(self, *args, **kwargs):
        return {
            **{
                'name': self.name,
                'value': self.value,
            },
            **self.get_base_dict()
        }

    def __repr__(self):
        return "<FeatureFlag(name='%s')>" % self.name
