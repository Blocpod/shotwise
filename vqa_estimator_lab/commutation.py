from __future__ import annotations

import numpy as np

def pauli_anticommutes(a: int, b: int) -> bool:
    '''
    Single-qubit Pauli anticommutation.
    0=I, 1=X, 2=Y, 3=Z.
    '''
    if a == 0 or b == 0 or a == b:
        return False
    return True

def commute(code_a, code_b) -> bool:
    '''
    Two Pauli strings commute iff the number of qubit positions with
    non-identity, different Paulis is even.
    '''
    anti = 0
    for a, b in zip(code_a, code_b):
        if pauli_anticommutes(int(a), int(b)):
            anti += 1
    return anti % 2 == 0

def anticommutation_graph(codes, include_identity: bool = False):
    '''
    Build an adjacency list for the anticommutation graph.
    An edge means two terms cannot be placed in the same commuting group.
    '''
    indices = [
        i for i, row in enumerate(codes)
        if include_identity or np.any(row != 0)
    ]

    graph = {i: set() for i in indices}

    for pos, i in enumerate(indices):
        for j in indices[pos + 1:]:
            if not commute(codes[i], codes[j]):
                graph[i].add(j)
                graph[j].add(i)

    return graph

def greedy_color_graph(graph):
    '''
    Greedy coloring of a graph represented as adjacency sets.
    Returns list of color groups, each a list of node IDs.
    '''
    # Largest-degree-first heuristic
    nodes = sorted(graph.keys(), key=lambda n: len(graph[n]), reverse=True)

    color_of = {}
    groups = []

    for node in nodes:
        forbidden = {color_of[nbr] for nbr in graph[node] if nbr in color_of}
        color = 0
        while color in forbidden:
            color += 1

        color_of[node] = color
        while len(groups) <= color:
            groups.append([])
        groups[color].append(node)

    return groups

def greedy_commuting_groups(coeffs, codes, include_identity: bool = False):
    '''
    General commuting grouping, not restricted to qubit-wise compatibility.

    Note:
        General commuting groups may require more sophisticated joint measurement
        circuits than simple single-qubit basis rotations. This grouping is therefore
        mainly a measurement-setting lower-bound / advanced backend planning tool
        unless a joint-measurement compiler is available.
    '''
    graph = anticommutation_graph(codes, include_identity=include_identity)
    return greedy_color_graph(graph)

def grouping_stats_general(coeffs, codes):
    groups = greedy_commuting_groups(coeffs, codes)
    sizes = np.array([len(g) for g in groups], dtype=int)
    term_count = int(np.sum(np.any(codes != 0, axis=1)))

    return {
        "terms_excluding_identity": term_count,
        "commuting_groups": len(groups),
        "average_terms_per_group": float(sizes.mean()) if len(sizes) else 0.0,
        "max_terms_in_group": int(sizes.max()) if len(sizes) else 0,
        "median_terms_per_group": float(np.median(sizes)) if len(sizes) else 0.0,
        "measurement_setting_reduction": term_count / len(groups) if len(groups) else float("inf"),
    }

def validate_commuting_groups(codes, groups) -> bool:
    for group in groups:
        for i, a in enumerate(group):
            for b in group[i+1:]:
                if not commute(codes[a], codes[b]):
                    return False
    return True

def greedy_color_graph_ordered(graph, order):
    color_of = {}; groups = []
    for node in order:
        forbidden = {color_of[nbr] for nbr in graph[node] if nbr in color_of}
        color = 0
        while color in forbidden: color += 1
        color_of[node] = color
        while len(groups) <= color: groups.append([])
        groups[color].append(node)
    return groups

def color_order_largest_degree(graph):
    return sorted(graph.keys(), key=lambda n: len(graph[n]), reverse=True)

def color_order_smallest_degree(graph):
    return sorted(graph.keys(), key=lambda n: len(graph[n]))

def color_order_largest_degree_tiebreak_weight(graph, codes):
    return sorted(graph.keys(), key=lambda n: (len(graph[n]), int(np.count_nonzero(codes[n]))), reverse=True)

def color_order_random(graph, seed=123):
    rng = np.random.default_rng(seed); nodes = list(graph.keys()); rng.shuffle(nodes); return nodes

def dsatur_color_graph(graph):
    uncolored = set(graph.keys()); color_of = {}
    while uncolored:
        best = None; best_key = None
        for node in uncolored:
            sat = {color_of[nbr] for nbr in graph[node] if nbr in color_of}
            key = (len(sat), len(graph[node]))
            if best is None or key > best_key: best, best_key = node, key
        forbidden = {color_of[nbr] for nbr in graph[best] if nbr in color_of}
        color = 0
        while color in forbidden: color += 1
        color_of[best] = color; uncolored.remove(best)
    groups = [[] for _ in range(max(color_of.values(), default=-1)+1)]
    for node, color in color_of.items(): groups[color].append(node)
    return groups

def greedy_commuting_groups_heuristic(coeffs, codes, heuristic="dsatur", seed=123, include_identity=False):
    graph = anticommutation_graph(codes, include_identity=include_identity)
    if heuristic == "largest_degree": return greedy_color_graph_ordered(graph, color_order_largest_degree(graph))
    if heuristic == "smallest_degree": return greedy_color_graph_ordered(graph, color_order_smallest_degree(graph))
    if heuristic == "weighted_degree": return greedy_color_graph_ordered(graph, color_order_largest_degree_tiebreak_weight(graph, codes))
    if heuristic == "random": return greedy_color_graph_ordered(graph, color_order_random(graph, seed))
    if heuristic == "dsatur": return dsatur_color_graph(graph)
    raise ValueError(f"Unknown coloring heuristic: {heuristic}")

def best_commuting_groups(coeffs, codes, heuristics=None, random_trials=2, seed=123, include_identity=False):
    if heuristics is None: heuristics = ["dsatur","largest_degree","weighted_degree","smallest_degree"]
    candidates = [(h, greedy_commuting_groups_heuristic(coeffs,codes,h,seed,include_identity)) for h in heuristics]
    for k in range(random_trials):
        candidates.append((f"random_{k}", greedy_commuting_groups_heuristic(coeffs,codes,"random",seed+k,include_identity)))
    def score(item):
        _, groups = item; sizes = [len(g) for g in groups]
        return (len(groups), -float(np.mean(sizes)) if sizes else 0.0)
    name, groups = min(candidates, key=score)
    return groups, {"heuristic": name, "num_groups": len(groups)}
