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
    'polygon': fields.List(fields.List(fields.List(fields.List(fields.Float))), required=True, default=[[[[100.907826607488175,1.030217731639408],[100.982651878775187,0.987015468017912],[100.983705755835558,0.915361707806548],[100.9763286164129,0.84581404086444],[100.964735968748684,0.832115107827134],[100.967897599929842,0.80155577924559],[100.975274739352528,0.785749139950523],[100.952089444024139,0.76888865881213],[100.946820058722224,0.746759176498607],[100.929958025756136,0.723575789880422],[100.928904148695764,0.698284687674263],[100.929958025756136,0.670885840226408],[100.883587435099415,0.669832035297473],[100.876210295676742,0.656132550730407],[100.867779279193698,0.661401587738312],[100.856186631529496,0.668778230141937],[100.897287836884331,0.752028111087282],[100.880425803918243,0.750974324676923],[100.876210295676742,0.780480246835824],[100.756068310793367,0.85213660908182],[100.907826607488175,1.030217731639408]]]])
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