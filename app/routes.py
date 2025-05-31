from flask import Blueprint, render_template, request, jsonify, flash, current_app
from .forms import CityForm
from .models import SearchHistory
from .utils import get_city_coordinates, get_3day_forecast, format_weather_data, get_weather_description
import json
from . import db
from .cities_list import CITIES

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = CityForm()
    weather_data = None
    recent_cities = json.loads(request.cookies.get('recent_cities', '[]'))

    if form.validate_on_submit():
        city = form.city.data.strip()
        lat, lon = get_city_coordinates(city)

        if not lat or not lon:
            flash('Не удалось определить координаты города.', 'error')
        elif lat and lon:
            raw_weather = get_3day_forecast(lat, lon)
            if raw_weather:
                weather_data = format_weather_data(raw_weather)

                search = SearchHistory.query.filter_by(city=city).first()
                if search:
                    search.count += 1
                else:
                    search = SearchHistory(city=city, ip_address=request.remote_addr)
                    db.session.add(search)
                db.session.commit()

                if city in recent_cities:
                    recent_cities.remove(city)
                recent_cities.insert(0, city)
                recent_cities = recent_cities[:5]

                flash(f'Погода для {city} получена!', 'success')
            else:
                flash('Не удалось получить прогноз погоды.', 'error')

    response = current_app.make_response(render_template(
        'index.html',
        form=form,
        weather=weather_data,
        recent_cities=recent_cities,
        get_weather_description=get_weather_description
    ))
    response.set_cookie('recent_cities', json.dumps(recent_cities), max_age=30*24*60*60)
    return response

@bp.route('/api/search_stats')
def search_stats():
    stats = db.session.query(SearchHistory.city, db.func.sum(SearchHistory.count)).group_by(SearchHistory.city).all()
    return jsonify([{'city': city, 'count': total} for city, total in stats])

@bp.route('/api/autocomplete')
def autocomplete():
    query = request.args.get('q', '').lower()
    suggestions = [city for city in CITIES if city.lower().startswith(query)][:10]
    return jsonify(suggestions)