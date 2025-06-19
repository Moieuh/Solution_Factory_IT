<template>
  <svg class="w-full h-auto" :viewBox="'0 0 ' + width + ' ' + height">
    <!-- Plan de fond -->
    <image href="/metrof_r.png" :width="width" :height="height" />

    <!-- 🔁 Chemins colorés -->
    <polyline
      v-for="(segment, index) in getSegmentsByLine()"
      :key="index"
      :points="segment.points"
      fill="none"
      :stroke="lineColor(segment.line)"
      stroke-width="4"
    />

    <!-- Cercles des stations -->
    <circle
      v-for="station in stations"
      :key="station.id"
      :cx="station.x"
      :cy="station.y"
      r="4"
      :fill="path.includes(station.id) ? 'white' : 'gray'"
      stroke="black"
      stroke-width="1"
    >
      <title>{{ station.name }} (Ligne {{ station.line }})</title>
    </circle>
  </svg>
</template>


<script setup>
const props = defineProps({
  stations: Array,
  path: Array  // liste d'IDs de stations
})

// Dimensions image
const width = 950
const height = 1000

// Extraire les points (x, y) des stations du chemin
const pathPoints = props.path.map(id =>
  props.stations.find(s => s.id === id)
).filter(Boolean)

const isInPath = id => props.path.includes(id)





// Fonction pour obtenir la couleur de la ligne ET l'afficher sur la carte 

const lineColor = (line) => {
  const colors = {
    "1": "#FFD700",     // Jaune
    "2": "#5DADE2",     // Bleu clair
    "6": "#2ECC71",     // Vert
    "12": "#9B59B6",    // Violet
    "14": "#E91E63",    // Magenta
    // Ajoute d’autres lignes ici...
  }
  return colors[line] || "#FF0000" // Rouge par défaut si non trouvé
}



const getSegmentsByLine = () => {
  if (!props.path || props.path.length < 2 || !props.stations.length) return []

  const segments = []
  let currentLine = null
  let currentPoints = []

  for (let i = 0; i < props.path.length; i++) {
    const id = props.path[i]
    const station = props.stations.find(s => s.id === id)
    if (!station) continue

    if (!currentLine) {
      currentLine = station.line
    }

    // Si ligne change ou dernier point
    if (station.line !== currentLine || i === props.path.length - 1) {
      if (i === props.path.length - 1) currentPoints.push(station)

      if (currentPoints.length > 1) {
        segments.push({
          line: currentLine,
          points: currentPoints.map(p => `${p.x},${p.y}`).join(" ")
        })
      }

      currentLine = station.line
      currentPoints = [station]
    } else {
      currentPoints.push(station)
    }
  }

  return segments
}



</script>
