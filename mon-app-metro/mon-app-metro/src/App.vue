<script setup>
import { ref, onMounted } from 'vue'
import SearchPanel from './components/SearchPanel.vue'
import MetroGraph from './components/MetroGraph.vue'
import runDijkstra from './utils/rundijkstra.js' 
import runDijkstraTimeAware from './utils/runDijkstra.js'


const stations = ref([])
const edges = ref([])
const path = ref([])
const totalTime = ref(null)
const checkPathResult = ref(null)
const arrivalTimes = ref({})
const steps = ref([])




onMounted(async () => {
  const response = await fetch('/graphe_metro_v2.json')
  const data = await response.json()

  edges.value = data.edges

  stations.value = data.nodes.map(station => ({
    id: station.id,
    name: station.name,
    line: station.line,
    x: station.x ?? 0,
    y: station.y ?? 0
  }))

  console.log("✅ Exemple ID de station :", stations.value[0]?.id)
  console.log("✅ Exemple arête :", edges.value[0])
})

const checkConnectivity = async () => {
  try {
    const res = await fetch('http://127.0.0.1:5000/check_connectivity')
    const data = await res.json()
    checkPathResult.value = data.connected
    return data.connected
  } catch (e) {
    checkPathResult.value = null
    console.error(e)
    alert("Erreur de connexion au serveur Flask.")
    return false
  }
}

const checkAndCalculatePath = async ({ source, destination }) => {
  console.log("🔎 Vérification ID valides ?")
  console.log("source existe ? ", stations.value.find(s => s.id === source))
  console.log("destination existe ? ", stations.value.find(s => s.id === destination))
  


  const isConnected = await checkConnectivity()
  if (isConnected) {
    const { path: shortestPath, total, steps: usedSteps } = runDijkstraTimeAware(
  stations.value,
  edges.value,
  source,
  destination
)
console.log("🔍 Étapes avec lignes :", usedSteps.map(s => ({ to: s.to, line: s.line })))
steps.value = usedSteps
path.value = shortestPath
totalTime.value = total

    // 🟡 Ajoute ces logs de vérification ici :
    console.log("✅ Trajet calculé :", shortestPath)
    console.log("🎯 Tous les IDs trouvés :", shortestPath)
    console.log("📍 Tous les station IDs connus :", stations.value.map(s => s.id))

    path.value = shortestPath
    totalTime.value = total
  } else {
    path.value = []
    totalTime.value = null
    alert("Le graphe n'est pas connexe.")
  }

}



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
    "1": "#FFCE00", "2": "#0064B0", "3": "#9F9825", "3bis": "#98D4E2",
    "4": "#C04191", "5": "#F28E42", "6": "#83C491", "7": "#F3A4BA", "7bis": "#83C491",
    "8": "#CEADD2", "9": "#D5C900", "10": "#E3B32A", "11": "#8E5E25", "12": "#00814F",
    "13": "#98D4E2", "14": "#662483"
  }

  if (!line || line === "?") return "#CCCCCC"

  const firstLine = line.split(",")[0].trim()
  return colors[firstLine] || "#CCCCCC"
}




const stepLine = (stationId, index) => {
  if (index === 0) return null;
  const step = steps.value.find(s => s.to === stationId);
  return step?.line || "?";
}

</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white flex">
    <aside class="w-1/3 p-6 bg-gray-800 flex flex-col gap-6">
      <h1 class="text-2xl font-bold mb-4">Itinéraire Métro</h1>

      <SearchPanel :stations="stations" @path-calculated="checkAndCalculatePath" />

      <div v-if="path.length && stations.length">
        <p class="mt-4 text-green-400">
          Temps estimé : {{ formatTime(totalTime) }}
        </p>

        <div class="mt-6">
  <div
    v-for="(step, index) in steps"
    :key="step.to"
    class="flex items-start gap-2 mb-3"
  >
    <!-- Point + ligne -->
    <div class="flex flex-col items-center">
      <div
        class="w-4 h-4 rounded-full"
        :style="{ backgroundColor: lineColor(step.line) }"
      ></div>
      <div v-if="index < steps.length - 1" class="w-px h-6 bg-gray-500"></div>
    </div>

    <!-- Infos station -->
    <div>
      <p class="text-sm font-medium">
        {{ stationName(step.to) }}
        <span class="ml-2 font-semibold" :style="{ color: lineColor(step.line) }">
          (Ligne {{ step.line || '?' }})
        </span>
      </p>
      <p class="text-xs text-gray-400 font-mono">
        Arrivée : {{ formatTime(step.arrival) }}
      </p>

      <!-- Correspondance -->
      <p
        v-if="index < steps.length - 1 && step.line !== steps[index + 1].line"
        class="text-yellow-400 text-xs mt-1"
      >
        ↪ Correspondance : Ligne {{ step.line }} → Ligne {{ steps[index + 1].line }}
      </p>
    </div>
  </div>
</div>



        <button
          class="mt-4 bg-purple-600 hover:bg-purple-700 p-2 rounded"
          @click="testCheckPath"
          :disabled="checkPathResult === false"
        >
          Vérifier chemin ({{ stationName(steps[0]?.from || '') }} → {{ stationName(steps.at(-1)?.to || '') }})
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
