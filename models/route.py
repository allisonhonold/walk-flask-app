# import necessary packages
import json
import requests
import pandas as pd
import polyline
# import geopandas as gpd
from shapely.geometry import LineString, Point
import numpy as np
from itertools import product
from haversine import haversine, Unit
from shapely.ops import nearest_points

def main():
    pass


def query_route_api(secret_loc, start_loc, end_loc):
    """queries the google maps api for walking route information

    Args:
        secret_loc: path to location of google api key
        start_loc: "lat,long" string of desired starting location for route
        end_loc: "lat,long" string of desired ending location for route

    Returns:
        response: google directions walking response
    """
    base_url = 'https://maps.googleapis.com/maps/api/directions/json?mode=walking'
    with open(secret_loc, "r") as f:
        key = json.load(f)['key']
    url = f"{base_url}&origin={start_loc}&destination={end_loc}&key={key}"
    response = requests.get(url)
    print(response.status_code, response.reason)

    print(response.text)

    return response


def extract_route_and_warnings(response_json):
    """extracts route and warnings from google directions API response
    
    args:
        response_json: the json of the google directions API response
    
    returns:
        rte: route as a geopandas dataframe with columns: longitude, latitude, geometry 
        warn: warnings for display
    """
    if "error_message" in response_json.keys():
        print(response_json['error_message'])
        return 'error', 'error'
    else:
        goog_polyline = response_json['routes'][0]['overview_polyline']['points']
        warnings = []
        if len(response_json['routes'][0]['warnings']) > 0:
            warnings.extend(response_json['routes'][0]['warnings'])
            warnings = warnings[0]
        rte = pd.DataFrame(polyline.decode(goog_polyline, geojson=True), 
                            columns=['longitude', 'latitude'])
        # rte = gpd.GeoDataFrame(rte, 
        #                         geometry=gpd.points_from_xy(rte['longitude'], 
        #                                                     rte['latitude']))
        rte = LineString([[x, y] for x, y in zip(rte['longitude'], 
                                                 rte['latitude'])])
        return rte, warnings


def get_route(secret_loc, start_loc, end_loc):
    """Calls to Google Service API to return the recommended route.
    
    Args:
        secret_loc: location of file with api key
        start_loc: starting location of the desired walk 
            (lat,long stringw/out spaces)
        end_loc: ending location of the desired walk 
            (lat,long string w/out spaces)
        
    Returns:
        route: shapely line of the recommended path
        warnings: route-related warnings for display
    """
    response = query_route_api(secret_loc, start_loc, end_loc)
    resp_json = json.loads(response.text)
    route, warnings = extract_route_and_warnings(resp_json)
    return route, warnings
    
    
def get_pts_near_path(line, distance):
    """returns all lat/longs within specified distance of line that are in 
    manhattan
    
    Args:
        line: shapely linestring of route
        distance: maximum distance from path for returned points

    Returns:
        pandas dataframe of all points within distance from line
    """
    # get line bounds
    (minx, miny, maxx, maxy) = line.bounds
    
    # extract values with buffer area
    minx = round(minx, 3) -0.002
    miny = round(miny, 3) -0.002
    maxx = round(maxx, 3) + 0.002
    maxy = round(maxy, 3) + 0.002

    # load manhattan lat_longs
    manhattan_pts = pd.read_csv('models/man_lat_longs.csv')
    manhattan_pts = manhattan_pts.loc[:, ['latitude', 'longitude', 'in_man']]
    
    # create a df of all lat, longs w/in bounds
    all_pts = create_pt_grid(minx, miny, maxx, maxy)
    
    # attempting to deal with edge case - pts not in manhattan
    # add column "in_man" indicating whether points are in manhattan
    # all_pts = pd.merge(all_pts, manhattan_pts, 
    #                     on=['latitude', 'longitude'],
    #                     how='left')
    all_pts['on_path'] = get_on_path(all_pts['geometry'], distance, line)
    return pd.DataFrame(all_pts.loc[(all_pts['on_path']==True)]) 
                        # & (all_pts['in_man']==True)])


def create_pt_grid(minx, miny, maxx, maxy):
    """creates a grid of points (lat/longs) in the range specified. lat longs 
    are rounded to hundredth place

    Args:
        minx: minimum longitude
        miny: minimum latitude
        maxx: maximum longitude
        maxy: maximum latitude

    Returns: DataFrame of all lat/long combinations in region
    """
    n_lats = round((maxy-miny)/.001) +1
    lats = np.linspace(miny, maxy, n_lats)
    n_longs = round((maxx - minx)/.001) +1
    longs = np.linspace(minx, maxx, n_longs)
    ll_df = pd.DataFrame(product(lats, longs), 
                    columns=['latitude', 'longitude'])
    ll_df['geometry'] = [Point(x, y) for x, y in zip(ll_df['longitude'], 
                                                     ll_df['latitude'])]
    return ll_df


def get_on_path(geom_series, dist, line):
    """gets the points from the geom_series falling on the path indicated by 
    the line (within given distance).

    Args:
        geom_series: series of shapely Points to test
        dist: max distance from the path that qualifies as on the path
        line: shapely linestring of the route/path
    """
    on_path = []
    for index in geom_series.index:
        x = geom_series[index].x
        y = geom_series[index].y
        pt1, ln_pt = nearest_points(Point(x, y), line)
        on_path.append(haversine((pt1.y, pt1.x), 
                                 (ln_pt.y, ln_pt.x), unit='ft')
                       < dist)
    return on_path


if __name__ == "__main__":
    main()