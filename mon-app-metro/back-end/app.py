from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)  #

### --- Classes et Fonctions de Graphe --- ###

class Graph:
    def __init__(self, nodes, arcs):
        self.nodes = nodes
        self.arcs = arcs
        self.adjacence = self.build_adjacence_list()

    def weight(self, n1, n2):
        for arc in self.arcs:
            if arc[0] == n1 and arc[1] == n2:
                return arc[2]
        return math.inf

    def init_distances(self, source):
        return {n: (0 if n == source else math.inf) for n in self.nodes}

    def build_adjacence_list(self):
        adj = {n: [] for n in self.nodes}
        for src, dst, _ in self.arcs:
            adj[src].append(dst)
        return adj

    def dijkstra(self, source):
        d = self.init_distances(source)
        non_visités = set(self.nodes)
        parent = {n: None for n in self.nodes}

        while non_visités:
            x = min(non_visités, key=lambda n: d[n])
            non_visités.remove(x)

            for y in self.adjacence.get(x, []):
                if y in non_visités:
                    poids = self.weight(x, y)
                    if d[y] > d[x] + poids:
                        d[y] = d[x] + poids
                        parent[y] = x

        return d, parent

def chemin_depuis_parents(parent, source, destination):
    chemin = []
    courant = destination
    while courant is not None:
        chemin.insert(0, courant)
        courant = parent[courant]
    if chemin and chemin[0] == source:
        return chemin
    return []

def lire_metro_txt(fichier_path):
    nodes = set()
    arcs = []
    with open(fichier_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("--") or "temps_en_secondes" in line:
                continue
            if line.startswith("V"):
                parts = line.split(" ", 2)
                if len(parts) >= 2:
                    node_id = parts[1].strip()
                    nodes.add(node_id)
            elif line.startswith("E"):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        src = parts[1].strip().zfill(4)  
                        dst = parts[2].strip().zfill(4)  
                        poids = int(parts[3])
                        arcs.append((src, dst, poids))
                        arcs.append((dst, src, poids))
                    except ValueError:
                        continue
    return list(nodes), arcs




### --- Chargement du graphe une fois au démarrage --- ###

nodes, arcs = lire_metro_txt("metro.txt")
graphe = Graph(nodes, arcs)

### --- API Flask --- ###

@app.route("/shortest-path", methods=["POST"])
def shortest_path():
    data = request.get_json()
    source = data.get("source", "").zfill(4)
    destination = data.get("destination", "").zfill(4)

    if source not in graphe.nodes or destination not in graphe.nodes:
        return jsonify({"error": "Station ID invalide"}), 400

    distances, parent = graphe.dijkstra(source)
    chemin = chemin_depuis_parents(parent, source, destination)
    total_time = distances[destination] if chemin else None

    return jsonify({
        "path": chemin,
        "total_time": total_time
    })

### --- Lancement --- ###

if __name__ == "__main__":
    app.run(debug=True)
