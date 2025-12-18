"""Graph algorithms for dependency analysis.

Provides cycle detection using depth-first search for validating
message/term reference graphs in FTL resources.

Python 3.13+.
"""

from collections.abc import Mapping


def detect_cycles(dependencies: Mapping[str, set[str]]) -> list[list[str]]:
    """Detect all cycles in a dependency graph using DFS.

    Implements Tarjan-style cycle detection with explicit stack tracking.
    Returns all unique cycles found in the graph.

    Args:
        dependencies: Mapping from node ID to set of referenced node IDs.
                     Example: {"a": {"b", "c"}, "b": {"c"}, "c": {"a"}}

    Returns:
        List of cycles, where each cycle is a list of node IDs forming
        the cycle path. Empty list if no cycles detected.

    Example:
        >>> deps = {"a": {"b"}, "b": {"c"}, "c": {"a"}}
        >>> cycles = detect_cycles(deps)
        >>> len(cycles)
        1
        >>> "a" in cycles[0] and "b" in cycles[0] and "c" in cycles[0]
        True

    Complexity:
        Time: O(V + E) where V = nodes, E = edges
        Space: O(V) for visited/recursion tracking
    """
    visited: set[str] = set()
    cycles: list[list[str]] = []
    seen_cycle_keys: set[str] = set()

    def _dfs(
        node: str,
        rec_stack: set[str],
        path: list[str],
    ) -> None:
        """DFS traversal with cycle detection."""
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in dependencies.get(node, set()):
            if neighbor not in visited:
                _dfs(neighbor, rec_stack, path)
            elif neighbor in rec_stack:
                # Found cycle - extract cycle path
                cycle_start = path.index(neighbor)
                cycle = [*path[cycle_start:], neighbor]

                # Deduplicate cycles using canonical form (sorted key)
                cycle_key = " -> ".join(sorted(set(cycle)))
                if cycle_key not in seen_cycle_keys:
                    seen_cycle_keys.add(cycle_key)
                    cycles.append(cycle)

        path.pop()
        rec_stack.remove(node)

    # Run DFS from each unvisited node
    for node in dependencies:
        if node not in visited:
            _dfs(node, set(), [])

    return cycles


def build_dependency_graph(
    entries: Mapping[str, tuple[set[str], set[str]]],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Build separate message and term dependency graphs.

    Args:
        entries: Mapping from entry ID to (message_refs, term_refs) tuple.
                 Message IDs are plain strings, term IDs should NOT include
                 the "-" prefix.

    Returns:
        Tuple of (message_deps, term_deps) where each is a mapping from
        entry ID to set of referenced entry IDs.

    Example:
        >>> entries = {
        ...     "welcome": ({"greeting"}, {"brand"}),
        ...     "greeting": (set(), set()),
        ... }
        >>> msg_deps, term_deps = build_dependency_graph(entries)
        >>> msg_deps["welcome"]
        {'greeting'}
    """
    message_deps: dict[str, set[str]] = {}
    term_deps: dict[str, set[str]] = {}

    for entry_id, (msg_refs, trm_refs) in entries.items():
        # Messages reference other messages
        message_deps[entry_id] = msg_refs.copy()
        # Terms reference other terms (term-to-term deps only)
        term_deps[entry_id] = trm_refs.copy()

    return message_deps, term_deps
