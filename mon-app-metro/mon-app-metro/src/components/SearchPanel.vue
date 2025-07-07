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

const fetchPath = () => {
  if (!start.value || !end.value) return

  emit('path-calculated', {
    source: extractRealId(start.value),
    destination: extractRealId(end.value)
  })
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
  </div>
</template>
