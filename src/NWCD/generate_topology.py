"""Utilities for generating network topology graphs."""

from __future__ import annotations

from typing import Iterable, List, Mapping, Sequence

from graphviz import Digraph


def build_graph(
    paths: Iterable[Sequence[str]], nodes: Mapping[str, Mapping[str, str]]
) -> Digraph:
    """Build a Graphviz digraph representing the topology.

    Parameters
    ----------
    paths:
        各経路を示すノードIDのリスト。
    nodes:
        ノードIDをキーとし、``hostname`` と ``vendor`` を含む辞書。

    Returns
    -------
    graphviz.Digraph
        生成されたグラフ。
    """
    graph = Digraph(format="svg")
    # Flutter 側のタップ処理のためノード形状は楕円とする
    graph.attr("node", shape="ellipse")

    added: set[str] = set()

    for path in paths:
        for idx, node_id in enumerate(path):
            info = nodes.get(node_id, {})
            if node_id not in added:
                hostname = info.get("hostname", "")
                vendor = info.get("vendor", "")
                label_parts: List[str] = [p for p in (hostname, vendor) if p]
                label = "\n".join(label_parts) if label_parts else node_id
                graph.node(node_id, label=label)
                added.add(node_id)
            if idx > 0:
                parent = path[idx - 1]
                graph.edge(parent, node_id)
    return graph
