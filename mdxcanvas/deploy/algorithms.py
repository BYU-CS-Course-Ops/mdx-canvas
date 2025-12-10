from collections import deque
from typing import TYPE_CHECKING

from ..our_logging import get_logger

if TYPE_CHECKING:
    from ..resources import CanvasResource

logger = get_logger()


def _detect_cycles_dfs(
    graph: dict[tuple[str, str], list[tuple[str, str]]],
) -> set[tuple[str, str]]:
    """
    Use DFS with three-color marking to detect cycles.
    Returns set of all resource keys involved in any cycle.

    WHITE (0) = unvisited
    GRAY (1) = visiting (currently in DFS path/recursion stack)
    BLACK (2) = visited (completely processed)

    If we encounter a GRAY node, we've found a cycle.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    colors = {node: WHITE for node in graph}
    cycle_nodes = set()

    def dfs(node: tuple[str, str], path: list[tuple[str, str]]):
        colors[node] = GRAY
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in graph:
                # Missing dependency, skip
                continue

            if colors[neighbor] == GRAY:
                # Found cycle! Add all nodes from neighbor to end of path
                cycle_start_idx = path.index(neighbor)
                for cycle_node in path[cycle_start_idx:]:
                    cycle_nodes.add(cycle_node)
            elif colors[neighbor] == WHITE:
                dfs(neighbor, path)

        path.pop()
        colors[node] = BLACK

    for node in graph:
        if colors[node] == WHITE:
            dfs(node, [])

    return cycle_nodes


def _find_strongly_connected_components(
    cycle_nodes: set[tuple[str, str]],
    graph: dict[tuple[str, str], list[tuple[str, str]]]
) -> list[set[tuple[str, str]]]:
    """
    Find strongly connected components among cycle nodes.
    Each SCC represents a separate cycle.
    """
    if not cycle_nodes:
        return []

    # Build subgraph with only cycle nodes
    subgraph = {node: [n for n in graph.get(node, []) if n in cycle_nodes]
                for node in cycle_nodes}

    # Simple DFS-based SCC detection
    visited = set()
    sccs = []

    def dfs_collect(node: tuple[str, str], component: set[tuple[str, str]]):
        if node in visited:
            return
        visited.add(node)
        component.add(node)

        # Forward edges
        for neighbor in subgraph.get(node, []):
            if neighbor not in visited:
                dfs_collect(neighbor, component)

        # Backward edges (to detect cycles properly)
        for potential_parent in subgraph:
            if node in subgraph.get(potential_parent, []) and potential_parent not in visited:
                dfs_collect(potential_parent, component)

    for node in cycle_nodes:
        if node not in visited:
            component = set()
            dfs_collect(node, component)
            if len(component) > 0:
                sccs.append(component)

    return sccs


def _select_shell_candidates(
    cycle_nodes: set[tuple[str, str]],
    graph: dict[tuple[str, str], list[tuple[str, str]]],
) -> list[tuple[str, str]]:
    """
    For each cycle, select ONE node to become a shell.

    Priority: page > assignment > quiz (easiest to hardest to create shells for)
    Within same type, sort by ID alphabetically for determinism.

    Returns list of selected shell candidates (one per cycle).
    """
    TYPE_PRIORITY = {
        'page': 1,
        'assignment': 2,
        'quiz': 3,
    }

    # Find strongly connected components (separate cycles)
    sccs = _find_strongly_connected_components(cycle_nodes, graph)

    shell_candidates = []
    for scc in sccs:
        if len(scc) == 0:
            continue

        # Sort by priority, then by type name, then by ID
        sorted_nodes = sorted(
            scc,
            key=lambda n: (TYPE_PRIORITY.get(n[0], 999), n[0], n[1])
        )
        shell_candidates.append(sorted_nodes[0])

    return shell_candidates


def linearize_dependencies(
    graph: dict[tuple[str, str], list[tuple[str, str]]],
    resources: dict[tuple[str, str], 'CanvasResource'] | None = None
) -> tuple[list[tuple[str, str]], list[tuple[tuple[str, str], 'CanvasResource']] | None]:
    # Original code courtesy of GPT-4o
    # Modified to detect and handle cycles

    in_degree = {}

    # Build the graph and compute in-degrees of nodes
    missing_deps = []
    for key, deps in graph.items():
        if key not in in_degree:
            in_degree[key] = 0
        for dep in deps:
            if dep not in in_degree:
                in_degree[dep] = 0
            if dep not in graph:
                missing_deps.append(dep)
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
        logger.info("Dependency graph has at least one cycle - attempting resolution")

        if resources is None:
            # Cannot resolve cycles without resource objects
            logger.error(graph)
            logger.error(in_degree)
            logger.warning("Cycles detected but resources not provided - cannot auto-resolve")
            return linearized_order[::-1], None

        # Detect cycles using DFS
        cycle_nodes = _detect_cycles_dfs(graph)
        logger.info(f"Detected {len(cycle_nodes)} nodes involved in cycles: {cycle_nodes}")

        # Select shell candidates (one per cycle)
        shell_keys = _select_shell_candidates(cycle_nodes, graph)
        logger.info(f"Selected {len(shell_keys)} shell candidates: {shell_keys}")

        # Build result with shell candidates and their resources
        shell_candidates = [(key, resources[key]) for key in shell_keys if key in resources]

        # Add non-shell cycle participants to the linearized order
        # These weren't added by Kahn's algorithm because they're in cycles
        for cycle_node in cycle_nodes:
            if cycle_node not in shell_keys and cycle_node not in linearized_order:
                linearized_order.append(cycle_node)
                logger.debug(f"Added non-shell cycle participant to order: {cycle_node}")

        # Remove shell candidates from linearized order (they deploy in Phase 1)
        linearized_order_filtered = [key for key in linearized_order if key not in shell_keys]

        return linearized_order_filtered[::-1], shell_candidates

    return linearized_order[::-1], None


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
