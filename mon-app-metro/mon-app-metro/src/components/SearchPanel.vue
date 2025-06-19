<template>
  <div class="bg-gray-800 p-4 rounded shadow">
    <label class="block mb-2">Départ</label>
    <select v-model="start" class="w-full p-2 mb-4 rounded bg-gray-700 text-white">
      <option disabled value="">Choisir une station...</option>
      <option v-for="station in stations" :key="station.id" :value="station.id">
        {{ station.name }} (Ligne {{ station.line }})
      </option>
    </select>

    <label class="block mb-2">Arrivée</label>
    <select v-model="end" class="w-full p-2 mb-4 rounded bg-gray-700 text-white">
      <option disabled value="">Choisir une station...</option>
      <option v-for="station in stations" :key="station.id + '_end'" :value="station.id">
        {{ station.name }} (Ligne {{ station.line }})
      </option>
    </select>

    <button
      class="w-full bg-blue-600 hover:bg-blue-700 p-2 rounded"
      @click="fetchPath"
      :disabled="!start || !end"
    >
      Rechercher
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  stations: Array
})

const emit = defineEmits(['path-calculated'])

const start = ref('')
const end = ref('')

const fetchPath = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/shortest-path', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        source: start.value,
        destination: end.value
      })
    })

    const data = await response.json()
    if (data.path) {
      emit('path-calculated', {
        path: data.path,
        total_time: data.total_time
      })
    } else {
      alert('Erreur : aucun chemin trouvé.')
    }
  } catch (err) {
    console.error("Erreur de connexion à l'API :", err)
    alert('Connexion au serveur impossible.')
  }
}
</script>
