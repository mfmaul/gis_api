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