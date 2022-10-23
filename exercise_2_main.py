from datetime import datetime
import numpy as np
import requests as requests
import exercise_2_constants as con
import pandas as pd
import matplotlib.pyplot as plt

api_key = con.API_KEY_CHECKWX


def get_metar_data(lat, lon):
    url = "https://api.checkwx.com/metar/lat/" + str(lat) + "/lon/" + str(lon) + "/decoded"
    response = requests.request("GET", url, headers={"X-API-Key": api_key})
    return response.json()


# print(get_metar_data(47.31, 21.37))


def get_weather_data(lat, lon):
    params = {"lon": lon, "lat": lat}
    url = "http://127.0.0.1:8000/weather/"
    response = requests.request("GET", url, params=params)
    return response.json()


# print(get_weather_data(47.31, 21.37))


def get_cities():
    url = "http://127.0.0.1:8000/city_coordinates/"
    response = requests.request("GET", url)
    return response.json()


class Location:
    def __init__(self, name, lat, lon, date, temp, hum, vis, wind_speed, wind_degree):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.date = date
        self.temp = temp
        self.hum = hum
        self.vis = vis
        self.wind_speed = wind_speed
        self.wind_degree = wind_degree

    def __str__(self):
        return "Name: " + self.name + " Lat: " + str(self.lat) + " Lon: " + str(self.lon) + " Date: " + str(
            self.date) + " Temp: " + str(
            self.temp) + " Hum: " + str(self.hum) + " Vis: " + str(self.vis) + " Wind Speed: " + str(
            self.wind_speed) + " Wind Degree: " + str(self.wind_degree)


def get_original_data(cities_json):
    original_data = []

    for city in cities_json:
        weather_json = get_weather_data(city["lat"], city["lon"])
        original_data.append(Location(city["name"], city["lat"], city["lon"],
                                      datetime.utcfromtimestamp(weather_json["dt"]).strftime('%Y-%m-%dT%H:%MZ'),
                                      weather_json["main"]["temp"],
                                      weather_json["main"]["humidity"], weather_json["visibility"],
                                      weather_json["wind"]["speed"], weather_json["wind"]["deg"]))
    return original_data


def get_new_data(cities_json):
    new_data = []

    for city in cities_json:
        metar_json = get_metar_data(city["lat"], city["lon"])
        new_data.append(Location(city["name"], metar_json["data"][0]["station"]["geometry"]["coordinates"][1],
                                 metar_json["data"][0]["station"]["geometry"]["coordinates"][0],
                                 metar_json["data"][0]["observed"],
                                 metar_json["data"][0]["temperature"]["celsius"],
                                 metar_json["data"][0]["humidity"]["percent"],
                                 metar_json["data"][0]["visibility"]["meters_float"],
                                 metar_json["data"][0]["wind"]["speed_mps"], metar_json["data"][0]["wind"]["degrees"]))
    return new_data


def create_plot(df, df2, column, name, location):
    # set width of bar
    bar_width = 0.25

    x_axis = np.arange(len(df[column]))
    plt.subplot(location)

    # Make the plot
    plt.bar(x_axis - (bar_width / 2), df[column], color='r', width=bar_width,
            edgecolor='grey', label='OpenWeather')
    plt.bar(x_axis + (bar_width / 2), df2[column], color='b', width=bar_width,
            edgecolor='grey', label='METAR')

    # for i in range(len(df[column])):
    #    plt.annotate(str(df[column][i]), xy=(i, df[column][i]), ha='right', va='bottom')
    #    plt.annotate(str(df2[column][i]), xy=(i, df2[column][i]), ha='left', va='bottom')

    plt.ylabel(name, fontweight='bold')
    plt.xticks(x_axis, ['Warsaw', 'Budapest', 'Prague', 'Wien'])


def calculate_metric():
    cities_json = get_cities()
    original_data = get_original_data(cities_json)
    new_data = get_new_data(cities_json)
    for location in original_data:
        print(location)
    for location in new_data:
        print(location)

    pd.set_option('display.max_columns', None)

    df = pd.DataFrame([vars(f) for f in original_data])
    print(df)

    df2 = pd.DataFrame([vars(f) for f in new_data])
    print(df2)

    columns = {231: ['temp', 'Temperature (°C)'], 232: ['hum', 'Humidity (%)'], 233: ['wind_speed', 'Wind Speed (mps)'],
               234: ['wind_degree', 'Wind Degree (°)'], 235: ['vis', 'Visibility (m)']}

    fig, axs = plt.subplots(5)

    for location, column in columns.items():
        create_plot(df, df2, column[0], column[1], location)

    handles, labels = plt.gca().get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower right')
    plt.suptitle('Comparing OpenWeather with METAR data', fontweight='bold')
    plt.show()


calculate_metric()

# date
# temp, humidity, visibility, wind speed, wind degree
