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

        source_station = request.form.get('station')
        total_wagons = int(request.form.get('wagons'))
        rake_type = request.form.get('rake')
        forecast_rakes = int(request.form.get('forecast_rakes'))

        # ✅ FIXED RANDOM SEED (schedule won't change for same input)
        import hashlib
        seed_string = f"{source_station}-{total_wagons}-{forecast_rakes}-{rake_type}"
        seed_value = int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (10**8)
        random.seed(seed_value)

        # Rake capacity mapping
        rake_capacity_map = {
            "BOXN": 58,
            "BCN": 42,
            "BTPN": 45
        }

        max_capacity = rake_capacity_map.get(rake_type, 58)

        destinations = [s for s in stations if s != source_station]
        num_destinations = len(destinations)

        station_summary = []

        remaining_rakes = forecast_rakes
        remaining_wagons = total_wagons

        for i, dest in enumerate(destinations):

            # ---------------- Rake Allocation ----------------
            if i == num_destinations - 1:
                rakes_assigned = remaining_rakes
            else:
                min_rakes = max(1, remaining_rakes // (num_destinations * 2))
                max_rakes = remaining_rakes - (num_destinations - i - 1)

                if max_rakes < min_rakes:
                    rakes_assigned = min_rakes
                else:
                    rakes_assigned = random.randint(min_rakes, max_rakes)

            rakes_assigned = min(rakes_assigned, remaining_rakes)

            # ---------------- Wagon Allocation (Capacity Safe) ----------------
            max_wagons_allowed = rakes_assigned * max_capacity

            if i == num_destinations - 1:
                wagons_assigned = min(remaining_wagons, max_wagons_allowed)
            else:
                if max_wagons_allowed > 0 and remaining_wagons > 0:
                    lower_bound = int(max_wagons_allowed * 0.7)
                    upper_bound = min(max_wagons_allowed, remaining_wagons)

                    if upper_bound < lower_bound:
                        wagons_assigned = upper_bound
                    else:
                        wagons_assigned = random.randint(lower_bound, upper_bound)
                else:
                    wagons_assigned = 0

            remaining_rakes -= rakes_assigned
            remaining_wagons -= wagons_assigned

            station_summary.append({
                "destination": dest,
                "total_wagons": wagons_assigned,
                "rakes_required": rakes_assigned
            })

        return render_template("schedule.html", station_summary=station_summary)

    return render_template("schedule.html", station_summary=[])
# -----------------------------
# RUN APPLICATION
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
