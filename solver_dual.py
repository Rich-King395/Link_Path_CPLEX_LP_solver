import cplex as cp 
from k_shortest_path import *
from Network_Topology import *


if __name__ == "__main__":
    # create cplex objective 
    cplex_obj = cp.Cplex()
    max_k = 5
    net = net_graph()
    net.draw_graph()
    paths = dict()

    # add variables
    n = dict()
    n_name = []
    for node in net.link_capacity:
        for node_adj in net.link_capacity[node]:
            name = "node:{}_node_adj:{}".format(node, node_adj)
            n_name.append(name)
            n[name] = cplex_obj.variables.add(names=[name], types=['C'], lb=[0])

    # print(n)
    # print(len(n))

    m = dict()
    m_name = []
    for src in net.flow:
        for des in net.flow[src]:
            paths[(src, des)] = ksp(net, src, des, max_k)
            name = "source:{}_destination:{}".format(src, des)
            m_name.append(name)
            m[name] = cplex_obj.variables.add(names=[name], types=['C'])

    # print(m)
    # print(len(m))
    
    # record edges to their corresponding paths
    edge2paths = dict()
    for src, des in paths:
        for path_id in paths[(src, des)]:
            path = paths[(src, des)][path_id]
            for node_index in range(len(path) - 1):
                # add edges to the dict
                if (path[node_index], path[node_index + 1]) not in edge2paths:
                    edge2paths[(path[node_index], path[node_index + 1])] = list()
                edge2paths[(path[node_index], path[node_index + 1])].append((src, des, path_id))

    # print(edge2paths.keys())
    # print(len(edge2paths.keys()))
   
    delta = dict() 
    for node in net.link_capacity:
        for node_adj in net.link_capacity[node]:
            delta[(node, node_adj)] = dict()
            for src in net.flow:
                for des in net.flow[src]:
                    for path_id in paths[(src, des)]:
                        delta[(node, node_adj)][(src, des, path_id)] = 0
            if (node, node_adj) in edge2paths:
                for src, des, path_id in edge2paths[(node, node_adj)]:
                    delta[(node, node_adj)][(src, des, path_id)] = 1

    # print(delta)
    # print(len(delta))        
    # print(len(delta[('Copenhagen', 'London')]))

    # add constraints
    '''Constraint 1'''
    lin_expr_vars_1 = [name for name in n_name]
    lin_expr_coeffs_1 = []
    for node in net.link_capacity:
        for node_adj in net.link_capacity[node]:
            lin_expr_coeffs_1 = lin_expr_coeffs_1 + [net.link_capacity[node][node_adj]]
    cplex_obj.linear_constraints.add(lin_expr=[[lin_expr_vars_1, lin_expr_coeffs_1]],
                                            senses=['E'], rhs=[1])
    
    '''Constraint 2'''
    for src in net.flow:
        for des in net.flow[src]:
            for i in range(max_k):
                lin_expr_vars_2 = [f"source:{src}_destination:{des}"] + n_name
                lin_expr_coeffs_2 = [-1]
                for node in net.link_capacity:
                    for node_adj in net.link_capacity[node]:
                        lin_expr_coeffs_2 = lin_expr_coeffs_2 + [delta[(node, node_adj)][(src, des, i)] * net.flow[src][des]]
                cplex_obj.linear_constraints.add(lin_expr=[[lin_expr_vars_2, lin_expr_coeffs_2]],senses=['G'], rhs=[0])

    # add objective function
    cplex_obj.objective.set_linear([(name, 1.0) for name in m_name])
    
    # set optimization direction
    cplex_obj.objective.set_sense(cplex_obj.objective.sense.maximize) 

    # get the solution time
    start_time = cplex_obj.get_time()

    # solve the problem
    cplex_obj.solve() 
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "model_dual.lp")
    cplex_obj.write("model_dual.lp")

    solve_time = cplex_obj.get_time() - start_time  


    if cplex_obj.solution.is_primal_feasible(): 
        print("Solution is feasible")     
        solution = cplex_obj.solution.get_values() 
        print(solution) 

        objective_value = cplex_obj.solution.get_objective_value()
        print("Objective value: ", objective_value)

        print("Solve time (seconds):", solve_time)

    else: 
        print("Solution is infeasible")
