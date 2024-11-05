import cplex as cp 
from k_shortest_path import *
from Network_Topology import *



if __name__ == "__main__":
    # create cplex objective 
    cplex_obj = cp.Cplex()
    max_k = 5
    net = net_graph()

    paths = dict()
    x = dict()
    x2src_dst = dict()
    for src in net.flow:
        for des in net.flow[src]:
            paths[(src, des)] = ksp(net, src, des, max_k)
            # add variables, binary variable indicate whether the path is selected
            for i in range(max_k):
                name = "source:{}_destination:{}_p{}".format(src, des, i + 1)
                # x[name] = cplex_obj.variables.add(names=[name], types=['B'])
                x[name] = cplex_obj.variables.add(names=[name], types=['C'], lb=[0], ub=[1])
                # each binary variable corresponds to a path
                x2src_dst[name] = (src, des, i)

    # add objective function
    utility = cplex_obj.variables.add(names=["utility"], types=['C'], lb=[0], ub=[1])

    # set optimization direction
    cplex_obj.objective.set_sense(cplex_obj.objective.sense.minimize)

    # record edges to their corresponding paths
    edge2paths = dict()
    for src, dst in paths:
        for path_id in paths[(src, dst)]:
            path = paths[(src, dst)][path_id]
            for node_index in range(len(path) - 1):
                # add edges to the dict
                if (path[node_index], path[node_index + 1]) not in edge2paths:
                    edge2paths[(path[node_index], path[node_index + 1])] = list() 
                edge2paths[(path[node_index], path[node_index + 1])].append((src, dst, path_id))

    # add flow constraints
    for src in net.flow:
        for dst in net.flow[src]: 
            # each src only select one path to reach one of its destination 
            cplex_obj.linear_constraints.add(lin_expr=[[["source:{}_destination:{}_p{}".format(src, dst, i + 1) for i in range(max_k)], [1.0 for i in range(max_k)]]], 
                                             senses=['E'], rhs=[1])
            # cplex_obj.linear_constraints.add(lin_expr=[sum(x["source:{}_destination:{}_p{}".format(src, dst, i + 1)] for i in range(max_k))], senses=['E'], rhs=[1])

    # add edge capacity constraints
    for node1, node2 in edge2paths:
        name_list = list()
        for src, des, path_no in edge2paths[(node1, node2)]:
            name_list.append(("source:{}_destination:{}_p{}".format(src, des, path_no + 1), src, des))
        # if (node2, node1) in edge2paths:
        #     for src, des, path_no in edge2paths[(node2, node1)]:
        #         name_list.append(("source:{}_destination:{}_p{}".format(src, des, path_no + 1), src, des))
        if name_list is not None:
            cplex_obj.linear_constraints.add(lin_expr=[[[name[0] for name in name_list],[net.flow[name[1]][name[2]] for name in name_list]]], 
                                             senses=['L'], rhs=[net.link_capacity[node1][node2]])
            cplex_obj.linear_constraints.add(lin_expr=[[[name[0] for name in name_list]+['utility'],[net.flow[name[1]][name[2]]/net.link_capacity[node1][node2] for name in name_list]+[-1]]],
                                             senses=['L'], rhs=[0])
        
    cplex_obj.objective.set_linear([('utility', 1.0)]) 

    # get the solution time
    start_time = cplex_obj.get_time()

    # solve the problem
    cplex_obj.solve() 
    cplex_obj.write("model.lp")

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
