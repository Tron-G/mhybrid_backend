# -*- coding: UTF-8 -*-
from .fileProcessing import FileProcessing


class ODModule:
    """返回上下车的热点网络数据"""
    def __init__(self, file_path):
        self.fp = FileProcessing(file_path)
        pass

    def get_on_data(self):
        data = self.fp.load_data("get_on_classed")
        return data

    def get_off_data(self):
        data = self.fp.load_data("get_off_classed")
        return data
