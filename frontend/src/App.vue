<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="max-w-7xl mx-auto px-4">
      <h1 class="text-4xl font-bold text-center mb-10">Astrology Chart Generator</h1>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- Left Column: Form + Saved Charts -->
        <div class="lg:col-span-7 space-y-8">
          <!-- Birth Data Form -->
          <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-b-gray-200 text-lg font-semibold bg-gray-50">
              Enter Birth Data
            </div>

            <form @submit.prevent="generateChart" class="p-6 space-y-6">
              <div class="mb-4 text-gray-700 text-sm">
                Name
                <InputText v-model="formData.name" placeholder="Full Name" class="w-full" fluid />
              </div>

              <div class="grid grid-cols-3 gap-4">
                <div class="col-span-1 text-gray-700 text-sm">
                  Day of Birth
                  <InputNumber v-model="formData.day" placeholder="Day" :min="1" :max="31" fluid />
                </div>

                <div class="col-span-1 text-gray-700 text-sm">
                  Month of Birth
                  <InputNumber
                    v-model="formData.month"
                    placeholder="Month"
                    :min="1"
                    :max="12"
                    fluid
                  />
                </div>

                <div class="col-span-1 text-gray-700 text-sm">
                  Year of Birth
                  <InputNumber v-model="formData.year" placeholder="Year" :min="1500" fluid />
                </div>

                <div class="col-span-1 text-gray-700 text-sm">
                  Hour of Birth
                  <InputNumber
                    v-model="formData.hour"
                    placeholder="Hour"
                    :min="0"
                    :max="23"
                    fluid
                  />
                </div>

                <div class="col-span-1 text-gray-700 text-sm">
                  Minute of Birth
                  <InputNumber
                    v-model="formData.minute"
                    placeholder="Minute"
                    :min="0"
                    :max="59"
                    fluid
                  />
                </div>

                <div class="col-span-1 text-gray-700 text-sm">
                  Timezone
                  <InputText
                    v-model="formData.tz_str"
                    placeholder="Timezone (e.g. Europe/Rome)"
                    fluid
                  />
                </div>

                <div class="col-span-1 text-gray-700 text-sm">
                  House System
                  <InputText
                    v-model="formData.houses_system"
                    placeholder="Houses System (e.g., P)"
                    fluid
                  />
                </div>

                <div class="col-span-1 text-gray-700 text-sm">
                  Latitude
                  <InputNumber
                    v-model="formData.lat"
                    :format="false"
                    :maxFractionDigits="6"
                    placeholder="Latitude"
                    :min="-90"
                    :max="90"
                    fluid
                  />
                </div>

                <div class="col-span-1 text-gray-700 text-sm">
                  Longitude
                  <InputNumber
                    v-model="formData.lng"
                    :format="false"
                    :maxFractionDigits="6"
                    placeholder="Longitude"
                    :min="-180"
                    :max="180"
                    fluid
                  />
                </div>

                <div class="col-span-1 text-gray-700 text-sm">
                  City
                  <InputText v-model="formData.city" placeholder="City" fluid />
                </div>

                <div class="col-span-1 text-gray-700 text-sm">
                  Country
                  <InputText v-model="formData.nation" placeholder="Country Code eg. AU" fluid />
                </div>
              </div>

              <div class="flex gap-4">
                <Button
                  type="submit"
                  label="Generate Chart"
                  :loading="loading"
                  class="flex-1"
                  icon="pi pi-chart-line"
                />
                <Button
                  type="button"
                  label="Save to Library"
                  @click="saveCurrent"
                  severity="success"
                  class="flex-1"
                  icon="pi pi-save"
                />
              </div>
            </form>
          </div>

          <!-- Saved Birth Charts (unchanged) -->
          <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            <div
              class="px-6 py-4 border-b border-b-gray-200 flex justify-between items-center bg-gray-50"
            >
              <span class="text-lg font-semibold">Saved Birth Charts</span>
              <Button label="Refresh List" icon="pi pi-refresh" @click="loadPersons" size="small" />
            </div>
            <div class="p-6">
              <DataTable :value="persons" :loading="loadingPersons" class="p-datatable-sm">
                <Column field="name" header="Name"></Column>
                <Column field="date" header="Birth Date"></Column>
                <Column field="city" header="Location"></Column>
                <Column header="Actions" style="width: 200px">
                  <template #body="slotProps">
                    <Button
                      label="Load"
                      icon="pi pi-folder-open"
                      severity="secondary"
                      size="small"
                      @click="loadPerson(slotProps.data.id)"
                      class="mr-2"
                    />
                    <Button
                      label="Delete"
                      icon="pi pi-trash"
                      severity="danger"
                      size="small"
                      @click="deletePerson(slotProps.data.id)"
                    />
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>
        </div>

        <!-- Right Column: Chart Display (unchanged) -->
        <div class="lg:col-span-5">
          <div
            class="bg-white rounded-xl shadow-lg border border-gray-200 p-8 min-h-[600px] flex flex-col items-center justify-center sticky top-8"
          >
            <div v-if="svgUrl" class="w-full flex flex-col items-center">
              <img
                :src="svgUrl"
                :key="svgUrl"
                alt="Birth Chart"
                class="max-w-full h-auto border border-gray-200 rounded-xl shadow-md mb-6"
              />
              <Button
                label="View Full Screen"
                icon="pi pi-external-link"
                @click="showFullScreen = true"
                severity="secondary"
              />
            </div>

            <div v-else class="text-center text-gray-400">
              <i class="pi pi-chart-line text-6xl mb-4"></i>
              <p class="text-xl">Your birth chart will appear here</p>
              <p class="text-sm mt-2">Fill the form and click Generate Chart</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Full Screen Chart Dialog (unchanged) -->
    <Dialog
      v-model:visible="showFullScreen"
      :maximizable="true"
      :modal="true"
      :style="{ width: '95vw', height: '95vh' }"
      position="center"
    >
      <div v-if="svgUrl" class="flex items-center justify-center h-full bg-gray-900 p-4">
        <img
          :src="svgUrl"
          :key="svgUrl"
          alt="Birth Chart Full Screen"
          class="max-h-full max-w-full object-contain"
        />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8080'

const formData = ref({
  name: '',
  year: null,
  month: null,
  day: null,
  hour: null,
  minute: null,
  lat: null,
  lng: null,
  tz_str: '',
  city: '',
  nation: '',
  zodiac_type: 'Tropical',
  houses_system: 'P',
})

const chartData = ref()
const loading = ref(false)
const svgUrl = ref()
const showFullScreen = ref(false)

const persons = ref([])
const loadingPersons = ref(false)

const generateChart = async () => {
  console.log('Generating chart with data:', formData.value)
  loading.value = true
  chartData.value = null
  svgUrl.value = null
  showFullScreen.value = false

  try {
    const res = await axios.post(
      `${API_BASE}/chart`,
      { ...formData.value },
      {
        headers: { 'Content-Type': 'application/json' },
      },
    )

    chartData.value = res.data
    svgUrl.value = res.data.svg_path || (res.data.chart && res.data.chart.svg_path)
    console.log('Chart generated successfully')
    loadPersons()
  } catch (e) {
    console.error('Chart generation error:', e)
    alert('Error generating chart: ' + JSON.stringify(e.response?.data?.detail || e.message || e))
  } finally {
    loading.value = false
  }
}

const saveCurrent = async () => {
  if (!formData.value.name) return alert('Name required to save')
  try {
    await axios.post(`${API_BASE}/persons`, { ...formData.value })
    alert('Saved successfully!')
    loadPersons()
  } catch (e) {
    alert('Save error: ' + e.message)
  }
}

const loadPersons = async () => {
  loadingPersons.value = true
  try {
    const res = await axios.get(`${API_BASE}/persons`)
    persons.value = res.data.map((p) => ({
      ...p,
      date: `${p.year}-${String(p.month).padStart(2, '0')}-${String(p.day).padStart(2, '0')}`,
    }))
  } catch (e) {
    console.error(e)
  } finally {
    loadingPersons.value = false
  }
}

const loadPerson = async (id) => {
  try {
    const res = await axios.get(`${API_BASE}/persons/${id}`)
    const p = res.data
    formData.value = {
      name: p.name || '',
      year: p.year,
      month: p.month,
      day: p.day,
      hour: p.hour,
      minute: p.minute,
      lat: p.lat,
      lng: p.lng,
      tz_str: p.tz_str || '',
      city: p.city || '',
      nation: p.nation || '',
      zodiac_type: p.zodiac_type || 'Tropical',
      houses_system: p.houses_system || 'P',
    }
    if (p.chart_data) {
      chartData.value = p.chart_data
      svgUrl.value = p.svg_path
    }
    alert(`Loaded ${p.name}'s data`)
  } catch (e) {
    alert('Load error: ' + e.message)
  }
}

const deletePerson = async (id) => {
  if (!confirm('Delete this record?')) return
  try {
    await axios.delete(`${API_BASE}/persons/${id}`)
    loadPersons()
  } catch (e) {
    alert('Delete error: ' + e.message)
  }
}

onMounted(() => {
  loadPersons()
})
</script>
