from collections import defaultdict, deque


def linearize_dependencies(dependency_dict):
    # Original code courtesy of GPT-4o

    # Parse the dependency dictionary to build the graph
    graph = defaultdict(list)
    in_degree = {key: 0 for key in dependency_dict}

    # Build the graph and compute in-degrees of nodes
    for key, value in dependency_dict.items():
        for k in dependency_dict:
            if k in value:
                graph[k].append(key)
                in_degree[key] += 1

    # Perform topological sort (Kahn's algorithm)
    queue = deque([key for key in in_degree if in_degree[key] == 0])
    linearized_order = []

    while queue:
        current_key = queue.popleft()
        linearized_order.append(current_key)

        for dependent_key in graph[current_key]:
            in_degree[dependent_key] -= 1
            if in_degree[dependent_key] == 0:
                queue.append(dependent_key)

    # Check for cycles (if not all keys are in the linearized order)
    if len(linearized_order) != len(dependency_dict):
        raise ValueError("Dependency graph has at least one cycle")

    return linearized_order


if __name__ == '__main__':
    dependency_dict = {
        '@@A@@': 'This value depends on @@B@@',
        '@@B@@': 'This value depends on @@C@@ and @@D@@',
        '@@C@@': 'This value does not depend on other keys',
        '@@D@@': 'This value depends on @@C@@'
    }

    order = linearize_dependencies(dependency_dict)
    print(order)
