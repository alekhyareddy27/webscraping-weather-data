from flask import Flask, request, render_template,jsonify
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import datetime

app = Flask(__name__)
api_key = "b07158c5f2e64ca963ba6a587b6194d7" 

# Forecasting weather data through API 
@app.route('/weather', methods=['GET'])
def weather():
    city = request.args.get('city', 'Detroit')  # Default to Detroit if no city provided
    date = request.args.get('date')
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    if date:
        filtered_data = [item for item in data['list'] if datetime.datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d') == date]
        if not filtered_data:
            return jsonify({'message': 'No data found for the selected date'}), 404
        data['list'] = filtered_data

    return jsonify(data)

#fetching weather data through scraping
def get_weather_data(city):
    location_encoded = urllib.parse.quote(city)  # URL encoding
    url = "https://www.weather-forecast.com/locations/" + location_encoded + "/forecasts/latest"
    try:
        req = requests.get(url)
        soup = BeautifulSoup(req.content, "lxml") #using beautiful soup to scrape data
        phrase_elements = soup.find_all("span", {"class": "phrase"})
        if phrase_elements:
            data = phrase_elements[0].text
            return parse_weather_data(data, soup)
    except Exception as err:
        return {"error": f"An error occurred: {err}"}

# Parsing high low temp data
def parse_weather_data(data, soup):
    weather_data = {}
    # Parsing temperature
    temp_list = re.findall(r'\b\d{1,2}\b', data)
    if len(temp_list) >= 2:
        weather_data["high_temp"] = temp_list[0]
        weather_data["low_temp"] = temp_list[1]

    # Parsing humidity
    humidity_element = soup.select_one('.b-forecast__table-cell-humidity .b-forecast__table-value')
    if humidity_element:
        weather_data["humidity"] = humidity_element.text.strip()

    # Parsing UV index
    uv_element = soup.select_one('.b-forecast__table-cell-uv .b-forecast__table-value')
    if uv_element:
        weather_data["uv_index"] = uv_element.text.strip()

    return weather_data

#rendering the results to index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    if request.method == 'POST':
        location = request.form['location']
        weather_data = get_weather_data(location)
    return render_template('index.html', weather_data=weather_data)


if __name__ == '__main__':
    app.run(debug=True)
