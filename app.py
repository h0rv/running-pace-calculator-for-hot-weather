from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    location = request.form['location']
    pace = request.form['pace']
    distance = request.form['distance']
    is_metric = request.form.get('unitToggle', 'off') == 'on'

    try:
        weather_response = requests.get(
            f'https://wttr.in/{location}?format=j1')
        weather_data = weather_response.json()

        temp_key = 'tempC' if is_metric else 'tempF'
        dew_point_key = 'DewPointC' if is_metric else 'DewPointF'

        weather_today = weather_data['weather'][0]['hourly'][0]
        temp = weather_today[temp_key]
        dew_point = weather_today[dew_point_key]
        humidity = weather_today['humidity']

        temp_f = (float(temp) * 9 / 5) + 32 if is_metric else float(temp)
        dew_point_f = (float(dew_point) * 9 / 5) + \
            32 if is_metric else float(dew_point)

        sum_temp_dew = temp_f + dew_point_f
        adjustment = 0

        if sum_temp_dew <= 100:
            adjustment = 0
        elif sum_temp_dew <= 110:
            adjustment = 0.005
        elif sum_temp_dew <= 120:
            adjustment = 0.0075
        elif sum_temp_dew <= 130:
            adjustment = 0.015
        elif sum_temp_dew <= 140:
            adjustment = 0.025
        elif sum_temp_dew <= 150:
            adjustment = 0.0375
        elif sum_temp_dew <= 160:
            adjustment = 0.0525
        elif sum_temp_dew <= 170:
            adjustment = 0.07
        elif sum_temp_dew <= 180:
            adjustment = 0.09
        else:
            return jsonify({"error": "Hard running not recommended under these conditions."})

        if distance == 'interval':
            adjustment /= 2

        pace_min, pace_sec = map(int, pace.split(':'))
        pace_seconds = pace_min * 60 + pace_sec
        adjusted_pace_seconds = pace_seconds * (1 + adjustment)
        adjusted_min = int(adjusted_pace_seconds // 60)
        adjusted_sec = round(adjusted_pace_seconds % 60)

        result = {
            "location": location,
            "temp": temp,
            "dew_point": dew_point,
            "humidity": humidity,
            "is_metric": is_metric,
            "adjusted_min": adjusted_min,
            "adjusted_sec": adjusted_sec
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True)

