<script setup>
import { ref } from 'vue'

const start = ref('')
const end = ref('')

const props = defineProps({
  stations: Array
})

const emit = defineEmits(['path-calculated'])

const fetchPath = () => {
  console.log("🔍 Départ sélectionné :", start.value)
  console.log("🔍 Arrivée sélectionnée :", end.value)

  emit('path-calculated', {
    source: start.value,
    destination: end.value
  })
}
</script>

<template>
  <div class="bg-gray-800 p-4 rounded shadow">
    <label class="block mb-2">Départ</label>
    <select v-model="start" class="w-full p-2 mb-4 rounded bg-gray-700 text-white">
      <option disabled value="">Choisir une station...</option>
      <option
        v-for="station in stations"
        :key="station.id"
        :value="station.id"
      >
        {{ station.name }} (Ligne {{ station.line }})
      </option>
    </select>

    <label class="block mb-2">Arrivée</label>
    <select v-model="end" class="w-full p-2 mb-4 rounded bg-gray-700 text-white">
      <option disabled value="">Choisir une station...</option>
      <option
        v-for="station in stations"
        :key="station.id + '_end'"
        :value="station.id"
      >
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
