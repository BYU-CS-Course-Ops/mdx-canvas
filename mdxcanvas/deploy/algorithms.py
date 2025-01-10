from collections import deque

from ..our_logging import get_logger

logger = get_logger()


def linearize_dependencies(graph: dict[tuple[str, str], list[tuple[str, str]]]) -> list[tuple[str, str]]:
    # Original code courtesy of GPT-4o
    # Some modifications required

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
        logger.error(graph)
        logger.error(in_degree)
        raise ValueError("Dependency graph has at least one cycle")

    return linearized_order[::-1]


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
