from flask import Flask, render_template, request, jsonify
import requests
import json
import uuid

app = Flask(__name__)

def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Гарантируем наличие нужных ключей
            if 'history' not in data:
                data['history'] = {}
            if 'stats' not in data:
                data['stats'] = {}
            return data
    except Exception:
        return {"history": {}, "stats": {}}

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_weather(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid=e257d5228f2418cc31185e3a9eb96f94'
    weather_data = requests.get(url).json()
    if 'main' not in weather_data:
        raise Exception('Город не найден')
    temperature = round(weather_data['main']['temp'])
    feels_like = round(weather_data['main']['feels_like'])
    wind_speed = round(weather_data['wind']['speed'])
    return {
        'city': city,
        'temperature': temperature,
        'feels_like': feels_like,
        'wind_speed': wind_speed
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    user_id = request.cookies.get('user_id') or str(uuid.uuid4())
    data = load_data()
    if request.method == 'POST':
        city = request.form.get('city', 'Москва')
        try:
            weather = get_weather(city)
            # Сохраняем в историю
            if user_id not in data.get('history', {}):
                data['history'][user_id] = []
            data['history'][user_id].append(city)
            data['history'][user_id] = data['history'][user_id][-5:]
            # Обновляем статистику
            if city not in data.get('stats', {}):
                data['stats'][city] = 0
            data['stats'][city] += 1
            save_data(data)
        except:
            weather = {'error': 'Город не найден'}
    user_history = data.get('history', {}).get(user_id, [])
    stats = data.get('stats', {})
    return render_template('index.html', weather=weather, history=user_history, stats=stats)

@app.route('/api/stats')
def get_stats():
    data = load_data()
    return jsonify(data.get('stats', {}))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 