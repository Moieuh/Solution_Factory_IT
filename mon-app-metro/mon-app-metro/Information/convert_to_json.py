import json
import os

# Dossier contenant les fichiers
base_path = os.path.dirname(__file__)

# Charger les stations depuis metro.txt
stations = []
with open(os.path.join(base_path, "metro.txt"), "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("V "):
            parts = line.strip().split(" ", 2)
            if len(parts) < 3:
                continue
            id_part = parts[1]
            rest = parts[2].split(";")
            if len(rest) < 2:
                continue
            name = rest[0].strip().replace("@", " ").replace(",", ", ")
            line_num = rest[1].strip()
            stations.append({
                "id": id_part,
                "name": name,
                "line": line_num
            })

# Charger les positions depuis pospoint.txt
positions = {}
with open(os.path.join(base_path, "pospoints.txt"), "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split(";")
        if len(parts) == 3:
            x, y, name = parts
            name = name.strip().replace("@", " ").replace(",", ", ")
            key = name.lower()
            if key not in positions:
                positions[key] = []
            positions[key].append((int(x), int(y)))

# Associer positions aux stations
final_stations = []
used_positions = {}

for station in stations:
    key = station["name"].lower()
    if key in positions:
        used = used_positions.get(key, 0)
        pos_list = positions[key]
        if used < len(pos_list):
            x, y = pos_list[used]
            station["x"] = x
            station["y"] = y
            used_positions[key] = used + 1
            final_stations.append(station)

# Sauvegarder au format JSON dans le même dossier
with open(os.path.join(base_path, "stations.json"), "w", encoding="utf-8") as f:
    json.dump(final_stations, f, indent=2, ensure_ascii=False)

print(f"{len(final_stations)} stations exportées dans 'stations.json'")
