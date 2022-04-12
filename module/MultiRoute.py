# -*- coding: UTF-8 -*-

from .fileProcessing import FileProcessing
from .MyGA import MyGA
import networkx as nx


class MultiRoute:
    """计算多模式路线"""
    def __init__(self, file_path):
        self.fp = FileProcessing(file_path)
        pass

    def calc_multi_route(self, input_data):
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
        return route

    def get_street_id_by_name(self, name):
        street_data = self.fp.load_data("resorted_community")["node"]
        for each in street_data:
            if each["name"] == name:
                return each["id"]
        return -1





