import json
import requests
import folium
from geopy.distance import geodesic
from pprint import pprint
from dotenv import load_dotenv
import os

load_dotenv()
def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
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


with open("C:\python_projects\8\coffee.json", "r") as my_file:
  file_contents = my_file.read()

coffee_data = json.loads(file_contents)


place = input('Где Вы находитесь? ')
apikey = os.getenv('api')
user_coords = fetch_coordinates(apikey, place)


if not user_coords:
    print("Не удалось определить координаты указанного места.")
else:
    print('Ваши координаты:', user_coords)

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

    coffee_shops_sorted = sorted(coffee_shops, key=lambda x: x['distance_km'])[:5]

    print("\n5 ближайших кофеен:")
    pprint(coffee_shops_sorted)

    m = folium.Map(location=user_coords, zoom_start=14)

    folium.Marker(
        location=user_coords,
        popup="Ваше местоположение",
        icon=folium.Icon(color='red', icon='user')
    ).add_to(m)

    for shop in coffee_shops_sorted:
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

    m.save('coffee_map.html')
    print("\nКарта сохранена в файл coffee_map.html")