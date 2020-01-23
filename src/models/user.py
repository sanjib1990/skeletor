from skeletor import db
from skeletor.config import DATE_TIME_FORMAT
from werkzeug.security import generate_password_hash
from skeletor.databases_connections.postgress.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    is_online = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_loggedin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if 'password' in kwargs:
            self.password = generate_password_hash(kwargs.get('password'))
            pass

    def asdict(self, *args, **kwargs):
        return {
            **{
                'email': self.email,
                'is_online': self.is_online,
                'is_loggedin': self.is_loggedin,
                'last_login': self.last_login.strftime(DATE_TIME_FORMAT) if self.last_login is not None else None,
            },
            **self.get_base_dict()
        }

    def __repr__(self):
        return "<User(email='%s')>" % self.email
