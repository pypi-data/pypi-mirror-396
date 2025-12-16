import math
import pytest
import numpy as np
import networkx as nx
from shapely.geometry import Point, LineString

# If you keep these imports at top-level, tests will fail loudly when libs are missing,
# which is what we want for a project that depends on them.
import geopandas as gpd
import osmnx as ox

# ---- Helpers ----------------------------------------------------------------

def make_grid_graph(n=3, m=3, weight_name="length"):
    """
    Build a small n x m rectilinear MultiDiGraph with unit weights, both directions,
    and OSMnx-friendly attributes (x, y on nodes; geometry and weight on edges).
    """
    G = nx.MultiDiGraph()
    # nodes: id -> (x, y)
    node_id = lambda r, c: r * m + c
    for r in range(n):
        for c in range(m):
            nid = node_id(r, c)
            G.add_node(nid, x=float(c), y=float(r))
    # edges (4-neighborhood)
    for r in range(n):
        for c in range(m):
            u = node_id(r, c)
            if c + 1 < m:
                v = node_id(r, c + 1)
                # add both directions with geometry + weight
                G.add_edge(u, v, geometry=LineString([(c, r), (c + 1, r)]), **{weight_name: 1.0})
                G.add_edge(v, u, geometry=LineString([(c + 1, r), (c, r)]), **{weight_name: 1.0})
            if r + 1 < n:
                v = node_id(r + 1, c)
                G.add_edge(u, v, geometry=LineString([(c, r), (c, r + 1)]), **{weight_name: 1.0})
                G.add_edge(v, u, geometry=LineString([(c, r + 1), (c, r)]), **{weight_name: 1.0})
    G.graph["crs"] = "EPSG:4326"
    return G

def manhattan_distance(G, o, d, weight="length"):
    # ground truth via networkx dijkstra
    dist = nx.shortest_path_length(G, source=o, target=d, weight=weight)
    path = nx.shortest_path(G, source=o, target=d, weight=weight)
    return float(dist), path

# ---- Import the function under test -----------------------------------------
# Adjust import as needed for your package layout, e.g.:
# from network_functions.functions import path_dijkstra
from network_functions.functions import path_dijkstra  # assumes you're running tests from repo root

# ---- Fixtures ----------------------------------------------------------------

@pytest.fixture
def grid3():
    G = make_grid_graph(3, 3, weight_name="length")
    return G

@pytest.fixture
def grid3_gdfs(grid3):
    # Use OSMnx to produce nodes/edges GeoDataFrames for the G=None branch
    nodes_gdf, edges_gdf = ox.graph_to_gdfs(grid3, nodes=True, edges=True)
    # Ensure expected indexing for graph_from_gdfs
    nodes_gdf = nodes_gdf.set_geometry("geometry")
    edges_gdf = edges_gdf.set_geometry("geometry")
    # CRS isn't used by nearest_nodes for synthetic coords, but set WGS84 to be safe
    nodes_gdf.set_crs(epsg=4326, inplace=True, allow_override=True)
    edges_gdf.set_crs(epsg=4326, inplace=True, allow_override=True)
    return nodes_gdf, edges_gdf

# ---- Tests: happy paths ------------------------------------------------------

def test_single_pair_nodes(grid3):
    o, d = 0, 8  # corner to corner in 3x3
    exp_dist, exp_path = manhattan_distance(grid3, o, d, "length")
    (distances, paths) = path_dijkstra(
        origins=o, destinations=d, G=grid3,
        origins_in_nodes=True, destinations_in_nodes=True,
        pairs=False, verbose=False
    )
    assert (o, d) in distances
    assert math.isclose(distances[(o, d)], exp_dist, rel_tol=1e-9)
    assert paths[(o, d)][0] == o
    assert paths[(o, d)][-1] == d

def test_one_to_many(grid3):
    o = 0
    dests = [2, 5, 8]
    (distances, paths) = path_dijkstra(
        origins=o, destinations=dests, G=grid3,
        origins_in_nodes=True, destinations_in_nodes=True,
        pairs=False, verbose=False
    )
    assert len(distances) == len(dests)
    for d in dests:
        exp_dist, exp_path = manhattan_distance(grid3, o, d, "length")
        assert math.isclose(distances[(o, d)], exp_dist, rel_tol=1e-9)
        assert paths[(o, d)][0] == o
        assert paths[(o, d)][-1] == d

def test_many_to_one(grid3):
    origins = [1, 2, 4]
    d = 8
    (distances, paths) = path_dijkstra(
        origins=origins, destinations=d, G=grid3,
        origins_in_nodes=True, destinations_in_nodes=True,
        pairs=False, verbose=False
    )
    assert len(distances) == len(origins)
    for o in origins:
        exp_dist, exp_path = manhattan_distance(grid3, o, d, "length")
        assert math.isclose(distances[(o, d)], exp_dist, rel_tol=1e-9)
        assert paths[(o, d)][0] == o
        assert paths[(o, d)][-1] == d

def test_many_to_many_cartesian(grid3):
    origins = [0, 1]
    dests = [7, 8]
    (distances, paths) = path_dijkstra(
        origins=origins, destinations=dests, G=grid3,
        origins_in_nodes=True, destinations_in_nodes=True,
        pairs=False, verbose=False
    )
    assert len(distances) == len(origins) * len(dests)
    for o in origins:
        for d in dests:
            exp_dist, exp_path = manhattan_distance(grid3, o, d, "length")
            assert math.isclose(distances[(o, d)], exp_dist, rel_tol=1e-9)
            assert paths[(o, d)][0] == o
            assert paths[(o, d)][-1] == d

def test_pairs_true_dedupes(grid3):
    # Include a duplicate pair to confirm set(zip(...)) behavior
    origins = [0, 0, 1]
    dests   = [8, 8, 7]
    (distances, paths) = path_dijkstra(
        origins=origins, destinations=dests, G=grid3,
        origins_in_nodes=True, destinations_in_nodes=True,
        pairs=True, verbose=False
    )
    # unique pairs are {(0,8), (1,7)}
    assert set(distances.keys()) == {(0, 8), (1, 7)}
    for (o, d), dist in distances.items():
        exp_dist, exp_path = manhattan_distance(grid3, o, d, "length")
        assert math.isclose(dist, exp_dist, rel_tol=1e-9)
        assert paths[(o, d)][0] == o
        assert paths[(o, d)][-1] == d

def test_snapping_with_points(grid3):
    # Use Points slightly offset from the node coords; nearest_nodes should snap correctly
    def node_point(nid, dx=0.02, dy=-0.015):
        x = grid3.nodes[nid]["x"] + dx
        y = grid3.nodes[nid]["y"] + dy
        return Point(x, y)

    o, d = 0, 8
    (distances, paths) = path_dijkstra(
        origins=node_point(o), destinations=node_point(d),
        G=grid3, origins_in_nodes=False, destinations_in_nodes=False,
        pairs=False, verbose=False
    )
    exp_dist, _ = manhattan_distance(grid3, o, d, "length")
    assert math.isclose(distances[(grid3.graph.get("last_origin", o), grid3.graph.get("last_dest", d))] if False else distances[(o, d)], exp_dist, rel_tol=1e-9)
    # Because the function returns keys as snapped node IDs (o,d), validate path endpoints directly:
    assert paths[(o, d)][0] == o
    assert paths[(o, d)][-1] == d

# ---- Tests: inputs & assertions ---------------------------------------------

def test_invalid_weight_asserts(grid3):
    with pytest.raises(AssertionError):
        path_dijkstra(
            origins=0, destinations=8, G=grid3,
            origins_in_nodes=True, destinations_in_nodes=True,
            dist_param="not_a_real_attr", verbose=False
        )

def test_missing_nodes_raise(grid3):
    with pytest.raises(KeyError):
        path_dijkstra(
            origins=[999], destinations=[8], G=grid3,
            origins_in_nodes=True, destinations_in_nodes=True,
            verbose=False
        )
    with pytest.raises(KeyError):
        path_dijkstra(
            origins=[0], destinations=[999], G=grid3,
            origins_in_nodes=True, destinations_in_nodes=True,
            verbose=False
        )

def test_empty_inputs_raise(grid3):
    with pytest.raises(ValueError):
        path_dijkstra(
            origins=[], destinations=[1], G=grid3,
            origins_in_nodes=True, destinations_in_nodes=True,
            verbose=False
        )
    with pytest.raises(ValueError):
        path_dijkstra(
            origins=[0], destinations=[], G=grid3,
            origins_in_nodes=True, destinations_in_nodes=True,
            verbose=False
        )

# ---- Test: G=None branch via nodes/edges gdfs --------------------------------

def test_nodes_edges_branch(grid3, grid3_gdfs):
    nodes_gdf, edges_gdf = grid3_gdfs
    o, d = 0, 8
    (distances, paths) = path_dijkstra(
        origins=o, destinations=d,
        G=None, nodes=nodes_gdf, edges=edges_gdf,
        origins_in_nodes=True, destinations_in_nodes=True,
        verbose=False
    )
    exp_dist, _ = manhattan_distance(grid3, o, d, "length")
    assert math.isclose(distances[(o, d)], exp_dist, rel_tol=1e-9)
    assert paths[(o, d)][0] == o
    assert paths[(o, d)][-1] == d
