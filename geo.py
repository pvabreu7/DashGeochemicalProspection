import pandas as pd
import csv
import geopandas as gpd
import json
import base64
import io
from shapely.geometry import LineString, MultiLineString
import numpy as np
import plotly.graph_objs as go
import plotly.express as px


def add_ids(gdf, index_list, labels_col, tolerance=0):

    geo_names = list(gdf[str(labels_col)])
    geojson = {'type': 'FeatureCollection', 'features': []}
    for index in index_list:
        geo = gdf['geometry'][index].simplify(tolerance)

        if isinstance(geo.boundary, LineString):
            gtype = 'Polygon'
            bcoords = np.dstack(geo.boundary.coords.xy).tolist()

        elif isinstance(geo.boundary, MultiLineString):
            gtype = 'MultiPolygon'
            bcoords = []
            for b in geo.boundary:
                x, y = b.coords.xy
                coords = np.dstack((x, y)).tolist()
                bcoords.append(coords)
        else:
            pass

        feature = {'type': 'Feature',
                   'id': index,
                   'properties': {'name': geo_names[index]},
                   'geometry': {'type': gtype,
                                'coordinates': bcoords},
                   }

        geojson['features'].append(feature)
    return geojson

def parse_geojson(contents, filename):
    try:
        if 'geojson' in filename:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            geojson = decoded.decode("ISO-8859-1")
            geodf = gpd.read_file(geojson)
            geodf['geometry'] = geodf['geometry'].astype(str)

    except Exception as e:
        print(e)
        return print('There was an error processing this file.')

    data = geodf.to_dict('records')
    columns = [{'name': i, 'id': i} for i in geodf.columns]

    return columns, data

