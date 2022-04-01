# -*- coding: UTF-8 -*-
from fileProcessing import FileProcessing


class TrafficNetwork:
    def __init__(self):
        self.fp = FileProcessing("./static/network_data")
        pass

    def clustered_node(self):
        """社区网络的geo节点数据"""
        return self.fp.load_data("center_node")

    def clustered_link(self):
        """社区网络的geo边数据"""
        return self.fp.load_data("link_geo")

