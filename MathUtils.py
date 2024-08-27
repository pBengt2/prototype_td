import math
import numpy as np

LARGE_NUMBER = math.inf


def normalize(values):
    v = np.array(values)
    return v / np.sqrt(np.sum(v ** 2))


def sq_dist(loc1, loc2):
    x1, y1 = loc1
    x2, y2 = loc2
    return (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)


def distance(loc1, loc2):
    return math.sqrt(sq_dist(loc1, loc2))


def pseudo_dijkstra(nodes, source):
    remaining_nodes = []  # list of nodes
    distances = {}  # Node : Dist to source
    previous_nodes = {}  # Prev node (at lowest dist)

    for node in nodes:
        if not node.is_occupied():
            distances[node] = None
            previous_nodes[node] = None
            remaining_nodes.append(node)

    distances[source] = 0

    while len(remaining_nodes) > 0:
        u = None
        min_dist = LARGE_NUMBER
        for node in remaining_nodes:
            dist = distances[node]
            if dist is not None and dist < min_dist:
                min_dist = dist
                u = node

        if u is None:
            # print("unreachable_nodes: " + str(len(remaining_nodes)))
            return distances, previous_nodes, remaining_nodes

        remaining_nodes.remove(u)

        for v in u.get_unoccupied_neighbors():
            if v in remaining_nodes:
                dist_u = distances[u]
                dist_v = distances[v]
                alt = dist_u + 1
                if dist_v is None or alt < dist_v:
                    distances[v] = alt
                    previous_nodes[v] = u

    return distances, previous_nodes, remaining_nodes
