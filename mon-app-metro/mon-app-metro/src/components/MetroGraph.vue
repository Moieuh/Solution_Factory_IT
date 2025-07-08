<template v-if="isMapReady">
  <div class="flex flex-col h-[calc(100vh-20px)] w-full">
    
    <!-- 🔘 Bouton et poids ACPM -->
    <div class="flex flex-col items-center justify-start p-4 text-white">
      <button @click="loadMST" class="codepen-button mb-2">
        <span>Afficher l'ACPM</span>
      </button>
      <div v-if="mstTotalWeight !== null" class="text-sm mt-1">
        Poids total de l’ACPM : 
        <template v-if="mstTotalWeight !== null">
          {{ Math.floor(mstTotalWeight / 3600) }}h 
          {{ Math.floor((mstTotalWeight % 3600) / 60) }}m 
          {{ Math.floor(mstTotalWeight % 60) }}s
        </template>
      </div>
    </div>

    <!-- 🗺️ Carte avec SVG overlay (grande hauteur et largeur) -->
    <div class="relative flex-grow w-full">
      <!-- 🌍 Carte Leaflet -->
      <div id="map" class="absolute inset-0 z-0"></div>

      <!-- 📍 SVG Overlay -->
      <svg id="overlay-svg" class="absolute inset-0 w-full h-full z-10 pointer-events-none">
        <!-- 🔁 Segments du chemin Dijkstra -->
        <line
          v-for="(segment, index) in projectedSegments"
          :key="index"
          :x1="segment.x1"
          :y1="segment.y1"
          :x2="segment.x2"
          :y2="segment.y2"
          :stroke="lineColor(segment.line)"
          stroke-width="4"
        />

        <!-- 🔁 Arêtes de l’ACPM -->
        <line
          v-for="(seg, idx) in getMSTSegments"
          :key="'mst-' + idx"
          :x1="seg.x1"
          :y1="seg.y1"
          :x2="seg.x2"
          :y2="seg.y2"
          :stroke="seg.color"
          stroke-width="2"
        >
          <title>{{ seg.tooltip }}</title>
        </line>

        <!-- ⚪ Stations -->
        <circle
          v-for="station in projectedStations"
          :key="station.id"
          :cx="station.x"
          :cy="station.y"
          r="5"
          :fill="getStationColor(station)"
          stroke="white"
          stroke-width="2"
          fill-opacity="1"
        >
          <title>{{ station.name }} (Ligne {{ station.line }})</title>
        </circle>
      </svg>
    </div>
  </div>
</template>

<style scoped>
/* From Uiverse.io by SelfMadeSystem */ 
/* Yoinked from CodePen, but improved the animation
so that it is smooth among other more minor things */

.codepen-button {
  display: block;
  cursor: pointer;
  color: white;
  margin: 0 auto;
  position: relative;
  text-decoration: none;
  font-weight: 600;
  border-radius: 6px;
  overflow: hidden;
  padding: 3px;
  isolation: isolate;
}

#map,
#overlay-svg {
  width: 100%;
  height: 100%;
  position: absolute;
  inset: 0;
}



circle {
  r: 6;
  stroke: white;
  stroke-width: 2;
  filter: drop-shadow(0 0 1px white) drop-shadow(0 0 3px white);
  transition: r 0.2s;
}

svg {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 1000;
}




.codepen-button::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 400%;
  height: 100%;
  background: linear-gradient(115deg,#4fcf70,#fad648,#a767e5,#12bcfe,#44ce7b);
  background-size: 25% 100%;
  animation: an-at-keyframe-css-at-rule-that-translates-via-the-transform-property-the-background-by-negative-25-percent-of-its-width-so-that-it-gives-a-nice-border-animation_-We-use-the-translate-property-to-have-a-nice-transition-so-it_s-not-a-jerk-of-a-start-or-stop .75s linear infinite;
  animation-play-state: paused;
  translate: -5% 0%;
  transition: translate 0.25s ease-out;
}

.codepen-button:hover::before {
  animation-play-state: running;
  transition-duration: 0.75s;
  translate: 0% 0%;
}

@keyframes an-at-keyframe-css-at-rule-that-translates-via-the-transform-property-the-background-by-negative-25-percent-of-its-width-so-that-it-gives-a-nice-border-animation_-We-use-the-translate-property-to-have-a-nice-transition-so-it_s-not-a-jerk-of-a-start-or-stop {
  to {
    transform: translateX(-25%);
  }
}

.codepen-button span {
  position: relative;
  display: block;
  padding: 1rem 1.5rem;
  font-size: 1.1rem;
  background: #000;
  border-radius: 3px;
  height: 100%;
}
</style>


<script setup>
import { ref, computed, onMounted, watch} from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { nextTick } from 'vue'

const isMapReady = ref(false)
const projectionKey = ref(0)

const props = defineProps({
  stations: Array,
  path: Array,
  edges: Array
})

const mstEdges = ref([])
const mstTotalWeight = ref(null)

// 📌 Carte Leaflet et projecteur
const mapRef = ref(null)
const project = ref(() => ({ x: 0, y: 0 }))



onMounted(() => {
  const map = L.map('map', {
    center: [48.8566, 2.3522],
    zoom: 12,
    zoomControl: false,
    attributionControl: false
  })

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap & CartoDB',
    subdomains: 'abcd',
    maxZoom: 18
  }).addTo(map)

  mapRef.value = map

  const updateProjection = () => {
    project.value = (lat, lon) => {
  const point = map.latLngToContainerPoint([lat, lon])
  return { x: point.x, y: point.y }
  }


    projectionKey.value++
    console.log("🔄 updateProjection called", new Date().toLocaleTimeString())
  }

  // ✅ Appelé sur chaque déplacement (pan)
  map.on('move', () => {
    const pane = map.getPane('overlayPane')
    const svg = document.getElementById('overlay-svg')
    if (svg && pane) {
      const transform = window.getComputedStyle(pane).transform
      svg.style.transform = transform
    }

    updateProjection() // ✅ crucial
  })

  map.on('zoom', updateProjection)
  map.on('resize', updateProjection)

  setTimeout(async () => {
    updateProjection()
    await nextTick()
    isMapReady.value = true
    console.log("✅ Carte prête, projection activée")
  }, 250)
})




// 🎨 Couleurs par ligne
const lineColors = {
  "1": "#FFCD00", "2": "#003CA6", "3": "#837902", "3bis": "#6EC4E8",
  "4": "#CF009E", "5": "#FF7E2E", "6": "#6ECA97", "7": "#FA9ABA", "7bis": "#6EC4E8",
  "8": "#C5A3C5", "9": "#B6BD00", "10": "#C9910D", "11": "#704B1C",
  "12": "#007852", "13": "#6EC4E8", "14": "#62259D"
}

const lineColor = (line) => {
  const first = line?.split(',')[0].trim()
  return lineColors[first] || 'white'
}

// 📍 Stations projetées
const projectedStations = computed(() => {
  projectionKey.value // ❗ dépendance forcée

  if (!mapRef.value || typeof project.value !== 'function') return []

  return props.stations
    .filter(s => typeof s.x === 'number' && typeof s.y === 'number')
    .map(s => {
      const { x, y } = project.value(s.x, s.y)
      return { ...s, x, y }
    })
})




// 🚇 Segments du trajet Dijkstra projetés
const projectedSegments = computed(() => {
  projectionKey.value  // ✅ déclenche recompute

  if (!props.path || props.path.length < 2) return []
  const segments = []

  for (let i = 0; i < props.path.length - 1; i++) {
    const fromId = props.path[i]
    const toId = props.path[i + 1]

    const from = props.stations.find(s => s.id === fromId)
    const to = props.stations.find(s => s.id === toId)
    if (!from || !to) continue

    const edge = props.edges.find(e =>
      (e.from === fromId && e.to === toId) ||
      (e.from === toId && e.to === fromId)
    )

    const line = (edge?.line || '?').split(',')[0].trim()
    const p1 = project.value(from.x, from.y) // ✅ appel correct
    const p2 = project.value(to.x, to.y)

    segments.push({
      line,
      x1: p1.x,
      y1: p1.y,
      x2: p2.x,
      y2: p2.y
    })
  }

  return segments
})


// 🧠 Ligne utilisée dans le trajet par station
const pathLineByStation = computed(() => {
  const map = {}
  for (let i = 0; i < props.path.length - 1; i++) {
    const fromId = props.path[i]
    const toId = props.path[i + 1]
    const edge = props.edges.find(e =>
      (e.from === fromId && e.to === toId) ||
      (e.from === toId && e.to === fromId)
    )
    const line = (edge?.line || '?').split(',')[0].trim()
    map[fromId] = line
    map[toId] = line
  }
  return map
})

// 🎨 Couleur des stations selon la ligne réellement empruntée
const getStationColor = (station) => {
  const stationId = String(station.id)
  if (!props.path || !props.path.includes(stationId)) return 'gray'
  const line = pathLineByStation.value[stationId]
  return lineColors[line] || 'white'
}

// 🧱 Segments ACPM projetés
const getMSTSegments = computed(() => {
  projectionKey.value  // ✅ pour forcer la mise à jour sur déplacement

  return mstEdges.value.map(({ src, dst, line, weight, name1, name2 }) => {
    const s1 = props.stations.find(s => s.id === src)
    const s2 = props.stations.find(s => s.id === dst)
    if (!s1 || !s2) return null

    const p1 = project.value(s1.x, s1.y)
    const p2 = project.value(s2.x, s2.y)

    return {
      x1: p1.x,
      y1: p1.y,
      x2: p2.x,
      y2: p2.y,
      color: lineColor(line),
      tooltip: `${name1} ↔ ${name2}\nLigne ${line}\n${weight} sec`
    }
  }).filter(Boolean)
})



// 📦 Requête pour récupérer l'ACPM
const loadMST = async () => {
  mstEdges.value = []
  mstTotalWeight.value = null

  try {
    const res = await fetch('http://127.0.0.1:5000/mst')
    const data = await res.json()
    const edges = data.edges
    mstTotalWeight.value = data.total_weight

    for (let [src, dst, weight] of edges) {
      const s1 = props.stations.find(s => s.id === src)
      const s2 = props.stations.find(s => s.id === dst)
      let line = null
      if (s1 && s2) line = s1.line === s2.line ? s1.line : (s1.line || s2.line)

      mstEdges.value.push({
        src,
        dst,
        weight,
        line,
        name1: s1?.name || src,
        name2: s2?.name || dst
      })

      await new Promise(r => setTimeout(r, 50)) // animation progressive
    }
  } catch (e) {
    alert("Erreur lors du chargement de l'ACPM.")
  }
}








watch(projectedStations, (val) => {
  console.log("📍 Stations projetées :", val.slice(0, 3)) // pour voir les 3 premières
})



</script>