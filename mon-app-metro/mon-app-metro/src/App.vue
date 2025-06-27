<template>
  <div class="min-h-screen bg-gray-900 text-white flex">
    <aside class="w-1/3 p-6 bg-gray-800 flex flex-col gap-6">
      <h1 class="text-2xl font-bold mb-4">Itinéraire Métro</h1>

      <!-- ⚠️ Modifié ici -->
      <SearchPanel :stations="stations" @path-calculated="checkAndCalculatePath" />

      <div v-if="path.length && stations.length">
        <p class="mt-4 text-green-400">
          Temps estimé : {{ formatTime(totalTime) }}
        </p>
        <div class="mt-6">
          <div
            v-for="(stationId, index) in path"
            :key="stationId"
            class="flex items-start"
          >
            <!-- Ligne verticale + cercle -->
            <div class="flex flex-col items-center">
              <div
                class="w-4 h-4 rounded-full z-10"
                :style="{ backgroundColor: lineColor(stationLine(stationId)) }"
              ></div>
              <div v-if="index < path.length - 1" class="w-px h-6 bg-gray-400"></div>
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

              <div
                v-if="index < path.length - 1 && stationLine(stationId) !== stationLine(path[index + 1])"
              >
                <p class="text-yellow-400 text-xs mt-1">
                  ↪ Correspondance : Ligne {{ stationLine(stationId) }} → Ligne
                  {{ stationLine(path[index + 1]) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <button
          class="mt-4 bg-purple-600 hover:bg-purple-700 p-2 rounded"
          @click="testCheckPath"
          :disabled="checkPathResult === false"
        >
          Vérifier chemin d'exemple ({{ stationName(path[0]) }} → {{ stationName(path[path.length - 1]) }})
        </button>

        <div v-if="checkPathResult !== null" class="mt-2 text-sm">
          Chemin connecté :
          <span :class="checkPathResult ? 'text-green-400' : 'text-red-400'">
            {{ checkPathResult ? 'Oui' : 'Non' }}
          </span>
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
const checkPathResult = ref(null)

onMounted(async () => {
  const response = await fetch('/stations.json')
  stations.value = await response.json()
})

// ✅ Vérifie si le graphe est connexe
const checkConnectivity = async () => {
  try {
    const res = await fetch('http://127.0.0.1:5000/check_connectivity')
    const data = await res.json()
    checkPathResult.value = data.connected
    return data.connected
  } catch (e) {
    checkPathResult.value = null
    console.error(e)
    alert("Erreur lors de la vérification de la connectivité du graphe.")
    return false
  }
}

// ✅ Vérifie d'abord la connectivité avant d'accepter un chemin
const checkAndCalculatePath = async (result) => {
  const isConnected = await checkConnectivity()
  if (isConnected) {
    path.value = result.path
    totalTime.value = result.total_time
  } else {
    path.value = []
    totalTime.value = null
    alert("Le graphe n'est pas connexe. Impossible de calculer un itinéraire.")
  }
}

// 🧪 Test manuel du graphe via bouton
const testCheckPath = async () => {
  await checkConnectivity()
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
    "1": "#FFCE00",
    "2": "#0064B0",
    "3": "#9F9825",
    "3bis": "#98D4E2",
    "4": "#C04191",
    "5": "#F28E42",
    "6": "#83C491",
    "7": "#F3A4BA",
    "7bis": "#83C491",
    "8": "#CEADD2",
    "9": "#D5C900",
    "10": "#E3B32A",
    "11": "#8E5E25",
    "12": "#00814F",
    "13": "#98D4E2",
    "14": "#662483"
  }
  return colors[line] || "#CCCCCC"
}
</script>
