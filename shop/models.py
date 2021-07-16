from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# model for user
class User(db.Model, UserMixin):
    UserId = db.Column(db.Integer, primary_key=True)
    Fname = db.Column(db.String(50), nullable=False)
    MiddleIn = db.Column(db.String(1), nullable=False)
    Lname = db.Column(db.String(50), nullable=False)
    Address = db.Column(db.String(50), nullable=False)
    City = db.Column(db.String(50), nullable=False)
    State = db.Column(db.String(2), nullable=False)
    ZipCode = db.Column(db.String(10), nullable=False)
    PhoneNumber = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100),unique=True, nullable=False)
    Password = db.Column(db.String(5), nullable=False)
    ProductsForSale = db.relationship('Product') # one-to-many relation
    CID = db.relationship('Cart', uselist=False, backref="user") # one-to-one relation
    
    # uses userId for getting ID
    def get_id(self):
        return self.UserId


class Cart(db.Model):
    CID = db.Column(db.Integer, primary_key=True) 
    UserId = db.Column(db.Integer, db.ForeignKey('user.UserId'))
    Products = db.relationship('Product') # one-to-many relation

     # uses cid for getting ID
    def get_id(self):
        return self.CID


class Product(db.Model):
    PID = db.Column(db.Integer, primary_key=True) 
    SellerID = db.Column(db.Integer, db.ForeignKey('user.UserId'))
    Name = db.Column(db.String(50), nullable=False)
    Description = db.Column(db.String(500))
    Price = db.Column(db.Float, nullable=False)
    ImgURL = db.Column(db.String(500))
    DateAdded = db.Column(db.DateTime(timezone=True), default=func.now())
    isSold = db.Column(db.Boolean, default=False)

     # uses userId for getting ID
    def get_id(self):
        return self.PID