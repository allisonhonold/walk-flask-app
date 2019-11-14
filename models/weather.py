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
    """Gets the NYC weather data from dark sky API and dumps it into
    the weather collection within the walk MongoDB.

    Based on Cristian Nuno's soccer_stats/Weather_Getter and export_weather
    https://github.com/cenuno/soccer_stats/blob/master/python/export_weather.py
    https://github.com/cenuno/soccer_stats/blob/master/python/weathergetter.py
    """
    # get most recent date from NYC's year to date arrests
    final_date_df = pd.read_csv('../nyc_ytd.csv', 
                        usecols=['ARREST_DATE'],
                        nrows=2)
    final_date = datetime.strptime(final_date_df.loc[0, 'ARREST_DATE'], '%m/%d/%Y')
    
    # set initial date to 1/1/2006
    initial_date = datetime.strptime('01/01/2006', '%m/%d/%Y')

    # get list of dates in data range
    dates = get_dates_list(initial_date, final_date)

    # load secret key
    with open(secret_loc, "r") as f:
        key = json.load(f)["key"]

    # store exclusions
    excl = "?exclude=currently,minutely,hourly,alerts,flags"

    # instatntiate MongoDB client
    client = MongoClient()
    db = client["walk"]
    weather = db["weather"]

    # set location and url
    ny_lat_long = (40.7420, -73.9073) # atlasobscura.com
    dk_sky_url = 'https://api.darksky.net/forecast/'

    # Broken into sets in order to stay in the free use level of 
    # darksky weather api.

    # get_weather for first date - done
    # date = dates[0]
    # get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #             dk_sky_url, excl, key, weather)

    # get_weather for next 998 dates - done
    # for date in dates[1:999]:
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Monday - done
    # for date in dates[999:1999]:
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Tues - done
    # for date in dates[1999:2999]:
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Weds - done
    # for date in dates[2999:3999]:
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Thurs - done
    # for date in dates[3999:4999]:
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)

    # get_weather for remaining dates - Fri - done
    # for date in dates[4999:len(dates)]:
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)


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