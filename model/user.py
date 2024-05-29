from database.database import db
from sqlalchemy.exc import IntegrityError

class User(db.Model):

    
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
    
    
    
    @staticmethod
    def create_user(payload):
        user = User(
            email=payload["email"],
            password=payload["password"],
            first_name=payload["first_name"],
            last_name=payload["last_name"],
            )

        try:
            db.session.add(user)
            db.session.commit()
            return True
        except IntegrityError:
            return False

# @staticmethod
# def hashed_password(password):
#     return bcrypt.generate_password_hash(str(password).encode("utf-8"))

    