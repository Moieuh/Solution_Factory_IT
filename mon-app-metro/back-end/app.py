from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import networkx as nx
from collections import defaultdict
import heapq

app = Flask(__name__)
CORS(app)

# --- Chargement du graphe ---
with open("graphe_metro_v2.json", encoding="utf-8") as f:
    graph_data = json.load(f)

nodes = [node["id"] for node in graph_data["nodes"]]
edges = graph_data["edges"]

# --- Construction des structures nécessaires ---
adjacence = defaultdict(list)
weight_map = {}

for edge in edges:
    src = edge["from"]
    dst = edge["to"]
    weight = edge["duration"]

    adjacence[src].append(dst)
    weight_map[(src, dst)] = weight

# --- Vérification de connexité ---
def is_connected():
    G = nx.Graph()
    for edge in edges:
        src = edge["from"]
        dst = edge["to"]
        weight = edge["duration"]

        G.add_edge(src, dst, weight=weight)
    return nx.is_connected(G)

@app.route("/check_connectivity", methods=["GET"])
def check_connectivity():
    return jsonify({"connected": is_connected()})

@app.route("/mst", methods=["GET"])
def get_mst():
    G = nx.Graph()
    for edge in edges:
        src = edge["from"]
        dst = edge["to"]
        weight = edge["duration"]
        G.add_edge(src, dst, weight=weight)

    mst = nx.minimum_spanning_tree(G, algorithm="kruskal")
    mst_edges = [[u, v, d["weight"]] for u, v, d in mst.edges(data=True)]
    total_weight = sum(d["weight"] for _, _, d in mst.edges(data=True))

    return jsonify({
        "edges": mst_edges,
        "total_weight": total_weight
    })

@app.route("/debug_components", methods=["GET"])
def debug_components():
    G = nx.Graph()
    for src, dst, weight in edges:
        G.add_edge(src, dst, weight=weight)

    components = list(nx.connected_components(G))
    return jsonify({
        "nb_components": len(components),
        "component_sizes": [len(c) for c in components]
    })

# ✅ Route pour le calcul du plus court chemin (Dijkstra)
@app.route("/shortest-path", methods=["POST"])
def shortest_path():
    data = request.get_json()
    source = data.get("source")
    destination = data.get("destination")

    if source not in nodes or destination not in nodes:
        return jsonify({"error": "Station inconnue"}), 400

    dist = {n: float('inf') for n in nodes}
    prev = {n: None for n in nodes}
    dist[source] = 0
    queue = [(0, source)]

    while queue:
        d, current = heapq.heappop(queue)
        if current == destination:
            break
        for neighbor in adjacence[current]:
            alt = dist[current] + weight_map.get((current, neighbor), float('inf'))
            if alt < dist[neighbor]:
                dist[neighbor] = alt
                prev[neighbor] = current
                heapq.heappush(queue, (alt, neighbor))

    path = []
    u = destination
    while u:
        path.insert(0, u)
        u = prev[u]

    if not path or path[0] != source:
        return jsonify({"error": "Aucun chemin trouvé"}), 404

    return jsonify({
        "path": path,
        "total_time": dist[destination]
    })








# --- Lancement ---
if __name__ == "__main__":
    print("📡 Routes disponibles :", app.url_map)
    app.run(debug=True)
