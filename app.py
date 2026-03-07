from flask import Flask, render_template, request
import math
import random

app = Flask(__name__)

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route('/')
def home():

    stations = [
        "Vijayawada",
        "Visakhapatnam",
        "Secunderabad",
        "Nagpur",
        "Dhanbad"
    ]

    return render_template("index.html", stations=stations)


# -----------------------------
# PREDICTION ROUTE
# -----------------------------
@app.route('/predict', methods=['POST'])
def predict():

    station = request.form['station']
    rake = request.form['rake']
    commodity = request.form['commodity']
    load = float(request.form['load'])
    date = request.form['date']

    # -----------------------------
    # Sample Forecast Logic
    # -----------------------------
    prediction = load

    # -----------------------------
    # Wagon Calculation
    # -----------------------------
    wagon_capacity = 60
    wagons = math.ceil(prediction / wagon_capacity)

    # -----------------------------
    # Rake Calculation
    # -----------------------------
    rake_capacity = 58
    rakes = math.ceil(wagons / rake_capacity)

    return render_template(
        "result.html",
        station=station,
        rake=rake,
        commodity=commodity,
        prediction=round(prediction, 2),
        wagons=wagons,
        rakes=rakes,
        date=date
    )


# -----------------------------
# SCHEDULING ROUTE
# -----------------------------
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():

    stations = [
        "Vijayawada",
        "Visakhapatnam",
        "Secunderabad",
        "Nagpur",
        "Dhanbad"
    ]

    if request.method == 'POST':

        station = request.form.get('station')
        total_wagons = int(request.form.get('wagons'))
        rake_type = request.form.get('rake')
        forecast_rakes = int(request.form.get('forecast_rakes'))

        # Capacity based on rake type
        if rake_type == "BOXN":
            max_capacity = 58
        elif rake_type == "BCN":
            max_capacity = 42
        elif rake_type == "BTPN":
            max_capacity = 45
        else:
            max_capacity = 58

        destinations = [s for s in stations if s != station]
        num_destinations = len(destinations)

        station_summary = []

        remaining_rakes = forecast_rakes
        remaining_wagons = total_wagons

        for i, dest in enumerate(destinations):

            # -----------------------------
            # Safe Rake Distribution
            # -----------------------------
            if i == num_destinations - 1:
                rakes_assigned = remaining_rakes
            else:

                max_rakes = remaining_rakes - (num_destinations - i - 1)

                if max_rakes <= 1:
                    rakes_assigned = 1
                else:
                    rakes_assigned = random.randint(1, max_rakes)

            remaining_rakes -= rakes_assigned

            # -----------------------------
            # Wagon Distribution
            # -----------------------------
            max_wagons_allowed = rakes_assigned * max_capacity

            if i == num_destinations - 1:
                wagons = remaining_wagons
            else:

                max_wagons_allowed = min(
                    max_wagons_allowed,
                    remaining_wagons - (num_destinations - i - 1)
                )

                if max_wagons_allowed <= 1:
                    wagons = 1
                else:
                    wagons = random.randint(1, max_wagons_allowed)

            remaining_wagons -= wagons

            station_summary.append({
                "destination": dest,
                "total_wagons": wagons,
                "rakes_required": rakes_assigned
            })

        return render_template("schedule.html", station_summary=station_summary)

    return render_template("schedule.html", station_summary=[])


# -----------------------------
# RUN APPLICATION
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)