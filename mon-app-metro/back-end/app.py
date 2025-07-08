from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import networkx as nx
from collections import defaultdict
import heapq
import time

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
        if edge.get("type") != "ride":
            continue
        src = edge["from"]
        dst = edge["to"]
        weight = edge["duration"]
        line = edge.get("line", "?")
        G.add_edge(src, dst, weight=weight, line=line)

    mst = nx.minimum_spanning_tree(G, algorithm="kruskal")
    
    mst_edges = []
    for u, v, data in mst.edges(data=True):
        mst_edges.append([u, v, data["weight"], data.get("line", "?")])
    
    total_weight = sum(data["weight"] for _, _, data in mst.edges(data=True))

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

    # Mesure du temps d'exécution
    t0 = time.perf_counter()

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

    t1 = time.perf_counter()
    algo_time_ms = round((t1 - t0) * 1000, 2)

    if not path or path[0] != source:
        return jsonify({"error": "Aucun chemin trouvé"}), 404

    # --- Ajout calcul émissions CO₂ ---
    # Hypothèses :
    # - Métro : 3.2 gCO₂/passager/km (source ADEME)
    # - Voiture : 120 gCO₂/passager/km (moyenne)
    # - Vitesse métro : 25 km/h (moyenne, arrêts inclus)
    # - Conversion : durée (s) → distance (km)
    total_time = dist[destination]
    speed_metro_kmh = 25
    speed_metro_ms = speed_metro_kmh * 1000 / 3600
    distance_km = (total_time * speed_metro_ms) / 1000 if total_time else 0

    co2_metro = round(distance_km * 3.2, 1)
    co2_car = round(distance_km * 120, 1)

    return jsonify({
        "path": path,
        "total_time": total_time,
        "co2_metro": co2_metro,
        "co2_car": co2_car,
        "algo_time_ms": algo_time_ms
    })








# --- Lancement ---
if __name__ == "__main__":
    print("📡 Routes disponibles :", app.url_map)
    app.run(debug=True)
