from collections import deque

from ..our_logging import get_logger

logger = get_logger()


def tarjan_scc(graph: dict[tuple[str, str], list[tuple[str, str]]]) -> list[list[tuple[str, str]]]:
    """Find strongly connected components (cycles) using Tarjan's algorithm."""
    index_counter = [0]
    stack = []
    lowlink = {}
    index = {}
    on_stack = set()
    sccs = []

    def strongconnect(node):
        index[node] = index_counter[0]
        lowlink[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)

        for successor in graph.get(node, []):
            if successor not in index:
                strongconnect(successor)
                lowlink[node] = min(lowlink[node], lowlink[successor])
            elif successor in on_stack:
                lowlink[node] = min(lowlink[node], index[successor])

        if lowlink[node] == index[node]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            sccs.append(scc)

    for node in graph.keys():
        if node not in index:
            strongconnect(node)

    return sccs


def kahns_topological_sort(graph: dict[tuple[str, str], list[tuple[str, str]]]) -> list[tuple[str, str]]:
    """Topological sort using Kahn's algorithm (dependencies first)."""
    in_degree = {node: 0 for node in graph}
    for deps in graph.values():
        for dep in deps:
            if dep in graph:
                in_degree[dep] += 1

    queue = deque([node for node, degree in in_degree.items() if degree == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        for dep in graph.get(node, []):
            if dep in in_degree:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

    if len(result) != len(graph):
        raise ValueError("Internal error: acyclic graph still has cycles")

    return result[::-1]


def linearize_dependencies(
    graph: dict[tuple[str, str], list[tuple[str, str]]]
) -> list[tuple[tuple[str, str], bool]]:
    """
    Linearize dependencies with cycle breaking via shell deployments.
    Example: A→B→C→A returns [((page, C),True), ((page, B), False), ((page, A), False), ((page, C), False)]
    """
    sccs = tarjan_scc(graph)

    cycle_breakers = set()
    scc_map = {}

    for scc in sccs:
        if len(scc) > 1:
            cycle_breakers.add(scc[0])
            for node in scc:
                scc_map[node] = scc

    for node, deps in graph.items():
        if node in deps:
            cycle_breakers.add(node)

    acyclic_graph = {}
    for node, deps in graph.items():
        if node in cycle_breakers:
            if node in scc_map:
                acyclic_graph[node] = [d for d in deps if d not in scc_map[node]]
            else:
                acyclic_graph[node] = [d for d in deps if d != node]
        else:
            acyclic_graph[node] = deps

    topo_order = kahns_topological_sort(acyclic_graph)

    result = [(node, node in cycle_breakers) for node in topo_order]
    result.extend((node, False) for node in topo_order if node in cycle_breakers)

    return result


if __name__ == '__main__':
    dependency_dict = {
        'A': ['B'],
        'B': ['C', 'D'],
        'C': [],
        'D': ['C']
    }

    # expect C, D, B, A
    order = linearize_dependencies(dependency_dict)
    print(order)
