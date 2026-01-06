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
        graph: dict[tuple[str, str], list[tuple[str, str]]],
        shell_deployers: list[str]
) -> list[tuple[tuple[str, str], bool]]:
    """
    Linearize dependencies with cycle breaking via shell deployments.
    Example: A→B→C→A returns [((page, C),True), ((page, B), False), ((page, A), False), ((page, C), False)]

    Note: Only certain resource types support shell deployments (assignment, page, quiz).
    Other types (syllabus, file, etc.) have deterministic IDs and don't need shell deployments.
    """

    sccs = tarjan_scc(graph)

    cycle_breakers = set()
    scc_map = {}

    for scc in sccs:
        if len(scc) > 1:
            # All nodes in an SCC that are depended upon by other nodes in the SCC
            # need to be cycle breakers (deployed as shells first)
            for node in scc:
                scc_map[node] = scc
                # Check if any other node in the SCC depends on this node
                # and that this node supports shell deployment
                if node[0] in shell_deployers:
                    for other_node in scc:
                        if other_node != node and node in graph.get(other_node, []):
                            cycle_breakers.add(node)
                            break

    for node, deps in graph.items():
        # Self-loops only need cycle breaking if the type supports shell deployment
        if node in deps and node[0] in shell_deployers:
            cycle_breakers.add(node)

    acyclic_graph = {}
    for node, deps in graph.items():
        if node in scc_map:
            # Remove all edges within the same SCC to break cycles
            acyclic_graph[node] = [d for d in deps if d not in scc_map[node]]
        elif node in cycle_breakers:
            # Self-loop case
            acyclic_graph[node] = [d for d in deps if d != node]
        else:
            acyclic_graph[node] = deps

    topo_order = kahns_topological_sort(acyclic_graph)

    # Shell deployments for cycle breakers must happen FIRST (before everything else)
    # so that other resources can reference them. Then the full deployment happens
    # in the natural topological order.
    result = [(node, True) for node in topo_order if node in cycle_breakers]
    result.extend((node, False) for node in topo_order)

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
