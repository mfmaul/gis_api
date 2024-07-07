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

from sqlalchemy.orm import aliased

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

    gdf_meter = None
    gdf_area_m2 = None

    return True, gdf
