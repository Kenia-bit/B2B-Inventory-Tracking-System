from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize database extension
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)

    farmers = db.relationship('Farmer', backref='owner', lazy=True)
    harvests = db.relationship('Harvest', backref='owner', lazy=True)

class Farmer(db.Model):
    __tablename__ = 'farmers'
    farmer_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Harvest(db.Model):
    __tablename__ = 'harvests'
    harvest_id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.farmer_id', ondelete='CASCADE'))
    crop_type = db.Column(db.String(100), nullable=False)
    quantity_kg = db.Column(db.Numeric(10, 2), nullable=False)
    harvest_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Buyer(db.Model):
    __tablename__ = 'buyers'
    buyer_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    location = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    orders = db.relationship('Order', backref='buyer', lazy=True, cascade="all, delete-orphan")

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.buyer_id', ondelete='CASCADE'), nullable=False)
    harvest_id = db.Column(db.Integer, db.ForeignKey('harvests.harvest_id', ondelete='CASCADE'), nullable=False)
    quantity_kg = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(12, 2), nullable=False)
    payment_status = db.Column(db.String(20), default='debt')  # 'paid' or 'debt'
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    harvest = db.relationship('Harvest', backref='orders', lazy=True)