# -*- coding: UTF-8 -*-
from time import sleep

from flask import Flask, jsonify, request
from flask_cors import cross_origin
from module import *


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello World!'


@app.route('/get_on_data', methods=['GET', 'POST'])
@cross_origin()
def get_on_data():
    """获取上车热点数据"""
    od = ODModule.ODModule("./static/od_data")
    data = od.get_on_data()
    return jsonify(data)


@app.route('/get_off_data', methods=['GET', 'POST'])
@cross_origin()
def get_off_data():
    """获取下车热点数据"""
    od = ODModule.ODModule("./static/od_data")
    data = od.get_off_data()
    return jsonify(data)


@app.route('/home_route', methods=['GET', 'POST'])
@cross_origin()
def home_route():
    """给定点使用api计算路线测试数据"""
    route = GetRoute.GetRoute()
    data = route.getroute()
    return jsonify(data)


@app.route('/get_cluster_network', methods=['GET', 'POST'])
@cross_origin()
def get_cluster_network():
    """社区聚类网络数据"""
    net = TrafficNetwork.TrafficNetwork("./static/network_data")
    data = net.clustered_network()
    return jsonify(data)


@app.route('/get_carbon_data', methods=['GET', 'POST'])
@cross_origin()
def get_carbon_data():
    """街道碳排放数据"""
    net = TrafficNetwork.TrafficNetwork("./static/network_data")
    data = net.carbon_data()
    return jsonify(data)


@app.route('/get_community_network', methods=['GET', 'POST'])
@cross_origin()
def get_community_network():
    """街道网络数据"""
    net = TrafficNetwork.TrafficNetwork("./static/community_data")
    data = net.community_network()
    return jsonify(data)


@app.route('/calc_multi_route', methods=['GET', 'POST'])
@cross_origin()
def calc_multi_route():
    """多模式路线计算结果数据"""
    data = request.get_json()
    print(data)
    ga = MultiRoute.MultiRoute("./static/GA_input_data")
    # route = ga.calc_multi_route(data)
    fp = fileProcessing.FileProcessing()
    # route = fp.load_data("test-add")
    # route = fp.load_data("test-change")
    # route = fp.load_data("test_one-moudle")

    sleep(1)
    if data["add_station"] is not None:
        route = fp.load_data("test-add")
    else:
        route = fp.load_data("实验路线")
    return jsonify(route)


if __name__ == '__main__':
    app.run()
