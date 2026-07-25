<template>
  <div class="flex flex-col h-screen">
    <AppMenuBar class="m-0! p-0! rounded-none! border-none!" />

    <div class="flex-1 overflow-hidden">
      <Toast position="bottom-right" />
      <div class="content min-h-screen bg-gray-50">
        <div class="w-full">
          <div class="flex flex-col md:flex-row gap-2 w-full">
            <!-- Left Sidebar: Form + Saved Charts -->
            <div
              class="w-full bg-slate-200 md:w-72 lg:w-80 xl:w-96 md:min-h-screen md:sticky md:top-0 md:self-start shrink-0 flex flex-col"
            >
              <!-- Birth Data Form -->
              <div
                class="bg-white shadow-lg border border-gray-200 overflow-hidden flex-1 flex flex-col"
              >
                <div class="px-4 py-3 border-b border-b-gray-200 font-semibold bg-gray-50">
                  Enter Birth Data
                </div>

                <form @submit.prevent="generateChart" class="p-4 flex-1 flex flex-col">
                  <div class="space-y-5 flex-1">
                    <div class="mb-3 text-gray-700 text-sm">
                      <InputText
                        v-model="formData.name"
                        class="w-full"
                        fluid
                        placeholder="Name"
                        size="small"
                      />
                    </div>
                    <p class="text-sm font-semibold m-0 pb-1">Date of Birth</p>
                    <div class="grid grid-cols-3 gap-3">
                      <div class="text-gray-700 text-sm">
                        <InputNumber
                          v-model="formData.day"
                          :min="1"
                          :max="31"
                          fluid
                          placeholder="Day"
                          size="small"
                        />
                      </div>
                      <div class="text-gray-700 text-sm">
                        <InputNumber
                          v-model="formData.month"
                          :min="1"
                          :max="12"
                          fluid
                          placeholder="Month"
                          size="small"
                        />
                      </div>
                      <div class="text-gray-700 text-sm">
                        <InputNumber
                          v-model="formData.year"
                          :format="false"
                          :min="1500"
                          fluid
                          placeholder="Year"
                          size="small"
                        />
                      </div>
                    </div>
                    <p class="text-sm font-semibold m-0 pb-1">Birth Information</p>
                    <div class="grid grid-cols-2 gap-3">
                      <div class="col-span-1 text-gray-700 text-sm">
                        <InputNumber
                          v-model="formData.hour"
                          :min="0"
                          :max="23"
                          fluid
                          placeholder="Hour"
                          size="small"
                        />
                      </div>

                      <div class="col-span-1 text-gray-700 text-sm">
                        <InputNumber
                          v-model="formData.minute"
                          :min="0"
                          :max="59"
                          fluid
                          placeholder="Minute"
                          size="small"
                        />
                      </div>

                      <div class="col-span-2 text-gray-700 text-sm">
                        <InputText
                          v-model="formData.tz_str"
                          fluid
                          placeholder="Timezone"
                          size="small"
                        />
                      </div>
                    </div>
                    <p class="text-sm font-semibold m-0 pb-1">Location Information</p>
                    <div class="grid grid-cols-2 gap-3">
                      <div class="col-span-1 text-gray-700 text-sm">
                        <InputNumber
                          v-model="formData.lat"
                          :format="false"
                          :maxFractionDigits="6"
                          :min="-90"
                          :max="90"
                          fluid
                          placeholder="Latitude"
                          size="small"
                        />
                      </div>

                      <div class="col-span-1 text-gray-700 text-sm">
                        <InputNumber
                          v-model="formData.lng"
                          :format="false"
                          :maxFractionDigits="6"
                          :min="-180"
                          :max="180"
                          fluid
                          placeholder="Longitude"
                          size="small"
                        />
                      </div>

                      <div class="col-span-2 text-gray-700 text-sm">
                        <InputText v-model="formData.city" fluid placeholder="City" size="small" />
                      </div>
                      <div class="col-span-2 text-gray-700 text-sm">
                        <InputText
                          v-model="formData.nation"
                          fluid
                          placeholder="Country"
                          size="small"
                        />
                      </div>
                    </div>
                    <p class="text-sm font-semibold m-0 pb-1">House System</p>
                    <div class="grid grid-cols-2 gap-3">
                      <div class="col-span-2 text-gray-700 text-sm">
                        <InputText
                          v-model="formData.houses_system"
                          fluid
                          placeholder="House System"
                          size="small"
                        />
                      </div>
                    </div>

                    <div class="flex gap-4 mt-6 pt-2">
                      <Button
                        type="submit"
                        label="Generate Chart"
                        :loading="loading"
                        class="w-full"
                        icon="pi pi-chart-line"
                        :pt="{ label: { class: 'text-xs p-1' } }"
                      />
                    </div>
                  </div>
                </form>
              </div>
            </div>

            <!-- Right Side: Chart Display -->
            <div class="flex-1 min-w-0 h-screen max-h-screen overflow-hidden">
              <div class="bg-white h-full max-h-screen overflow-hidden">
                <div
                  v-if="svgUrl"
                  class="h-full max-h-screen flex flex-col p-6 lg:p-8 overflow-hidden"
                >
                  <div class="flex-1 min-h-0 flex justify-center items-center">
                    <div
                      class="relative w-full max-w-full max-h-full flex justify-center items-center"
                    >
                      <img
                        :src="svgUrl"
                        :key="svgUrl"
                        alt="Birth Chart"
                        class="print-chart-image"
                      />
                      <Button
                        icon="pi pi-search-plus"
                        severity="secondary"
                        rounded
                        class="absolute right-2 top-2 z-20 bg-white/90 border border-gray-300 shadow-sm"
                        @click="toggleMagnifier"
                        aria-label="Toggle zoom"
                      />
                      <div
                        v-if="showMagnifier"
                        class="pointer-events-none absolute inset-0 z-10 overflow-hidden rounded border border-gray-300 bg-white shadow-lg"
                      >
                        <div
                          class="h-full w-full bg-no-repeat bg-cover"
                          :style="{
                            backgroundImage: `url(${svgUrl})`,
                            backgroundPosition: `${magnifierX}% ${magnifierY}%`,
                            backgroundSize: `${magnifierScale * 100}% ${magnifierScale * 100}%`,
                          }"
                        />
                      </div>
                    </div>
                  </div>
                  <div class="pt-4 flex justify-center shrink-0">
                    <Button
                      label="View Full Screen"
                      icon="pi pi-external-link"
                      @click="showFullScreen = true"
                      severity="secondary"
                    />
                  </div>
                </div>

                <div
                  v-else
                  class="h-full max-h-screen flex items-center justify-center text-center text-gray-400 p-6 lg:p-8"
                >
                  <i class="pi pi-chart-line text-6xl mb-4"></i>
                  <p class="text-xl">Your birth chart will appear here</p>
                  <p class="text-sm mt-2">Fill the form and click Generate Chart</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="showFullScreen && svgUrl"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/95 p-4"
        >
          <div class="absolute right-4 top-4 z-10">
            <Button
              icon="pi pi-times"
              severity="secondary"
              rounded
              text
              @click="showFullScreen = false"
              aria-label="Close full screen chart"
            />
          </div>
          <img
            :src="svgUrl"
            :key="svgUrl"
            alt="Birth Chart Full Screen"
            class="max-h-full max-w-full object-contain"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import AppMenuBar from './components/AppMenuBar.vue'
import { ref, onMounted, provide } from 'vue'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

const formData = ref({
  name: 'Christopher Robert Nuss',
  year: 1972,
  month: 1,
  day: 24,
  hour: 17,
  minute: 30,
  lat: -27.485994,
  lng: 153.027624,
  tz_str: 'Australia/Brisbane',
  city: 'Brisbane',
  nation: 'Australia',
  zodiac_type: 'Tropical',
  houses_system: 'P',
})

const chartData = ref()
const loading = ref(false)
const svgUrl = ref()
const showFullScreen = ref(false)
const showMagnifier = ref(false)
const magnifierX = ref(50)
const magnifierY = ref(50)
const magnifierScale = 1.8
const recentFiles = ref([])
const toast = useToast()

// Helper to call backend via IPC
const apiCall = async (method, endpoint, body = null) => {
  if (!window.electronAPI) {
    console.error('electronAPI not available - falling back?')
    throw new Error('Electron API not loaded. Restart the app.')
  }
  return window.electronAPI.apiRequest({ method, endpoint, body })
}

const generateChart = async () => {
  console.log('Generating chart with data:', formData.value)
  loading.value = true
  chartData.value = null
  svgUrl.value = null
  showFullScreen.value = false

  try {
    const res = await apiCall('POST', '/chart', { ...formData.value })

    chartData.value = res

    let svgPath = res.svg_path
    if (svgPath && svgPath.startsWith('/charts_output')) {
      svgUrl.value = `http://127.0.0.1:8080${svgPath}` // Backend serves static files
    } else {
      svgUrl.value = svgPath
    }

    toast.add({ severity: 'success', summary: 'Chart Generated', life: 3000 })
  } catch (e) {
    console.error('Chart generation error:', e)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: e.message || 'Failed to generate chart',
      life: 5000,
    })
  } finally {
    loading.value = false
  }
}

const loadRecentFiles = async () => {
  try {
    recentFiles.value = await window.electronAPI.getRecentFiles()
  } catch (e) {
    console.error('Failed to load recent files:', e)
  }
}

const saveChartToFile = async () => {
  if (!chartData.value) {
    toast.add({
      severity: 'warn',
      summary: 'No chart to save',
      detail: 'Generate a chart first',
      life: 3000,
    })
    return
  }
  try {
    const payload = JSON.parse(
      JSON.stringify({ version: '1.0', birthData: formData.value, chartData: chartData.value }),
    )
    const result = await window.electronAPI.saveChartFile(payload, formData.value.name || 'chart')
    if (result?.success) {
      toast.add({ severity: 'success', summary: 'Chart saved', life: 3000 })
      await loadRecentFiles()
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Save failed', detail: e.message })
  }
}

const openChartFromFile = async () => {
  try {
    const result = await window.electronAPI.openChartFile()
    if (!result) return
    formData.value = { ...formData.value, ...result.birthData }
    await generateChart()
    await loadRecentFiles()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Open failed', detail: e.message })
  }
}

const openRecentChartFile = async (filePath) => {
  try {
    const result = await window.electronAPI.openRecentFile(filePath)
    if (!result) return
    formData.value = { ...formData.value, ...result.birthData }
    await generateChart()
    await loadRecentFiles()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Open failed', detail: e.message })
  }
}

const toggleMagnifier = () => {
  showMagnifier.value = !showMagnifier.value
}

// Provide to child components (AppMenuBar)
provide('saveChart', saveChartToFile)
provide('openChart', openChartFromFile)
provide('recentFiles', recentFiles)
provide('openRecentFile', openRecentChartFile)

// Auto-start backend
onMounted(async () => {
  window.addEventListener('theme-updated', (e) => {
    // Sync PrimeVue/Tailwind dark mode if needed
    if (e.detail) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  })
  await window.electronAPI.startBackend() // Ensures backend is running
  await loadRecentFiles()
})
</script>
