# application/apis/__init__.py
from flask import Blueprint, Response, request

swagger_apis_blueprint = Blueprint('swagger_apis', __name__)

# restx
from flask_restx import Api
from .user_apis import api as docs_account

authorizations = {
    'api_key': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Sample: GIS {the api key}'
    }
}

api_extension = Api(
    swagger_apis_blueprint,
    authorizations=authorizations,
    title='GIS APIs',
    version='22.0',
    doc='/',
    security='api_key',
)

api_extension.add_namespace(docs_account)