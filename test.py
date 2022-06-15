# -*- coding: UTF-8 -*-
from module.fileProcessing import FileProcessing
import copy
from module import *
import math
from math import radians, cos, sin, asin, sqrt

def CorrectionCoordErr(coord_data):
    """mapbox下的坐标偏移纠正,lng,lat"""
    coord_data[0] -= 0.0113
    coord_data[1] -= 0.0034
    return coord_data


def distance_computaion(coord1, coord2):
    """
    计算经纬度的直线距离
    :param coord1:[lng1, lat1]
    :param coord2:[lng2, lat2]
    :return 距离/米
    """
    lng1, lat1, lng2, lat2 = map(radians, [float(coord1[0]), float(coord1[1]), float(coord2[0]), float(coord2[1])])  # 经纬度转换成弧度
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    distance = 2 * asin(sqrt(a)) * 6371 * 1000  # 地球平均半径，6371km
    # distance = round(distance / 1000, 3)
    return int(distance)


def extract_get_on_off_data():
    data = fp.load_data("./static/od_data/get_off_clustered")
    node_result = {
        "type": "FeatureCollection",
        "features": []
    }
    for each in data["features"]:
        if each["properties"]["label"] != "-1":
            node_result["features"].append(each)

    fp.save_file(node_result, "./static/od_data/get_off_classed")


def change_time_data(start, end, add_time, is_save=-1):
    """手动修改时间表里的两个节点间的时间"""
    time_data = fp.load_data("./static/GA_input_data/min_price_graph")
    dis_data = fp.load_data("./static/GA_input_data/real_distance_table")
    index_data = fp.load_data("./static/GA_input_data/transport_index")

    if is_save == 1:
        time_data[start][end] += add_time
        # time_data[end][start] += add_time
        print("time: ", time_data[start][end], " , distance: ", dis_data[start][end], " , type(0-by,1-car): ",
              index_data[start][end])
        fp.save_file(time_data, "./static/GA_input_data/min_price_graph")
    else:
        print("time: ", time_data[start][end], " , distance: ", dis_data[start][end], " , type(0-by,1-car): ",
              index_data[start][end])


fp = FileProcessing()
if __name__ == '__main__':

    node_result = {
        "type": "FeatureCollection",
        "features": []
    }
    node_tmp = {
        "type": "Feature",
        "properties": {
        },
        "geometry": {
            "type": "Point",
            "coordinates": [
            ]
        }
    }

    # extract_get_on_off_data()

    # 统计无向边
    # data = fp.load_data("./static/network_data/center_network")
    # links = copy.deepcopy(data["link"])
    # undirected_link = []
    # for i in range(0, len(links)):
    #     source = links[i]["source"]
    #     target = links[i]["target"]
    #     if source == -1 or target == -1:
    #         continue
    #     for j in range(i+1, len(links)):
    #         if links[j]["source"] == target and links[j]["target"] == source:
    #             links[i]["visit_count"] += links[j]["visit_count"]
    #             links[j]["source"] = -1
    #             links[j]["target"] = -1
    #             break
    #     undirected_link.append(links[i])
    # data["undirected_link"] = undirected_link
    # fp.save_file(data, "new_data")

    # data = fp.load_data("./static/network_data/new_data")
    # node = data["node"]
    # for each in node:
    #     t = copy.deepcopy(tmp)
    #     t["properties"]["color"] = each["color"]
    #     t["properties"]["cluster_center"] = each["cluster_center"]
    #     t["properties"]["center_street"] = each["center_street"]
    #     t["geometry"]["coordinates"] = [each["lng"], each["lat"]]
    #     result["features"].append(t)
    # fp.save_file(result, "./static/network_data/center_node")

    # data = fp.load_data("./static/network_data/center_node")
    # for each in data["features"]:
    #     each["geometry"]["coordinates"][0] -= 0.0113
    #     each["geometry"]["coordinates"][1] -= 0.0034
    # fp.save_file(data, "./static/network_data/center_node1")

    # data = fp.load_data("./static/network_data/new_data")
    # node = data["node"]
    # link = data["undirected_link"]

    # 根据流量计算边的粗细
    # res = []
    # for each in link:
    #     temp = []
    #     visit_count = each["visit_count"]
    #     if visit_count < 1000:
    #         temp.append(1)
    #     elif 1000 <= visit_count < 20000:
    #         temp.append(int(visit_count / 1000))
    #     elif 20000 <= visit_count < 40000:
    #         temp.append(22)
    #     elif 40000 <= visit_count < 90000:
    #         temp.append(25 + int((visit_count - 40000) / 10000))
    #     else:
    #         temp.append(30)
    #
    #     for item in node:
    #         if item["cluster_center"] == each["source"]:
    #             temp.append([item["lng"], item["lat"]])
    #         elif item["cluster_center"] == each["target"]:
    #             temp.append([item["lng"], item["lat"]])
    #     res.append(temp)
    # fp.save_file(res, "link_geo")

    # create community graph
    # data = fp.load_data("./static/community_data/resorted_community")
    # node_data = data["node"]
    # for each in node_data:
    #     t = copy.deepcopy(node_tmp)
    #     t["properties"]["name"] = each["name"]
    #     t["properties"]["id"] = each["id"]
    #     t["properties"]["speed"] = each["speed"]
    #     if "color" not in each.keys():
    #         t["properties"]["color"] = "#808080"
    #     else:
    #         t["properties"]["color"] = each["color"]
    #
    #     coord = CorrectionCoordErr([each["lng"], each["lat"]])
    #     t["geometry"]["coordinates"] = coord
    #     node_result["features"].append(t)
    #
    # merge_link = copy.deepcopy(data["link"])
    #
    # for i in range(0, len(merge_link)):
    #     source = merge_link[i]["source"]
    #     target = merge_link[i]["target"]
    #     for j in range(i+1, len(merge_link)):
    #         if (merge_link[j]["source"] == target and merge_link[j]["target"] == source) and merge_link[j]["source"]!=-1:
    #             merge_link[j]["source"] = -1
    #             merge_link[j]["target"] = -1
    #             break
    # for item in merge_link:
    #     if item["source"] != -1 and item["target"] != -1:
    #         t = copy.deepcopy(tmp)
    #         start = None
    #         end = None
    #         for obj in node_data:
    #             if obj["id"] == item["source"]:
    #                 start = obj
    #             if obj["id"] == item["target"]:
    #                 end = obj
    #         start_coord = CorrectionCoordErr([start["lng"], start["lat"]])
    #         end_coord = CorrectionCoordErr([end["lng"], end["lat"]])
    #         t["geometry"]["coordinates"] = [start_coord, end_coord]
    #         result["features"].append(t)
    #
    # community_geo = {"node": node_result, "link": result}
    # fp.save_file(community_geo, "community_geo")

    # data = {"origin_site": "福津大街", "destination_site": "中山路步行街"}
    # ga = MultiRoute.MultiRoute("./static/GA_input_data")
    # route = ga.calc_multi_route(data)
    # print(route)

    ############################################################################################
    # ga = MultiRoute.MultiRoute("./static/GA_input_data")
    # ga.update_min_price_by_add_station([310, 309])
    # data = fp.load_data("./static/GA_input_data/min_price_graph")
    # da = fp.load_data("./static/GA_input_data/transport_index")
    # print(data[140][287], da[140][287])

    change_time_data(20, 4, 100, 11)

    pass


