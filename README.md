### The Ripple-Spreading Algorithm for the Multi-Objective Shortest Path Problem

##### Reference: Hu X B, Gu S H, Zhang C, et al. Finding all Pareto optimal paths by simulating ripple relay race in multi-objective networks[J]. Swarm and Evolutionary Computation, 2021, 64: 100908.

The multi-objective shortest path problem aims to find a set of paths with minimized costs. 

| Variables     | Meaning                                                      |
| ------------- | ------------------------------------------------------------ |
| network       | Dictionary, {node 1: {node 2: [weight 1, weight 2, ...], ...}, ...} |
| s_network     | The network described by a crisp weight on which we conduct the ripple relay race |
| source        | The source node                                              |
| destination   | The destination node                                         |
| nn            | The number of nodes                                          |
| nw            | The number of objectives                                     |
| neighbor      | Dictionary, {node1: [the neighbor nodes of node1], ...}      |
| v             | The ripple-spreading speed (i.e., the minimum length of arcs) |
| t             | The simulated time index                                     |
| nr            | The number of ripples - 1                                    |
| epicenter_set | List, the epicenter node of the i-th ripple is epicenter_set[i] |
| path_set      | List, the path of the i-th ripple from the source node to node i is path_set[i] |
| radius_set    | List, the radius of the i-th ripple is radius_set[i]         |
| active_set    | List, active_set contains all active ripples                 |
| objective_set | List, the objective value of the traveling path of the i-th ripple is objective_set[i] |
| Omega         | Dictionary, Omega[n] = i denotes that ripple i is generated at node n |

#### Example

![image](https://github.com/Xavier-MaYiMing/The-ripple-spreading-algorithm-for-the-mutli-objective-shortest-path-problem/blob/main/MOSPP.png)

The red number associated with each arc is the first weight, and the green number is the second weight.

```python
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
```

##### Output:

```python
[
    {'path': [0, 2, 4], 'objective': [96, 130]}, 
    {'path': [0, 3, 4], 'objective': [121, 110]}, 
    {'path': [0, 3, 2, 4], 'objective': [151, 60]},
]
```

