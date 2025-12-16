import os
import requests
from urllib.parse import urlencode


class GeocodeService:
    @staticmethod
    def get_address_by_latlng(latlng):
        api_key = os.getenv('GOOGLE_GEOCODE_KEY', 'your_default_key')  # Встановіть ключ API
        url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latlng}&key={api_key}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    @staticmethod
    def get_latlng_by_address(address):
        if not address:
            return {"lat": None, "lng": None}

        api_key = os.getenv('GOOGLE_GEOCODE_KEY', 'your_default_key')  # Встановіть ключ API
        query = urlencode({"address": address})
        url = f'https://maps.googleapis.com/maps/api/geocode/json?{query}&key={api_key}'

        try:
            response = requests.get(url)
            response.raise_for_status()
            response_data = response.json()

            if response_data.get('results'):
                location = response_data['results'][0]['geometry']['location']
                return {
                    "lat": location.get('lat'),
                    "lng": location.get('lng'),
                }
        except requests.exceptions.RequestException as e:
            pass

        return {"lat": None, "lng": None}
