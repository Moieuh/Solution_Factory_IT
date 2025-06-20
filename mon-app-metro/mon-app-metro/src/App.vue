<template>
  <div class="min-h-screen bg-gray-900 text-white flex">
    <aside class="w-1/3 p-6 bg-gray-800 flex flex-col gap-6">
      <h1 class="text-2xl font-bold mb-4">Itinéraire Métro</h1>
      <SearchPanel :stations="stations" @path-calculated="updatePath" />

      <div v-if="path.length && stations.length">
        <p class="mt-4 text-green-400">
          Temps estimé : {{ formatTime(totalTime) }}
        </p>
        <div class="mt-6">
  <div v-for="(stationId, index) in path" :key="stationId" class="flex items-start">
  <!-- Ligne verticale + cercle -->
  <div class="flex flex-col items-center">
    <div
      class="w-4 h-4 rounded-full z-10"
      :style="{ backgroundColor: lineColor(stationLine(stationId)) }"
    ></div>
    <div
      v-if="index < path.length - 1"
      class="w-px h-6 bg-gray-400"
    ></div>
  </div>

  <!-- Infos station -->
  <div class="ml-4">
    <p class="text-sm">
      {{ stationName(stationId) }}
      <span
        class="ml-2 font-semibold"
        :style="{ color: lineColor(stationLine(stationId)) }"
      >
        (Ligne {{ stationLine(stationId) }})
      </span>
    </p>

    <div v-if="index < path.length - 1 && stationLine(stationId) !== stationLine(path[index + 1])">
      <p class="text-yellow-400 text-xs mt-1">
        ↪ Correspondance : Ligne {{ stationLine(stationId) }} → Ligne {{ stationLine(path[index + 1]) }}
      </p>
    </div>
  </div>
</div>

</div>


      </div>
    </aside>

    <main class="flex-1 overflow-auto bg-black flex justify-center items-start p-4">
      <div class="scale-[0.8] origin-top-left w-[950px]">
        <MetroGraph :stations="stations" :path="path" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import SearchPanel from './components/SearchPanel.vue'
import MetroGraph from './components/MetroGraph.vue'

const stations = ref([])
const path = ref([])
const totalTime = ref(null)

onMounted(async () => {
  const response = await fetch('/stations.json')
  stations.value = await response.json()
})

const updatePath = (result) => {
  path.value = result.path
  totalTime.value = result.total_time
}

const stationName = (id) => {
  const s = stations.value.find(st => st.id === id)
  return s ? s.name : id
}

const stationLine = (id) => {
  const s = stations.value.find(st => st.id === id)
  return s ? s.line : '?'
}

const formatTime = (seconds) => {
  const min = Math.floor(seconds / 60)
  const sec = seconds % 60
  return `${min} min ${sec.toString().padStart(2, '0')} s`
}



const lineColor = (line) => {
  const colors = {
  "1":  "#FFCE00",  // Jaune
  "2":  "#0064B0",  // Bleu foncé
  "3":  "#9F9825",  // Vert olive
  "3bis": "#98D4E2", // Bleu clair
  "4":  "#C04191",  // Rose fuchsia
  "5":  "#F28E42",  // Orange
  "6":  "#83C491",  // Vert clair
  "7":  "#F3A4BA",  // Rose
  "7bis": "#83C491", // Même couleur que la 6 (vert clair)
  "8":  "#CEADD2",  // Violet pâle
  "9":  "#D5C900",  // Jaune citron
  "10": "#E3B32A",  // Jaune orangé
  "11": "#8E5E25",  // Marron
  "12": "#00814F",  // Vert foncé
  "13": "#98D4E2",  // Bleu clair
  "14": "#662483",  // Violet foncé
};
  return colors[line] || "#CCCCCC"  // gris par défaut
}

</script>
