import json
import unittest
from unittest.mock import patch
from src.exercise_2_main import *


def get_mock_response(filename):
    with open(filename, 'r') as f:
        return json.loads(f.read())


class MyTestCase(unittest.TestCase):
    # Testing get_openweather_data & get_openweather_json
    @patch('src.exercise_2_main.get_openweather_json')
    def test_get_openweather_data(self, mock_get_openweather):
        cities_json = [{"name": "Warsaw", "lat": "52.2319581", "lon": "21.0067249"},
                       {"name": "Budapest", "lat": "47.4979937", "lon": "19.0403594"}]

        mock_get_openweather.side_effect = get_mock_response("../data/mock_openweather.json")
        expected = [Location("Warsaw", 52.232, 21.0067,
                             datetime.utcfromtimestamp(1666728111).strftime('%Y-%m-%dT%H:%MZ'),
                             "OpenWeather", 13.26, 90, 10000, 3.6, 260),
                    Location("Budapest", 47.498, 19.0404,
                             datetime.utcfromtimestamp(1666727746).strftime('%Y-%m-%dT%H:%MZ'),
                             "OpenWeather", 13.88, 80, 10000, 2.24, 309)]

        self.assertListEqual(get_openweather_data(cities_json), expected)

    # Testing get_metar_data & get_metar_json
    @patch('src.exercise_2_main.get_metar_json')
    def test_get_metar_data(self, mock_get_metar):
        cities_json = [{"name": "Warsaw", "lat": "52.2319581", "lon": "21.0067249"},
                       {"name": "Budapest", "lat": "47.4979937", "lon": "19.0403594"}]

        mock_get_metar.side_effect = get_mock_response("../data/mock_metar.json")
        expected = [Location("Warsaw", 52.2319581, 21.0067249,
                             "2022-10-25T20:30Z",
                             "METAR", 13, 94, 9999, 5, 270),
                    Location("Budapest", 47.4979937, 19.0403594,
                             "2022-10-25T20:30Z",
                             "METAR", 10, 88, 9999, 1, 330)]
        self.assertListEqual(get_metar_data(cities_json), expected)

    # Testing compare_weather_data & df_to_json_file
    def test_compare_weather_data(self):
        df1 = pd.DataFrame(
            {'name': ['Warsaw', 'Budapest'], 'lat': [52.2319581, 47.4979937], 'lon': [21.0067249, 19.0403594]})
        df2 = pd.DataFrame({'name': ['Warsaw', 'Budapest'], 'lat': [52.232, 47.498], 'lon': [21.0067, 19.0404]})

        compare_weather_data(df1, df2)

        with open('../data/metric.json', 'r') as actual:
            with open('../data/metric_test.json', 'r') as expected:
                self.assertEqual(expected.read(), actual.read())


if __name__ == '__main__':
    unittest.main()
