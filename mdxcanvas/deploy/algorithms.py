from collections import deque

from ..our_logging import get_logger
from ..resources import CanvasResource

logger = get_logger()


def linearize_dependencies(
    graph: dict[tuple[str, str], list[tuple[str, str]]],
    resources: dict[tuple[str, str], CanvasResource]
) -> list[tuple[tuple[str, str], CanvasResource]]:
    """
    Performs DFS-based topological sort with cycle detection via back edges.

    Args:
        graph: Dependency graph where each key maps to a list of dependencies
        resources: Dictionary mapping resource keys to CanvasResource objects

    Returns:
        List of (resource_key, CanvasResource) tuples in dependency order.
        When back edges (cycles) are detected, placeholder resources are created
        with the same type/id but data=None.
    """
    # DFS node states
    WHITE = 0  # Unvisited
    GRAY = 1   # Currently being processed (in DFS stack)
    BLACK = 2  # Completely processed

    color = {}
    result = []
    back_edges = set()

    def dfs(node):
        """DFS traversal with back edge detection."""
        if node in color:
            if color[node] == GRAY:
                # Back edge detected - node is currently in DFS stack (ancestor)
                return
            elif color[node] == BLACK:
                # Already completely processed
                return

        # Mark as being processed
        color[node] = GRAY

        # Visit all dependencies
        for dep in graph.get(node, []):
            if dep not in color:
                # Unvisited dependency - recurse
                dfs(dep)
            elif color[dep] == GRAY:
                # Back edge detected: dep is an ancestor in the DFS tree
                back_edges.add((node, dep))
                logger.warning(f"Back edge (cycle) detected: {node} -> {dep}")

        # Mark as completely processed
        color[node] = BLACK
        result.append(node)

    # Start DFS from all nodes in the graph
    for node in graph:
        if node not in color:
            dfs(node)

    # Build result with CanvasResource objects
    result_with_resources = []

    for key in result:
        if key in resources:
            result_with_resources.append((key, resources[key]))
        else:
            # Create placeholder resource if not found
            rtype, rid = key
            placeholder = CanvasResource(type=rtype, id=rid, data=None)
            result_with_resources.append((key, placeholder))

    # Log summary of back edges
    if back_edges:
        logger.info(f"Detected {len(back_edges)} back edge(s) forming cycle(s): {back_edges}")

    return result_with_resources


if __name__ == '__main__':
    # Test 1: Simple dependency graph without cycles
    print("Test 1: Simple dependency graph (no cycles)")
    dependency_dict = {
        ('page', 'A'): [('page', 'B')],
        ('page', 'B'): [('page', 'C'), ('page', 'D')],
        ('page', 'C'): [],
        ('page', 'D'): [('page', 'C')]
    }

    resources = {
        ('page', 'A'): CanvasResource(type='page', id='A', data={'body': 'Page A'}),
        ('page', 'B'): CanvasResource(type='page', id='B', data={'body': 'Page B'}),
        ('page', 'C'): CanvasResource(type='page', id='C', data={'body': 'Page C'}),
        ('page', 'D'): CanvasResource(type='page', id='D', data={'body': 'Page D'}),
    }

    # Expect: C, D, B, A (dependencies processed first)
    order = linearize_dependencies(dependency_dict, resources)
    print("Order:", [(key, res['id']) for key, res in order])
    print()

    # Test 2: Dependency graph with a cycle (back edge)
    print("Test 2: Dependency graph with cycle (back edge)")
    cyclic_dependency_dict = {
        ('page', 'X'): [('page', 'Y')],
        ('page', 'Y'): [('page', 'Z')],
        ('page', 'Z'): [('page', 'X')]  # Creates a cycle: X -> Y -> Z -> X
    }

    cyclic_resources = {
        ('page', 'X'): CanvasResource(type='page', id='X', data={'body': 'Page X'}),
        ('page', 'Y'): CanvasResource(type='page', id='Y', data={'body': 'Page Y'}),
        ('page', 'Z'): CanvasResource(type='page', id='Z', data={'body': 'Page Z'}),
    }

    order_cyclic = linearize_dependencies(cyclic_dependency_dict, cyclic_resources)
    print("Order:", [(key, res['id']) for key, res in order_cyclic])
    print("(Back edges should be logged as warnings above)")
    print()

    # Test 3: Realistic example with pages, assignments, and quizzes with cycles
    print("Test 3: Realistic cyclical references (pages, assignments, quizzes)")

    # Create resources with cyclical references using the @@type||id||field@@ format
    realistic_resources = {
        # Pages with cyclical references
        ('page', 'intro'): CanvasResource(
            type='page',
            id='intro',
            data={
                'title': 'Introduction to Course',
                'body': 'Welcome! For advanced topics, see @@page||advanced||url@@. Complete @@assignment||hw1||url@@ to get started.'
            }
        ),
        ('page', 'advanced'): CanvasResource(
            type='page',
            id='advanced',
            data={
                'title': 'Advanced Topics',
                'body': 'Before reading this, review @@page||intro||url@@. Then take @@quiz||final||url@@.'
            }
        ),
        ('page', 'study-guide'): CanvasResource(
            type='page',
            id='study-guide',
            data={
                'title': 'Study Guide',
                'body': 'Practice with @@quiz||practice||url@@ and review @@page||intro||url@@.'
            }
        ),

        # Assignments with cyclical references
        ('assignment', 'hw1'): CanvasResource(
            type='assignment',
            id='hw1',
            data={
                'name': 'Homework 1',
                'description': 'Complete this before @@assignment||hw2||url@@. See @@page||intro||url@@ for help.',
                'points_possible': 100
            }
        ),
        ('assignment', 'hw2'): CanvasResource(
            type='assignment',
            id='hw2',
            data={
                'name': 'Homework 2',
                'description': 'Review your work from @@assignment||hw1||url@@. Study @@page||advanced||url@@ first.',
                'points_possible': 100
            }
        ),

        # Quizzes with cyclical references
        ('quiz', 'practice'): CanvasResource(
            type='quiz',
            id='practice',
            data={
                'title': 'Practice Quiz',
                'description': 'Before taking @@quiz||final||url@@, review @@page||study-guide||url@@.',
                'quiz_type': 'practice_quiz'
            }
        ),
        ('quiz', 'final'): CanvasResource(
            type='quiz',
            id='final',
            data={
                'title': 'Final Quiz',
                'description': 'Complete @@quiz||practice||url@@ first. Review @@assignment||hw2||url@@.',
                'quiz_type': 'assignment'
            }
        ),
    }

    # Build dependency graph by parsing the embedded references
    import re
    realistic_deps = {}
    for key, resource in realistic_resources.items():
        realistic_deps[key] = []
        if resource.get('data'):
            # Convert resource data to text to search for references
            text = str(resource['data'])
            # Find all @@type||id||field@@ references
            for match in re.finditer(r'@@([^|]+)\|\|([^|]+)\|\|([^@]+)@@', text):
                dep_type = match.group(1)
                dep_id = match.group(2)
                realistic_deps[key].append((dep_type, dep_id))

    print("Dependency graph:")
    for key, deps in realistic_deps.items():
        if deps:
            print(f"  {key} -> {deps}")
    print()

    order_realistic = linearize_dependencies(realistic_deps, realistic_resources)
    print("Linearized order:")
    for i, (key, res) in enumerate(order_realistic, 1):
        resource_type, resource_id = key
        title = res.get('data', {}).get('title') or res.get('data', {}).get('name') or resource_id
        print(f"  {i}. [{resource_type}] {title} ({resource_id})")
    print()
    print("(Check warnings above for detected back edges)")
