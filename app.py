from flask import Flask, send_from_directory, render_template, request, abort
from waitress import serve
from models.arrest_predictor import predict_arrest
import time

import sys
sys.path.insert(1, '../walk_risk_engine')
from results import get_backend_results

app = Flask(__name__, static_url_path="/static")

@app.route("/")
def index():
    """Return the main page."""
    return send_from_directory("static", "index.html")

@app.route("/get_results", methods=["POST"])
def get_results():
    """ Predict the probability of 1+ arrests at this location today based on 
    the inputs. """
    data = request.form

    expected_features = ("start_lat", "start_long", "end_lat", "end_long")

    if data and all(feature in data for feature in expected_features):
        # Convert the dict of fields into a list
        # test_value = [float(data[feature]) for feature in expected_features]

        m, risk, warning = get_backend_results(str(data['start_lat']), 
                                                str(data['start_long']),
                                                str(data['end_lat']),
                                                str(data['end_long'])
                                                )

        new_map_name = ("results_map_" + str(round(time.time())) + ".html")

        m.save('static/' + new_map_name)
        
        # risk = (1, 'low')
        # warning = 'Google Warning'
        # new_map_name = 'results_map_1573495916.762036.html'

        return render_template("results.html", 
                                risk=risk[1],
                                goog_warning=warning,
                                map_file_name=new_map_name
                                )
    else:
        return abort(400)

    # validate inputs - float, float w/in manhattan (make into a function)
    # try:
        # cast to float
    # except:
        # return abort(400) (or make a error page)

    
    

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
