import random
import copy
import networkx as nx
import matplotlib.pyplot as plt
import os

class net_graph:
    INFINITY = 100000  # 无限大的边值

    def __init__(self) -> None:
        # 邻接矩阵
        self.graph = {
            "Copenhagen": {"London": 1, "Amsterdam": 1, "Berlin":1},
            "London": {"Copenhagen": 1, "Amsterdam": 1, "Brussels": 1, "Paris":1},
            "Amsterdam": {"Copenhagen": 1, "London": 1, "Brussels": 1, "Luxemburg": 1, "Berlin": 1},
            "Berlin": {"Copenhagen": 1, "Amsterdam": 1, "Paris": 1, "Prague": 1, "Vienna":1},
            "Brussels": {"London": 1, "Amsterdam": 1, "Luxemburg": 1, "Paris":1},
            "Luxemburg": {"Amsterdam": 1, "Prague": 1, "Zurich": 1, "Paris":1, "Brussels":1},
            "Prague": {"Copenhagen": 1, "Berlin": 1, "Vienna": 1, "Zurich": 1, "Luxemburg": 1},
            "Paris": {"London": 1, "Brussels": 1, "Luxemburg": 1, "Berlin":1, "Zurich":1, "Milan":1},
            "Zurich": {"Luxemburg": 1, "Prague": 1, "Vienna": 1, "Milan": 1, "Milan": 1},
            "Vienna": {"Berlin": 1, "Prague": 1, "Zurich": 1, "Milan": 1},
            "Milan": {"Paris": 1, "Brussels": 1, "Zurich": 1, "Vienna": 1},
        }

        # 设置随机数种子
        random.seed(42)

        # 随机生成边权重
        for node in self.graph:
            for adj_node in self.graph[node]:
                self.graph[node][adj_node] = random.randint(1, 5)
                self.graph[adj_node][node] = self.graph[node][adj_node]

        # 随机生成边容量
        self.link_capacity = copy.deepcopy(self.graph)
        for node in self.graph:
            for adj_node in self.graph[node]:
                self.link_capacity[node][adj_node] = random.randint(20, 100)*10
                self.link_capacity[adj_node][node] = self.link_capacity[node][adj_node]

        # 生成n*(n-1)条流量，流量大小从[10,100]的区间随机生成
        self.flow = dict()        
        for src in self.graph.keys():
            self.flow[src] = dict()
            for des in self.graph.keys():
                if des != src: 
                    self.flow[src][des] = random.randint(10, 100) 

    def draw_graph(self):
        G = nx.Graph()

        # 添加节点和边
        for node in self.graph:
            for adj_node in self.graph[node]:
                G.add_edge(node, adj_node, weight=self.link_capacity[node][adj_node])

        pos = nx.spring_layout(G, k=5)  # 布局算法

        # 绘制节点
        nx.draw_networkx_nodes(G, pos)
        nx.draw_networkx_labels(G, pos, font_size=8)

        # 绘制边
        edges = G.edges(data=True)
        nx.draw_networkx_edges(G, pos)

        # 标注边的容量
        edge_labels = {(u, v): f'{d["weight"]}' for u, v, d in edges}

        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

        plt.title("Network Topology with Link Capacities")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "network_topology.png")


        plt.savefig(file_path, format="png", bbox_inches='tight', dpi=500)
        plt.close()  


# 示例用法
if __name__ == "__main__":
    ng = net_graph()
    ng.draw_graph()