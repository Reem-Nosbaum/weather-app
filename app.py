import requests
from flask import Flask, request, render_template, send_file
import os
from dotenv import load_dotenv
import pycountry
from datetime import datetime
import json

load_dotenv()

app = Flask(__name__)

bg_color = os.getenv('BG_COLOR')

api_key = os.getenv('API_KEY')

PLACES = ["New York", "London", "Paris", "Tokyo", "Sydney", "Berlin", "Moscow", "Toronto"]

fake_forecast_data = [
    {
        "date": "2024-05-27",
        "humidity": 49,
        "temp_day": 19.3,
        "temp_night": 19.4,
        "icon": "c01d"
    },
    {
        "date": "2024-05-28",
        "humidity": 69,
        "temp_day": 22.6,
        "temp_night": 19.1,
        "icon": "c02d"
    },
    {
        "date": "2024-05-29",
        "humidity": 66,
        "temp_day": 21.8,
        "temp_night": 17.1,
        "icon": "c03d"
    },
    {
        "date": "2024-05-30",
        "humidity": 65,
        "temp_day": 19.3,
        "temp_night": 17.5,
        "icon": "r01d"
    },
    {
        "date": "2024-05-31",
        "humidity": 61,
        "temp_day": 22.1,
        "temp_night": 18.1,
        "icon": "r02d"
    },
    {
        "date": "2024-06-01",
        "humidity": 58,
        "temp_day": 19.3,
        "temp_night": 18.6,
        "icon": "s01d"
    },
    {
        "date": "2024-06-02",
        "humidity": 58,
        "temp_day": 24.2,
        "temp_night": 19.7,
        "icon": "c01d"
    }
]


# Function to save search data to history
def save_search_to_history(location, weather_data):
    history_file = 'search_history.json'

    # Load existing history if it exists
    if os.path.exists(history_file):
        with open(history_file, 'r') as file:
            history = json.load(file)
    else:
        history = []

    # Append the new search data
    history_entry = {
        "location": location,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "data": weather_data
    }
    history.append(history_entry)

    # Save the updated history
    with open(history_file, 'w') as file:
        json.dump(history, file, indent=4)


def format_date(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d.%m')


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', bg_color=bg_color)


@app.route('/weather', methods=['POST'])
def get_weather():
    location = request.form['location']
    if location.lower() == 'test':
        city_name = 'Test City'
        country_name = 'Test Country'
        forecast_data = fake_forecast_data
    else:
        url = f'http://api.weatherbit.io/v2.0/forecast/daily?key={api_key}&city={location}&days=7'
        response = requests.get(url)

        if response.status_code != 200:
            error_message = f"Error fetching weather data: {response.status_code} - {response.reason}"
            return render_template('weather.html', error=error_message, bg_color=bg_color)

        data = response.json()

        if 'error' in data:
            error_message = f"API error: {data['error']}"
            return render_template('weather.html', error=error_message, bg_color=bg_color)

        city_name = data['city_name']
        country_code = data['country_code']
        country_name = pycountry.countries.get(alpha_2=country_code).name

        forecast_data = []
        for day in data['data']:
            forecast_data.append({
                'date': format_date(day['valid_date']),
                'temp_day': day['temp'],
                'temp_night': day['min_temp'],
                'humidity': day['rh'],
                'icon': day['weather']['icon']
            })

    # Save the search data to history
    save_search_to_history(location, {
        'location': city_name,
        'country': country_name,
        'forecast': forecast_data
    })

    return render_template('weather.html', data={
        'location': city_name,
        'country': country_name,
        'forecast': forecast_data
    }, bg_color=bg_color)


@app.route('/history')
def history():
    history_file = 'search_history.json'

    if os.path.exists(history_file):
        with open(history_file, 'r') as file:
            history = json.load(file)
    else:
        history = []

    return render_template('history.html', history=history, bg_color=bg_color)


@app.route('/download')
def download():
    file_name = request.args.get('file')
    if file_name and os.path.exists(file_name):
        return send_file(file_name, as_attachment=True)
    else:
        return "File not found", 404


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405


if __name__ == '__main__':
    app.run(debug=True)
