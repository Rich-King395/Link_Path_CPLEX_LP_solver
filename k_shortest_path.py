from typing import List
import copy
import heapq as hq
from Network_Topology import net_graph


def dijkstra(gp: net_graph, src, des, node_set: set = None):
    distances = dict()
    parent = dict()
    visited = set()
    path = list()

    for node in gp.graph:
        distances[node] = gp.INFINITY # 初始时，所有节点到达初始节点的距离设置为无穷大
        parent[node] = None 

    if node_set is not None:
        visited = copy.deepcopy(node_set)
    visited.add(src)

    distances[src] = 0 # 起始点与起始点的距离为0
    # 遍历起始点的相邻点
    for node_adj in gp.graph[src]:
        parent[node_adj] = src
        # 起始点与相邻点的距离等于链路权重
        distances[node_adj] = gp.graph[src][node_adj]

    node_min_weight = gp.INFINITY
    node_min = src # 当前正在处理的节点

    while True:
        for node in distances:
            # 找到距离节点最近的相邻点
            if node not in visited and distances[node] < node_min_weight:
                node_min = node
                node_min_weight = distances[node]

        if node_min == des:
            path, path_weight = build_path(gp, parent, src, des)
            return path, path_weight
            # path_weight = 0
            # # 通过 parent 字典反向构建最短路径
            # while node_min != src:
            #     path.append(node_min)
            #     path_weight += gp.graph[node_min][parent[node_min]]
            #     node_min = parent[node_min]
            # path.append(src)
            # # 列表翻转，得到最短路径 path
            # path.reverse()
            # # 返回包含构成最短路径的节点列表和权重和
            # return path, path_weight

        # 跳过已经处理过的节点避免重复处理
        if node_min in visited:
            break

        visited.add(node_min)
        for node_adj in gp.graph[node_min]:
            if distances[node_min] + gp.graph[node_min][node_adj] < distances[node_adj]:
                parent[node_adj] = node_min
                # 更新当前节点与起始节点的距离
                distances[node_adj] = distances[node_min] + gp.graph[node_min][node_adj]

        node_min_weight = gp.INFINITY

    return [], 0

def build_path(gp: net_graph, parent, src, des):
    path = []
    path_weight = 0
    node = des

    while node != src:
        path.append(node)
        path_weight += gp.graph[node][parent[node]]
        node = parent[node]

    path.append(src)
    path.reverse()
    return path, path_weight


def ksp(gp: net_graph, src, des, max_k):
    if max_k < 1:
        return {}

    paths = dict()
    paths_set = set()
    paths_weight = dict()
    paths_deviate = list()

    # 通过Dijkstra算法找到最短路径
    path_tmp, path_weight_tmp = dijkstra(gp, src, des)

    hq.heappush(paths_deviate, (path_weight_tmp, path_tmp))
    paths_set.add(tuple(path_tmp))

    num = 0
    while paths_deviate:
        paths_weight[num], paths[num] = hq.heappop(paths_deviate)
        paths_set.remove(tuple(paths[num]))
        path_now = paths[num]
        num += 1

        if num >= max_k:
            break

        for index in range(len(path_now) - 1):
            gp_tmp = copy.deepcopy(gp)
            remove_edges(gp_tmp, paths, path_now, index)
            # for path in paths:
            #     if paths[path][:index + 1] == path_now[:index + 1]:
            #         each_path = paths[path]
            #         if each_path[index + 1] in gp_tmp.graph[each_path[index]]:
            #             del gp_tmp.graph[each_path[index]][each_path[index + 1]]
            #             del gp_tmp.graph[each_path[index + 1]][each_path[index]]

            path_tmp, path_weight_tmp = dijkstra(gp_tmp, path_now[index], des, set(path_now[:index + 1]))
            if path_weight_tmp == 0:
                continue
            path_s2t_tmp = path_now[:index + 1] + path_tmp[1:]

            if tuple(path_s2t_tmp) not in paths_set:
                hq.heappush(paths_deviate, (path_weight_tmp, path_s2t_tmp))
                paths_set.add(tuple(path_s2t_tmp))

    return paths


def remove_edges(gp_tmp, paths, path_now, index):
    for p in paths:
        if paths[p][:index + 1] == path_now[:index + 1]:
            each_path = paths[p]
            if each_path[index + 1] in gp_tmp.graph[each_path[index]]:
                del gp_tmp.graph[each_path[index]][each_path[index + 1]]
                del gp_tmp.graph[each_path[index + 1]][each_path[index]]