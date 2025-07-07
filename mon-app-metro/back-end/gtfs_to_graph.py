import csv
import json
from collections import defaultdict

base_path = "./gtfs_data/"
valid_metro_lines = {
    "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "10", "11", "12", "13", "14", "3bis", "7bis"
}

def parse_time(t):
    try:
        h, m, s = map(int, t.split(":"))
        return h * 3600 + m * 60 + s
    except:
        return None

def main():
    # 1. Charger les lignes de métro
    metro_routes = {}
    with open(base_path + "routes.txt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["route_type"] == "1" and row["route_short_name"] in valid_metro_lines:
                metro_routes[row["route_id"]] = row["route_short_name"]

    # 2. Associer trip_id → route_id
    trip_to_route = {}
    with open(base_path + "trips.txt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["route_id"] in metro_routes:
                trip_to_route[row["trip_id"]] = row["route_id"]

    # 3. Stations
    stop_id_to_station = {}
    logical_station_info = {}
    stop_id_to_main = {}
    stop_id_to_latlon = {}

    with open(base_path + "stops.txt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stop_id = row["stop_id"]
            name = row["stop_name"]
            parent = row.get("parent_station", "")
            location_type = row.get("location_type", "0")
            lat = row.get("stop_lat")
            lon = row.get("stop_lon")

            # Déterminer station logique
            main_id = parent if parent else stop_id
            stop_id_to_main[stop_id] = main_id
            stop_id_to_station[stop_id] = main_id

            if main_id not in logical_station_info:
                logical_station_info[main_id] = {
                    "name": name,
                    "lines": set(),
                    "coords": (float(lat), float(lon)) if lat and lon else None
                }

    # 4. Arêtes depuis stop_times
    raw_edges = []
    useful_stop_ids = set()
    with open(base_path + "stop_times.txt", encoding="utf-8") as f:
        trip_stops = defaultdict(list)
        for row in csv.DictReader(f):
            trip_id = row["trip_id"]
            if trip_id not in trip_to_route:
                continue
            stop_id = row["stop_id"]
            time = parse_time(row["departure_time"])
            seq = int(row["stop_sequence"])
            route_id = trip_to_route[trip_id]
            line = metro_routes[route_id]
            trip_stops[trip_id].append((seq, stop_id, time, line))

        for stops in trip_stops.values():
            stops.sort()
            for i in range(len(stops) - 1):
                s1, s2 = stops[i], stops[i + 1]
                from_id, to_id = s1[1], s2[1]
                t1, t2 = s1[2], s2[2]
                line1, line2 = s1[3], s2[3]
                from_station = stop_id_to_station.get(from_id)
                to_station = stop_id_to_station.get(to_id)

                if not from_station or not to_station or from_station == to_station:
                    continue
                if t1 is None or t2 is None or not (0 < t2 - t1 < 3600):
                    continue

                delta = t2 - t1
                raw_edges.append((from_station, to_station, delta, "ride", line1))
                raw_edges.append((to_station, from_station, delta, "ride", line2))

                useful_stop_ids.update([from_id, to_id])

                logical_station_info[from_station]["lines"].add(line1)
                logical_station_info[to_station]["lines"].add(line2)

    # 5. Correspondances (transfers.txt)
    with open(base_path + "transfers.txt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            from_id = row["from_stop_id"]
            to_id = row["to_stop_id"]
            if from_id not in useful_stop_ids or to_id not in useful_stop_ids:
                continue
            try:
                duration = int(row["min_transfer_time"])
                from_station = stop_id_to_station.get(from_id)
                to_station = stop_id_to_station.get(to_id)
                if from_station and to_station and from_station != to_station:
                    raw_edges.append((from_station, to_station, duration, "transfer", None))
                    raw_edges.append((to_station, from_station, duration, "transfer", None))

            except:
                continue

    # 6. Dédoublonner les arêtes
    edge_map = defaultdict(list)
    for src, dst, d, t, line in raw_edges:
        edge_map[(src, dst)].append((d, t, line))


    edges = []
    for (src, dst), infos in edge_map.items():
        durations = [item[0] for item in infos]
        types = [item[1] for item in infos]
        lines = [item[2] for item in infos if item[2] is not None]
        avg = int(sum(durations) / len(durations))
        edge_type = types[0]  # "ride" ou "transfer"
        edge = {
            "from": src,
            "to": dst,
            "duration": avg,
            "type": edge_type
        }
        if edge_type == "ride" and lines:
            edge["line"] = lines[0]  # on garde la première ligne rencontrée
        edges.append(edge)


    # 7. Nœuds
    nodes = []
    valid_ids = set()
    for node_id, info in logical_station_info.items():
        if not info["lines"].intersection(valid_metro_lines):
            continue
        valid_ids.add(node_id)
        node = {
            "id": node_id,
            "name": info["name"],
            "line": ",".join(sorted(info["lines"]))
        }
        if info["coords"]:
            node["x"], node["y"] = info["coords"]
        nodes.append(node)

    # 8. Nettoyer les arêtes
    edges = [e for e in edges if e["from"] in valid_ids and e["to"] in valid_ids]

    with open("graphe_metro_v2.json", "w", encoding="utf-8") as f:
        json.dump({
            "nodes": nodes,
            "edges": edges
        }, f, indent=2, ensure_ascii=False)

    print(f"✅ Graphe V3 filtré : {len(nodes)} stations, {len(edges)} arêtes")

if __name__ == "__main__":
    main()
