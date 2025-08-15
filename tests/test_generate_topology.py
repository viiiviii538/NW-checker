from src.NWCD.generate_topology import build_graph


def test_build_graph_hierarchy():
    paths = [
        ["1", "2", "3"],
        ["1", "2", "4"],
        ["1", "5"],
    ]
    nodes = {
        "1": {"hostname": "root", "vendor": "Cisco"},
        "2": {"hostname": "sw1", "vendor": "Juniper"},
        "3": {"hostname": "hostA", "vendor": "Dell"},
        "4": {"hostname": "hostB", "vendor": "HP"},
        "5": {"hostname": "sw2", "vendor": "Cisco"},
    }

    graph = build_graph(paths, nodes)
    src = graph.source

    assert 'node [shape=ellipse]' in src
    assert '1 -> 2' in src
    assert '2 -> 3' in src
    assert '2 -> 4' in src
    assert '1 -> 5' in src

    assert '1 [label="root\nCisco"]' in src
    assert '3 [label="hostA\nDell"]' in src
