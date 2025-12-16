__all__ = []

import uuid
import networkx as nx
import osmnx as ox
from shapely import Point, LineString
import scipy.sparse as sp
from scipy.sparse.csgraph import dijkstra as _sp_dijkstra
import numpy as np

# Helper functions

def new_node_id() -> str:
    """Return a globally‑unique node ID that will never clash with
       OSM’s integer IDs (we prefix with 'alt_')."""
    return f"alt_{uuid.uuid4().hex[:12]}"

def add_node_to_G(G, pt: Point) -> str:
    """Insert a geometrically‑defined node into the graph and
       return its new node ID."""
    nid = new_node_id()
    G.add_node(nid,
               x=float(pt.x),
               y=float(pt.y),
               geometry=pt)
    return nid

def add_undirected_edge(G, u, v, geom: LineString, scaling=1.0, **extras):
    """Add *both* directions if G is directed, preserving length."""
    length = geom.length*scaling                    # already metres if G is projected
    attrs  = dict(length=length,
                  geometry=geom,
                  **extras)
    G.add_edge(u, v, **attrs)
    if G.is_directed():
        G.add_edge(v, u, **attrs)

def filter_edges(G: nx.MultiDiGraph,
                edge_exclusions: dict) -> nx.MultiDiGraph:
    """
    Wrapper to filter out any edges in the edge_exclusions parameter of compute_area_access
    Parameters:
        G: nx.MultiDiGraph
            The graph to remove edges from.
        edge_exclusions : dict[str, str | list | set | tuple]
            Keys are edge attributes; values are either a single value
            to exclude or an iterable of values to exclude.
    Outputs:
        G: nx.MultiDiGraph
            The graph with removed edges (all nodes will remain)    
    """
    edges_to_keep = [
        (u, v, k)
        for u, v, k, d in G.edges(keys=True, data=True)
        if not any(
            attr in d and (
                (isinstance(vals, list) and d[attr] in vals) or
                (not isinstance(vals, list) and d[attr] == vals)
            )
            for attr, vals in edge_exclusions.items()
        )
    ]
    return G.edge_subgraph(edges_to_keep).copy()

def _ensure_csr_int32(csgraph):
    """
    Return a CSR matrix whose index arrays (indptr/indices) are int32.
    Avoids 'Buffer dtype mismatch, expected const int but got long'.
    """
    A = csgraph.tocsr()
    if A.indptr.dtype != np.int32 or A.indices.dtype != np.int32:
        A = sp.csr_matrix(
            (A.data, A.indices.astype(np.int32, copy=False), A.indptr.astype(np.int32, copy=False)),
            shape=A.shape,
        )
    return A

def dijkstra(csgraph, directed=True, indices=None,
             return_predecessors=False, unweighted=False, limit=np.inf):
    """
    Wrapper that preserves SciPy's signature but ensures `indices`
    is C-int on this platform (np.intc), avoiding
    'Buffer dtype mismatch, expected const int but got long'.
    """
    """
    Wrapper that preserves SciPy's signature but:
      1) Forces CSR index arrays to int32 (indptr/indices)
      2) Ensures `indices` is np.intc / int where needed
    """
    A = _ensure_csr_int32(csgraph)

    idx = None
    if indices is not None:
        if np.isscalar(indices):
            # keep as a plain Python int (mapped to C int by SciPy)
            idx = int(indices)
        else:
            arr = np.asarray(indices)
            if arr.dtype != np.intc or not arr.flags.c_contiguous:
                arr = np.ascontiguousarray(arr, dtype=np.intc)
            idx = arr

    return _sp_dijkstra(
        A,
        directed=directed,
        indices=idx,
        return_predecessors=return_predecessors,
        unweighted=unweighted,
        limit=limit,
    )

def _reconstruct_path(preds, di):
    """
    Helper that reconstructs the dijkstra path calls from predecessors into paths. 
    """
    chain_idx = [di]
    while True:
        prev = preds[chain_idx[-1]]
        if prev < 0:
            break
        chain_idx.append(prev)
    return chain_idx