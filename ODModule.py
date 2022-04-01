# -*- coding: UTF-8 -*-
from fileProcessing import FileProcessing


class ODModule:
    def __init__(self):
        self.fp = FileProcessing("./static/od_data")
        pass

    def get_on_data(self):
        data = self.fp.load_data("get_on_classed")
        return data

    def get_off_data(self):
        data = self.fp.load_data("get_off_classed")
        return data
