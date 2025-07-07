<template>
  <div class="text-white p-6">
    <h2 class="text-xl font-semibold mb-4">Films DataGouv (extrait)</h2>

    <ul class="space-y-2">
      <li v-for="film in films" :key="film.__id" class="bg-gray-800 p-4 rounded">
        🎬 {{ film["Titre de l'œuvre"] }} ({{ film["Date de sortieau cinéma"] }})
        <br />
        Réalisateur : {{ film["Réalisateur"] }}
      </li>
    </ul>

    <div class="mt-4 text-sm text-gray-400">
      Page {{ meta.page }} / {{ totalPages }}
    </div>

    <div class="mt-4 flex gap-2">
      <button @click="prevPage" :disabled="meta.page <= 1" class="bg-blue-600 px-4 py-2 rounded">⬅ Précédent</button>
      <button @click="nextPage" :disabled="meta.page >= totalPages" class="bg-blue-600 px-4 py-2 rounded">Suivant ➡</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const films = ref([])
const meta = ref({ page: 1, page_size: 20, total: 0 })
const rid = '1c5075ec-7ce1-49cb-ab89-94f507812daf' // exemple

const fetchFilms = async () => {
  const url = `https://tabular-api.data.gouv.fr/api/resources/${rid}/data/?page=${meta.value.page}`
  const res = await fetch(url)
  const json = await res.json()
  films.value = json.data
  meta.value = json.meta
}

onMounted(fetchFilms)

const totalPages = computed(() =>
  Math.ceil(meta.value.total / meta.value.page_size)
)

const nextPage = () => {
  if (meta.value.page < totalPages.value) {
    meta.value.page++
    fetchFilms()
  }
}

const prevPage = () => {
  if (meta.value.page > 1) {
    meta.value.page--
    fetchFilms()
  }
}
</script>
