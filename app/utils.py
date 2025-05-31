from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import requests


def get_city_coordinates(city_name):
    geolocator = Nominatim(user_agent="weather_app")
    try:
        location = geolocator.geocode(city_name, exactly_one=True, language='ru', addressdetails=True)
        if location:
            address = location.raw.get('address', {})
            for key in ['city', 'town', 'village', 'municipality', 'locality', 'hamlet', 'state', 'region']:
                if key in address and city_name.lower() in address[key].lower():
                    return location.latitude, location.longitude
        return None, None
    except GeocoderTimedOut:
        return get_city_coordinates(city_name)
    except Exception as e:
        print(f"Ошибка геокодирования: {e}")
        return None, None

def get_3day_forecast(lat, lon):
    if not lat or not lon:
        return None
        
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lon,
        'current_weather': True,
        'hourly': 'temperature_2m,relativehumidity_2m,windspeed_10m,winddirection_10m,windgusts_10m,weathercode,is_day',
        'daily': 'weathercode,temperature_2m_max,temperature_2m_min,windspeed_10m_max,winddirection_10m_dominant,sunrise,sunset',
        'forecast_days': 3,
        'timezone': 'auto'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def format_weather_data(raw_data):
    if not raw_data:
        return {}
    
    hourly_times = raw_data.get('hourly', {}).get('time', [])[:24]
    hourly_temps = raw_data.get('hourly', {}).get('temperature_2m', [])[:24]
    hourly_codes = raw_data.get('hourly', {}).get('weathercode', [])[:24]
    
    hourly_forecast = [
        {
            'time': time,
            'temperature': temp,
            'weathercode': code
        } for time, temp, code in zip(hourly_times, hourly_temps, hourly_codes)
    ]
    
    daily_forecast = [
        {
            'date': date,
            'temp_max': max_temp,
            'temp_min': min_temp,
            'weathercode': code
        } for date, max_temp, min_temp, code in zip(
            raw_data.get('daily', {}).get('time', []),
            raw_data.get('daily', {}).get('temperature_2m_max', []),
            raw_data.get('daily', {}).get('temperature_2m_min', []),
            raw_data.get('daily', {}).get('weathercode', [])
        )
    ]
    
    return {
        'current': {
            'temperature': raw_data.get('current_weather', {}).get('temperature'),
            'windspeed': raw_data.get('current_weather', {}).get('windspeed'),
            'weathercode': raw_data.get('current_weather', {}).get('weathercode'),
            'time': raw_data.get('current_weather', {}).get('time')
        },
        'hourly': hourly_forecast,
        'daily': daily_forecast,
        'timezone': raw_data.get('timezone', 'UTC')
    }

def get_weather_description(weathercode):
    weather_descriptions = {
        0: 'Ясно',
        1: 'Преимущественно ясно',
        2: 'Переменная облачность',
        3: 'Пасмурно',
        45: 'Туман',
        55: 'Морось',
        63: 'Дождь',
        73: 'Снег',
        81: 'Ливень',
        86: 'Снегопад',
        95: 'Гроза',
    }
    return weather_descriptions.get(weathercode, 'Неизвестно')