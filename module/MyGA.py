# -*- coding:utf-8 -*-
import networkx as nx
import random
from tqdm import tqdm
import copy
import operator
import numpy as np


class MyGA:
    """使用a-star改良的遗传算法"""
    def __init__(self, graph_g, min_price_graph, transport_index, node_list, from_to, size_pop=20, max_iter=50, prob_cross=0.5,
                 prob_mut=0.01):
        """
        :param graph_g: networkx 生成的网络图
        :param min_price_graph: 二维矩阵，节点到节点的最短用时表， -1表示不可达
        :param transport_index: 对应最短用时表中的出行模式，0为单车，1为出租车，-1表示不可达
        :param node_list: 输入的网络图中的节点编号数组，字符串数组，用于生成随机路线时选择中间节点
        :param from_to:[from, to] 起点和终点
        :param size_pop: 种群数量
        :param max_iter: 迭代次数
        :param prob_cross: 交叉几率 [0,1]
        :param prob_mut: 变异几率 [0,1]
        """
        self.graph_g = graph_g
        self.min_price_graph = min_price_graph
        self.transport_index = transport_index
        self.node_list = node_list
        self.node_len = len(self.node_list)
        self.from_to = from_to
        self.size_pop = size_pop
        self.max_iter = max_iter
        self.prob_cross = prob_cross
        self.prob_mut = prob_mut
        # 目标函数
        self.func = self.path_cost
        # 一次迭代后的种群个体,在图的最短路径问题中X和染色体可以一致
        self.X = []
        # 个体对应的目标函数值
        self.Y = []
        # 个体适应值,在图的最短路径问题中Y和适应值可以一致，不过需要重新定义适应度，Y越小适应度越大
        self.FitV = None

        # self.FitV_history = []
        self.generation_best_X = []
        self.generation_best_Y = []
        # 每一代种群的平均适应度
        self.generation_avg_Y = []

        # 添加一个数组记录每一代所有的x值
        self.all_history_X = []
        self.all_history_Y = []
        self.all_history_FitV = []
        self.best_x, self.best_y = None, None

        # 保存染色体,在图的最短路径问题中X和染色体可以一致
        self.chrom = []
        # 缓存每一代最优个体，不交叉，不变异
        self.last_best_chrom_index = 0
        self.last_best_chrom = []

        # A*算法生成初始种群
        self.create_origin_chrom()
        # for each in self.chrom:
        #     print(each)
        # print(len(self.chrom))
        pass

    def create_origin_chrom(self):
        """使用A*算法，生成初始种群"""
        middle_node = []
        for i in range(0, self.size_pop):
            temp_node = self.node_list[int(random.random() * self.node_len)]
            # 随机节点度必须大于等于2，否则无法形成路径
            while (temp_node in middle_node) or (temp_node in self.from_to) or (len(self.graph_g.adj[temp_node]) < 2):
                temp_node = self.node_list[int(random.random() * self.node_len)]
            else:
                middle_node.append(temp_node)
        # print(middle_node, len(middle_node))
        for i in range(self.size_pop):
            # 增加多样性，随机选择1到3个中间节点, 增加中间节点为1的概率
            dice = random.random()
            middle_node_nums = 1
            if 0 < dice <= 0.3:
                middle_node_nums = 2
            elif 0.3 < dice <= 0.7:
                middle_node_nums = 1
            elif 0.7 < dice < 1:
                middle_node_nums = 3
            # middle_node_nums = random.randint(1, 3)
            path = []
            if middle_node_nums == 1:
                rand_node1 = int(random.random() * len(middle_node))
                path1 = nx.astar_path(self.graph_g, self.from_to[0], middle_node[rand_node1])
                path2 = nx.astar_path(self.graph_g, middle_node[rand_node1], self.from_to[1])
                path = path1 + path2[1:]
            elif middle_node_nums == 2:
                rand_node1 = int(random.random() * len(middle_node))
                rand_node2 = int(random.random() * len(middle_node))
                path1 = nx.astar_path(self.graph_g, self.from_to[0], middle_node[rand_node1])
                path2 = nx.astar_path(self.graph_g, middle_node[rand_node1], middle_node[rand_node2])
                path3 = nx.astar_path(self.graph_g, middle_node[rand_node2], self.from_to[1])
                path = path1 + path2[1:] + path3[1:]
            elif middle_node_nums == 3:
                rand_node1 = int(random.random() * len(middle_node))
                rand_node2 = int(random.random() * len(middle_node))
                rand_node3 = int(random.random() * len(middle_node))
                path1 = nx.astar_path(self.graph_g, self.from_to[0], middle_node[rand_node1])
                path2 = nx.astar_path(self.graph_g, middle_node[rand_node1], middle_node[rand_node2])
                path3 = nx.astar_path(self.graph_g, middle_node[rand_node2], middle_node[rand_node3])
                path4 = nx.astar_path(self.graph_g, middle_node[rand_node3], self.from_to[1])
                path = path1 + path2[1:] + path3[1:] + path4[1:]

            self.chrom.append(path)
        pass

    def selection(self):
        """自然选择"""
        total_fit = sum(self.FitV)
        # print("fitV", self.FitV)
        new_fit = []
        for each in self.FitV:
            new_fit.append(each / total_fit)
        # print("new_fit0", new_fit, sum(new_fit))
        new_fit = self.range_reverse(new_fit)
        # print("new_fit1", new_fit, sum(new_fit))
        new_fit = self.accumulation_fit(new_fit)
        # print(new_fit)

        # 生成随机序列，用于轮盘选择, 随机选择n-1次，将最优个体直接保留（精英主义）
        prob_list = []
        for i in range(self.size_pop - 1):
            prob_list.append(random.random())
        prob_list.sort()
        # print("prob", prob_list)
        fit_index = 0
        prob_index = 0

        new_X = copy.deepcopy(self.chrom)
        # 转轮盘选择法, 随机选择n-1次
        while prob_index < (self.size_pop - 1):
            if prob_list[prob_index] < new_fit[fit_index]:
                new_X[prob_index] = self.chrom[fit_index]
                prob_index += 1
            else:
                fit_index += 1
        # 保留最优个体
        new_X[self.size_pop - 1] = self.chrom[self.FitV.index(min(self.FitV))]
        self.last_best_chrom_index = self.size_pop - 1
        self.last_best_chrom = new_X[self.size_pop - 1]
        # 更新子代染色体
        self.renew_pop(new_X)
        pass

    def crossover(self):
        """染色体单点交叉，随机选择两条不相同的染色体，检查是否存在潜在交叉节点（相同中间节点），随机选择潜在节点中的一个进行交叉"""
        next_generation = []
        # 标记被选中交叉的染色体，子代数量不足优先从未被选择的染色体中补充
        choose_flag = [0] * len(self.chrom)
        for i in range(0, int(self.size_pop / 2)):
            if random.random() < self.prob_cross:
                chrom1 = int(random.random() * self.size_pop)
                chrom2 = int(random.random() * self.size_pop)
                if not operator.eq(self.chrom[chrom1], self.chrom[chrom2]):
                    # 查找相同中间节点作为潜在交叉节点
                    possb_cross_index = []
                    for j in range(1, len(self.chrom[chrom1]) - 1):
                        if (self.chrom[chrom1][j] in self.chrom[chrom2]) and \
                                (self.chrom[chrom2].index(self.chrom[chrom1][j]) != 0 and self.chrom[chrom2].index(
                                    self.chrom[chrom1][j]) != len(self.chrom[chrom2]) - 1):
                            possb_cross_index.append(j)
                    # 交叉操作
                    if len(possb_cross_index) != 0:
                        possb_cross_index_flag = [1]*len(possb_cross_index)
                        cross_not_over = True
                        # 随机选择潜在节点作为交叉节点，若交叉后有断路，重新选择
                        while sum(possb_cross_index_flag) != 0 and cross_not_over:
                            cross_index = int(random.random() * len(possb_cross_index))
                            new_chrom1 = self.chrom[chrom1][:cross_index] + self.chrom[chrom2][cross_index:]
                            new_chrom2 = self.chrom[chrom2][:cross_index] + self.chrom[chrom1][cross_index:]
                            # 有断路
                            if self.check_edge(new_chrom1) == -1 or self.check_edge(new_chrom2) == -1:
                                possb_cross_index_flag[cross_index] = 0
                                continue
                            # print("before", self.chrom[chrom1], self.chrom[chrom2])
                            # print("after", temp1, temp2)
                            choose_flag[chrom1] = 1
                            choose_flag[chrom2] = 1
                            next_generation.append(new_chrom1)
                            next_generation.append(new_chrom2)
                            cross_not_over = False
                            pass
        has_renew = False
        # 交叉后子代数量不足种群数量，进行补充
        while len(next_generation) < self.size_pop:
            # 优先从未被选择的染色体中补充
            if sum(choose_flag) != len(self.chrom):
                for i in range(self.size_pop - len(next_generation)):
                    # 每次补充一个
                    for j in range(len(choose_flag)):
                        if choose_flag[j] != 1:
                            next_generation.append(self.chrom[j])
                            choose_flag[j] = 1
                            break
                    # print("chose form unchoose", next_generation)
            else:
                # 随机补充
                for i in range(self.size_pop - len(next_generation)):
                    index = int(random.random() * len(self.chrom))
                    next_generation.append(self.chrom[index])
                    # print("random choose", next_generation)
        # 子代数量刚好足够或者种群补充完毕，确保最优个体保留(替换最差个体)
        else:
            self.renew_pop(next_generation)
            # need_renew = self.retain_best_individual()
            pass
        # if need_renew:
        #     # 更新子代
        #     self.renew_pop(self.chrom)
        pass

    def mutation(self):
        new_pop = []
        for i in range(self.size_pop):
            if random.random() < self.prob_mut:
                # 变异尝试最多失败10次
                count = 0
                while True:
                    # 在首尾节点间随机定位变异节点，变异节点不能接近尾节点
                    if len(self.chrom[i]) > 3:
                        mut_index = random.randint(1, len(self.chrom[i]) - 3)
                    else:
                        mut_index = random.randint(1, len(self.chrom[i]) - 2)
                    if count == 10:
                        new_pop.append(self.chrom[i])
                        break
                    # 获取变异节点的邻居节点
                    neighbor_nodes = []
                    for each in self.graph_g.adj[self.chrom[i][mut_index]]:
                        neighbor_nodes.append(each)
                    new_neighbor = [i for i in neighbor_nodes if i not in self.from_to]
                    if len(new_neighbor) == 0:
                        count += 1
                        # print("has no neighbor")
                        continue
                    else:
                        find_node = False
                        mut_node = None
                        for each in new_neighbor:
                            # 变异节点必须不在原始路线中
                            if each not in self.chrom[i]:
                                mut_node = each
                                find_node = True
                        # 该节点的所有邻居均在原始路线，变异失败，重新定位节点
                        if not find_node:
                            count += 1
                            # print("no another node")
                            continue
                        path1 = nx.astar_path(self.graph_g, self.from_to[0], mut_node)
                        path2 = nx.astar_path(self.graph_g, mut_node, self.from_to[1])
                        has_same_node = False
                        for p in range(0, len(path1) - 1):
                            if path1[p] in path2:
                                has_same_node = True
                                break
                        if has_same_node:
                            count += 1
                            # print("has same node")
                            continue
                        else:
                            new_path = path1 + path2[1:]
                            new_pop.append(new_path)
                            break
            else:
                # 不进行变异
                new_pop.append(self.chrom[i])

        # 更新子代
        self.renew_pop(new_pop)
        # need_renew = self.retain_best_individual()
        # if need_renew:
        #     self.renew_pop(self.chrom)
        # for each in self.chrom:
        #     if self.check_edge(each) == -1:
        #         self.error = True
        #         print("mutation error")
        pass

    def x2y(self):
        result = []
        for each in self.chrom:
            result.append(self.func(each))
        return result

    def accumulation_fit(self, value):
        """
        计算累积适应度
        :param value:
        :return:
        """
        new_value = copy.deepcopy(value)
        for i in range(len(value) - 1, -1, -1):
            t = 0
            j = 0
            while j <= i:
                t += value[j]
                j += 1
            new_value[i] = t
        new_value[len(value) - 1] = 1
        return new_value

    def range_reverse(self, prob_list):
        """将适应度列表以中位数为界限镜像变换，实现值域反转，并重新归一化"""
        max_value = max(prob_list)
        min_value = min(prob_list)
        mid_value = (max_value + min_value) / 2
        new_prob = []
        # print(mid_value)
        for each in prob_list:
            temp = mid_value - (each - mid_value)
            new_prob.append(temp)
        # print(new_prob)
        sum_prob = sum(new_prob)
        for i in range(len(new_prob)):
            new_prob[i] = new_prob[i] / sum_prob
        # print(new_prob, sum(new_prob))
        return new_prob

    def retain_best_individual(self):
        """保留最优个体, 返回值为false时表示没有操作， true表示替换了最差个体"""
        # 定位最坏个体
        worst_index = self.FitV.index(max(self.FitV))
        # 对比最优
        now_best_index = self.FitV.index(min(self.FitV))
        now_best = min(self.FitV)
        # 当前更优，不进行操作
        if now_best < self.func(self.last_best_chrom):
            self.last_best_chrom = self.chrom[now_best_index]
            self.last_best_chrom_index = now_best_index
            return False
        else:
            # 替换最差个体,改变了self.chrom
            self.chrom[worst_index] = self.last_best_chrom
            self.last_best_chrom_index = worst_index
            return True

    def renew_pop(self, new_chrom):
        """更新子代"""
        self.chrom = new_chrom
        self.X = self.chrom
        self.Y = self.x2y()
        self.FitV = self.Y

    def path_cost(self, path):
        """目标函数"""
        total_time = 0
        for i in range(0, len(path) - 1):
            start = int(path[i])
            end = int(path[i + 1])
            total_time += self.min_price_graph[start][end]
        return round(total_time, 1)

    def run(self):
        for i in tqdm(range(self.max_iter)):
            self.X = self.chrom
            self.Y = self.x2y()
            self.FitV = self.Y
            # print(self.X)
            self.selection()
            self.crossover()
            self.mutation()

            generation_best_index = self.FitV.index(min(self.FitV))
            self.generation_best_X.append(self.X[generation_best_index])
            self.generation_best_Y.append(self.Y[generation_best_index])
            self.generation_avg_Y.append(int(sum(self.Y)/len(self.Y)))
            # add X record
            self.all_history_X.append(self.X.copy())
            self.all_history_Y.append(self.Y.copy())
            self.all_history_FitV.append(self.FitV.copy())

        res = self.output_result()
        return res
        # 返回最后一代
        # return self.X, self.Y

    def check_edge(self, path):
        """断路检查，有断路返回-1"""
        error_path = False
        for i in range(len(path) - 1):
            start = path[i]
            end = path[i + 1]
            find = False
            for each in self.graph_g.edges:
                if (start == each[0] and end == each[1]) or (start == each[1] and end == each[0]):
                    find = True
                    break
            if not find:
                error_path = True
                # print(start, end)
        if error_path:
            return -1
        else:
            return 0

    def trans_mode(self, path):
        """输出路线对应的出行方式"""
        ways = []
        for i in range(len(path) - 1):
            ways.append(self.transport_index[int(path[i])][int(path[i + 1])])
        # print(ways)
        return ways

    def output_result(self):
        """输出全局最短路径、最后一代的路线对应的时间，按时间排序的推荐路线"""

        sorted_route = []

        target_path = nx.astar_path(self.graph_g, self.from_to[0], self.from_to[1])
        target_cost = self.path_cost(target_path)
        print("*************** Shortest Path *************** ")
        print("shortest path:      ", target_path)
        print("transport mode:     ", self.trans_mode(target_path))
        print("path time cost(s):  ", target_cost)
        print("*************** latest generation X *************** ")
        print(self.X)
        print("*************** latest generation Y *************** ")
        print(self.Y)
        print("*************** generation_best_Y *************** ")
        print(self.generation_best_Y)
        print("\n*************** final time sorted routes *************** ")
        x_set = []
        y_set = []
        for i in range(len(self.X)):
            if self.X[i] not in x_set:
                x_set.append(self.X[i])
                y_set.append(self.Y[i])
        np_y = np.array(y_set)
        # 对数据进行从小到大进行排序，返回数据的索引值
        sort_index = np_y.argsort()
        print("*************** total routes: ", len(x_set), "  ********************* ")
        for i in range(len(x_set)):
            cost_time = y_set[sort_index[i]]
            route = x_set[sort_index[i]]
            transport_mode = self.trans_mode(x_set[sort_index[i]])
            tmp = {
                "cost_time": cost_time,
                "route": route,
                "transport_mode": transport_mode
            }
            print("cost time & route ==>  ", cost_time, " , ", route)
            print("transport mode    ==>  ", transport_mode)
            print("------------------------------------------------------")
            sorted_route.append(tmp)

        return sorted_route


