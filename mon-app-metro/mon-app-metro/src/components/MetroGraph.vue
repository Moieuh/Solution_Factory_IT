<template>
  <div class="flex justify-end mb-2">
    <div class="w-full flex justify-center">
      <button
        @click="loadMST"
        class="codepen-button"
      >
        <span>Afficher l'ACPM</span>
      </button>
      <div v-if="mstTotalWeight !== null" class="text-center text-white mt-2">
  Poids total de l’ACPM : {{ mstTotalWeight }} secondes
</div>


    </div>
  </div>
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
    <!-- 🔁 Arêtes de l’ACPM -->
    <line
      v-for="(segment, idx) in getMSTSegments"
      :key="'mst-' + idx"
      :x1="segment.split(' ')[0].split(',')[0]"
      :y1="segment.split(' ')[0].split(',')[1]"
      :x2="segment.split(' ')[1].split(',')[0]"
      :y2="segment.split(' ')[1].split(',')[1]"
      stroke="#00ccff"
      stroke-width="2"
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
  path: Array // pour les trajets Dijkstra
})

const width = 950
const height = 1000

const mstEdges = ref([])
const mstTotalWeight = ref(null)

// 🔁 Rechercher les coordonnées des deux stations liées par une arête
const getMSTSegments = computed(() => {
  return mstEdges.value.map(([src, dst]) => {
    const s1 = props.stations.find(s => s.id === src)
    const s2 = props.stations.find(s => s.id === dst)
    if (!s1 || !s2) return null
    return `${s1.x},${s1.y} ${s2.x},${s2.y}`
  }).filter(Boolean)
})

const lineColor = (line) => {
  const colors = {
    "1": "#FFCE00", "2": "#0064B0", "3": "#9F9825", "3bis": "#98D4E2",
    "4": "#C04191", "5": "#F28E42", "6": "#83C491", "7": "#F3A4BA",
    "7bis": "#83C491", "8": "#CEADD2", "9": "#D5C900", "10": "#E3B32A",
    "11": "#8E5E25", "12": "#00814F", "13": "#98D4E2", "14": "#662483",
  }
  return colors[line] || "#FF0000"
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

// Chargement progressif de l'ACPM
const loadMST = async () => {
  mstEdges.value = []
  mstTotalWeight.value = null

  try {
    const res = await fetch('http://127.0.0.1:5000/mst')
    const data = await res.json()
    const edges = data.edges
    mstTotalWeight.value = data.total_weight

    // Animation progressive des arêtes
    for (let i = 0; i < edges.length; i++) {
      mstEdges.value.push([edges[i][0], edges[i][1]])
      await new Promise(r => setTimeout(r, 50)) // 50ms entre chaque trait
    }
  } catch (e) {
    alert("Erreur lors du chargement de l'ACPM.")
  }
}
</script>
