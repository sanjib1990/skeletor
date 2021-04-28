from werkzeug.security import generate_password_hash

from src.models.postgress.user import User as UserModel


data = {
    'admin@admin.com': {
        'password': 'admin123'
    }
}


def run():
    from skeletor import db
    for email, obj in data.items():
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            try:
                user = UserModel()
                user.email = email
                user.is_active = True
                user.password = generate_password_hash(obj.get('password'))
                user.updated_by = 'seeder'
                user.created_by = 'seeder'
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                print('User insert error: {0}'.format(e))
                return {"errors": "db error: Something went wrong while inserting user"}
        pass
