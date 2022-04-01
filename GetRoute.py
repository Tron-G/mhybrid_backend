# -*- coding: UTF-8 -*-
from urllib.request import urlopen, quote
import json
import random
from urllib import request


class Getroute:
    def getroute(self):
        url = ' https://api.mapbox.com/directions/v5/mapbox/driving/118.090901,24.499548;118.136823,24.482383?geometries=geojson&access_token='
        # url2 = url + str(street1[0]) + ',' + str(street1[1]) + "|" + str(street1[0]) + ',' + str(street1[1]) + '&destinations=' + str(street2[0]) + ',' + str(street2[1]) + "|" + str(street2[0]) + ',' + str(street2[1]) + "&ak=" + key
        url2 = url + "pk.eyJ1IjoieGlhb2JpZSIsImEiOiJja2pndjRhMzQ1d2JvMnltMDE2dnlkMGhrIn0.bCKzSCs5tHTIYk4xQ65doA"
        # print(url2)
        proxy_list = [
            {"http": "124.88.67.54:80"},
            {"http": "61.135.217.7:80"},
            {"http": "42.231.165.132:8118"},
            {"http": "218.91.13.2:46332"},
            {"http": "121.31.176.85:8132"},
            {"http": "218.71.161.56:80"}
        ]
        proxy = random.choice(proxy_list)  # 随机选择一个ip地址
        httpproxy_handler = request.ProxyHandler(proxy)
        opener = request.build_opener(httpproxy_handler)
        req = request.Request(url2)
        response = opener.open(req)
        res = response.read().decode()
        temp = json.loads(res)
        route = temp["routes"][0]["geometry"]["coordinates"]
        template = {
            "type": 'Feature',
            "properties": {},
            "geometry": {
                "type": 'LineString',
                "coordinates": route
            }
        }
        return template

