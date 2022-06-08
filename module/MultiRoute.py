# -*- coding: UTF-8 -*-

from .fileProcessing import FileProcessing
from .MyGA import MyGA
import networkx as nx
import copy
import math
from math import radians, cos, sin, asin, sqrt


class MultiRoute:
    """计算多模式路线"""

    def __init__(self, file_path):
        self.fp = FileProcessing(file_path)
        # 最多返回路线数量
        self.MAX_ROUTE = 5
        self.street_data = self.fp.load_data("resorted_community")
        self.min_price_graph = self.fp.load_data("min_price_graph")
        self.transport_index = self.fp.load_data("transport_index")
        pass

    def calc_multi_route(self, input_data):
        """计算多模式路线"""
        origin_site = input_data["origin_site"]
        destination_site = input_data["destination_site"]
        origin_site_id = str(self.get_street_id_by_name(origin_site))
        destination_site_id = str(self.get_street_id_by_name(destination_site))

        # 添加站点后更新时间表
        if input_data["add_station"] is not None:
            self.update_min_price_by_add_station(input_data["add_station"])

        node_len = len(self.min_price_graph)
        input_nodes = []
        for i in range(node_len):
            # 去除90和96的街道点
            if i != 90 and i != 96:
                input_nodes.append(str(i))

        input_edges = []
        for i in range(node_len):
            for j in range(node_len):
                if self.min_price_graph[i][j] != -1:
                    input_edges.append((str(i), str(j), self.min_price_graph[i][j]))

        G = nx.Graph()
        # 往图添加节点和边
        G.add_nodes_from(input_nodes)
        G.add_weighted_edges_from(input_edges)

        ga = MyGA(G, self.min_price_graph, self.transport_index, input_nodes, [origin_site_id, destination_site_id], 100, 40, 0.8,
                  0.05)
        route = ga.run()

        # 截取排行前的结果，减少计算
        if len(route) > self.MAX_ROUTE:
            route = route[:self.MAX_ROUTE]

        route_attr = self.calc_attr(route)
        route_data = self.get_route_geo(route, route_attr)

        result = {"route": route_data, "route_attr": route_attr, "all_history_Y": ga.all_history_Y}
        # self.fp.save_file(result, "test")
        return result

    def get_street_id_by_name(self, name):
        """根据站点id获取名称"""
        street_data = self.fp.load_data("resorted_community")["node"]
        for each in street_data:
            if each["name"] == name:
                return each["id"]
        return -1

    def get_route_geo(self, route, route_attr):
        """将路线节点数组转换成geo类型的数据"""

        route_geo_data = []

        for i in range(0, len(route)):
            result = {}
            # 将路线节点数组转换成节点geo数据
            route_lis = route[i]["route"]
            route_mode = route[i]["transport_mode"]
            route_coord_lis = []
            node_tmp = []
            for item in route_lis:
                for node_info in self.street_data["node"]:
                    if int(item) == node_info["id"]:
                        node_tmp.append({
                            "properties": {
                                "id": node_info["id"],
                                "name": node_info["name"],
                                "speed": node_info["speed"],
                                "color": self.speed_to_color(node_info["speed"])
                            },
                            "coordinates": [node_info["lng"], node_info["lat"]]
                        })
                        route_coord_lis.append([node_info["lng"], node_info["lat"]])
            node_geo = self.get_geo_format(node_tmp, "node")

            # 将路线节点数组转换成边geo数据，加入边的出行模式属性
            link_tmp = []
            for j in range(1, len(route_lis)):
                transport_mode = "car" if route_mode[j - 1] == 1 else "bike"
                carbon_percent = route_attr[i]["route_carbon_list"][j-1]/max(route_attr[i]["route_carbon_list"])
                heat_color = self.get_color_by_percentage(carbon_percent)
                link_tmp.append({
                    "properties": {
                        "transport_mode": transport_mode,
                        "carbon_heat_color": heat_color,
                    },
                    "coordinates": [
                        route_coord_lis[j - 1],
                        route_coord_lis[j]
                    ]
                })

            link_geo = self.get_geo_format(link_tmp, "link")

            result["cost_time"] = route[i]["cost_time"]
            result["node"] = node_geo
            result["link"] = link_geo
            route_geo_data.append(result)
        return route_geo_data

    def speed_to_color(self, speed):
        """根据速度匹配颜色"""
        speed = int(speed)
        speed_color = ["#E02401", "#F78812", "#FFE1AF", "#B1E693", "#6ECB63"]
        if speed <= 20:
            color = speed_color[0]
        elif 20 < speed < 30:
            color = speed_color[1]
        else:
            color = speed_color[4]
        return color

    def get_geo_format(self, data, data_type):
        """构造geo类型数据"""
        result = {
            "type": "FeatureCollection",
            "features": []
        }
        if data_type == "node":
            item_tmp = {
                "type": "Feature",
                "properties": {
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                    ]
                }
            }
        else:
            item_tmp = {
                "type": "Feature",
                "properties": {
                    "link_width": ""
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": []
                }
            }
        for each in data:
            tmp = copy.deepcopy(item_tmp)
            for item in each["properties"]:
                tmp["properties"][item] = each["properties"][item]
            tmp["geometry"]["coordinates"] = each["coordinates"]
            result["features"].append(tmp)
        return result

    def calc_attr(self, route_data):
        """计算属性：换乘次数，花费，碳排放"""
        route_attr = []
        distance_table = self.fp.load_data("real_distance_table")
        index = 0
        for each in route_data:
            route_node = each["route"]
            route_mode = each["transport_mode"]
            cost_time = each["cost_time"]
            # 路线上街道的速度
            route_speed = []
            # 各条路段的真实街道距离
            route_distance = []
            # 各条路段的出行用时
            route_time = []
            # 各路段街道名
            route_street = []

            for node in route_node:
                for item in self.street_data["node"]:
                    if int(node) == item["id"]:
                        route_speed.append(item["speed"])
                        route_street.append(item["name"])

            for i in range(1, len(route_node)):
                start = int(route_node[i - 1])
                end = int(route_node[i])
                route_distance.append(distance_table[start][end])
                route_time.append(self.min_price_graph[start][end])

            # 换乘次数
            trans_time = 0
            for i in range(1, len(route_mode)):
                if route_mode[i] != route_mode[i - 1]:
                    trans_time += 1
            # 路线花费
            cost_money = 0
            car_dis = 0
            for i in range(0, len(route_distance)):
                if route_mode[i] == 1 and i != len(route_distance) - 1:
                    car_dis += route_distance[i]
                elif car_dis != 0 and (route_mode[i] == 0 or i == len(route_distance) - 1):
                    if car_dis <= 3000:
                        money = 10
                    else:
                        money = math.ceil((car_dis - 3000) / 1000) * 2 + 10
                    cost_money += money
                    car_dis = 0

            # 路程碳排放量, 公式参见：dx.doi.org/10.1016/j.jtrangeo.2017.05.001
            route_carbon_list = []
            for i in range(1, len(route_speed)):
                if route_mode[i-1] == 0:
                    route_carbon_list.append(0)
                else:
                    if route_speed[i] > route_speed[i - 1]:
                        delta = 1
                    else:
                        delta = 0
                    carbon = 0.002633 * (0.3 * route_time[i-1] + 0.028 * route_distance[i-1] + 0.056*delta*(route_speed[i] ** 2 - route_speed[i - 1] ** 2))
                    route_carbon_list.append(carbon)

            street_color = []
            for item in route_speed:
                street_color.append(self.speed_to_color(item))

            tmp = {
                "route_id": index,
                "cost_time": cost_time,
                "route_time": route_time,
                "total_distance": sum(route_distance),
                "route_distance": route_distance,
                "route_street": route_street,
                "route_mode": route_mode,
                "transfer_time": trans_time,
                "cost_money": cost_money,
                "route_carbon": sum(route_carbon_list),
                "route_carbon_list": route_carbon_list,
                "street_color": street_color
            }
            route_attr.append(tmp)
            index += 1

        return route_attr

    def get_color_by_percentage(self, value):
        """热力图颜色转换，根据0-1返回对应颜色"""
        value *= 100
        r = g = b = 0
        if value <= 50:
            g = 210
            r = int((value / 50) * 250)
        else:
            r = 230
            g = int(((100 - value) / 50) * 180)
        t1 = hex(r)[2:]
        t1 = ("0" + t1) if len(t1) == 1 else t1
        t2 = hex(g)[2:]
        t2 = ("0" + t2) if len(t2) == 1 else t2
        t3 = hex(b)[2:]
        t3 = ("0" + t3) if len(t3) == 1 else t3
        return "#" + t1 + t2 + t3

    def distance_computaion(self, coord1, coord2):
        """
        计算经纬度的直线距离
        :param coord1:[lng1, lat1]
        :param coord2:[lng2, lat2]
        :return 距离/米
        """
        lng1, lat1, lng2, lat2 = map(radians, [float(coord1[0]), float(coord1[1]), float(coord2[0]),
                                               float(coord2[1])])  # 经纬度转换成弧度
        dlon = lng2 - lng1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        distance = 2 * asin(sqrt(a)) * 6371 * 1000  # 地球平均半径，6371km
        # distance = round(distance / 1000, 3)
        return int(distance)

    def update_min_price_by_add_station(self, add_station):
        """
        根据输入的添加单车站点，更新最短用时表
        :param add_station 添加站点id列表
        """
        # 设置单车到达的最远街区直线距离
        reach_dis = 1000
        # 设置单车平均速度15km/h, 4.17m/s
        bike_speed = 4.17

        distance_table = self.fp.load_data("real_distance_table")
        add_coord = []
        for i in range(0, len(add_station)):
            for each in self.street_data["node"]:
                if each["id"] == add_station[i]:
                    add_coord.append([each["lng"], each["lat"]])
                    break
        print(add_station, add_coord)
        reach_street = []
        for i in range(0, len(add_coord)):
            tmp = []
            for each in self.street_data["node"]:
                dis = self.distance_computaion(add_coord[i], [each["lng"], each["lat"]])
                if dis <= 1000:
                    tmp.append(each["id"])
            reach_street.append(tmp)
        # print(reach_street)

        for i in range(0, len(add_coord)):
            for item in reach_street[i]:
                new_bike_time = round(distance_table[add_station[i]][item] / bike_speed)
                # print(str(add_station) + ":" + str(item) + "   , " + str(self.min_price_graph[add_station][item]) + "   , " + str(self.transport_index[add_station][item]) ,distance_table[add_station][item])
                # print(new_bike_time)

                if new_bike_time < self.min_price_graph[add_station[i]][item] or self.min_price_graph[add_station[i]][item] == -1:
                    self.min_price_graph[add_station[i]][item] = new_bike_time
                    self.transport_index[add_station[i]][item] = 0
                    # print(add_station[i], item)

