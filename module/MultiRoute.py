# -*- coding: UTF-8 -*-

from .fileProcessing import FileProcessing
from .MyGA import MyGA
import networkx as nx
import copy


class MultiRoute:
    """计算多模式路线"""
    def __init__(self, file_path):
        self.fp = FileProcessing(file_path)
        pass

    def calc_multi_route(self, input_data):
        """计算多模式路线"""
        origin_site = input_data["origin_site"]
        destination_site = input_data["destination_site"]
        origin_site_id = str(self.get_street_id_by_name(origin_site))
        destination_site = str(self.get_street_id_by_name(destination_site))

        # dual_graph = self.fp.load_data("Undirected_community_dual_matrix")
        transport_index = self.fp.load_data("transport_index")
        min_price_graph = self.fp.load_data("min_price_graph")

        node_len = len(min_price_graph)
        input_nodes = []
        for i in range(node_len):
            if i != 90 and i != 96:
                input_nodes.append(str(i))

        input_edges = []
        for i in range(node_len):
            for j in range(node_len):
                if min_price_graph[i][j] != -1:
                    input_edges.append((str(i), str(j), min_price_graph[i][j]))

        G = nx.Graph()
        # 往图添加节点和边
        G.add_nodes_from(input_nodes)
        G.add_weighted_edges_from(input_edges)

        ga = MyGA(G, min_price_graph, transport_index, input_nodes, [origin_site_id, destination_site], 100, 40, 0.8, 0.05)
        route = ga.run()
        route_data = self.get_route_geo(route)
        return route_data

    def get_street_id_by_name(self, name):
        """根据站点id获取名称"""
        street_data = self.fp.load_data("resorted_community")["node"]
        for each in street_data:
            if each["name"] == name:
                return each["id"]
        return -1

    def get_route_geo(self, route):
        """将路线节点数组转换成geo类型的数据"""
        street_data = self.fp.load_data("resorted_community")
        route_geo_data = []
        for each in route:
            result = {}
            # 将路线节点数组转换成节点geo数据
            route_lis = each["route"]
            route_mode = each["transport_mode"]
            route_coord_lis = []
            node_tmp = []
            for item in route_lis:
                for node_info in street_data["node"]:
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
            for i in range(1, len(route_lis)):
                transport_mode = "car" if route_mode[i-1] == 1 else "bike"
                link_tmp.append({
                    "properties": {
                        "transport_mode": transport_mode
                    },
                    "coordinates": [
                        route_coord_lis[i-1],
                        route_coord_lis[i]
                    ]
                })

            link_geo = self.get_geo_format(link_tmp, "link")

            result["cost_time"] = each["cost_time"]
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




