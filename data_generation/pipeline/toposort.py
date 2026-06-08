from collections import defaultdict, deque
from typing import DefaultDict


def topo_sort(deps: dict[str, list[str]]) -> list[str]:
    graph = defaultdict(list)
    indegree: DefaultDict[str, int] = defaultdict(int)

    # build graph
    for node, parents in deps.items():
        indegree[node] = indegree.get(node, 0)
        for p in parents:
            graph[p].append(node)
            indegree[node] += 1

    # queue roots
    q = deque([n for n in indegree if indegree[n] == 0])

    order = []

    while q:
        n = q.popleft()
        order.append(n)

        for nei in graph[n]:
            indegree[nei] -= 1
            if indegree[nei] == 0:
                q.append(nei)

    if len(order) != len(deps):
        missing = set(deps) - set(order)
        raise ValueError(f"Circular or missing deps: {missing}")

    return order
