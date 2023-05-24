#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/25 12:41
# @Author  : Xavier Ma
# @Email   : xavier_mayiming@163.com
# @File    : RSA4MOSPP.py
# @Statement : The ripple-spreading algorithm for the multi-objective shortest path problem
# @Reference : Hu X B, Gu S H, Zhang C, et al. Finding all Pareto optimal paths by simulating ripple relay race in multi-objective networks[J]. Swarm and Evolutionary Computation, 2021, 64: 100908.
import copy


def find_neighbor(network):
    """
    find the neighbor of each node
    :param network:
    :return: {node 1: [the neighbor nodes of node 1], ...}
    """
    nn = len(network)
    neighbor = []
    for i in range(nn):
        neighbor.append(list(network[i].keys()))
    return neighbor


def find_speed(network, neighbor, nw):
    """
    find the ripple-spreading speed
    :param network:
    :param neighbor:
    :param nw:
    :return:
    """
    s_network = copy.deepcopy(network)
    min_value = [1e6 for i in range(nw)]
    max_value = [0 for i in range(nw)]
    for i in range(len(network)):
        for j in neighbor[i]:
            temp_list = network[i][j]
            for k in range(nw):
                min_value[k] = min(min_value[k], temp_list[k])
                max_value[k] = max(max_value[k], temp_list[k])
    max_min = [max_value[k] / min_value[k] for k in range(nw)]
    best_index = max_min.index(min(max_min))
    for i in range(len(network)):
        for j in neighbor[i]:
            s_network[i][j] = network[i][j][best_index]
    return min_value[best_index], s_network


def dominated(obj1, obj2):
    """
    judgment whether ripple 1 is dominated by ripple 2
    :param obj1: the objective value of ripple 1
    :param obj2: the objective value of ripple 2
    :return:
    """
    sum_less = 0
    for i in range(len(obj1)):
        if obj1[i] < obj2[i]:
            return False
        elif obj1[i] != obj2[i]:
            sum_less += 1
    if sum_less != 0:
        return True
    return False


def find_new_ripples(incoming_ripples):
    """
    screen out the dominated ripple from incoming ripples
    :param incoming_ripples:
    :return:
    """
    ripple_num = len(incoming_ripples)
    new_ripples_flag = [True for n in range(ripple_num)]
    for i in range(ripple_num):
        obj1 = incoming_ripples[i]['objective']
        for j in range(ripple_num):
            if i != j:
                obj2 = incoming_ripples[j]['objective']
                if dominated(obj1, obj2):
                    new_ripples_flag[i] = False
                    break
    new_feasible_ripples = []
    for i in range(ripple_num):
        if new_ripples_flag[i]:
            new_feasible_ripples.append(incoming_ripples[i])
    return new_feasible_ripples


def find_POR(incoming_ripples, omega, objective_set, omega_destination):
    """
    find the new Pareto-optimal ripples at a node
    :param incoming_ripples:
    :param omega:
    :param objective_set:
    :param omega_destination: the ripples at the destination nodes
    :return:
    """
    new_ripples = []
    new_feasible_ripples = find_new_ripples(incoming_ripples)
    if not omega:
        return new_feasible_ripples
    else:
        for ripple1 in new_feasible_ripples:
            flag = True
            obj1 = ripple1['objective']
            for ripple2 in omega:
                if dominated(obj1, objective_set[ripple2]):
                    flag = False
                    break
            if flag:
                for ripple3 in omega_destination:
                    if dominated(obj1, objective_set[ripple3]):
                        flag = False
                        break
            if flag:
                new_ripples.append(ripple1)
    return new_ripples


def main(network, source, destination):
    """
    the main function
    :param network: {node 1: {node 2: [weight1, weight2, ...], ...}, ...}
    :param source: the source node
    :param destination: the destination node
    :return:
    """
    # Step 1. Initialization
    nn = len(network)  # node number
    neighbor = find_neighbor(network)
    nw = len(network[source][neighbor[source][0]])  # the number of objectives
    v, s_network = find_speed(network, neighbor, nw)
    t = 0  # time
    nr = 0  # the number of ripples - 1
    epicenter_set = []  # epicenter set
    radius_set = []  # radius set
    path_set = []  # path set
    objective_set = []  # objective set
    active_set = []  # all active ripples
    omega = {}  # the ever generated ripples at each node
    for node in range(nn):
        omega[node] = []

    # Step 2. Initialize the first ripple
    epicenter_set.append(source)
    radius_set.append(0)
    objective_set.append([0 for n in range(nw)])
    path_set.append([source])
    active_set.append(nr)
    omega[source].append(nr)
    nr += 1

    # Step 3. The main loop
    while True:

        # Step 3.1. Termination judgment
        if not active_set:
            break

        # Step 3.2. Time updates
        t += 1
        incoming_ripples = {}
        remove_ripples = []
        for ripple in active_set:
            flag_inactive = True

            # Step 3.3. Active ripples spread out
            radius_set[ripple] += v

            # Step 3.4. New incoming ripples
            epicenter = epicenter_set[ripple]
            radius = radius_set[ripple]
            path = path_set[ripple]
            obj = objective_set[ripple]
            for node in neighbor[epicenter]:
                temp_length = s_network[epicenter][node]
                if node not in path and temp_length <= radius < temp_length + v:
                    temp_list = network[epicenter][node]
                    temp_path = copy.deepcopy(path)
                    temp_path.append(node)
                    temp_obj = [obj[n] + temp_list[n] for n in range(nw)]
                    if node in incoming_ripples.keys():
                        incoming_ripples[node].append({
                            'path': temp_path,
                            'radius': radius - temp_length,
                            'objective': temp_obj,
                        })
                    else:
                        incoming_ripples[node] = [{
                            'path': temp_path,
                            'radius': radius - temp_length,
                            'objective': temp_obj,
                        }]

                # Step 3.5. Active ripple -> inactive
                if radius < temp_length:
                    flag_inactive = False
            if flag_inactive:
                remove_ripples.append(ripple)
        for ripple in remove_ripples:
            active_set.remove(ripple)

        # Step 3.6. Generate new ripples
        if destination in incoming_ripples.keys():
            new_ripples = find_POR(incoming_ripples[destination], omega[destination], objective_set, [])
            for item in new_ripples:
                path_set.append(item['path'])
                radius_set.append(item['radius'])
                epicenter_set.append(destination)
                objective_set.append(item['objective'])
                omega[destination].append(nr)
                nr += 1

        for node in incoming_ripples.keys():
            if node != destination:
                new_ripples = find_POR(incoming_ripples[node], omega[node], objective_set, omega[destination])
                for item in new_ripples:
                    path_set.append(item['path'])
                    radius_set.append(item['radius'])
                    epicenter_set.append(node)
                    objective_set.append(item['objective'])
                    omega[node].append(nr)
                    active_set.append(nr)
                    nr += 1

    # Step 4. Sort the results
    result = []
    for ripple in omega[destination]:
        result.append({
            'path': path_set[ripple],
            'objective': objective_set[ripple],
        })
    return result


if __name__ == '__main__':
    test_network = {
        0: {1: [62, 50], 2: [44, 90], 3: [67, 10]},
        1: {0: [62, 50], 2: [33, 25], 4: [52, 90]},
        2: {0: [44, 90], 1: [33, 25], 3: [32, 10], 4: [52, 40]},
        3: {0: [67, 10], 2: [32, 10], 4: [54, 100]},
        4: {1: [52, 90], 2: [52, 40], 3: [54, 100]},
    }
    source_node = 0
    destination_node = 4
    print(main(test_network, source_node, destination_node))
