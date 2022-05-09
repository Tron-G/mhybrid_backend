# -*- coding: UTF-8 -*-
from .fileProcessing import FileProcessing


class TrafficNetwork:
    def __init__(self, file_path):
        self.fp = FileProcessing(file_path)
        pass

    def clustered_network(self):
        """社区聚类网络的geo节点数据"""
        node = self.fp.load_data("center_node")
        link = self.fp.load_data("link_geo")
        network_data = {"node": node, "link": link}
        return network_data

    def community_network(self):
        """街道级别混合网络的geo数据"""
        net = self.fp.load_data("community_geo")
        node = self.fp.load_data("traffic_flow")
        station = self.fp.load_data("bike_station_geo")
        data = {"network": net, "traffic_flow": node, "station": station}
        return data

    def carbon_data(self):
        data = self.fp.load_data("carbon_heat")
        return data