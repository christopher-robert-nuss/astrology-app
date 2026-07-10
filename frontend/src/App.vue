<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="max-w-3xl mx-auto px-4">
      <h1 class="text-4xl font-bold text-center mb-10">Astrology Chart Generator</h1>

      <Card class="shadow-lg">
        <template #header>
          <div class="px-6 py-4 border-b border-b-gray-200 text-lg font-semibold">
            Enter Birth Data
          </div>

          <Form
            v-slot="$form"
            :initial-values="formData"
            @submit="generateChart"
            class="p-6 space-y-6"
            ><div class="mb-4 text-gray-700 text-sm">
              Name
              <InputText
                v-model="formData.name"
                name="name"
                placeholder="Full Name"
                class="w-full"
                fluid
              />
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div class="col-span-1 text-gray-700 text-sm">
                Day of Birth
                <InputNumber
                  v-model="formData.day"
                  name="day"
                  placeholder="Day"
                  :min="1"
                  :max="31"
                  label="Day"
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Month of Birth
                <InputNumber
                  v-model="formData.month"
                  name="month"
                  placeholder="Month"
                  :min="1"
                  :max="12"
                  label="Month"
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Year of Birth
                <InputNumber
                  v-model="formData.year"
                  name="year"
                  placeholder="Year"
                  :min="1500"
                  label="Year"
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Hour of Birth
                <InputNumber
                  v-model="formData.hour"
                  name="hour"
                  placeholder="Hour"
                  :min="0"
                  :max="23"
                  label="Hour"
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Minute of Birth
                <InputNumber
                  v-model="formData.minute"
                  name="minute"
                  placeholder="Minute"
                  :min="0"
                  :max="59"
                  label="Minute"
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Timezone
                <InputText
                  name="tz_str"
                  placeholder="Timezone (e.g. Europe/Rome)"
                  label="Timezone"
                  v-model="formData.tz_str"
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                House System
                <InputText
                  name="houses_system"
                  placeholder="Houses System (e.g., P)"
                  label="Houses System"
                  v-model="formData.houses_system"
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Latitude
                <InputNumber
                  name="lat"
                  :format="false"
                  :maxFractionDigits="6"
                  placeholder="Latitude"
                  :min="-90"
                  :max="90"
                  label="Latitude"
                  v-model="formData.lat"
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Longtitude
                <InputNumber
                  name="lng"
                  :format="false"
                  :maxFractionDigits="6"
                  placeholder="Longitude"
                  :min="-180"
                  :max="180"
                  label="Longitude"
                  v-model="formData.lng"
                  fluid
                />
              </div>
              <div class="col-span-1 text-gray-700 text-sm">
                City
                <InputText
                  v-model="formData.city"
                  name="city"
                  placeholder="City"
                  label="City"
                  fluid
                />
              </div>
              <div class="col-span-1 text-gray-700 text-sm">
                Country
                <InputText
                  v-model="formData.nation"
                  name="nation"
                  placeholder="Country Code eg. AU"
                  label="Country"
                  fluid
                />
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
          </Form>
        </template>
      </Card>

      <div v-if="svgUrl" class="mt-8">
        <img :src="svgUrl" :key="svgUrl" alt="Birth Chart" />
      </div>

      <!-- <div v-if="chartData" class="mt-8">
        <Card>
          <template #title> Generated Chart Data</template>
          <template #content>
            <div class="p-6">
              <pre class="bg-zinc-900 text-emerald-300 text-sm overflow-auto">{{ chartData }}</pre>
            </div>
          </template>
        </Card>
      </div> -->

      <!-- Saved Persons Section -->
      <Card class="mt-8 shadow-lg">
        <template #header>
          <div class="px-6 py-4 border-b border-b-gray-200 flex justify-between items-center">
            <span class="text-lg font-semibold">Saved Birth Charts</span>
            <Button label="Refresh List" icon="pi pi-refresh" @click="loadPersons" size="small" />
          </div>
        </template>
        <template #content>
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
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { Form } from '@primevue/forms'

const formData = ref({
  name: 'Christopher Robert Nuss',
  year: 1972,
  month: 1,
  day: 24,
  hour: 17,
  minute: 30,
  lat: -27.485,
  lng: 153.0280556,
  tz_str: 'Australia/Brisbane',
  city: 'Brisbane',
  nation: 'AU',
  zodiac_type: 'Tropical',
  houses_system: 'P',
})

const chartData = ref()
const loading = ref(false)
const svgUrl = ref()

const persons = ref([])
const loadingPersons = ref(false)
const selectedPerson = ref(null)

const generateChart = async (payload) => {
  console.log('Form submitted:', payload)
  loading.value = true
  chartData.value = null
  svgUrl.value = null

  try {
    const res = await axios.post('http://localhost:8000/chart', payload.values)
    chartData.value = res.data
    svgUrl.value = res.data.svg_path
    console.log('Chart generated successfully')

    // Refresh list after generating
    loadPersons()
  } catch (e) {
    console.error(e)
    alert('Error: ' + JSON.stringify(e.response?.data?.detail || e.message))
    // Clear on error to avoid stale state
    svgUrl.value = null
    chartData.value = null
  } finally {
    loading.value = false
  }
}

const saveCurrent = async () => {
  if (!formData.value.name) return alert('Name required to save')
  try {
    await axios.post('http://localhost:8000/persons', formData.value)
    alert('Saved successfully!')
    loadPersons()
  } catch (e) {
    alert('Save error: ' + e.message)
  }
}

const loadPersons = async () => {
  loadingPersons.value = true
  try {
    const res = await axios.get('http://localhost:8000/persons')
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
    const res = await axios.get(`http://localhost:8000/persons/${id}`)
    const p = res.data
    // Populate form
    formData.value = {
      name: p.name,
      year: p.year,
      month: p.month,
      day: p.day,
      hour: p.hour,
      minute: p.minute,
      lat: p.lat,
      lng: p.lng,
      tz_str: p.tz_str,
      city: p.city,
      nation: p.nation,
      zodiac_type: p.zodiac_type,
      houses_system: p.houses_system,
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
    await axios.delete(`http://localhost:8000/persons/${id}`)
    loadPersons()
  } catch (e) {
    alert('Delete error: ' + e.message)
  }
}

onMounted(() => {
  loadPersons()
})
</script>
