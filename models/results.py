from weather import get_weather, prep_weather
from datetime import datetime
from route import (query_route_api, extract_route_and_warnings, 
                   get_route, get_pts_near_path)
from mapping import map_predictions
from predict import get_arrest_probas, get_risk
import json
import pandas as pd

# global constants
secret_location_goog = '/Users/allisonhonold/.secrets/google_maps_api.json'
secret_loc_weather = "/Users/allisonhonold/.secrets/dark_sky_api.json"

def get_backend_results(start_lat, start_long, end_lat, end_long):
    """gets the walk risk results for a path on the day called

    Args:
        start_lat: start latitude
        start_long: start longitude
        end_lat: end latitude
        end_long: end longitude
    
    Returns:
        map: Folium map with choropleth of relative risk near walking path
        risk rating: overall risk rating (#, string)
        warning: warning supplied by google routes for display
    """
    # load weather secret key
    with open(secret_loc_weather, "r") as f:
        weather_key = json.load(f)["key"]
    print('weather key laoded')

    # combine lat/longs into start_loc, end_loc
    start_loc = start_lat + ',' + start_long
    end_loc = end_lat + ',' + end_long

    # get route and weather from APIs
    route, warning = get_route(secret_location_goog, start_loc, end_loc)
    today = datetime.today()
    weather = get_weather(today, start_lat, start_long, weather_key)

    # process weather, path to get predictions, map, relative risk
    try:
        # process weather and path
        weather_df = prep_weather(weather['daily']['data'][0], today)
        pts = get_pts_near_path(route, 750).reset_index(drop=True)
        
        # get predictions and prepare for mapping
        arrest_probas = get_arrest_probas(pts, weather_df)
        pts_proba_df = pd.concat([pts, 
                                    pd.Series(arrest_probas, 
                                    name='probability')], 
                                    axis='columns')
        
        # get map and risk rating
        m = map_predictions(start_lat, start_long, end_lat, end_long, 
                            pts_proba_df)
        risk_rating = get_risk(route, weather_df)
        
    
        return m, risk_rating, warning

    except:
        print("API error")
        return "", "", ""