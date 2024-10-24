"""
pytest -v tests/test_splitting.py
"""
import logging
import pytest
from wayfarer import splitter, functions, loader, routing
from tests.helper import simple_features


@pytest.mark.parametrize("use_reverse_lookup", [(True), (False)])
def test_split_network_edge(use_reverse_lookup):

    feats = simple_features()
    net = loader.load_network_from_geometries(
        feats, use_reverse_lookup=use_reverse_lookup
    )

    assert len(net.nodes()) == 4
    assert len(net.edges()) == 3

    # split the second edge
    edge_id_to_split = 2
    measure = 50
    splitter.split_network_edge(net, edge_id_to_split, [measure])

    split_node_id = splitter.create_split_key(edge_id_to_split, measure)
    assert split_node_id in net.nodes(), "The split node has been added to the network"

    # after the split operation there should be one extra edge
    # and one extra node
    assert len(net.nodes()) == 5
    assert len(net.edges()) == 4

    # the split edges no longer have the EdgeId as a key
    split_edges = functions.get_edge_by_attribute(net, "EDGE_ID", edge_id_to_split)
    split_edges = list(split_edges)
    assert len(split_edges) == 2

    # if use_reverse_lookup: print(net.graph["keys"].keys())

    split_edge_id = splitter.create_split_key(edge_id_to_split, measure)

    split_edge = functions.get_edge_by_key(net, split_edge_id, with_data=True)
    assert split_edge.attributes["LEN_"] == 50
    assert split_edge.attributes["OFFSET"] == 0

    split_edge_id = splitter.create_split_key(edge_id_to_split, 100)
    split_edge = functions.get_edge_by_key(net, split_edge_id, with_data=True)
    assert split_edge.attributes["LEN_"] == 50
    assert split_edge.attributes["OFFSET"] == 50


@pytest.mark.parametrize("use_reverse_lookup", [(True), (False)])
def test_multiple_split_network_edge(use_reverse_lookup):

    feats = simple_features()
    net = loader.load_network_from_geometries(
        feats, use_reverse_lookup=use_reverse_lookup
    )

    # split the second edge multiple times
    edge_id_to_split = 2
    splitter.split_network_edge(net, edge_id_to_split, [20, 40, 60])

    if use_reverse_lookup:
        print(net.graph["keys"].keys())

    # after the split operation there should be one extra edge
    # and one extra node
    assert len(net.nodes()) == 7
    assert len(net.edges()) == 6


@pytest.mark.parametrize("use_reverse_lookup", [(True), (False)])
def test_double_split_network_edge(use_reverse_lookup):
    feats = simple_features()
    net = loader.load_network_from_geometries(
        feats, use_reverse_lookup=use_reverse_lookup
    )

    # split the second edge multiple times
    edge_id_to_split = 2
    splitter.split_network_edge(net, edge_id_to_split, [20, 40, 60])

    split_edge_id = splitter.create_split_key(edge_id_to_split, 40)

    if use_reverse_lookup:
        print(net.graph["keys"].keys())

    splitter.split_network_edge(net, split_edge_id, [10])

    if use_reverse_lookup:
        print(net.graph["keys"].keys())

    assert len(net.nodes()) == 8
    assert len(net.edges()) == 7


@pytest.mark.parametrize("use_reverse_lookup", [(True), (False)])
def test_split_invalid_measure(use_reverse_lookup):

    feats = simple_features()
    net = loader.load_network_from_geometries(
        feats, use_reverse_lookup=use_reverse_lookup
    )
    error = False

    try:
        # 150 is greater than edge length
        splitter.split_network_edge(net, 2, [150])
    except ValueError:
        error = True

    assert error


@pytest.mark.parametrize("use_reverse_lookup", [(True), (False)])
def test_split_invalid_measure2(use_reverse_lookup):

    feats = simple_features()
    net = loader.load_network_from_geometries(
        feats, use_reverse_lookup=use_reverse_lookup
    )
    error = False

    try:
        # 100 is equal to edge length
        splitter.split_network_edge(net, 2, [100])
    except ValueError:
        error = True

    assert error


@pytest.mark.parametrize("use_reverse_lookup", [(True), (False)])
def test_split_with_points(use_reverse_lookup):

    feats = simple_features()
    net = loader.load_network_from_geometries(
        feats, use_reverse_lookup=use_reverse_lookup
    )

    recs = [
        {"EDGE_ID": 1, "POINT_ID": "A", "MEASURE": 50, "LEN_": 12},
        {"EDGE_ID": 2, "POINT_ID": "B", "MEASURE": 20, "LEN_": 14},
        {"EDGE_ID": 2, "POINT_ID": "C", "MEASURE": 40, "LEN_": 16},
    ]

    splitter.split_with_points(net, recs)

    # run a test solve to the newly added point
    point_id = "B"
    edges = routing.solve_shortest_path(net, (0, 0), point_id, with_direction_flag=True)
    # print(edges)
    assert len(edges) == 4

    # run a solve from start to finish across the original (now split) edges
    edges = routing.solve_shortest_path(net, (0, 0), (300, 0), with_direction_flag=True)
    # print(edges)
    assert len(edges) == 6


def test_doctest():
    import doctest

    print(doctest.testmod(splitter))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # test_multiple_split_network_edge(True)
    # test_split_invalid_measure(True)
    # test_split_invalid_measure2(True)
    # test_multiple_split_network_edge(True)
    # test_multiple_split_network_edge(True)
    # test_double_split_network_edge(True)
    # test_split_with_points(True)
    test_split_network_edge(True)
    print("Done!")
