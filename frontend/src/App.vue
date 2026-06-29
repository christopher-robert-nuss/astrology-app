<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="max-w-3xl mx-auto px-4">
      <h1 class="text-4xl font-bold text-center mb-10">Astrology Chart Generator</h1>

      <Card class="shadow-lg">
        <template #header>
          <div class="px-6 py-4 border-b border-b-gray-200 text-lg font-semibold">
            Enter Birth Data
          </div>

          <Form v-slot="$form" @submit="generateChart" class="p-6 space-y-6"
            ><div class="mb-4 text-gray-700 text-sm">
              Name
              <InputText name="name" placeholder="Full Name" class="w-full" fluid />
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div class="col-span-1 text-gray-700 text-sm">
                Day of Birth
                <InputNumber name="day" placeholder="Day" :min="1" :max="31" label="Day" fluid />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Month of Birth
                <InputNumber
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
                <InputNumber name="year" placeholder="Year" :min="1500" label="Year" fluid />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Hour of Birth
                <InputNumber name="hour" placeholder="Hour" :min="0" :max="23" label="Hour" fluid />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Minute of Birth
                <InputNumber
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
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                House System
                <InputChips
                  name="houses_system"
                  placeholder="Houses System (e.g., P)"
                  label="Houses System"
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Latitude
                <InputNumber
                  name="lat"
                  format="false"
                  maxFractionDigits="6"
                  placeholder="Latitude"
                  :min="-90"
                  :max="90"
                  label="Latitude"
                  fluid
                />
              </div>

              <div class="col-span-1 text-gray-700 text-sm">
                Longtitude
                <InputNumber
                  name="lng"
                  format="false"
                  maxFractionDigits="6"
                  placeholder="Longitude"
                  :min="-180"
                  :max="180"
                  label="Longitude"
                  fluid
                />
              </div>
              <div class="col-span-1 text-gray-700 text-sm">
                City
                <InputText name="city" placeholder="City" label="City" fluid />
              </div>
              <div class="col-span-1 text-gray-700 text-sm">
                Country
                <InputText name="nation" placeholder="Country Code eg. AU" label="Country" fluid />
              </div>
            </div>

            <Button
              type="submit"
              label="Generate Chart"
              :loading="loading"
              class="w-full"
              icon="pi pi-chart-line"
            />
          </Form>
        </template>
      </Card>

      <div v-if="svgUrl">
        <img :src="svgUrl" alt="Birth Chart" />
      </div>

      <div v-if="chartData" class="mt-8">
        <Card>
          <template #title> Generated Chart Data</template>
          <template #content>
            <div class="p-6">
              <pre class="bg-zinc-900 text-emerald-300 text-sm overflow-auto">{{ chartData }}</pre>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import InputChips from 'primevue/inputchips'
import Button from 'primevue/button'
import { Form } from '@primevue/forms'

const formValues = ref({
  name: 'Christopher Robert Nuss',
  year: 1972,
  month: 1,
  day: 24,
  hour: 5,
  minute: 30,
  lat: -27.485,
  lng: 153.0280556,
  tz_str: 'Australia/Brisbane',
  city: 'Brisbane',
  nation: 'AU',
  zodiac_type: 'Tropical',
  houses_system: 'P',
})
const chartData = ref(null)
const loading = ref(false)
const svgUrl = ref(null)

const generateChart = async (form) => {
  console.log('Form submitted:', form)
  loading.value = true
  try {
    const res = await axios.post('http://localhost:8000/chart', form.values)
    chartData.value = res.data
    svgUrl.value = res.data.svg_path
    console.log('Chart data received:', chartData.value)
  } catch (e) {
    console.error(e)
    alert('Error: ' + JSON.stringify(e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}
</script>
