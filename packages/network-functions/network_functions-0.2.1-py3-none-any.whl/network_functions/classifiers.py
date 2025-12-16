__all__ = [
    "fill_holes_and_dissolve",
    "classify_node",
    "find_bridges",
    "find_res_links",
    "collapse_one_in_one_out"
]

from shapely.geometry import *
from shapely.ops import linemerge  
import networkx as nx
import osmnx as ox


def fill_holes_and_dissolve(geom):
    """Remove every interior ring, then dissolve overlaps.
    • Polygon        → Polygon without holes
    • MultiPolygon   → each part without holes, then unioned into
                       a single valid geometry (islands kept)"""
    if geom.geom_type == "Polygon":
        cleaned = Polygon(geom.exterior)
    elif geom.geom_type == "MultiPolygon":
        cleaned = MultiPolygon([Polygon(p.exterior) for p in geom.geoms])
    else:          
        return geom
    return cleaned.buffer(0) 

def classify_node(G, n):
    """Return number of in/out edges of each node."""
    in1  = sum(1 for _, _, d in G.in_edges(n, data=True)  if d.get("oneway"))
    out1 = sum(1 for _, _, d in G.out_edges(n, data=True) if d.get("oneway"))
    return in1, out1                       # mixed or no oneway edges

def find_bridges(G, max_len_ft=100):
    bridges = []
    for u, v, k, dat in G.edges(keys=True,data=True):
        if G.has_edge(u, v) and G.has_edge(v, u):
            if dat.get('length', float("inf")) > max_len_ft*0.3048 or dat.get('highway') in ['footway', 'bridleway', 'path', 'sidewalk', 'crossing', 'traffic_island', 'cycleway']:
                continue
            u_class = classify_node(G,u) #                                                 -|
            v_class = classify_node(G,v) #                                                  |
            if u_class[0] and u_class[1] and v_class[0] and v_class[1]: #                   |- Identify topoligical signature of a bridge
                bridges.append((u,v,k)) #                                                   |
            if (u_class[0] and v_class[1]) or (v_class[0] and u_class[1]): #                |
                bridges.append((u,v,k)) #                                                  -|
    return bridges

def find_res_links(G, max_len_ft=300):
    slips = []
    for u, v, k, dat in G.edges(keys=True,data=True):
        check_top = False
        if dat.get("length", float("inf")) > max_len_ft*0.3048 or dat.get('highway') in ['footway', 'bridleway', 'path', 'sidewalk', 'crossing', 'traffic_island', 'cycleway']:
            continue
        
        u_class = classify_node(G,u) #                                                                        --|
        v_class = classify_node(G,v) #                                                                          |
        u_in, u_out = list(G.in_edges(u, keys=True, data=True)), list(G.out_edges(u, keys=True, data=True)) #    =-   Collect in/out data about u and v
        v_in, v_out = list(G.in_edges(v, keys=True, data=True)), list(G.out_edges(v, keys=True, data=True)) #   |
        u_highways = [d.get('highway') for _, _, _, d in u_in + u_out if d.get('highway') != 'residential'] #   |
        v_highways = [d.get('highway') for _, _, _, d in v_in + v_out if d.get('highway') != 'residential'] # --|

        if dat.get('highway') == 'residential' and (len(u_highways) + len(v_highways) < 4): #                         --|
            if u_class == (1,2): #                                                                                      |
                residential_count = sum(1 for _, _, _, d in u_out if d.get('highway') == 'residential') #               |
                if residential_count == 1 and len(u_highways) == 2 and u_highways[0] == u_highways[1]: # Logic Gate     |
                    slips.append((u,v,k)) #                                                                             |-- Topological signature of a residential-marked slip
            if v_class == (2,1): #                                                                                      |                
                residential_count = sum(1 for _, _, _, d in v_in if d.get('highway') == 'residential') #                |
                if residential_count == 1 and len(v_highways) == 2 and v_highways[0] == v_highways[1]: # Logic Gate     |
                    slips.append((u,v,k)) #                                                                           --|
    return slips

def collapse_one_in_one_out(G):
    G = G.copy()
    edge_data = {}
    for n,d in list(G.nodes(data=True)):
        if G.in_degree(n) == 1 and G.out_degree(n) == 1:
            (u, _, k_in), (_, v, k_out) = list(G.in_edges(n, keys=True)) + list(G.out_edges(n, keys=True))
            if u == v:          # skip potential self-loops
                continue
            in_data  = G.edges[u, n, k_in]
            out_data = G.edges[n, v, k_out]

            # stitch geometries end-to-end (respecting direction)
            geom   = linemerge([in_data["geometry"], out_data["geometry"]])
            if geom.coords[0] != in_data["geometry"].coords[0]:     # 
                geom = LineString(list(geom.coords)[::-1])
            if geom.length == 0:                                # skip if the geometry has 0 length
                continue       
            orig_in = in_data.get("orig_edges", [(u, n, k_in)])
            orig_out = out_data.get("orig_edges", [(n, v, k_out)])
            attrs = {**out_data, **in_data, "geometry": geom, "orig_edges": orig_in + orig_out}

            if (u, v) not in edge_data: #                                                          --|
                edge_data[(u, v)] = [] #                                                             |
            if (u, n) in edge_data: #                                                                |
                edge_data[(u, v)].extend(edge_data[(u, n)]) #                                        |---- Need to update edge_data to include new edge data, without losing the nodes
            if (n, v) in edge_data: #                                                                |      that existed before
                edge_data[(u, v)].extend(edge_data[(n, v)]) #                                        |
            new_data = d['osmid_original'] #                                                         |
            edge_data[(u,v)].extend(new_data if isinstance(new_data, list) else [new_data]) #      --|

            G.add_edge(u, v, **attrs)
            # remove the old pieces
            G.remove_edge(u, n, k_in)
            G.remove_edge(n, v, k_out)
            G.remove_node(n)
    return G, edge_data