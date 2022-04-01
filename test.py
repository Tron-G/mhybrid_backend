# -*- coding: UTF-8 -*-
from fileProcessing import FileProcessing
import copy


def CorrectionCoordErr(coord_data):
    """mapbox下的坐标偏移纠正"""
    coord_data[0] -= 0.0113
    coord_data[1] -= 0.0034
    return coord_data


fp = FileProcessing()
if __name__ == '__main__':

    data = fp.load_data("./static/od_data/get_on_clustered")
    result = {
        "type": "FeatureCollection",
        "features": []
    }
    tmp = {
        "type": "Feature",
        "properties": {
        },
        "geometry": {
            "type": "Point",
            "coordinates": [
            ]
        }
    }

    for each in data["features"]:
        if each["properties"]["label"] != "-1":
            result["features"].append(each)

    fp.save_file(result, "./static/od_data/get_on_classed")
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

    # result = {
    #     "type": "FeatureCollection",
    #     "features": []
    # }
    # tmp = {
    #     "type": "Feature",
    #     "properties": {
    #       "link_width": ""
    #     },
    #     "geometry": {
    #       "type": "LineString",
    #       "coordinates": []
    #     }
    #   }
    #
    # data = fp.load_data("link_geo")
    # for each in data:
    #     link_width = each[0]
    #     start_point = CorrectionCoordErr(each[1])
    #     end_point = CorrectionCoordErr(each[2])
    #
    #     t = copy.deepcopy(tmp)
    #     t["properties"]["link_width"] = link_width
    #     t["geometry"]["coordinates"] = [start_point, end_point]
    #     result["features"].append(t)
    # fp.save_file(result, "link_geo")

    pass
