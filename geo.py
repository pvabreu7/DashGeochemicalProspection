import pandas as pd
import geopandas as gpd
import json

from shapely.geometry import LineString, MultiLineString
import numpy as np
import plotly.graph_objs as go
import plotly.express as px


def shapefile_to_geojson(gdf, index_list, labels_col, tolerance=0):
    # gdf - geopandas dataframe containing the geometry column and values to be mapped to a colorscale
    # index_list - a sublist of list(gdf.index)  or gdf.index  for all data
    # tolerance - float parameter to set the Polygon/MultiPolygon degree of simplification
    # returns a geojson type dict

    geo_names = list(gdf[str(labels_col)])  # Desnecessário, substituir
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



