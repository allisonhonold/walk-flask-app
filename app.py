from flask import Flask, send_from_directory, render_template, request, abort
from waitress import serve
from models.arrest_predictor import predict_arrest

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
    print(data)

    expected_features = ("start_lat", "start_long", "end_lat", "end_long")

    if data and all(feature in data for feature in expected_features):
        # Convert the dict of fields into a list
        test_value = [float(data[feature]) for feature in expected_features]
        predicted_class = predict_arrest(test_value)
        return render_template("results.html", predicted_class=predicted_class)
    else:
        return abort(400)

    # validate inputs - float, float w/in manhattan (make into a function)
    # try:
        # cast to float
    # except:
        # return abort(400) (or make a error page)
    

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
