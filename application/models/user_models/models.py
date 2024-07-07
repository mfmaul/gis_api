# application/models/user_models/models.py
from ... import db
from datetime import datetime
from flask_login import UserMixin
from passlib.hash import sha256_crypt
import uuid

import os

from datetime import timedelta
from ...utils import get_date, map_attr

class Account(UserMixin, db.Model):
    __tablename__ = 'user_account'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, default=uuid.uuid4)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=True)
    email = db.Column(db.String(128), nullable=False, index=True)
    
    username = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), unique=False, nullable=False)

    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Integer, default=0)
    authenticated = db.Column(db.Boolean, default=False)

    api_key = db.Column(db.String(255), unique=True, nullable=True)
    api_key_expires = db.Column(db.DateTime, default=get_date)

    rowstatus = db.Column(db.Integer, default=1)
    created_by = db.Column(db.String(100), nullable=True)
    created_date = db.Column(db.DateTime, default=get_date)
    modified_by = db.Column(db.String(100), nullable=True)
    modified_date = db.Column(db.DateTime, onupdate=get_date)

    def encode_api_key(self):
        self.api_key = sha256_crypt.hash(self.username + str(get_date))
        self.api_key_expires = datetime.utcnow() + timedelta(hours=7) + timedelta(hours=24)

    def encode_password(self):
        self.password = sha256_crypt.hash(self.password)

    def __repr__(self):
        return '<User %r>' % (self.username)

    def to_json(self, attr=[]):
        if attr:
            return map_attr(self, attr)
        
        return {
            'uid': self.uid,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,

            'username': self.username,
        }