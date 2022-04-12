# -*- coding:utf-8 -*-
import pandas as pd
import os
import json
from tqdm import tqdm


class FileProcessing:
    """文件读取及存储操作, 默认json类型文件"""

    def __init__(self, read_folder="", save_folder=""):
        """检查文件夹是否存在"""
        if read_folder != "":
            self.__read_folder = read_folder
        else:
            self.__read_folder = ""
        if save_folder != "":
            self.__save_folder = save_folder
            self.check_folder_exist(self.__save_folder)
        else:
            self.__save_folder = ""

    def load_data(self, file, file_type="json"):
        """
        文件加载
        :param file: 文件名
        :param file_type: 文件类型
        :return: 文件数据
        """
        if self.__read_folder != "":
            file_name = self.__read_folder + "/" + file + "." + file_type
        else:
            file_name = file + "." + file_type

        if file_type == "json":
            with open(file_name) as f:
                data = json.load(f, encoding='UTF-8')
                return data
        elif file_type == "csv":
            data = pd.read_csv(file_name)
            return data

    def save_file(self, data, file, file_type="json"):
        """
        文件保存
        :param data: 待保存数据
        :param file: 保存的文件名
        :param file_type: 文件类型
        :return:
        """
        if self.__save_folder == "":
            file_name = file + "." + file_type
        else:
            file_name = self.__save_folder + "/" + file + "." + file_type

        if file_type == "json":
            with open(file_name, "w") as fp:
                fp.write(json.dumps(data, indent=4, ensure_ascii=False))
        elif file_type == "csv":
            data.to_csv(file_name, index=False)

    def create_geojson(self, list_data, lng_col, lat_col, save_file_name):
        """
        将经纬度表格转为geojson格式
        :param list_data: 输入数组
        :param lng_col: 要读取的经度名
        :param lat_col: 要读取的纬度名
        :param save_file_name: 保存的文件名
        :return:
        """
        # print(list_data[0])
        data = {
            "type": "FeatureCollection",
            "features": []
        }
        sample = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": []
            }
        }
        for i in tqdm(range(0, len(list_data))):
            # print(list_data[i][0])
            # temp = copy.deepcopy(sample)
            sample["geometry"]["coordinates"].append([list_data[i][lng_col], list_data[i][lat_col]])
        data["features"].append(sample)
        #
        # print(type(data))
        with open(save_file_name + ".json", "w") as fp:
            fp.write(json.dumps(data, indent=2, ensure_ascii=False))
        pass

    def load_cut_data(self, length, file, file_type="json"):
        """返回切割指定长度的数据, 暂时只支持csv"""
        data = self.load_data(file, file_type)
        if len(data) < length:
            return data
        else:
            new_data = data[-length:]
            new_data = new_data.reset_index(drop=True)
            return new_data

    def check_folder_exist(self, path):
        folder = os.path.exists(path)
        if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        pass


# def data_cut():
#     """数据切割函数"""
#     data = load_data("0601.json", "json")
#     index = 0
#     file_index = 1
#     count = 0
#     cut_data = []
#     for each in data:
#         cut_data.append(data[each])
#         count += 1
#         index += 1
#         if index == 640 or count == 6742:
#             save_file(cut_data, "data_part_" + str(file_index), "json")
#             index = 0
#             cut_data = []
#             print("---> ", file_index)
#             file_index += 1
