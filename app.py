# -*- coding: UTF-8 -*-
from flask import Flask, redirect, jsonify, request
from flask_cors import cross_origin
from ODModule import ODModule
from GetRoute import Getroute
from TrafficNetwork import TrafficNetwork

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello World!'


@app.route('/get_on_data', methods=['GET', 'POST'])
@cross_origin()
def get_on_data():
    """获取上车热点数据"""
    od = ODModule()
    data = od.get_on_data()
    return jsonify(data)


@app.route('/get_off_data', methods=['GET', 'POST'])
@cross_origin()
def get_off_data():
    """获取下车热点数据"""
    od = ODModule()
    data = od.get_off_data()
    return jsonify(data)


@app.route('/home_route', methods=['GET', 'POST'])
@cross_origin()
def home_route():
    """给定点使用api计算路线测试数据"""
    route = Getroute()
    data = route.getroute()
    return jsonify(data)


@app.route('/get_cluster_network', methods=['GET', 'POST'])
@cross_origin()
def get_cluster_network():
    """社区聚类网络数据"""
    net = TrafficNetwork()
    data = {"node": net.clustered_node(), "link": net.clustered_link()}
    return jsonify(data)


if __name__ == '__main__':
    app.run()
