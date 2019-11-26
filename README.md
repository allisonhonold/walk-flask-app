# WalkSafe Flask App

## Purpose

This repo contains a flask app that, when deployed, allows users to mark their start and end location on a Google Map, and then displays a map of the relative walk safety along the route recommended by Google's Route API.

## How it works

1) The user inputs the start and end locations

2) The app calls the Dark Sky API for the day's weather information and Google Maps API for the recommended route.

3) The locations and weather data are fed to the model to predict for each location. (Learn more about the model in this [repo] https://github.com/allisonhonold/walk_risk_engine)

4) The predictions are displayed for the user along with an overall risk rating and the weather.

## Requirements

This repo uses Python 3.6.0. All python packages can be found in the `requirements.txt` file.  The requirements are in `pip` style, because this is supported by Heroku.

To create a new `conda` environment to use this repo, run:
```bash
conda create --name flask-env
conda activate flask-env
pip install -r requirements.txt
```

## Running the Flask Application

To run in a development environment (on your local computer)
```bash
export FLASK_ENV=development
env FLASK_APP=app.py flask run
```

To run in a production environment (used for deployment, but test it out locally first):
```bash
export FLASK_ENV=production
python app.py
```
