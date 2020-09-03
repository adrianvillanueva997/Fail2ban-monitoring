import os
import requests
import time

from sqlalchemy import create_engine
from sqlalchemy.sql import text
from dotenv import load_dotenv

load_dotenv(verbose=True)
engine = create_engine(f"mysql+mysqldb://{os.getenv('username')}:{os.getenv('password')}@{os.getenv('ip')}",
                       encoding='utf-8')
ips = []
with open('f2b.txt', 'r', encoding='utf-8') as file:
    for ip in file:
        ips.append(str(ip).replace('\n', ''))

with engine.connect() as conn:
    for ip in ips:
        try:
            re = requests.get(f'http://ip-api.com/json/{ip}')  # This endpoint is limited to 45 requests per minute
            data = re.json()
            country = data['country']
            region = data['regionName']
            city = data['city']
            cp = data['zip']
            lat = data['lat']
            lon = data['lon']
            isp = data['isp']
            query = text(
                'insert into Grafana.ips values (:_ip,:_country,:_city,:_zip,:_lat,:_lng,:_isp, curdate()) ')
            print(f'Insertado: {ip}')
            conn.execute(query, _ip=ip, _country=country, _city=city, _zip=cp, _lat=lat, _lng=lon, _isp=isp)
            time.sleep(1.5)
        except Exception as e:
            print(e)
            time.sleep(1.5)
