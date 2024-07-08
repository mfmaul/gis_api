# application/apis/auction_apis/auction/routes.py
from flask import jsonify, request, make_response, abort
from flask_login import current_user
from . import gis_apis_blueprint
from ... import db

from datetime import datetime
from datetime import timedelta

from flask_cors import cross_origin

import uuid
import random
import gc
import time
import arrow
import geopandas
import pyproj

from shapely import Polygon, MultiPolygon
from shapely.ops import transform

from ...utils import AppMessageException, get_date, set_attr, get_default_list_param, exception_handler, success_handler
from ...utils import eprint, sanitize_psycopg2_query

con = db.get_engine(bind='postgis')

@gis_apis_blueprint.route('/test-gis', methods=['GET'])
@cross_origin()
def test_gis():
    try:
        if not current_user.is_authenticated:
            return make_response(jsonify(exception_handler('not logged in', 401)), 401)
        
        sql = 'select geom,namobj from postgis limit 1;'
        df = geopandas.read_postgis(sql, con)

        results = {
            'test': str(df)
        }

        gc.collect()

        return make_response(jsonify(success_handler(results)))
    except Exception as e:
        return make_response(jsonify(exception_handler(e, services='test-gis')), 500)

@gis_apis_blueprint.route('/city/<city_name>', methods=['GET'])
@cross_origin()
def get_city_details(city_name:str):
    try:
        if not current_user.is_authenticated:
            return make_response(jsonify(exception_handler('not logged in', 401)), 401)

        succ, gdf = getdata(t='city', args=city_name)
        if not succ:
            raise AppMessageException('invalid type of operation')
        
        results = gdf.to_dict(orient='records')

        gdf = None

        gc.collect()

        return make_response(jsonify(success_handler(results)))
    except Exception as e:
        return make_response(jsonify(exception_handler(e, services='city-details')), 500)

@gis_apis_blueprint.route('/district/<district_name>', methods=['GET'])
@cross_origin()
def get_district_details(district_name:str):
    try:
        if not current_user.is_authenticated:
            return make_response(jsonify(exception_handler('not logged in', 401)), 401)

        succ, gdf = getdata(t='district', args=district_name)
        if not succ:
            raise AppMessageException('invalid type of operation')
        
        results = gdf.to_dict(orient='records')

        gdf = None

        gc.collect()

        return make_response(jsonify(success_handler(results)))
    except Exception as e:
        return make_response(jsonify(exception_handler(e, services='district-details')), 500)

@gis_apis_blueprint.route('/area-polygon', methods=['POST'])
@cross_origin()
def post_area_polygon():
    try:
        if not current_user.is_authenticated:
            return make_response(jsonify(exception_handler('not logged in', 401)), 401)

        if not request.is_json:
            raise AppMessageException('please provide json data')
        
        data = request.get_json()
        if not type(data) == list:
            raise AppMessageException('json data should be list of list, sample: [[[[], [], []]]]')
        try:
            # test multipolygon input
            data[0][0][0][0]
        except:
            raise AppMessageException('invalid multipolygon format, currently we accepts [[[[1, 1], [2, 2]]]] formats')
        
        polygon = MultiPolygon(data)
        sgri2013_degree = pyproj.CRS('EPSG:9470')
        sgri2013_metre = pyproj.CRS('EPSG:9468')
        project = pyproj.Transformer.from_crs(sgri2013_degree, sgri2013_metre, always_xy=True).transform
        polygon_metre = transform(project, polygon)

        polygon_gdf = geopandas.GeoDataFrame(geometry=geopandas.GeoSeries(polygon))
        polygon_gdf.to_postgis('polytemp', con, if_exists='replace')

        gdf = get_intersections()

        results = {
            # 'area': float(polygon_gdf.area.iloc[0]),
            # 'length': float(polygon_gdf.length.iloc[0]),
            'luas': polygon_metre.area,
            'intersections': gdf.to_dict(orient='records')
        }

        polygon = None
        polygon_metre = None
        polygon_gdf = None
        gdf = None

        gc.collect()

        return make_response(jsonify(success_handler(results)))
    except Exception as e:
        return make_response(jsonify(exception_handler(e, services='city-details')), 500)

@gis_apis_blueprint.route('/area-shapefile', methods=['POST'])
@cross_origin()
def post_area_shapefile():
    try:
        if not current_user.is_authenticated:
            return make_response(jsonify(exception_handler('not logged in', 401)), 401)

        shp_file = request.files.get('shp_file')
        
        if not shp_file:
            raise AppMessageException('please provide shp files (shp_file)')
        
        polygon_gdf = geopandas.read_file(shp_file)
        polygon_gdf.crs = 'EPSG:9470'
        polygon_gdf.to_postgis('polytemp', con, if_exists='replace')
        polygon_gdf = polygon_gdf.to_crs(epsg=9468)

        gdf = get_intersections(t='shapefile')

        results = {
            'luas': float(polygon_gdf.area.iloc[0]),
            'intersections': gdf.to_dict(orient='records')
        }

        gc.collect()

        return make_response(jsonify(success_handler(results)))
    except Exception as e:
        return make_response(jsonify(exception_handler(e, services='city-details')), 500)

def getdata(t:str = 'city', args:str = '\0'):
    query = '''
        select 
            a.geom,a.objectid,a.namobj,a.uupp,
            a.wadmpr,a.wiadkk,a.wadmkk,a.wiadkc,a.wadmkc,
            a.wiadkd,a.wadmkd
        from postgis a
        where
            1=1
    '''

    if t == 'city':
        query += ''' and lower(a.wadmkk) like '%{}%' '''
    elif t == 'district':
        query += ''' and lower(a.wadmkc) like '%{}%' '''
    else:
        return False, None
    
    query = sanitize_psycopg2_query(query.format(args))

    # https://epsg.io/9470 | indonesia SGRI2013 in degree | latest revision?
    gdf = geopandas.read_postgis(query, con, crs='epsg:9470')
    gdf = gdf.to_crs(epsg=9468) # SGRI2013 in metre

    # set the area units
    gdf['luaswh'] = gdf['geom'].area

    gdf = gdf_sanitize(gdf)

    gdf_meter = None
    gdf_area_m2 = None

    return True, gdf

def get_intersections(t:str = None):
    query = '''
        select
            b.geom,b.objectid,b.namobj,b.uupp,
            b.wadmpr,b.wiadkk,b.wadmkk,b.wiadkc,b.wadmkc,
            b.wiadkd,b.wadmkd
        from polytemp a
        left join postgis b on 
    '''

    if t == 'shapefile':
        query += ''' ST_Intersects(ST_SetSRID(b.geom, 9470), a.geometry) '''
    else:
        query += ''' ST_Intersects(b.geom, a.geometry) '''

    gdf = geopandas.read_postgis(query, con)

    gdf = gdf_sanitize(gdf)

    return gdf

def gdf_sanitize(gdf):

    # drop null data
    gdf.dropna(subset=['objectid'], inplace=True)

    # drop geom data
    gdf = gdf.drop('geom', axis=1)

    # cast objectid to int, bcs somehow its float
    gdf['objectid'] = gdf['objectid'].astype('int64')

    # rename for fe's readable field :)
    gdf.rename(columns={
        'objectid': 'object_id',
        'namobj': 'object_name',
        'uupp': 'referensi_peraturan',
        'wadmpr': 'prov_name',
        'wiadkk': 'kab_parent_name',
        'wadmkk': 'kab_name',
        'wiadkc': 'kec_parent_name',
        'wadmkc': 'kec_name',
        'wiadkd': 'kel_parent_name',
        'wadmkd': 'kel_name',
        'luaswh': 'luas',
    }, inplace=True)

    return gdf