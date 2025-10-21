from flask import Flask, render_template, request, jsonify, session
import requests
from datetime import datetime, timedelta
import random
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

API_KEY = "fe7baef8dcd28e3dd516811461fdf32a"

# Add custom Jinja2 filters
@app.template_filter('datetime')
def format_datetime(value, format='%H:%M'):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value).strftime(format)
    elif isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime(format)
        except:
            return value
    return value

@app.template_filter('round')
def round_filter(value, precision=0):
    try:
        return round(float(value), precision)
    except (ValueError, TypeError):
        return value

# Favorite cities storage
FAVORITE_CITIES_FILE = 'favorite_cities.json'

def load_favorite_cities():
    try:
        if os.path.exists(FAVORITE_CITIES_FILE):
            with open(FAVORITE_CITIES_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_favorite_cities(cities):
    try:
        with open(FAVORITE_CITIES_FILE, 'w') as f:
            json.dump(cities, f)
    except:
        pass

def get_weather_data(city):
    try:
        # Current weather
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        current_response = requests.get(current_url)
        
        if current_response.status_code != 200:
            return None
        
        current_data = current_response.json()
        
        # Forecast
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()
        
        return {
            'current': current_data,
            'forecast': forecast_data
        }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_weather_alerts(city):
    """Fetch severe weather alerts - simplified version"""
    try:
        # For now, return empty alerts since One Call API might not be available
        # You can implement this later with a paid OpenWeatherMap plan
        return []
    except:
        return []

def process_weather_data(raw_data):
    if not raw_data:
        return None
    
    current = raw_data['current']
    forecast = raw_data['forecast']
    
    # Process current weather
    current_weather = {
        'city': current['name'],
        'country': current['sys']['country'],
        'temp': current['main']['temp'],
        'feels_like': current['main']['feels_like'],
        'temp_min': current['main']['temp_min'],
        'temp_max': current['main']['temp_max'],
        'humidity': current['main']['humidity'],
        'pressure': current['main']['pressure'],
        'visibility': current.get('visibility', 0),
        'description': current['weather'][0]['description'],
        'icon': current['weather'][0]['icon'],
        'wind_speed': current['wind']['speed'],
        'wind_deg': current['wind'].get('deg', 0),
        'sunrise': datetime.fromtimestamp(current['sys']['sunrise']).strftime('%H:%M'),
        'sunset': datetime.fromtimestamp(current['sys']['sunset']).strftime('%H:%M'),
        'uv_index': random.randint(1, 10),  # Placeholder
    }
    
    # Process hourly forecast (next 12 hours)
    hourly_forecast = []
    for i in range(12):
        if i < len(forecast['list']):
            hour_data = forecast['list'][i]
            time = datetime.fromtimestamp(hour_data['dt']).strftime('%H:%M')
            # Use a different key name to avoid conflict with list.pop() method
            precipitation_probability = hour_data.get('pop', 0) * 100
            hourly_forecast.append({
                'time': time,
                'temp': hour_data['main']['temp'],
                'icon': hour_data['weather'][0]['icon'],
                'humidity': hour_data['main']['humidity'],
                'wind_speed': hour_data['wind']['speed'],
                'description': hour_data['weather'][0]['description'],
                'precipitation': precipitation_probability  # Changed from 'pop' to 'precipitation'
            })
    
    # Process 7-day forecast
    daily_forecast = []
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Today
    daily_forecast.append({
        'day': 'Today',
        'date': datetime.now().strftime('%b %d'),
        'high': current['main']['temp_max'],
        'low': current['main']['temp_min'],
        'icon': current['weather'][0]['icon'],
        'precipitation': random.randint(5, 20),
        'description': current['weather'][0]['description'],
        'wind_speed': current['wind']['speed']
    })
    
    # Next 6 days
    for i in range(6):
        day_index = (i + 1) * 8  # Each day has 8 data points (3-hour intervals)
        if day_index < len(forecast['list']):
            day_data = forecast['list'][day_index]
            date = datetime.fromtimestamp(day_data['dt'])
            daily_forecast.append({
                'day': days[date.weekday()],
                'date': date.strftime('%b %d'),
                'high': day_data['main']['temp_max'],
                'low': day_data['main']['temp_min'],
                'icon': day_data['weather'][0]['icon'],
                'precipitation': random.randint(5, 50),
                'description': day_data['weather'][0]['description'],
                'wind_speed': day_data['wind']['speed']
            })
    
    # Tomorrow's outlook
    tomorrow_outlook = daily_forecast[1] if len(daily_forecast) > 1 else daily_forecast[0]
    
    return {
        'current': current_weather,
        'hourly': hourly_forecast,
        'daily': daily_forecast,
        'tomorrow_outlook': f"{tomorrow_outlook['description'].capitalize()}. High of {tomorrow_outlook['high']:.0f}°",
        'alerts': get_weather_alerts(current['name'])
    }

@app.route('/')
def index():
    # Default city or get from request
    city = request.args.get('city', 'Patna')
    weather_data = get_weather_data(city)
    
    if weather_data:
        processed_data = process_weather_data(weather_data)
        favorite_cities = load_favorite_cities()
        return render_template('index.html', 
                             weather=processed_data, 
                             city=city,
                             favorite_cities=list(favorite_cities.keys()))
    else:
        return render_template('index.html', weather=None, city=city, error="City not found")

@app.route('/search', methods=['POST'])
def search():
    city = request.form.get('city', 'Patna')
    return jsonify({'redirect': f'/?city={city}'})

@app.route('/favorite', methods=['POST'])
def favorite_city():
    city = request.json.get('city')
    action = request.json.get('action')  # 'add' or 'remove'
    
    favorite_cities = load_favorite_cities()
    
    if action == 'add':
        favorite_cities[city] = True
    elif action == 'remove' and city in favorite_cities:
        del favorite_cities[city]
    
    save_favorite_cities(favorite_cities)
    return jsonify({'success': True})

@app.route('/favorites')
def favorites():
    favorite_cities = load_favorite_cities()
    cities_weather = []
    
    for city in favorite_cities:
        weather_data = get_weather_data(city)
        if weather_data:
            processed = process_weather_data(weather_data)
            cities_weather.append({
                'city': city,
                'current_temp': processed['current']['temp'],
                'description': processed['current']['description'],
                'icon': processed['current']['icon']
            })
    
    return render_template('favorites.html', cities=cities_weather)

@app.route('/api/geolocation')
def geolocation():
    """Simple geolocation endpoint - in production, use a proper geocoding service"""
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    # For now, return a mock response
    # In production, you'd use a geocoding API like OpenCage, Google Maps, etc.
    return jsonify({'city': 'Patna'})  # Placeholder

@app.route('/api/weather/<city>')
def api_weather(city):
    weather_data = get_weather_data(city)
    if weather_data:
        processed_data = process_weather_data(weather_data)
        return jsonify(processed_data)
    return jsonify({'error': 'City not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)