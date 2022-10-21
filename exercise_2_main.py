import requests as requests
import exercise_2_constants as con

api_key = con.API_KEY_CHECKWX


def get_metar_data(lat, lon):
    url = "https://api.checkwx.com/metar/lat/"+str(lat)+"/lon/"+str(lon)+"/decoded"
    response = requests.request("GET", url, headers={"X-API-Key": api_key})
    return response.json()


print(get_metar_data(47.31, 21.37))


def get_weather_data(lat, lon):
    params = {"lon": lon, "lat": lat}
    url = "http://127.0.0.1:8000/weather/"
    response = requests.request("GET", url, params=params)
    return response.json()


print(get_weather_data(47.31, 21.37))
