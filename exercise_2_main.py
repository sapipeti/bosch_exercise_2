import requests as requests
import exercise_2_constants as con

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
    def __init__(self, name, lat, lon, temp, hum, vis, wind_speed, wind_degree):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.temp = temp
        self.hum = hum
        self.vis = vis
        self.wind_speed = wind_speed
        self.wind_degree = wind_degree

    def __str__(self):
        return "Name: " + self.name + " Lat: " + str(self.lat) + " Lon: " + str(self.lon) + " Temp: " + str(
            self.temp) + " Hum: " + str(self.hum) + " Vis: " + str(self.vis) + " Wind Speed: " + str(
            self.wind_speed) + " Wind Degree: " + str(self.wind_degree)


def get_original_data(cities_json):
    original_data = []

    for city in cities_json:
        weather_json = get_weather_data(city["lat"], city["lon"])
        original_data.append(Location(city["name"], city["lat"], city["lon"], weather_json["main"]["temp"],
                                      weather_json["main"]["humidity"], weather_json["visibility"],
                                      weather_json["wind"]["speed"], weather_json["wind"]["deg"]))
    return original_data


def get_new_data(cities_json):
    new_data = []

    for city in cities_json:
        metar_json = get_metar_data(city["lat"], city["lon"])
        new_data.append(Location(city["name"], city["lat"], city["lon"], metar_json["data"][0]["temperature"]["celsius"],
                                 metar_json["data"][0]["humidity"]["percent"],
                                 metar_json["data"][0]["visibility"]["meters_float"],
                                 metar_json["data"][0]["wind"]["speed_kph"], metar_json["data"][0]["wind"]["degrees"]))
    return new_data


def calculate_metric():
    cities_json = get_cities()
    original_data = get_original_data(cities_json)
    new_data = get_new_data(cities_json)
    for location in original_data:
        print(location)
    for location in new_data:
        print(location)

calculate_metric()

# date
# temp, humidity, visibility, wind speed, wind degree

