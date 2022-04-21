# -*- coding: UTF-8 -*-
from module.fileProcessing import FileProcessing
import copy
from module import *
import math


def CorrectionCoordErr(coord_data):
    """mapbox下的坐标偏移纠正,lng,lat"""
    coord_data[0] -= 0.0113
    coord_data[1] -= 0.0034
    return coord_data


fp = FileProcessing()
if __name__ == '__main__':

    # data = fp.load_data("./static/od_data/get_on_clustered")
    # node_result = {
    #     "type": "FeatureCollection",
    #     "features": []
    # }
    # node_tmp = {
    #     "type": "Feature",
    #     "properties": {
    #     },
    #     "geometry": {
    #         "type": "Point",
    #         "coordinates": [
    #         ]
    #     }
    # }
    #
    # for each in data["features"]:
    #     if each["properties"]["label"] != "-1":
    #         result["features"].append(each)
    #
    # fp.save_file(result, "./static/od_data/get_on_classed")
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

    data = {"origin_site": "福津大街", "destination_site": "中山路步行街"}
    ga = MultiRoute.MultiRoute("./static/GA_input_data")
    route = ga.calc_multi_route(data)
    print(route["route_attr"])



    pass


