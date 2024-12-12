from extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    profile_picture = db.Column(db.String(120), nullable=True)  # New column for storing image filename

    def __repr__(self):
        return f"User('{self.username}', '{self.name}', '{self.age}', '{self.profile_picture}')"
