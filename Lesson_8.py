import json
import os
from geopy.distance import geodesic

import folium
import requests
from dotenv import load_dotenv


COFFEE_SHOPS_FILE = "coffee.json"
MAP_FILE = "coffee_map.html"
YANDEX_GEOCODE_API_URL = "https://geocode-maps.yandex.ru/1.x"


def fetch_coordinates(apikey, address):
    response = requests.get(YANDEX_GEOCODE_API_URL, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)


def load_coffee_shops_data(file_path):
    with open(file_path, "r", encoding='utf-8') as my_file:
        return json.loads(my_file.read())


def calculate_distances(user_coords, coffee_data):
    coffee_shops = []
    for shop in coffee_data:
        try:
            shop_coords = (float(shop['Latitude_WGS84']), float(shop['Longitude_WGS84']))
            distance_km = geodesic(user_coords, shop_coords).km
            coffee_shops.append({
                'name': shop['Name'],
                'address': shop.get('Address', 'Адрес не указан'),
                'coordinates': shop_coords,
                'distance_km': round(distance_km, 2)
            })
        except (ValueError, KeyError):
            continue
    return sorted(coffee_shops, key=lambda x: x['distance_km'])[:5]


def create_map(user_coords, coffee_shops):
    m = folium.Map(location=user_coords, zoom_start=14)

    folium.Marker(
        location=user_coords,
        popup="Ваше местоположение",
        icon=folium.Icon(color='red', icon='user')
    ).add_to(m)

    for shop in coffee_shops:
        folium.Marker(
            location=shop['coordinates'],
            popup=f"{shop['name']}<br>{shop['address']}<br>Расстояние: {shop['distance_km']} км",
            icon=folium.Icon(color='green', icon='coffee')
        ).add_to(m)

    folium.Circle(
        location=user_coords,
        radius=500,
        color='blue',
        fill=True,
        fill_opacity=0.2,
        popup='500 м'
    ).add_to(m)

    folium.Circle(
        location=user_coords,
        radius=1000,
        color='orange',
        fill=True,
        fill_opacity=0.1,
        popup='1 км'
    ).add_to(m)

    return m


def main():
    load_dotenv()
    
    place = input('Где Вы находитесь? ')
    apikey = os.getenv('api')
    
    user_coords = fetch_coordinates(apikey, place)
    if not user_coords:
        print("Не удалось определить координаты указанного места.")
        return

    coffee_data = load_coffee_shops_data(COFFEE_SHOPS_FILE)
    nearest_coffee_shops = calculate_distances(user_coords, coffee_data)
    
    coffee_map = create_map(user_coords, nearest_coffee_shops)
    coffee_map.save(MAP_FILE)
    print(f"Карта сохранена в файл {MAP_FILE}")


if __name__ == "__main__":
    main()
