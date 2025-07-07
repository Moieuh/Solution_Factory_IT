<template>
  <!-- Bouton -->
  <div class="flex justify-end mb-2">
    <div class="w-full flex justify-center">
      <button @click="loadMST" class="codepen-button">
        <span>Afficher l'ACPM</span>
      </button>
    </div>
  </div>

  <!-- Poids total -->
  <div v-if="mstTotalWeight !== null" class="text-center text-white mt-2">
    Poids total de l’ACPM : {{ mstTotalWeight }} secondes
  </div>

  <!-- Plan SVG -->
  <svg class="w-full h-auto" :viewBox="'0 0 ' + width + ' ' + height">
    <!-- Image de fond -->

    <!-- 🔁 Segments du chemin Dijkstra (par ligne) -->
    <polyline
      v-for="(segment, index) in getSegmentsByLine()"
      :key="index"
      :points="segment.points"
      fill="none"
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
import { ref, computed } from 'vue'

const props = defineProps({
  stations: Array,
  path: Array,
  edges: Array  // nécessaire pour getSegmentsByLine
})

const width = 950
const height = 1000

const mstEdges = ref([])
const mstTotalWeight = ref(null)

// 🎨 Couleurs par ligne
const lineColor = (line) => {
  const colors = {
    "1": "#FFCE00", "2": "#0064B0", "3": "#9F9825", "3bis": "#98D4E2",
    "4": "#C04191", "5": "#F28E42", "6": "#83C491", "7": "#F3A4BA",
    "7bis": "#83C491", "8": "#CEADD2", "9": "#D5C900", "10": "#E3B32A",
    "11": "#8E5E25", "12": "#00814F", "13": "#98D4E2", "14": "#662483",
  }
  return colors[line] || "#FF0000"
}

// 🔁 Segments à dessiner pour l’ACPM (x1,y1,x2,y2, couleur)
const getMSTSegments = computed(() => {
  return mstEdges.value.map(({ src, dst, line, weight, name1, name2 }) => {
    const s1 = props.stations.find(s => s.id === src)
    const s2 = props.stations.find(s => s.id === dst)
    if (!s1 || !s2) return null
    return {
      x1: s1.x, y1: s1.y,
      x2: s2.x, y2: s2.y,
      color: lineColor(line),
      tooltip: `${name1} ↔ ${name2}\nLigne ${line}\n${weight} sec`
    }
  }).filter(Boolean)
})


// 🔁 Segments pour les trajets Dijkstra
const getSegmentsByLine = () => {
  if (!props.path || props.path.length < 2 || !props.stations.length) return []

  const segments = []
  for (let i = 0; i < props.path.length - 1; i++) {
    const fromId = props.path[i]
    const toId = props.path[i + 1]

    const fromStation = props.stations.find(s => s.id === fromId)
    const toStation = props.stations.find(s => s.id === toId)

    if (!fromStation || !toStation) continue

    // Trouver l'arête utilisée
    const edge = props.edges?.find(e => e.from === fromId && e.to === toId)
    const line = edge?.line || '?'

    segments.push({
      line,
      points: `${fromStation.x},${fromStation.y} ${toStation.x},${toStation.y}`
    })
  }

  return segments
}


// 📡 Appel à l'API /mst
const loadMST = async () => {
  mstEdges.value = []
  mstTotalWeight.value = null

  try {
    const res = await fetch('http://127.0.0.1:5000/mst')
    const data = await res.json()
    const edges = data.edges // [src, dst, weight]
    mstTotalWeight.value = data.total_weight

    for (let i = 0; i < edges.length; i++) {
      const [src, dst, weight] = edges[i]
      const s1 = props.stations.find(s => s.id === src)
      const s2 = props.stations.find(s => s.id === dst)

      let line = null
      if (s1 && s2) {
        line = s1.line === s2.line ? s1.line : (s1.line || s2.line)
      }

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

</script>
