# application/apis/user_apis/__init__.py
from flask import Blueprint, Response, request

user_apis_blueprint = Blueprint('user_apis', __name__)

from . import routes

# swagger 'flask restx' docs
from flask_restx import Namespace, Resource, fields, reqparse
import werkzeug

api = Namespace('users', 'user account related endpoints.')

register_parser = api.parser()
register_parser.add_argument('first_name', type=str, required=True, help="first name, sample: John", location="json")
register_parser.add_argument('last_name', type=str, required=False, help="last name, sample: Doe", location="json")
register_parser.add_argument('email', type=str, required=True, help="email, sample: john_doe@mail.com", location="json")
register_parser.add_argument('password', type=str, required=True, help="account password, sample: P@ssw0rd", location="json")

login_parser = api.parser()
login_parser.add_argument('username', type=str, required=True, help="account username, sample: john_doe, john_doe@mail.com", location="json")
login_parser.add_argument('password', type=str, required=True, help="account password, sample: P@ssw0rd", location="json")

account_model = api.model('Account', {
    'uid': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'username': fields.String,
})

api_response_model = api.model('ApiResponse', {
    'api_key': fields.String,
    'api_key_expired': fields.DateTime(dt_format='rfc822'),
    'user': fields.Nested(account_model, skip_none=True),
})

register_model = api.model('Register', {
    'uid': fields.String,
    'username': fields.String,
})

blank_model = api.model('BlankObject', {})

# error results
error_results_model = api.model('ErrorStatus', {
    'message': fields.String,
    'success': fields.Boolean,
})

# blank results
blank_results_object_model = api.model('BlankResultsObject', {
    'data': fields.Nested(blank_model),
    'success': fields.Boolean,
})
blank_results_list_model = api.model('BlankResultsList', {
    'data': fields.List(fields.Nested(blank_model)),
    'total_records': fields.Integer,
})

# account results
results_object_model = api.model('ResObjAccount', {
    'data': fields.Nested(account_model),
    'success': fields.Boolean,
})

# api response results
api_response_results_model = api.model('ApiResponseResults', {
    'data': fields.Nested(api_response_model),
    'success': fields.Boolean,
})

# register results
register_results_model = api.model('RegisterResults', {
    'data': fields.Nested(register_model),
    'success': fields.Boolean,
})

# verify results
verify_results_model = api.model('VerifyResults', {
    'data': fields.String,
    'success': fields.Boolean,
})

@api.route('/register')
class RegisterUsers(Resource):
    @api.response(200, 'Success', model=register_results_model)
    @api.response(401, 'Unauthorized, please provide api key', model=error_results_model)
    @api.response(500, 'Internal Server error, refer to the error code and messages status.', model=error_results_model)
    @api.doc(parser=register_parser)
    def post(self):
        pass

@api.route('/login')
class LoginUsers(Resource):
    @api.response(200, 'Success', model=api_response_results_model)
    @api.response(401, 'Unauthorized, please provide api key', model=error_results_model)
    @api.response(500, 'Internal Server error, refer to the error code and messages status.', model=error_results_model)
    @api.doc(parser=login_parser)
    def post(self):
        pass

@api.route('/logout')
class LogoutUsers(Resource):
    @api.response(200, 'Success', model=blank_results_object_model)
    @api.response(401, 'Unauthorized, please provide api key', model=error_results_model)
    @api.response(500, 'Internal Server error, refer to the error code and messages status.', model=error_results_model)
    def post(self):
        pass

@api.route('/verify/<register_key>')
class VerifyUsers(Resource):
    @api.response(200, 'Success', model=verify_results_model)
    @api.response(401, 'Unauthorized, please provide api key', model=error_results_model)
    @api.response(500, 'Internal Server error, refer to the error code and messages status.', model=error_results_model)
    def get(self):
        pass