# application/apis/user_apis/account/routes.py
from . import user_apis_blueprint
from ... import db, login_manager
from ...models.user_models.models import Account
from flask import make_response, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from passlib.hash import sha256_crypt

import uuid
import base64

from datetime import datetime
from datetime import timedelta

from flask_cors import cross_origin

import gc
import os
import json

from ...utils import AppMessageException, get_date, set_attr, get_default_list_param, exception_handler, success_handler

@login_manager.user_loader
def load_user(user_id):
    return Account.query.filter_by(id=user_id).first()

@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('GIS ', '', 1)
        user = Account.query.filter_by(api_key=api_key).first()
        if user:
            if user.api_key_expires > get_date():
                return user
    return None

@user_apis_blueprint.route('/register', methods=['POST'])
@cross_origin()
def register():
    try:
        if not request.is_json:
            raise AppMessageException('please provide json data')
        data = request.get_json()

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        if not first_name:
            raise AppMessageException('please input: first_name (text mandatory)')
        if not email:
            raise AppMessageException('please input: email (text mandatory)')
        if '@' not in email:
            raise AppMessageException('invalid input format: email')
        
        username = email.split('@')[0]
        password = sha256_crypt.hash(str(password))

        known_account = Account.query.filter_by(email=email).first()
        if known_account:
            raise AppMessageException('email has been registered')
        
        known_account = Account.query.filter(Account.username.op('~')('^{}[0-9][0-9]*[0-9]*[0-9]*$'.format(username)))
        total_account = known_account.count()
        if known_account:
            username = '{}{}'.format(username, total_account+1)
        
        known_account = Account()
        known_account.uid = str(uuid.uuid4())
        
        known_account.first_name = first_name
        known_account.last_name = last_name
        known_account.email = email

        known_account.username = username
        known_account.password = password

        known_account.register_key = str(uuid.uuid4())

        known_account.rowstatus = 1
        known_account.created_by = known_account.uid
        known_account.created_date = get_date()

        db.session.add(known_account)
        db.session.commit()

        # send mail
        
        return make_response(jsonify(success_handler( known_account.to_json(attr=['uid', 'username']) )), 200)
    except Exception as e:
        return make_response(jsonify(exception_handler(e, services='register')), 500)

@user_apis_blueprint.route('/verify/<register_key>', methods=['GET'])
@cross_origin()
def verify(register_key:str):
    try:
        register_key = str(register_key)
        
        known_account = Account.query.filter_by(register_key=register_key).first()
        if not known_account:
            raise AppMessageException('invalid register key!')
        if known_account.is_verified:
            raise AppMessageException('already verified! login available.')
        
        known_account.is_verified = 1

        db.session.add(known_account)
        db.session.commit()

        return make_response(jsonify(success_handler('account verified. login available.')), 200)
    except Exception as e:
        return make_response(jsonify(exception_handler(e, services='verify')), 500)

@user_apis_blueprint.route('/login', methods=['POST'])
@cross_origin()
def post_login():
    try:
        if not request.is_json:
            raise AppMessageException('please provide json data')
        form = request.get_json()
        username = form.get('username')
        user = Account.query.filter_by(username=username, is_verified=1).first()
        if not user:
            user = Account.query.filter_by(email=username, is_verified=1).first()
        if user:
            if sha256_crypt.verify(str(form.get('password')), user.password):
                if not user.api_key or get_date() > user.api_key_expires:
                    user.encode_api_key()
                db.session.commit()
                login_user(user)
                results = {
                    'api_key': user.api_key,
                    'api_key_expires': user.api_key_expires.isoformat(),
                    'user': user.to_json(attr=[])
                }

                gc.collect()
                return make_response(jsonify(success_handler(results)))
        
        gc.collect()
        return make_response(jsonify(exception_handler('not logged in', 401)), 401)
    except Exception as e:
        return make_response(jsonify(exception_handler(e, services='post_login')), 500)

@user_apis_blueprint.route('/logout', methods=['POST'])
@cross_origin()
def post_logout():
    if current_user.is_authenticated:
        current_user.api_key = None
        current_user.api_key_expires = None
        db.session.commit()
        logout_user()
        gc.collect()
        return make_response(jsonify(success_handler({ })))
    gc.collect()
    return make_response(jsonify(exception_handler('not logged in', 401)), 401)