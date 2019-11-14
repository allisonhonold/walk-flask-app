import pandas as pd
import numpy as np
from models.route import get_pts_near_path
from sqlalchemy import create_engine
import joblib


def get_arrest_probas(pts_df, day_weather_df):
    """returns predicted arrest probabilities

    Args:
        pts_df: a dataframe with columns: latitude, longitude
        weather_df: a dataframe with columns:

    Returns:
        a numpy array with the resulting predictions
    """
    # setup dataframe for preprocessing
    inputs_df = setup_df_for_preprocessing(pts_df, day_weather_df)
    pipeline = load_joblib_pipeline(file_path='models/pipeline.joblib')
    probas = pipeline.predict_proba(inputs_df)
    return probas[:, 1]


def load_joblib_pipeline(file_path='pipeline.joblib'):
    """ Load the pipeline from the .joblib file """
    pipeline_file = open(file_path, "rb")
    loaded_pipeline = joblib.load(pipeline_file)
    pipeline_file.close()
    return loaded_pipeline


def get_overall_proba(path, day_weather):
    """gets the overall probability of arrest along a path. Uses all lat/long
    coordinates within 200 feet of the path. Assumes the arrest occurance
    probabilities are independent for each lat/long along the path.

    Args:
        path: a shapely Linestring of the recommended walking route
        weather: a dataframe of weather features for use in predictions

    Returns:
        a single overall proability of an arrest occuring along the path for
        the given day and weather conditions
    """
    pts = get_pts_near_path(path, 200).reset_index(drop=True)
    arrest_probas = get_arrest_probas(pts, day_weather)
    return np.prod(arrest_probas)


def setup_df_for_preprocessing(pts_df, day_weather_df):
    """sets up the dataframe based on the inputs for preprocessing by combining
    the lat/longs in the pts_df data frame with the day/weather information,
    and eliminating extra columns
    
    Args:
        pts_df: a dataframe of the points of interest
        day_weather_df: a dataframe with the needed information of the day of
            interest

    Returns:
        dataframe with each row representing a lat/long point and the day/
        weather information repeated for each lat/long
    """
    pts_df = pts_df.drop(columns=['geometry', 'on_path'])
    pts_df['latitude'] = pts_df['latitude'].round(3)
    pts_df['longitude'] = pts_df['longitude'].round(3)
    pts_df['latlong'] = (pts_df['latitude'].astype(str) 
                        + pts_df['longitude'].astype(str))
    # add values of each weather feature
    pts_df[day_weather_df.name] = day_weather_df[0]
    # for col in day_weather_df.columns:
    #     pts_df[col] = day_weather_df[col].values[0]
    print(pts_df)
    return pts_df


def get_risk(path, day_weather, cutoffs=[.1, .2, .3, .4]):
    """gets the relative risk of a path.

    Args:
        path: shapely linestring of the path
        weather: pandas dataframe with columns ['date', 'ap_t_high100', 
          'ap_t_low100', 'cloud', 'humidity', 'precip_inten_max10000', 
          'precip_proba100', 'sunriseTime', 'sunsetTime',
          'wind_gust100', 'precip_accum100']
        cutoffs: (optional) division points between the five ratings

    Returns:
        tuple (number rating 1-5, rating desciption)
    """
    proba = get_overall_proba(path, day_weather)
    if proba < cutoffs[0]:
        return (1, 'low')
    elif proba < cutoffs[1]:
        return (2, "medium low")
    elif proba < cutoffs[2]:
        return (3, "medium")
    elif proba < cutoffs[3]:
        return (4, 'medium high')
    else:
        return (5, 'high')
    
