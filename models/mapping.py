import folium
import matplotlib as mpl
import pandas as pd
from matplotlib import pyplot


def map_predictions(start_lat, start_long, end_lat, end_long, pts_proba_df):
    """Maps the predicted values as a shaded geojson overaly on a folium map

    Args:
        start_lat: start latitude string
        start_long: start longitude string
        end_lat: end latitude string
        end_long: end longitude string
        pts_proba_df: a dataframe of the points and their arrest probabilities

    Returns:
        m: folium map with a geojson grid overlay shaded with the predictions
    """
    m = get_basemap(start_lat, start_long, end_lat, end_long)

    print(f"basemap type(m): {type(m)}")

    geojson_grid = get_geojson_grid(pts_proba_df)
    m = add_grid_to_map(geojson_grid, m)

    print(f"after add_grid_to_map type(m): {type(m)}")

    return m


def get_basemap(start_lat, start_long, end_lat, end_long):
    """gets a folium basemap with the start and end points marked

    Args:
        start_lat: start latitude string
        start_long: start longitude string
        end_lat: end latitude string
        end_long: end longitude string

    Returns:
        folium_map: returns a folium map
    """
    folium_map = folium.Map(location=[str((float(start_lat)+float(end_lat))/2), 
                               str((float(start_long)+float(end_long))/2)], 
                     zoom_start=15, tiles='Stamen Terrain')
    folium.Marker(location=[start_lat, start_long], 
                  icon=folium.Icon(color='green', prefix='fa', 
                                    icon='fas fa-play-circle')
                 ).add_to(folium_map)
    folium.Marker(location=[end_lat, end_long], 
              icon=folium.Icon(color='red', prefix='fa', 
                                icon='fas fa-times-circle')
              ).add_to(folium_map)
    return folium_map


def get_geojson_grid(df, proba_column='probability'):
    """gets a geojson grid shaded by probability

    Args:
        df: dataframe with columns=['latitude', 'longitude', and probability
        proba_column: column name of column with probability (string)
    Returns:
        a list of geoJSON rectangles with their probabilities
    """
    all_boxes = []

    for index in df.index:
        lat = df.loc[index, 'latitude']
        lng = df.loc[index, 'longitude']
        proba = df.loc[index, proba_column]

        # Define json coordinates for polygon
        coordinates = [
            [lng - .0005, lat - .0005],
            [lng - .0005, lat + .0005],
            [lng + .0005, lat + .0005],
            [lng + .0005, lat - .0005],
            [lng - .0005, lat - .0005]
        ]

        geo_json = {"type": "FeatureCollection",
                    "properties":{
                        "lat": lat,
                        "long": lng,
                        "proba": proba
                    },
                    "features": []
                   }

        grid_feature = {
            "type": "Feature",
            "geometry":{
                "type": "Polygon",
                "coordinates": [coordinates]
            }
        }

        geo_json['features'].append(grid_feature)
        all_boxes.append(geo_json)
    return all_boxes


def add_grid_to_map(grid, m):
    """adds a geoJSON grid to map, colored by the probability
    
    Args:
        grid: a list of geoJSON shapes w/ proberty "proba" to shade on
        m: a folium map

    Returns:
        folium map
    """
    for geo_json in grid:
        color = pyplot.cm.Reds(geo_json['properties']['proba']*4)
        color = mpl.colors.to_hex(color)
        gj = folium.GeoJson(geo_json,
                            style_function=lambda feature, color=color: {
                                                            'fillColor': color,
                                                            'color': color,
                                                            'weight': 0,
                                                            'fillOpacity': 0.5,
                            }
                        )
        m.add_child(gj)
    return m