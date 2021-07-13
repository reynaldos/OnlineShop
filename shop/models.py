from enum import unique
from . import db
from flask_login import UserMixin
# from sqlalchemy.sql import func

# model for user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True,)
    FirstName = db.Column(db.String(50))
    MiddleInitial = db.Column(db.String(1))
    LastName = db.Column(db.String(50))
    Address = db.Column(db.String(50))
    City = db.Column(db.String(50))
    State = db.Column(db.String(2))
    ZipCode = db.Column(db.String(10))
    PhoneNumber = db.Column(db.String(50))
    EmailAddress = db.Column(db.String(100),unique=True)
    Password = db.Column(db.String(5))

    # uses id for getting ID
    def get_id(self):
        return self.id
