from datetime import datetime
import numpy as np
import requests as requests
import exercise_2_constants as con
import pandas as pd
import matplotlib.pyplot as plt

api_key = con.API_KEY_CHECKWX


def get_cities():
    url = "http://127.0.0.1:8000/city_coordinates/"
    response = requests.request("GET", url)
    return response.json()


def get_openweather_json(lat, lon):
    params = {"lon": lon, "lat": lat}
    url = "http://127.0.0.1:8000/weather/"
    response = requests.request("GET", url, params=params)
    return response.json()


def get_metar_json(lat, lon):
    url = "https://api.checkwx.com/metar/lat/" + str(lat) + "/lon/" + str(lon) + "/decoded"
    response = requests.request("GET", url, headers={"X-API-Key": api_key})
    return response.json()


class Location:
    def __init__(self, name, lat, lon, date, source, temp, hum, vis, wind_speed, wind_degree):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.date = date
        self.source = source
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


def get_openweather_data(cities_json):
    openweather_data = []

    for city in cities_json:
        openweather_json = get_openweather_json(city["lat"], city["lon"])
        openweather_data.append(Location(city["name"], city["lat"], city["lon"],
                                         datetime.utcfromtimestamp(openweather_json["dt"]).strftime('%Y-%m-%dT%H:%MZ'),
                                         "OpenWeather",
                                         openweather_json["main"]["temp"],
                                         openweather_json["main"]["humidity"], openweather_json["visibility"],
                                         openweather_json["wind"]["speed"], openweather_json["wind"]["deg"]))
    return openweather_data


def get_metar_data(cities_json):
    metar_data = []
    # TODO: Nullcheck here
    for city in cities_json:
        metar_json = get_metar_json(city["lat"], city["lon"])
        metar_data.append(Location(city["name"], metar_json["data"][0]["station"]["geometry"]["coordinates"][1],
                                   metar_json["data"][0]["station"]["geometry"]["coordinates"][0],
                                   metar_json["data"][0]["observed"],
                                   "METAR",
                                   metar_json["data"][0]["temperature"]["celsius"],
                                   metar_json["data"][0]["humidity"]["percent"],
                                   metar_json["data"][0]["visibility"]["meters_float"],
                                   metar_json["data"][0]["wind"]["speed_mps"],
                                   metar_json["data"][0]["wind"]["degrees"]))
    return metar_data


def df_to_json_file(df, filename):
    out = df.to_json(orient='records')
    with open(str(filename) + '.json', 'w') as f:
        f.write(out)


def compare_weather_data(df, df2):
    pd.set_option('display.max_columns', None)
    metric_df = pd.concat([df, df2])
    metric_df.sort_values(by=['name'], inplace=True)
    print(metric_df)

    df_to_json_file(metric_df, "metric")


def create_subplot(df, df2, data_source_1, data_source_2, column, name, ax):
    bar_width = 0.25

    x_axis = np.arange(len(df[column]))

    ax.bar(x_axis - (bar_width / 2), df[column], color='r', width=bar_width,
           edgecolor='grey', label=data_source_1)
    ax.bar(x_axis + (bar_width / 2), df2[column], color='b', width=bar_width,
           edgecolor='grey', label=data_source_2)

    ax.set_ylabel(name, fontweight='bold')
    ax.set_xticks(x_axis, df['name'], fontweight='bold')


def calculate_dates_matrix(df, df2):
    dates = [[], []]

    for i in range(len(df['date'])):
        dates[0].append(df['date'][i])
        dates[1].append(df2['date'][i])
    return dates


def create_plot(df, df2, dates_matrix, cells):
    fig, axes = plt.subplots(figsize=(16, 9))

    data_source_1 = df['source'].unique()[0]
    data_source_2 = df2['source'].unique()[0]

    ax = plt.subplot2grid((5, 3), (4, 0), colspan=3)
    ax.set_axis_off()
    table = ax.table(bbox=[0.0, -0.5, 1.0, 1.0], cellText=dates_matrix,
                     rowLabels=[data_source_1, data_source_2],
                     rowColours=['r', 'b'], colLabels=df['name'], loc='center')
    table.set_fontsize(12)

    for location, column in cells.items():
        ax = plt.subplot2grid((5, 3), (location[0], location[1]), rowspan=2)
        create_subplot(df, df2,data_source_1, data_source_2, column[0], column[1], ax)

    handles, labels = plt.gca().get_legend_handles_labels()
    fig.legend(handles, labels, prop={'size': 12}, bbox_to_anchor=(1, 0.32))
    plt.suptitle('Comparing '+data_source_1+' with '+data_source_2+' data', fontweight='bold')
    plt.tight_layout()
    plt.show()


def calculate_metric():
    cities_json = get_cities()
    openweather_data = get_openweather_data(cities_json)
    metar_data = get_metar_data(cities_json)

    openweather_df = pd.DataFrame([vars(f) for f in openweather_data])
    metar_df = pd.DataFrame([vars(f) for f in metar_data])

    compare_weather_data(openweather_df, metar_df)

    dates_matrix = calculate_dates_matrix(openweather_df, metar_df)

    cells = {tuple([0, 0]): ['vis', 'Visibility (m)'], tuple([0, 1]): ['temp', 'Temperature (°C)'],
             tuple([0, 2]): ['hum', 'Humidity (%)'],
             tuple([2, 0]): ['wind_speed', 'Wind Speed (mps)'], tuple([2, 1]): ['wind_degree', 'Wind Degree (°)']}

    create_plot(openweather_df, metar_df, dates_matrix, cells)


calculate_metric()
