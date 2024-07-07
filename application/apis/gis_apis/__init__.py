# application/apis/gis_apis/__init__.py
from flask import Blueprint, Response, request

gis_apis_blueprint = Blueprint('gis_apis', __name__)

from . import routes

# swagger 'flask restx' docs
from flask_restx import Namespace, Resource, fields, reqparse
from ..user_apis import error_results_model
import werkzeug

api = Namespace('giss', 'gis related endpoints.')

area_shapefile_parser = api.parser()
area_shapefile_parser.add_argument('shp_file', type=werkzeug.datastructures.FileStorage, help="shp zip files", required=True, location="files")

area_polygon_input = api.model('AreaPolygonInput', {
    
})

gis_data_model = api.model('GisData', {
    'object_id': fields.Integer,
    'object_name': fields.String,
    'referensi_peraturan': fields.String,
    'prov_name': fields.String,
    'kab_parent_name': fields.String,
    'kab_name': fields.String,
    'kec_parent_name': fields.String,
    'kec_name': fields.String,
    'kel_parent_name': fields.String,
    'kel_name': fields.String,
})

gis_data_area_model = api.model('GisDataArea', {
    'object_id': fields.Integer,
    'object_name': fields.String,
    'referensi_peraturan': fields.String,
    'prov_name': fields.String,
    'kab_parent_name': fields.String,
    'kab_name': fields.String,
    'kec_parent_name': fields.String,
    'kec_name': fields.String,
    'kel_parent_name': fields.String,
    'kel_name': fields.String,
    'luas': fields.Float,
})

poly_post_model = api.model('PolyPost', {
    'luas': fields.Float,
    'intersections': fields.List(fields.Nested(gis_data_model)),
})

# poly post results
poly_post_results_model = api.model('PolyPostResults', {
    'data': fields.Nested(poly_post_model),
    'success': fields.Boolean,
})

# gis area results
gis_area_results_model = api.model('GisAreaResults', {
    'data': fields.List(fields.Nested(gis_data_area_model)),
    'succes': fields.Boolean,
})


@api.route('/area-polygon')
class AreaPolygon(Resource):
    @api.response(200, 'Success', model=poly_post_results_model)
    @api.response(401, 'Unauthorized, please provide api key', model=error_results_model)
    @api.response(500, 'Internal Server error, refer to the error code and messages status.', model=error_results_model)
    @api.expect(area_polygon_input)
    def post(self):
        pass

@api.route('/area-shapefile')
class AreaShapefile(Resource):
    @api.response(200, 'Success', model=poly_post_results_model)
    @api.response(401, 'Unauthorized, please provide api key', model=error_results_model)
    @api.response(500, 'Internal Server error, refer to the error code and messages status.', model=error_results_model)
    @api.doc(parser=area_shapefile_parser)
    def post(self):
        pass

@api.route('/city/<city_name>')
class CityInfo(Resource):
    @api.response(200, 'Success', model=gis_area_results_model)
    @api.response(401, 'Unauthorized, please provide api key', model=error_results_model)
    @api.response(500, 'Internal Server error, refer to the error code and messages status.', model=error_results_model)
    def get(self):
        pass

@api.route('/district/<district_name>')
class DistrictInfo(Resource):
    @api.response(200, 'Success', model=gis_area_results_model)
    @api.response(401, 'Unauthorized, please provide api key', model=error_results_model)
    @api.response(500, 'Internal Server error, refer to the error code and messages status.', model=error_results_model)
    def get(self):
        pass