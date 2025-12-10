import pytest
from mdxcanvas.deploy.algorithms import linearize_dependencies
from mdxcanvas.resources import CanvasResource


def test_no_cycles():
    """Test linearization with no cycles"""
    graph = {
        ('assignment', 'A'): [('page', 'B')],
        ('page', 'B'): [('page', 'C')],
        ('page', 'C'): []
    }
    resources = {
        ('assignment', 'A'): CanvasResource(type='assignment', id='A', data={'name': 'A'}),
        ('page', 'B'): CanvasResource(type='page', id='B', data={'title': 'B'}),
        ('page', 'C'): CanvasResource(type='page', id='C', data={'title': 'C'})
    }

    order, shell_candidates = linearize_dependencies(graph, resources)

    assert shell_candidates is None or len(shell_candidates) == 0
    assert ('page', 'C') in order
    assert order.index(('page', 'C')) < order.index(('page', 'B'))
    assert order.index(('page', 'B')) < order.index(('assignment', 'A'))


def test_simple_cycle():
    """Test detection of simple A -> B -> A cycle"""
    graph = {
        ('assignment', 'A'): [('page', 'B')],
        ('page', 'B'): [('assignment', 'A')]
    }
    resources = {
        ('assignment', 'A'): CanvasResource(type='assignment', id='A', data={'name': 'A'}),
        ('page', 'B'): CanvasResource(type='page', id='B', data={'title': 'B'})
    }

    order, shell_candidates = linearize_dependencies(graph, resources)

    assert shell_candidates is not None
    assert len(shell_candidates) >= 1

    shell_keys = [key for key, _ in shell_candidates]
    # Should select page over assignment (priority)
    assert ('page', 'B') in shell_keys


def test_three_node_cycle():
    """Test A -> B -> C -> A cycle"""
    graph = {
        ('assignment', 'A'): [('page', 'B')],
        ('page', 'B'): [('quiz', 'C')],
        ('quiz', 'C'): [('assignment', 'A')]
    }
    resources = {
        ('assignment', 'A'): CanvasResource(type='assignment', id='A', data={'name': 'A'}),
        ('page', 'B'): CanvasResource(type='page', id='B', data={'title': 'B'}),
        ('quiz', 'C'): CanvasResource(type='quiz', id='C', data={'title': 'C'})
    }

    order, shell_candidates = linearize_dependencies(graph, resources)

    assert shell_candidates is not None
    assert len(shell_candidates) >= 1

    shell_keys = [key for key, _ in shell_candidates]
    # Should select page (highest priority)
    assert ('page', 'B') in shell_keys


def test_self_cycle():
    """Test A -> A self-reference"""
    graph = {
        ('page', 'A'): [('page', 'A')]
    }
    resources = {
        ('page', 'A'): CanvasResource(type='page', id='A', data={'title': 'A'})
    }

    order, shell_candidates = linearize_dependencies(graph, resources)

    assert shell_candidates is not None
    shell_keys = [key for key, _ in shell_candidates]
    assert ('page', 'A') in shell_keys


def test_multiple_separate_cycles():
    """Test two independent cycles: A<->B and C<->D"""
    graph = {
        ('page', 'A'): [('page', 'B')],
        ('page', 'B'): [('page', 'A')],
        ('assignment', 'C'): [('assignment', 'D')],
        ('assignment', 'D'): [('assignment', 'C')]
    }
    resources = {
        ('page', 'A'): CanvasResource(type='page', id='A', data={'title': 'A'}),
        ('page', 'B'): CanvasResource(type='page', id='B', data={'title': 'B'}),
        ('assignment', 'C'): CanvasResource(type='assignment', id='C', data={'name': 'C'}),
        ('assignment', 'D'): CanvasResource(type='assignment', id='D', data={'name': 'D'})
    }

    order, shell_candidates = linearize_dependencies(graph, resources)

    assert shell_candidates is not None
    # Should detect 2 cycles, select 2 shells (one per cycle)
    assert len(shell_candidates) == 2


def test_backward_compatibility_without_resources():
    """Test that function works without resources parameter (backward compat)"""
    graph = {
        ('assignment', 'A'): [('page', 'B')],
        ('page', 'B'): []
    }

    order, shell_candidates = linearize_dependencies(graph, None)

    # Should still linearize, but no cycle detection
    assert shell_candidates is None
    assert len(order) == 2


def test_cycle_priority_selection():
    """Test that pages are selected over assignments and quizzes"""
    graph = {
        ('assignment', 'A'): [('page', 'P'), ('quiz', 'Q')],
        ('page', 'P'): [('quiz', 'Q')],
        ('quiz', 'Q'): [('assignment', 'A')]
    }
    resources = {
        ('assignment', 'A'): CanvasResource(type='assignment', id='A', data={'name': 'A'}),
        ('page', 'P'): CanvasResource(type='page', id='P', data={'title': 'P'}),
        ('quiz', 'Q'): CanvasResource(type='quiz', id='Q', data={'title': 'Q'})
    }

    order, shell_candidates = linearize_dependencies(graph, resources)

    assert shell_candidates is not None
    shell_keys = [key for key, _ in shell_candidates]

    # Page should be selected (highest priority)
    assert ('page', 'P') in shell_keys
    # Only one shell needed for the cycle
    assert len(shell_candidates) == 1
