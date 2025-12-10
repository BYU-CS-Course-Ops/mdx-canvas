from collections import deque

from ..our_logging import get_logger

logger = get_logger()


def tarjan_scc(graph: dict[tuple[str, str], list[tuple[str, str]]]) -> list[list[tuple[str, str]]]:
    """
    Find all strongly connected components using Tarjan's algorithm.

    Args:
        graph: Dependency graph where keys are nodes and values are lists of dependencies

    Returns:
        List of SCCs, where each SCC is a list of nodes.
        SCCs with size > 1 represent cycles.
        The first node in each SCC is the one encountered first during DFS.
    """
    index_counter = [0]
    stack = []
    lowlink = {}
    index = {}
    on_stack = set()
    sccs = []

    def strongconnect(node):
        # Set the depth index for this node to the smallest unused index
        index[node] = index_counter[0]
        lowlink[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)

        # Consider successors of node
        for successor in graph.get(node, []):
            if successor not in index:
                # Successor has not been visited; recurse on it
                strongconnect(successor)
                lowlink[node] = min(lowlink[node], lowlink[successor])
            elif successor in on_stack:
                # Successor is on stack and hence in the current SCC
                lowlink[node] = min(lowlink[node], index[successor])

        # If node is a root node, pop the stack and generate an SCC
        if lowlink[node] == index[node]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            sccs.append(scc)

    # Run DFS from all nodes to handle disconnected components
    for node in graph.keys():
        if node not in index:
            strongconnect(node)

    return sccs


def kahns_topological_sort(graph: dict[tuple[str, str], list[tuple[str, str]]]) -> list[tuple[str, str]]:
    """
    Perform topological sort using Kahn's algorithm.

    Args:
        graph: Dependency graph (assumed to be acyclic)

    Returns:
        List of nodes in topological order (dependencies first)

    Raises:
        ValueError: If the graph contains cycles (shouldn't happen if cycles are broken first)
    """
    in_degree = {}

    # Build the graph and compute in-degrees of nodes
    for key, deps in graph.items():
        if key not in in_degree:
            in_degree[key] = 0
        for dep in deps:
            if dep not in in_degree:
                in_degree[dep] = 0
            if dep in graph:  # Only count dependencies that are in the graph
                in_degree[dep] += 1

    # Perform topological sort (Kahn's algorithm)
    queue = deque([key for key in in_degree if in_degree[key] == 0])
    linearized_order = []

    while queue:
        current_key = queue.popleft()
        linearized_order.append(current_key)

        for dependent_key in graph.get(current_key, []):
            in_degree[dependent_key] -= 1
            if in_degree[dependent_key] == 0:
                queue.append(dependent_key)

    # Check for cycles (if not all keys are in the linearized order)
    if any(v != 0 for v in in_degree.values()):
        logger.error(graph)
        logger.error(in_degree)
        raise ValueError("Internal error: acyclic graph still has cycles")

    return linearized_order[::-1]


def linearize_dependencies(
    graph: dict[tuple[str, str], list[tuple[str, str]]]
) -> list[tuple[tuple[str, str], bool]]:
    """
    Linearize dependencies with automatic cycle breaking.

    When cycles are detected, they are broken by creating "shell" deployments.
    Cycle-breaking nodes appear twice in the output: first as a shell (True),
    then as a full deployment (False) at their natural topological position.

    Args:
        graph: Dependency graph where keys are nodes and values are lists of dependencies

    Returns:
        List of (node, is_shell) tuples in deployment order.
        - is_shell=True: Deploy as shell with stripped content
        - is_shell=False: Deploy with full content

    Example:
        For cycle A → B → C → A:
        Returns [(A, True), (A, False), (B, False), (C, False)]
        Deployment: shell_A, full_A, B, C
    """
    # Step 1: Detect all strongly connected components (cycles)
    sccs = tarjan_scc(graph)

    # Step 2: Identify cycle-breaking nodes and map nodes to their SCCs
    cycle_breakers = set()
    node_to_scc = {}

    for scc in sccs:
        if len(scc) > 1:  # This SCC is a cycle
            # First node in the SCC becomes the cycle breaker
            cycle_breakers.add(scc[0])
            logger.info(f"Detected cycle with {len(scc)} nodes. Breaking at node: {scc[0]}")
        # Map all nodes to their SCC
        for node in scc:
            node_to_scc[node] = scc

    # Also check for self-loops (node depending on itself)
    for node, deps in graph.items():
        if node in deps:
            cycle_breakers.add(node)
            logger.info(f"Detected self-loop at node: {node}")

    # Step 3: Break cycles by removing edges from cycle breakers to nodes in same SCC
    acyclic_graph = {}
    for node, deps in graph.items():
        if node in cycle_breakers:
            # Remove dependencies that point to nodes in the same SCC
            if node in node_to_scc:
                scc = node_to_scc[node]
                filtered_deps = [d for d in deps if d not in scc]
            else:
                # Self-loop case: just remove self-reference
                filtered_deps = [d for d in deps if d != node]
            acyclic_graph[node] = filtered_deps
            logger.debug(f"Breaking cycle: {node} originally depended on {len(deps)} nodes, now {len(filtered_deps)}")
        else:
            acyclic_graph[node] = deps

    # Step 4: Perform topological sort on the acyclic graph
    topo_order = kahns_topological_sort(acyclic_graph)

    # Step 5: Build output with shell markers
    result = []

    # First pass: add shells for cycle breakers, full versions for others
    for node in topo_order:
        if node in cycle_breakers:
            # Add only shell version for now
            result.append((node, True))
        else:
            # Non-cycle-breakers get deployed normally
            result.append((node, False))

    # Second pass: add full versions of cycle breakers at the end
    # This ensures all original dependencies are met before deploying the full version
    for node in topo_order:
        if node in cycle_breakers:
            result.append((node, False))

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
