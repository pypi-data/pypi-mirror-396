__all__ = [
    "inject_crossing",
    "path_dijkstra",
    "shortest_path",
    "k_shortest",
    "geomerge",
    "compute_area_access"
]

import networkx as nx
import osmnx as ox
from tqdm import tqdm
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import *

from .utils import helpers as _helpers

def inject_crossing(Graph: nx.MultiDiGraph, 
                    G: nx.MultiDiGraph, 
                    alternatives: gpd.GeoDataFrame, 
                    crossing, 
                    typedict={'normal': 1.0, 'bridge': 1.25, 'tunnel': 1.15}) -> list:
    """
    Inject the new alternative into the graph
    
    Inputs:
    - Graph (nx.MultiDiGraph): The parent graph, which should *not* be modified
    - G (nx.MultiDiGraph): The child graph, which will be modified to produce the new graph
    - alternatives (gpd.GeoDataFrame): Shapefiles of alternative crossings
    - crossing (str): The name of the crossing, extracted from alternatives['name']
    - typedict (dict): Dictionary of scaling factor for elevated or submerged segments

    Outputs:
    - endpoint_ids (list): The list of the node ids of the two new endpoints of the injected segment
    """
    alt_consid=alternatives[alternatives['Name'].isin([crossing])]
    endpoints = alt_consid.geometry.boundary
    endpoints = endpoints.to_crs(G.graph["crs"])
    # Find the nearest connection in the network & record distance from endpoint to node
    lon = endpoints.explode().x
    lat = endpoints.explode().y
    nnodes, ndists = ox.distance.nearest_nodes(Graph,lon,lat, return_dist=True) # nnodes references an index of G, dists gives the euclidean distance in meters
    nedges, edists = ox.distance.nearest_edges(Graph,lon,lat, return_dist=True) # nedges are u,v,k indices of G, dists give projection distance in meters
    alt_line   = alt_consid.to_crs(G.graph["crs"]).geometry.iloc[0] # Project alt_consid into G's crs
    alt_pts    = list(endpoints.explode()) # end‑points to list

    # Implement node-snapping behavior and inject nodes
    endpoint_ids = []          
    for i in range(2):
        pt           = alt_pts[i]
        snap_to_node = (ndists[i] - edists[i]) < 5.0   # snaps if distance to node is less than 5m more than distance to edge
        end_id = _helpers.add_node_to_G(G, pt) # Add endpoint as new node in graph
        endpoint_ids.append(end_id) # Send to endpoint ids

        if snap_to_node:
            # Case 1: snap to node
            target_id = nnodes[i] # extract the integer ID to locate node in G
            node_pt   = Point(Graph.nodes[target_id]['x'], Graph.nodes[target_id]['y']) # Find the point in a geometric space
            seg_geom  = LineString([(pt.x, pt.y), (node_pt.x, node_pt.y)]) # make a straight segment to new
            _helpers.add_undirected_edge(G, end_id, target_id, seg_geom,
                                         highway='cycleway', access='yes') # create an edge between endpoint and node
        else:
            # Case 2: don't snap to node, build new node inside edge, and connect to new node
            u, v, k   = nedges[i]                         # unpack edge key
            edata     = Graph.edges[u, v, k]
            full_geom = edata.get(                        # get the geometry of the edge
                'geometry',
                LineString([(Graph.nodes[u]['x'], Graph.nodes[u]['y']),
                            (Graph.nodes[v]['x'], Graph.nodes[v]['y'])])
            ) 
            split_pt  = full_geom.interpolate(full_geom.project(pt))    # Create the split node at the closest point along the edge
            split_id  = _helpers.add_node_to_G(G, split_pt)                      # <--^
            G.remove_edge(u, v, k) # Remove the original edge
            if G.is_directed() and G.has_edge(v, u, k):
                G.remove_edge(v, u, k)
            # Build two replacement edge pieces u–split and split–v
            geom_u    = LineString([(G.nodes[u]['x'], G.nodes[u]['y']), (split_pt.x, split_pt.y)])
            geom_v = LineString([(split_pt.x, split_pt.y), (G.nodes[v]['x'], G.nodes[v]['y'])])
            _helpers.add_undirected_edge(G, u,      split_id, geom_u,                        # create u-split edge
                                         **{k: v for k, v in edata.items()
                                         if k not in ('geometry', 'length')})
            _helpers.add_undirected_edge(G, split_id, v,      geom_v,                        # create split-v edge
                                         **{k: v for k, v in edata.items()
                                         if k not in ('geometry', 'length')})
            # Connect our endpoint to the split node
            seg_geom = LineString([(pt.x, pt.y), (split_pt.x, split_pt.y)])
            _helpers.add_undirected_edge(G, end_id, split_id, seg_geom,
                                         highway='cycleway', access='yes')
   
    # Add the alignment itself as a series of edges between its two endpoints
    alignment_id_0, alignment_id_1 = endpoint_ids
    scaling = typedict[alternatives.loc[alternatives['Name'] == crossing, 'type'].iloc[0]]
    _helpers.add_undirected_edge(G, alignment_id_0, alignment_id_1,      # add the alignment
                                 alt_line,
                                 scaling=scaling,
                                 highway='cycleway', access='yes',
                                 name='Alternative alignment')
    
    return endpoint_ids

import osmnx as ox
import networkx as nx
import geopandas as gpd
import numpy as np
from shapely import Point, MultiPoint, LineString, MultiLineString
from tqdm import tqdm
import warnings
import heapq
import re

def path_dijkstra(origins: int | list | np.ndarray,
                  destinations: int | list,
                  G: nx.MultiDiGraph = None,
                  nodes: gpd.GeoDataFrame = None,
                  edges: gpd.GeoDataFrame = None,
                  *,
                  dist_param: str = 'length',
                  origins_in_nodes: bool = False,
                  destinations_in_nodes: bool = False,
                  pairs: bool = False,
                  verbose: bool = True) -> tuple[dict[tuple, float], dict[tuple, list]]:
    """
    DEPRECATED: use `shortest_path` instead.

    Backwards-compatible wrapper that:
      - accepts either (G) or (nodes, edges) and constructs G if needed
      - accepts origins/destinations either as node IDs or as Point geometries
      - supports OD pairs via `pairs=True`

    In future versions, only node-based (origins, destinations) and a pre-built G
    will be supported via `shortest_path`.
    """
    warnings.warn(
        "FutureWarning: nf.path_dijkstra is deprecated. Use nf.shortest_path instead.",
        FutureWarning,
        stacklevel=2,
    )
    if not origins_in_nodes or not destinations_in_nodes:
        warnings.warn(
            "FutureWarning: nf.shortest_path will require origins and destinations "
            "to be node IDs in the graph (no geometry snapping).",
            FutureWarning,
            stacklevel=2,
        )
    if G is None:
        warnings.warn(
            "FutureWarning: nf.shortest_path will require only graph input. "
            "Transform nodes/edges to G prior to use.",
            FutureWarning,
            stacklevel=2,
        )

    # Build graph if needed
    if G is None:
        if nodes is None or edges is None:
            raise ValueError("Provide either G or both nodes and edges.")
        G = ox.graph_from_gdfs(nodes, edges)

    # Helper to snap geometries to nearest nodes
    def _snap(arr, flag):
        arr = np.ravel([arr])
        if flag:
            return list(arr)
        assert all(isinstance(pt, Point) for pt in arr), "Pointlike geometry required."
        coords = [(pt.x, pt.y) for pt in arr]
        xs, ys = zip(*coords)
        return list(ox.nearest_nodes(G, xs, ys))

    # Normalize origin/destination inputs to node lists
    if origins_in_nodes:
        orig_list = [origins] if isinstance(origins, (int, float, np.integer)) else list(origins)
    else:
        orig_list = _snap(origins, False)

    if destinations_in_nodes:
        dest_list = [destinations] if isinstance(destinations, (int, float, np.integer)) else list(destinations)
    else:
        dest_list = _snap(destinations, False)

    if not orig_list:
        raise ValueError("`origins` must contain at least one element.")
    if not dest_list:
        raise ValueError("`destinations` must contain at least one element.")

    if set(orig_list) - set(G.nodes()):
        raise KeyError(f"The following origins are not in graph: {set(orig_list) - set(G.nodes())!r}")
    if set(dest_list) - set(G.nodes()):
        raise KeyError(f"The following destinations are not in graph: {set(dest_list) - set(G.nodes())!r}")

    # Delegate to the new clean implementation
    return shortest_path(
        origins=orig_list,
        destinations=dest_list,
        G=G,
        dist_param=dist_param,
        pairs=pairs,
        verbose=verbose,
    )


def shortest_path(origins: int | list | np.ndarray,
                  destinations: int | list,
                  G: nx.MultiDiGraph,
                  *,
                  dist_param: str = 'length',
                  pairs: bool = False,
                  verbose: bool = True) -> tuple[dict[tuple, float], dict[tuple, list]]:
    """
    A data-structure optimized algorithm for computing shortest paths between sets of points. Utilizes
    compressed sparse row (CSR) matricies for efficient adjacent-node searching across the graph. 
    Can compute between one origin and one destination, many origins and one destination, one origin
    and many destinations, or many origins and many destinations, which will compute pairwise if `pairs`
    is specified, and every possible combination otherwise. Note that unreachable paths will have a distance
    of 'inf' and a path list of length 1 (the origin node only).

    Parameters:

        origins: int | list | np.ndarray
        - The origin nodes to be used. Must correspond with nodes in `G`.

        destinations: int | list
        - The destination nodes to be used. Must correspond with nodes in `G`.

        G: nx.MultiDiGraph
        - The graph to be used in the calculation. If `G` is not strongly connected, many distances may 
          return 0 or infinity. This can be fixed beforehand with `nx.connected_components()`. 

        dist_param: str = 'length'
        - The distance parameter to be used for computing distance. Defaults to `length` (natively
          in OSM). Useful if passing uniquely weighted edges. Must be one of the edge attributes.

        pairs: bool = False
        - Whether the origins and destinations should be interpreted as OD pairs. Will perform single 
          routings between each pair

        verbose: bool = True
        - If passing multiorigin/multidestination, will add a `tqdm` wrapper and verbosity to the calculations,
          so the user can get a sense of how long it will take to run.

    Outputs:

        dists: dict
        - A dictionary of floating-point distances, indexed by OD tuple.

        paths: dict
        - A dictionary of paths, indexed by OD tuple. Each path is represented as a node list of ndoes
          in the path.
    """
    if G is None:               # Make sure Graph is well-built
        raise ValueError("`G` must be provided to shortest_path (no nodes/edges construction).")

    assert all(dist_param in data and data[dist_param] is not None for _, _, data in G.edges(data=True)),\
            "`dist_param` is not a valid edge attribute. Make sure it is non-null for all edges."
    
    def _ensure_list(x):
        if isinstance(x, (int, float, np.integer)):
            return [x]
        return list(x)
    
    orig_list = _ensure_list(origins)
    dest_list = _ensure_list(destinations)

    if not orig_list:
        raise ValueError("`origins` must contain at least one element.")
    if not dest_list:
        raise ValueError("`destinations` must contain at least one element.")

    if set(orig_list) - set(G.nodes()):
        raise KeyError(f"The following origins are not in graph: {set(orig_list) - set(G.nodes())!r}")
    if set(dest_list) - set(G.nodes()):
        raise KeyError(f"The following destinations are not in graph: {set(dest_list) - set(G.nodes())!r}")

    nodes_list = list(G.nodes())                    
    idx_map = {node: i for i, node in enumerate(nodes_list)}    # Build map of nodes and their indices
    inv_idx = {i: node for node, i in idx_map.items()}
    A = nx.to_scipy_sparse_array(G, nodelist=nodes_list, weight=dist_param, format="csr")   # CSR matrix for speed

    def multimulti(origin_to_dests: list):
        distances = {}
        all_preds = {}
        sources = list(origin_to_dests.keys())
        scs = tqdm(sources) if verbose else sources
        for s in scs:
            si = idx_map[s]
            dist_arr, preds_arr = _helpers.dijkstra(A, directed=True, indices=si, return_predecessors=True)
            for d in origin_to_dests[s]:
                di = idx_map[d]
                distances[(s, d)] = float(dist_arr[di])
                chain = [di]
                while True:
                    prev = preds_arr[chain[-1]]
                    if prev < 0:
                        break
                    chain.append(prev)
                path = [inv_idx[idx] for idx in reversed(chain)]
                all_preds[(s, d)] = path
        return distances, all_preds    

    if pairs:                                                   # Allow user to specify that origin and destinations should be pathed pairwise 
        print('pairs chosen') if verbose else None
        if len(orig_list) != len(dest_list):
            raise ValueError("When pairs=True, origins and destinations must be the same length.")
        unique_pairs = set(zip(orig_list, dest_list))
        origin_to_dests = {}
        for o, d in unique_pairs:
            origin_to_dests.setdefault(o, []).append(d)
        print('sources made. length', len(origin_to_dests)) if verbose else None
        return multimulti(origin_to_dests)

    if len(orig_list) > 1 and len(dest_list) == 1:                                                            # multiorigin, one destination
        d = dest_list[0]
        dest_i = idx_map[d]                                                                         
        dist_arr, preds = _helpers.dijkstra(A.transpose(), directed=True, indices=dest_i, return_predecessors=True)
        distances = {}
        paths = {}
        for o in orig_list:
            oi = idx_map[o]
            distances[(o, d)] = float(dist_arr[oi])
            chain_idx = [oi]
            while True:
                nxt = preds[chain_idx[-1]]
                if nxt < 0:
                    break
                chain_idx.append(nxt)
            paths[(o, d)] = [inv_idx[idx] for idx in chain_idx]
        return distances, paths        

    if len(orig_list) == 1 and len(dest_list) > 1:                                                            # one origin, multidestination
        o = orig_list[0]
        orig_i = idx_map[o]                                                                        
        dist_arr, preds = _helpers.dijkstra(A, directed=True, indices=orig_i, return_predecessors=True)                
        distances = {}
        paths = {}
        for d in dest_list:
            di = idx_map[d]
            distances[(o, d)] = float(dist_arr[di])
            chain_idx = [di]
            while True:
                prev = preds[chain_idx[-1]]
                if prev < 0:
                    break
                chain_idx.append(prev)
            paths[(o, d)] = [inv_idx[idx] for idx in reversed(chain_idx)]
        return distances, paths                              

    if len(orig_list) == 1 and len(dest_list) == 1:                                                           # one origin, one destination
        o, d = orig_list[0], dest_list[0]
        oi, di = idx_map[o], idx_map[d]                                         
        dist_arr, preds_arr = _helpers.dijkstra(A, directed=True, indices=oi, return_predecessors=True)                
        distances = {(o, d): float(dist_arr[di])}
        chain_idx = [di]
        while True:
            prev = preds_arr[chain_idx[-1]]
            if prev < 0:
                break
            chain_idx.append(prev)
        paths = {(o, d): [inv_idx[idx] for idx in reversed(chain_idx)]}
        return distances, paths                                      

    print('multi x multi chosen') if verbose else None  # multiorigin, multidestination
    uniq_origs = list(dict.fromkeys(orig_list))
    uniq_dests = list(dict.fromkeys(dest_list))
    origin_to_dests = {o: uniq_dests for o in uniq_origs}
    print(f'unique origins: {len(uniq_origs)}, unique destinations: {len(uniq_dests)},' 
          f'paths: {len(uniq_origs)*len(uniq_dests)}') if verbose else None
    return multimulti(origin_to_dests)

def k_shortest(
    G: nx.DiGraph | nx.MultiDiGraph,
    pairs: list[tuple],                 # list or set of (origin_node, destination_node)
    k: int = 3,
    weight_attr: str = "length",
    pct_disticnt: float = 0.15,
    tol: float = 2.0,
) -> dict[tuple, dict]:
    """
    Optimized all-pairs K-shortest simple paths via (per-pair) Eppstein's algorithm. 

    Parameters

    G : nx.DiGraph | nx.MultiDiGraph
        Graph to compute k-shortest paths on (nodes are SUMO edge IDs here).
    pairs : list[(o, d)]
        Iterable of (origin_node, destination_node) pairs to compute KSP for.
    k : int
        Max number of shortest paths per OD pair.
    weight_attr : str
        Edge attribute for weights (e.g. "travel_time").
    pct_disticnt : float
        Jaccard distinctness threshold for accepting alternative paths.
    tol : float
        Max path length as multiplier of base shortest-path length.

    Returns

    result : dict
        {(o, d): {"dists": {rank: dist, ...},
                  "paths": {rank: [node0, node1, ...], ...}}, ...}
    """
    if not pairs:
        return {}

    # -----------------------------------------------------------------------
    # 1) Index maps & CSR matrices (once)
    # -----------------------------------------------------------------------
    nodes = list(G.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    inv = {i: n for n, i in idx.items()}

    AF = nx.to_scipy_sparse_array(
        G, nodelist=nodes, weight=weight_attr, format="csr"
    )
    AR = nx.to_scipy_sparse_array(
        G.reverse(), nodelist=nodes, weight=weight_attr, format="csr"
    )

    # Filter out pairs that don't exist in idx at all
    pairs = [(o, d) for (o, d) in pairs if o in idx and d in idx]
    if not pairs:
        return {}

    # -----------------------------------------------------------------------
    # 2) Unique sources / sinks -> single-source Dijkstra SPTs
    # -----------------------------------------------------------------------
    sources = sorted({o for (o, _) in pairs})
    sinks   = sorted({d for (_, d) in pairs})

    forward_spt: dict = {}   # origin_node -> (d_s, p_s)
    reverse_spt: dict = {}   # dest_node   -> (d_t, p_t)

    # forward SPT: distances FROM each source to all nodes
    for o in tqdm(sources, desc="Forward SPT (sources)"):
        s = idx[o]
        d_s, p_s = _helpers.dijkstra(AF, directed=True, indices=s, return_predecessors=True)
        forward_spt[o] = (d_s, p_s)

    # reverse SPT: distances TO each sink from all nodes (via reversed graph)
    for d in tqdm(sinks, desc="Reverse SPT (sinks)"):
        t = idx[d]
        d_t, p_t = _helpers.dijkstra(AR, directed=True, indices=t, return_predecessors=True)
        reverse_spt[d] = (d_t, p_t)

    # -----------------------------------------------------------------------
    # 3) Single-pair KSP logic (same as your original, factored into a helper)
    # -----------------------------------------------------------------------
    if G.is_multigraph():
        def edge_w(u, v):
            return min(
                (d.get(weight_attr, 1.0) for d in G[u][v].values()),
                default=1.0,
            )
    else:
        def edge_w(u, v):
            return G[u][v].get(weight_attr, 1.0)

    def path_edges(P): return list(zip(P, P[1:]))
    def edge_set(P):   return set(path_edges(P))

    def ksp_for_pair(o, d):
        d_s, p_s = forward_spt[o]
        d_t, p_t = reverse_spt[d]
        t_idx = idx[d]

        # If dest unreachable from source, skip
        if not (d_s[t_idx] < float("inf")):
            return {}, {}

        # base path 0 (same as before)
        base_idx_path = _helpers._reconstruct_path(p_s, t_idx)[::-1]
        base_path = [inv[i] for i in base_idx_path]
        base_len = float(d_s[t_idx])

        dists = {0: base_len}
        paths = {0: base_path}

        def suffix_from(v):
            # NOTE: same pattern as your original: use reverse SPT from dest
            return [inv[j] for j in _helpers._reconstruct_path(p_t, idx[v])]

        base_edge_set = set(path_edges(base_path))
        accepted_edge_sets = [base_edge_set]

        def distinct(P):
            C = edge_set(P)
            for E in accepted_edge_sets:
                inter = len(C & E)
                union = len(C | E) or 1
                jaccard_dist = 1.0 - inter / union
                if jaccard_dist + 1e-12 < pct_disticnt:
                    return False
            return True

        # global heap of candidates
        H = []
        seen_paths = {tuple(base_path)}
        seen_cids  = set()  # (prefix_tuple, nbr) structure id

        def spawn_from(base_id):
            P = paths[base_id]
            next_on = {
                P[i]: (P[i+1] if i+1 < len(P) else None)
                for i in range(len(P))
            }
            prev_on = {
                P[i]: (P[i-1] if i-1 >= 0 else None)
                for i in range(len(P))
            }
            for i, u in enumerate(P):
                for v in G.neighbors(u):
                    if v == next_on[u] or v == prev_on[u]:
                        continue  # skip on-path edge and one-step backtrack
                    w = edge_w(u, v)
                    delta = d_s[idx[u]] + w + d_t[idx[v]] - d_s[t_idx]
                    cid = (tuple(P[: i + 1]), v)
                    if cid in seen_cids:
                        continue
                    heapq.heappush(
                        H,
                        (dists[base_id] + float(delta), base_id, i, v, cid),
                    )

        # seed from base path
        spawn_from(0)

        # main KSP loop
        while len(paths) < k and H:
            total, b_id, i_on, nbr, cid = heapq.heappop(H)
            cand = paths[b_id][: i_on + 1] + suffix_from(nbr)
            T = tuple(cand)

            if T in seen_paths:
                continue
            if total > tol * base_len:
                continue
            if len(cand) != len(set(cand)):
                continue
            if not distinct(cand):   # equivalent to your bool+threshold trick
                continue

            new_id = len(paths)
            paths[new_id] = cand
            dists[new_id] = float(total)
            seen_paths.add(T)
            seen_cids.add(cid)
            accepted_edge_sets.append(edge_set(cand))
            spawn_from(new_id)

        return dists, paths

    # -----------------------------------------------------------------------
    # 4) Run KSP for all requested pairs
    # -----------------------------------------------------------------------
    result: dict[tuple, dict] = {}
    for (o, d) in tqdm(pairs, desc="K-shortest for gateway pairs"):
        dists_k, paths_k = ksp_for_pair(o, d)
        if paths_k:
            result[(o, d)] = {"dists": dists_k, "paths": paths_k}

    return result

def geomerge(
    df: gpd.GeoDataFrame,
    field: str,
    base_osm: gpd.GeoDataFrame,
    *,
    name: str = None,
    categories: list = None,
    road_id: str = None,
    area: gpd.GeoDataFrame | gpd.GeoSeries = None,
    type_join: str = 'range',
    buffer_ft: float = 10,
    n_samples: int = 10,
    threshold: float = 0.85,
    crs_ft: str = "EPSG:2236",  # Using local CRS as default, can change this for future projects
    verbose: bool = False,
    ) -> gpd.GeoDataFrame:      # Type hint to GeoDataFrame output            
    r"""
    Approximate the n%-overlap of `df` with `base_osm` via interpolated point-sampling along each 
    OSM segment. $n$ is set by `threshold`. Note that n_samples does not include the two endpoints,
    so $n$% is mathematically $\lceil t\times\text{n samples} \rceil / (\text{n samples} + 2)$. Any
    values computed as `NaN` will be imputed as -1, for convenience.
    Parameters
    - df: gpd.GeoDataFrame
        Vendor GeoDataFrame containing the attribute `field`. This will be merged 
        *onto* `base_osm`.
    - field: str
        column in df with the raw attribute values to be merged onto `base_osm`.
    - base_osm: gpd.GeoDataFrame
        OSM road GeoDataFrame. Output will have the same geometry and attributes.
    - name: str 
        name of the new categorical column to add. If not passed, will be inferred
        from the `field` parameter.
    - categories: list
        list of thresholds (for "range") or exact values (for "exact"). If `categories`
        is not passed, it will be inferred as a linspace or a logspace (if `mean >= 3x median`).
    - road_id: str
        column in `base_osm` GeoFrames that uniquely identifies roads. If not passed, will
        default to a new column set as the index of `base_osm`. 
    - area: gpd.GeoDataFrame | gpd.GeoSeries
        polygon boundary of the study area. If not passed, defaults to a the minimum
        bounding rectangle of `df`.
    - type_join: str
        "range" ⇒ bin by intervals; "exact" ⇒ only keep exact matches. Defaults to `range`
    - buffer_ft: float
        distance to buffer each line/point by to find its match. Defaults to 10 of CRS unit
    - n_samples: int
        number of points to interpolate along each segment. Defaults to 10 (meaning 12 total)
    - threshold: float
        percentage threshold used to "match" segments. Defaults to 0.85 (85%)
    - crs_ft: str
        projected CRS in feet for geometry ops. Defaults to `EPSG:2236` (Florida)
    - verbose: bool
        Whether to show print statements and progress bars. Default is False
    Returns
    - GeoDataFrame in the CRS of base_osm with the extra column `name`.
    """
    assert buffer_ft > 0, "Buffer must be positive nonzero."
    assert n_samples > 0, "Number of points to interpolate must be positive nonzero"

    df_ft   = df.to_crs(crs_ft)                             # Set all CRS in one go
    base_ft = base_osm.to_crs(crs_ft)
    ### BASE CHECKS ###
    if area is None:                                                        # Infer area polygon if one is not passed
        min_bbox = base_ft.geometry.unary_union.minimum_rotated_rectangle
        area = gpd.GeoDataFrame(geometry=[min_bbox], crs=crs_ft)
        area_ft = area.geometry[0]
    else:
        area_ft = area.to_crs(crs_ft).geometry.unary_union

    if categories is None:                                                  # Infer categories if none passed
        if not pd.api.types.is_numeric_dtype(df_ft[field]):
            raise ValueError("Cannot infer `categories`: non-numeric `field` type passed")
        nzmin = df_ft[df_ft[field] > 0][field].min()
        maxi = df_ft[field].max()
        om = len(str(int(nzmin//1))) - 1                                     # Set the rounding level for the output, `om` means order of magnitude
        multval = 1*(10**(om - 1)) if om >= 2 else 1
        if (df_ft[field].mean() >= 3*df_ft[field].median()) and (df_ft[field] >= 0).all():
            categories = list((np.exp(np.linspace(np.log(nzmin), np.log(maxi), 8))//multval*multval).astype(int))
        else:
            categories = list((np.linspace(nzmin, maxi, 8)//multval*multval).astype(int))
    else:
        if not pd.api.types.is_numeric_dtype(df_ft[field]):
            raise ValueError("Non-numeric `field` type passed")

    if road_id is None:                                                     # Create new road_id column if none passed
        base_ft['road_id_new'] = base_ft.index
        road_id = 'road_id_new'

    if name is None:                                                        # Set name column if none passed
        name = f'{field}_new'
    ###------------###
    df_ft   = df_ft[df_ft.geometry.intersects(area_ft)]     # Clip to area polygon
    base_ft = base_ft[base_ft.geometry.intersects(area_ft)]

    if type_join == "range":                                            
        cats_sorted = sorted(set(categories))                               # Sort categories in place
        bins   = [0] + cats_sorted + [df_ft[field].max()] \
                        if df_ft[field].max() not in cats_sorted \
                        else [0] + cats_sorted                              # Control for if the max is in the set already (useful if range created from linspace)  
        labels = [f"{lo} - {hi}" for lo, hi in zip(bins[:-1], bins[1:])]
        df_ft[name] = pd.cut(                                               # Bin the categories and label them, including rightmost value   
            df_ft[field],
            bins=bins,
            labels=labels,
            right=True, #---------------------------< Keep rightmost (not sure if these should all be kept, might need consult)
            include_lowest=True #-------------------< Keep leftmost (lowest)
        )
    elif type_join == "exact":                                              # Place exact value if parameter is passed
        df_ft[name] = df_ft[field].map({x: x for x in categories})
    else:
        raise ValueError("type_join must be 'range' or 'exact'")            # Handle exceptions i.e. incorrect type passed

    if pd.api.types.is_categorical_dtype(df_ft[name]):                      # Add category (pandas has weird categorical datatypes) to infill with -1
        df_ft[name] = (
            df_ft[name]
            .cat.add_categories([-1])
            .fillna(-1)
        )
    else:
        df_ft[name] = df_ft[name].fillna(-1)                                # Or just blatantly fill with -1, if possible

    df_ft = df_ft.copy()
    df_ft['geometry'] = df_ft.geometry.buffer(buffer_ft, cap_style="flat")  # Buffer the lines by buffer_ft

    base_ft = base_ft.copy()
    base_ft["length_full"] = base_ft.geometry.length                        # Extract lengths

    samples = []
    itt = base_ft[[road_id, "geometry"]].iterrows()
    for _, row in (itt if not verbose else tqdm(itt)):                # Sample along lines
        line = row.geometry
        if line.length == 0:    # Skip if zero linelength            
            continue
        distances = np.linspace(0, line.length, n_samples + 2)[1:-1]    # Sample n_samples + 2 along the line's distance 
        for d in distances:                                             
            samples.append({
                road_id: row[road_id],
                "geometry": line.interpolate(d) #-----------------------< Critical line, interpolate the points onto the actual line shape
            })
    pts = gpd.GeoDataFrame(samples, crs=crs_ft)

    tagged = gpd.sjoin(pts, #-------------------------------------------< Where the biggest efficiency gain is had, just checking for points (super computationally cheap)
        df_ft[[name, "geometry"]],
        how="left",
        predicate="within")
    vote_counts = (tagged   #-------------------------------------------< Aggregate the number needed for a "pass"
        .groupby([road_id, name])
        .size()
        .unstack(fill_value=0))

    max_votes = vote_counts.max(axis=1) 
    best_cat  = vote_counts.idxmax(axis=1)  #---------------------------< idxmax finds the index where the max happend
    thresh    = int(np.ceil(threshold * n_samples))  #------------------< Threshold it at the parameterized threshold level
    best_cat  = best_cat.where(max_votes >= thresh, -1)
    best_df   = best_cat.rename(name).reset_index()
    out = base_ft.merge(best_df, on=road_id, how="left") #--------------< Merge onto original DF
    out[name] = out[name].fillna(-1)

    return out.to_crs(base_osm.crs) #-----------------------------------< Set to CRS and return

def compute_area_access(G: nx.MultiDiGraph, 
                        endpoints: LineString | Point, 
                        *, 
                        return_nodes: bool = False,
                        return_edges: bool = False,
                        return_graph: bool = False,
                        step: int | float = 1609, 
                        n_steps: int = 4, 
                        dist_param: str = 'length',
                        network_type: str = 'all',
                        edge_exclusions: dict = None) -> gpd.GeoDataFrame | nx.MultiDiGraph:
    """
    A function to compute consecutive ego graphs. It computes n ego graphs at each step to create a GeoDataFrame of edges in the access area 
    with a new dist calculation classifying each edge into a 'distance band'. Useful for avoiding expensive multi_source_dijkstra calls.
    Parameters:
        G: nx.MultiDiGraph
            The graph to be used for computation.
        endpoints: LineString, MultiLineString, Point, MultiPoint
            The points to be used for centering the ego graphs.
        return_nodes: bool
            Whether the function should return a nodes GeoDataFrame. Default is False.
        return_edges: bool
            Whether the function should return an edges GeoDataFrame. Default is False.
        return_graph: bool
            Whether the function should return a graph. Default is False. Exactly *one* of the returns must be true. 
        step: int, float
            The size of the distance steps the output will contain, in meters. Default is set at 1 mile (1609 meters).
        n_steps: int
            The number of distance steps the function will check. 
        dist_param: str
            The attribute in the graph's edges that will be used to compute distance. The function will raise a ValueError 
            if it is not a valid attribute.
        network_type: str - {"all", "all_public", "bike", "drive", "drive_service", "walk"} 
            The network type to compute the distances on. Passing an invalid type will default to "all".
        edge_exclusions: dict
            A dictionary of the form {_field_: str | list}; exclude edge values in _field_ attribute
    Outputs:
        output: geopandas.GeoDataFrame, nx.MultiDiGraph
            Either the resulting graph, the nodes of the resulting graph, or the edges of the resulting graph, based on the user's inputs
    """
    assert isinstance(endpoints, (Point, MultiPoint, LineString, MultiLineString)), "endpoints must be of type Point, LineString, or MultiLineString"
    assert nx.get_edge_attributes(G, dist_param), "invalid dist_param. Must be in the edge attributes!" 
    if not any((return_nodes, return_edges, return_graph)):
        raise ValueError("Nothing to return!  Set at least one flag True.")
    
    if sum([return_graph, return_nodes, return_edges]) > 1: 
        warnings.warn("Multiple values set as True. compute_area_access() will either return nodes, edges, or the full graph, but not all 3. Graph will be returned.")
        return_edges = return_nodes = False
        return_graph = True
    set_state = np.where([return_graph, return_nodes, return_edges])[0][0]

    ep_list = []
    if isinstance(endpoints, Point):
        ep_list.append(endpoints)
    elif isinstance(endpoints, MultiPoint):
        ep_list.extend(list(endpoints.geoms))
    else:
        ep_list.extend(list(endpoints.boundary.geoms)) 

    GC = None
    try:
        filtered = ox._overpass._get_network_filter(network_type)
    except ValueError: 
        warnings.warn('Invalid network type parameter. Using "all" instead.')
        network_type = "all"
        GC = G.copy()
    
    if network_type != "all":
        excluded: dict[str, set[str]] = {}
        for tag, values in re.findall(r'\["([^"]+)"!~"([^"]+)"\]', filtered):
            excluded[tag] = set(values.split("|"))
        geonodes, geoedges = ox.graph_to_gdfs(G, nodes=True, edges=True)
        mask = ~pd.concat([
            geoedges[key].isin(values) for key, values in excluded.items() if key in geoedges.columns and not isinstance(key, list)
        ], axis=1).any(axis=1)
        GC = ox.graph_from_gdfs(geonodes, geoedges[mask])
        isolated_nodes = list(nx.isolates(GC))
        GC.remove_nodes_from(isolated_nodes)

    if edge_exclusions:
        GC = _helpers.filter_edges(GC, edge_exclusions)
        GC.remove_nodes_from(list(nx.isolates(GC)))

    args = [(1, 1), (1, 0), (0, 1)][set_state]
    G_out = nx.MultiDiGraph()
    G_out.graph["crs"] = GC.graph.get("crs")
    for point in ep_list:
        node = ox.nearest_nodes(GC, point.x, point.y)
        warn = 0
        for n in np.arange(n_steps)+1:
            try:
                distance = n*step
                subgraph = nx.ego_graph(GC, node, radius=distance, distance=dist_param)
                meta = {"loc"   : f'({round(point.x, 4)}, {round(point.y, 4)})',
                    "dist"      : n,
                    "dist_class": f'{round(distance/1609, 2)}-mile {network_type if network_type != "all" else "travel"}shed',
                    "mode"      : network_type}
                for attr, val in meta.items():
                    nx.set_edge_attributes(subgraph, val, attr)
                    nx.set_node_attributes(subgraph, val, attr)
                G_out = nx.compose(subgraph, G_out)
            except Exception as Err:
                warn += 1
                if warn == 1: print(Err)
                continue
        if warn:
            warnings.warn(f'Exception: {warn}/{n_steps} invalid parameters were found. {warn} points were not computed.')
    return G_out if not set_state else ox.graph_to_gdfs(G_out, nodes=args[0], edges=args[1])