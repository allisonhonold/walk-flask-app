# load necessary modules
import pandas as pd
from datetime import datetime, timedelta, date
import requests
import json
from pymongo import MongoClient
from typing import List
import pandas as pd
import numpy as np

# secret file location
secret_loc = "/Users/allisonhonold/.secrets/dark_sky_api.json"

def main():
    pass


def get_dates_list(initial_date: datetime, 
                   final_date: datetime) -> List[datetime]:
    """Create a list of datetime objects with each date between the initial_date
    and final_date.

    Args: 
        initial_date: the first date in the list
        final_data: the last date in the list
    
    Returns:
        a list of datetime objects with a one day interval between the initial
        and final dates.
    """
    return [initial_date + timedelta(x) 
            for x in range(int((final_date - initial_date).days)+1)]


def get_weather(date: datetime, lat, long, secret_key,
                base_url='https://api.darksky.net/forecast/', 
                exclusions="?exclude=currently,minutely,hourly,alerts,flags", 
                collection=None):
    """Retrieve weather for a particular date based on exclusions passed.
    Stores weather in mongoDB collection passed
    
    Args:
        date: datetime object
        lat: latitude of interest
        long: longitude of interest
        base_url: the base url of the weather api (default: darksky)
        exclusions: list of exclusions to pass to the api
        secret_key: your secret key to access the weather api
        collection: the MongoDB collection you would like to store the weather
            data in

    Returns:
        If no MongoDB collection, returns weather json.
        Else, data is stored in the collection passed.
    """
    date_str = date.strftime('%Y-%m-%d') + 'T12:00:00'
    url = f"{base_url}{secret_key}/{lat},{long},{date_str}{exclusions}"
    response = requests.get(url)
    output = response.json()
    output['date'] = date
    if collection == None:
        return output
    collection.insert_one(output)


def prep_weather(weather_data_json, today):
    """prepares weather data for modeling. Current model requires only 
    'ap_t_high100'.
    
    Args:
        weather_df: pandas dataframe of daily weather data json returned by 
            darksky api ex. pd.DataFrame(dk_sky_weather_json['daily']['data'])
        date: datetime of date
        
    Returns: single line weather dataframe only missing lats/longs for model 
        pipeline
    """
    weather_df = pd.DataFrame(np.zeros((1,10)), 
                            columns=['apparentTemperatureHigh',
                               'apparentTemperatureLow', 'cloudCover', 
                               'humidity', 'precipIntensityMax', 
                               'precipProbability',
                               'sunriseTime', 'sunsetTime', 'windGust', 
                               'precipAccumulation'])
    for col in weather_df.columns:
        if col in weather_data_json.keys():
            weather_df[col] = weather_data_json[col]
    # weather_df['date'] = date
    weather_df['ap_t_high100'] = int(weather_df['apparentTemperatureHigh']*100)
    # weather_df['ap_t_low100'] = int(weather_df['apparentTemperatureLow']*100)
    # weather_df['cloud'] = int(weather_df['cloudCover']*100)
    # weather_df['humidity'] = int(weather_df['humidity']*100)
    # weather_df['precip_inten_max10000'] = int(weather_df['precipIntensityMax']*10000)
    # weather_df['precip_proba100'] = int(weather_df['precipProbability']*100)
    # weather_df['sunriseTime'].astype(int)
    # weather_df['sunsetTime'].astype(int)
    # weather_df['wind_gust100'] = int(weather_df['windGust']*100)
    # weather_df['precip_accum100'] = int(weather_df['precipAccumulation']*100)
    # weather_df = weather_df.drop(columns=['apparentTemperatureHigh',
    #                            'apparentTemperatureLow', 'cloudCover', 
    #                            'humidity', 'precipIntensityMax', 
    #                            'precipProbability', 'windGust', 
    #                            'precipAccumulation',
    #                            ])
    return weather_df['ap_t_high100']


if __name__ == '__main__':
    main()