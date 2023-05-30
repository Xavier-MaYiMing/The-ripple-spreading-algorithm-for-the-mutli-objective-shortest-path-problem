#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/5/24 13:14
# @Author  : Xavier Ma
# @Email   : xavier_mayiming@163.com
# @File    : RSA.py
# @Statement : The ripple-spreading algorithm (RSA) for the multi-objective shortest path problem
# @Reference : Hu X B, Gu S H, Zhang C, et al. Finding all Pareto optimal paths by simulating ripple relay race in multi-objective networks[J]. Swarm and Evolutionary Computation, 2021, 64: 100908.
from copy import deepcopy
from numpy import inf, any, all, array, argmin


class Ripple:
    def __init__(self, epicenter, radius, path, objective):
        self.epicenter = epicenter
        self.radius = radius
        self.path = path
        self.obj = objective
        self.dominated = False

    def spread(self, v):
        self.radius += v


def find_neighbors(network):
    # find the neighbors of each node
    neighbor = []
    for i in network.keys():
        neighbor.append(list(network[i].keys()))
    return neighbor


def find_speed(network, neighbor, nw):
    # find the ripple-spreading speed
    max_value = array([0 for _ in range(nw)])
    min_value = array([inf for _ in range(nw)])
    for i in network.keys():
        for j in neighbor[i]:
            for k in range(nw):
                min_value[k] = min(min_value[k], network[i][j][k])
                max_value[k] = max(max_value[k], network[i][j][k])
    best_ind = argmin(max_value / min_value)
    s_net = deepcopy(network)
    for i in network.keys():
        for j in neighbor[i]:
            s_net[i][j] = network[i][j][best_ind]
    return min_value[best_ind], s_net


def dominate(obj1, obj2):
    # judge if obj1 Pareto dominates obj2
    return all(obj1 <= obj2) and any(obj1 != obj2)


def find_POR(incoming_ripples, omega, ripples, node, destination):
    # find the Pareto-optimal ripples
    new_ripples = []
    for ripple1 in incoming_ripples:
        for ripple2 in incoming_ripples:
            if ripple1 != ripple2 and not ripple2.dominated and dominate(ripple1.obj, ripple2.obj):
                ripple2.dominated = True
    for r in range(len(incoming_ripples) - 1, -1, -1):
        if incoming_ripples[r].dominated:
            incoming_ripples.pop(r)
    for ripple1 in incoming_ripples:
        for r2 in omega[node]:
            if dominate(ripples[r2].obj, ripple1.obj):
                ripple1.dominated = True
                break
        if not ripple1.dominated and node != destination:
            for r3 in omega[destination]:
                if dominate(ripples[r3].obj, ripple1.obj):
                    ripple1.dominated = True
                    break
        if not ripple1.dominated:
            new_ripples.append(ripple1)
    return new_ripples


def main(network, source, destination):
    """
    The main function
    :param network: {node 1: {node 2: [weight1, weight2, ...], ...}, ...}
    :param source: the source node
    :param destination: the destination node
    :return:
    """
    # Step 1. Initialization
    nn = len(network)  # node number
    neighbor = find_neighbors(network)
    nw = len(network[source][neighbor[source][0]])  # objective number
    v, s_net = find_speed(network, neighbor, nw)
    nr = 0  # the number of ripples - 1
    ripples = []  # ripple set
    active_ripples = []  # active ripple set
    omega = {}  # the set that records the ripple generated at each node
    for node in range(nn):
        omega[node] = []

    # Step 2. Initialize the first ripple
    ripples.append(Ripple(source, 0, [source], array([0 for _ in range(nw)])))
    active_ripples.append(nr)
    omega[source].append(nr)
    nr += 1

    # Step 3. The main loop
    while active_ripples:

        # Step 3.1. Active ripples spread out
        incoming_ripples = {}
        inactive_ripples = []
        for r in active_ripples:
            flag_inactive = True
            ripple = ripples[r]
            ripple.spread(v)
            for node in neighbor[ripple.epicenter]:
                temp_length = s_net[ripple.epicenter][node]
                if node not in ripple.path and temp_length <= ripple.radius < temp_length + v:
                    new_path = ripple.path.copy()
                    new_path.append(node)
                    if node in incoming_ripples.keys():
                        incoming_ripples[node].append(Ripple(node, ripple.radius - temp_length, new_path, ripple.obj + network[ripple.epicenter][node]))
                    else:
                        incoming_ripples[node] = [Ripple(node, ripple.radius - temp_length, new_path, ripple.obj + network[ripple.epicenter][node])]

                # Step 3.2. Active -> inactive
                if flag_inactive and ripple.radius < temp_length:
                    flag_inactive = False
            if flag_inactive:
                inactive_ripples.append(r)
        for r in inactive_ripples:
            active_ripples.remove(r)

        # Step 3.3. Generate new ripples
        for node in incoming_ripples.keys():
            new_ripples = find_POR(incoming_ripples[node], omega, ripples, node, destination)
            for ripple in new_ripples:
                ripples.append(ripple)
                if node != destination:
                    active_ripples.append(nr)
                omega[node].append(nr)
                nr += 1

    # Step 4. Sort the results
    result = []
    for r in omega[destination]:
        ripple = ripples[r]
        result.append({
            'path': ripple.path,
            'objective': list(ripple.obj),
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
