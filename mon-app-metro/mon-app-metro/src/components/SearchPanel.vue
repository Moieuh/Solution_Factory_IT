<script setup>
import { ref, computed } from 'vue'

const start = ref('')
const end = ref('')

const startQuery = ref('')
const endQuery = ref('')

const props = defineProps({
  stations: Array
})

const emit = defineEmits(['path-calculated'])

const groupedStations = (query, excludeId = null) => {
  const groups = {}
  const lowercaseQuery = query.toLowerCase()

  props.stations.forEach(station => {
    if (excludeId && station.id === excludeId) return

    const matches = station.name.toLowerCase().includes(lowercaseQuery)
    if (!matches) return

    const lines = station.line?.split(',').map(l => l.trim()) || ['?']

    for (const line of lines) {
      if (!groups[line]) groups[line] = []

      groups[line].push({
        ...station,
        line, // ⬅️ remplace par la ligne spécifique
        id: `${station.id}__${line}` // ⬅️ rend chaque option unique
      })
    }
  })

  return groups
}
const filteredStartStations = computed(() => groupedStations(startQuery.value))
const filteredEndStations = computed(() => groupedStations(endQuery.value, start.value))

const extractRealId = (val) => val.split('__')[0]

// Ajout pour afficher l'heure d'arrivée estimée
const estimatedArrival = ref(null)
const estimatedDuration = ref(null)
const showDepartureInput = ref(false)
const desiredArrival = ref('')
const computedDeparture = ref(null)

const fetchPath = async () => {
  if (!start.value || !end.value) return

  // Appel l'API pour obtenir le chemin et la durée
  const source = extractRealId(start.value)
  const destination = extractRealId(end.value)
  try {
    const res = await fetch('http://127.0.0.1:5000/shortest-path', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source, destination })
    })
    const data = await res.json()
    if (data.path && data.total_time != null) {
      // Heure de départ actuelle
      const now = new Date()
      // Ajoute la durée du trajet (en secondes)
      const arrival = new Date(now.getTime() + data.total_time * 1000)
      estimatedArrival.value = arrival.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      estimatedDuration.value = data.total_time
      // Émet le chemin pour le parent
      emit('path-calculated', {
        source,
        destination,
        path: data.path,
        total_time: data.total_time
      })
    } else {
      estimatedArrival.value = null
      estimatedDuration.value = null
      computedDeparture.value = null
      emit('path-calculated', { source, destination, path: [], total_time: null })
    }
  } catch (e) {
    estimatedArrival.value = null
    estimatedDuration.value = null
    computedDeparture.value = null
    emit('path-calculated', { source, destination, path: [], total_time: null })
  }
}

const computeDepartureTime = () => {
  if (!desiredArrival.value || !estimatedDuration.value) return
  // desiredArrival au format "HH:mm"
  const [h, m] = desiredArrival.value.split(':').map(Number)
  const arrivalDate = new Date()
  arrivalDate.setHours(h, m, 0, 0)
  // Soustraire la durée du trajet (en secondes)
  const departureDate = new Date(arrivalDate.getTime() - estimatedDuration.value * 1000)
  computedDeparture.value = departureDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="bg-gray-800 p-4 rounded shadow space-y-6">

    <!-- Départ -->
    <div>
      <label class="block mb-1 text-sm font-semibold">🔹 Station de départ</label>
      <input
        v-model="startQuery"
        type="text"
        placeholder="Rechercher une station..."
        class="w-full p-2 mb-2 rounded bg-gray-700 text-white placeholder-gray-400"
      />
      <select v-model="start" class="w-full p-2 rounded bg-gray-700 text-white">
        <option disabled value="">-- Choisir une station --</option>
        <optgroup
          v-for="(stations, line) in filteredStartStations"
          :key="'start-group-' + line"
          :label="'Ligne ' + line"
        >
          <option
            v-for="station in stations"
            :key="'start-' + station.id"
            :value="station.id"
          >
            {{ station.name }}
          </option>
        </optgroup>
      </select>
    </div>

    <!-- Arrivée -->
    <div>
      <label class="block mb-1 text-sm font-semibold">🔸 Station d'arrivée</label>
      <input
        v-model="endQuery"
        type="text"
        placeholder="Rechercher une station..."
        class="w-full p-2 mb-2 rounded bg-gray-700 text-white placeholder-gray-400"
      />
      <select v-model="end" class="w-full p-2 rounded bg-gray-700 text-white">
        <option disabled value="">-- Choisir une station --</option>
        <optgroup
          v-for="(stations, line) in filteredEndStations"
          :key="'end-group-' + line"
          :label="'Ligne ' + line"
        >
          <option
            v-for="station in stations"
            :key="'end-' + station.id"
            :value="station.id"
          >
            {{ station.name }}
          </option>
        </optgroup>
      </select>
    </div>

    <button
      class="w-full bg-blue-600 hover:bg-blue-700 p-2 rounded font-semibold"
      @click="fetchPath"
      :disabled="!start || !end"
    >
      🔍 Rechercher
    </button>

    <!-- Affiche toujours le bloc Heure d'arrivée estimée, même si pas encore calculée -->
    <div class="mt-4 text-green-400 text-center">
      Heure d'arrivée estimée :
      <span class="font-bold">
        {{ estimatedArrival ? estimatedArrival : '--:--' }}
      </span>
    </div>

    <div v-if="showDepartureInput" class="mt-4">
      <label class="block mb-2 text-white">Heure d'arrivée souhaitée :</label>
      <input
        type="time"
        v-model="desiredArrival"
        class="w-full p-2 rounded bg-gray-700 text-white"
      />
      <button
        class="mt-2 w-full bg-purple-600 hover:bg-purple-700 p-2 rounded font-semibold"
        @click="computeDepartureTime"
        :disabled="!desiredArrival || !estimatedDuration"
      >
        Calculer l'heure de départ
      </button>
      <div v-if="computedDeparture" class="mt-2 text-blue-300 text-center">
        Heure de départ recommandée : <span class="font-bold">{{ computedDeparture }}</span>
      </div>
    </div>

    <button
      class="mt-4 w-full bg-gray-700 hover:bg-gray-600 p-2 rounded text-sm"
      @click="showDepartureInput = !showDepartureInput"
      v-if="estimatedDuration"
    >
      {{ showDepartureInput ? 'Masquer' : 'Déduire l\'heure de départ à partir de l\'heure d\'arrivée' }}
    </button>
  </div>
</template>
