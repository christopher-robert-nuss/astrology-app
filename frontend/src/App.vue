<template>
  <div class="flex h-dvh flex-col overflow-hidden">
    <AppMenuBar class="relative z-40 m-0! p-0! rounded-none! border-none!" />

    <div class="flex-1 min-h-0 overflow-hidden">
      <Toast position="bottom-right" />
      <div class="content h-full min-h-0 bg-gray-50">
        <div class="h-full min-h-0 w-full">
          <div class="relative h-full min-h-0 w-full">
            <Drawer
              v-model:visible="showSidebar"
              header="Enter Birth Data"
              position="left"
              class="w-full sm:w-md"
            >
              <form @submit.prevent="generateChart" class="p-1 flex-1 flex flex-col">
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

                  <div class="flex gap-3 mt-6 pt-2">
                    <Button
                      type="submit"
                      label="Generate Chart"
                      :loading="loading"
                      class="w-full"
                      icon="pi pi-chart-line"
                      :pt="{ label: { class: 'text-xs p-1' } }"
                    />
                    <Button
                      type="button"
                      label="Reset"
                      severity="secondary"
                      outlined
                      class="w-full"
                      icon="pi pi-refresh"
                      @click="resetForm"
                      :disabled="loading"
                    />
                  </div>
                </div>
              </form>
            </Drawer>

            <!-- Right Side: Chart Display -->
            <div class="relative z-0 min-w-0 h-full min-h-0 w-full overflow-hidden bg-white">
              <Button
                label="Birth Data"
                icon="pi pi-bars"
                class="absolute left-6 top-6 lg:left-8 lg:top-8"
                severity="secondary"
                @click="showSidebar = true"
                :pt="{ root: { class: 'rounded-none!' } }"
                :ptOptions="{ mergeProps: true }"
              />
              <div class="bg-white h-full min-h-0 overflow-auto">
                <div v-if="svgUrl" class="h-full min-h-0 flex flex-col p-6 lg:p-8">
                  <div class="flex-1 min-h-0 flex justify-center items-center">
                    <div
                      class="relative h-full w-full min-h-0 min-w-0 overflow-hidden flex justify-center items-center"
                    >
                      <img
                        :src="svgUrl"
                        :key="svgUrl"
                        alt="Birth Chart"
                        class="print-chart-image block h-auto w-auto max-h-full max-w-full object-contain"
                      />
                      <div
                        v-if="showMagnifier"
                        class="absolute inset-0 z-10 overflow-hidden rounded border border-gray-300 bg-white shadow-lg"
                      >
                        <div class="h-full w-full overflow-auto">
                          <img
                            :src="svgUrl"
                            alt="Magnified Birth Chart"
                            class="block max-w-none"
                            :style="{
                              width: `${magnifierScale * 100}%`,
                              height: 'auto',
                            }"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="pt-4 flex justify-center gap-3 shrink-0">
                    <Button
                      label="View Full Screen"
                      icon="pi pi-external-link"
                      @click="showFullScreen = true"
                      severity="secondary"
                      class="h-10!"
                    />
                    <Button
                      :label="showMagnifier ? 'Hide Magnifier' : 'Show Magnifier'"
                      icon="pi pi-search-plus"
                      @click="toggleMagnifier"
                      severity="secondary"
                      class="h-10!"
                    />
                  </div>

                  <div
                    v-if="preferencesOptions.aspects.length"
                    class="mt-4 shrink-0 border-t border-gray-200 pt-4"
                  >
                    <p class="mb-2 text-sm font-semibold text-gray-700">Aspect Display</p>
                    <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-3">
                      <label
                        v-for="aspect in preferencesOptions.aspects"
                        :key="`chart-aspect-${aspect.key}`"
                        class="flex items-center gap-2 rounded border border-gray-200 px-3 py-2 text-sm"
                      >
                        <input
                          type="checkbox"
                          :checked="!!preferences.aspects_enabled[aspect.key]"
                          :disabled="savingPreferences || loadingPreferences || loading"
                          @change="updateAspectPreference(aspect.key, $event.target.checked)"
                        />
                        <span>
                          {{ aspect.label }}
                          <span class="text-gray-400">(orb {{ aspect.default_orb }})</span>
                        </span>
                      </label>
                    </div>
                  </div>
                </div>

                <div
                  v-else
                  class="h-full min-h-0 flex items-center justify-center text-center text-gray-400 p-6 lg:p-8"
                >
                  <p class="text-xl">Your birth chart will appear here</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="showFullScreen && svgUrl"
          class="fixed inset-0 z-50 flex items-center justify-center bg-white p-4"
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

        <div
          v-if="showPreferencesDialog"
          class="fixed inset-0 z-60 flex items-center justify-center bg-black/40 p-4"
          @click="cancelPreferences"
        >
          <div
            class="w-full max-w-2xl rounded-lg border border-gray-200 bg-white shadow-2xl"
            @click.stop
          >
            <div class="border-b border-gray-200 px-5 py-4">
              <h2 class="text-lg font-semibold">Edit Preferences</h2>
              <p class="text-sm text-gray-500">
                Configure zodiac, house system, and enabled aspects.
              </p>
            </div>

            <div class="space-y-5 px-5 py-4" v-if="preferencesDraft">
              <div>
                <label class="mb-1 block text-sm font-medium text-gray-700">Zodiac Type</label>
                <select
                  v-model="preferencesDraft.zodiac_type"
                  class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                  :disabled="savingPreferences || loadingPreferences"
                >
                  <option
                    v-for="zodiac in preferencesOptions.zodiac_types"
                    :key="zodiac"
                    :value="zodiac"
                  >
                    {{ zodiac }}
                  </option>
                </select>
              </div>

              <div>
                <label class="mb-1 block text-sm font-medium text-gray-700">House System</label>
                <select
                  v-model="preferencesDraft.houses_system"
                  class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                  :disabled="savingPreferences || loadingPreferences"
                >
                  <option
                    v-for="house in preferencesOptions.house_systems"
                    :key="house.code"
                    :value="house.code"
                  >
                    {{ house.code }} - {{ house.label }}
                  </option>
                </select>
              </div>

              <div>
                <label class="mb-2 block text-sm font-medium text-gray-700">Enabled Aspects</label>
                <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
                  <label
                    v-for="aspect in preferencesOptions.aspects"
                    :key="aspect.key"
                    class="flex items-center gap-2 rounded border border-gray-200 px-3 py-2 text-sm"
                  >
                    <input
                      v-model="preferencesDraft.aspects_enabled[aspect.key]"
                      type="checkbox"
                      :disabled="savingPreferences || loadingPreferences"
                    />
                    <span
                      >{{ aspect.label }}
                      <span class="text-gray-400">(orb {{ aspect.default_orb }})</span></span
                    >
                  </label>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-end gap-2 border-t border-gray-200 px-5 py-4">
              <Button
                label="Cancel"
                severity="secondary"
                outlined
                @click="cancelPreferences"
                :disabled="savingPreferences"
              />
              <Button
                label="Save Preferences"
                icon="pi pi-save"
                @click="savePreferences"
                :loading="savingPreferences"
              />
            </div>
          </div>
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
import Drawer from 'primevue/drawer'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

const preferences = ref({
  zodiac_type: 'Tropical',
  houses_system: 'P',
  aspects_enabled: {},
})

const preferencesOptions = ref({
  zodiac_types: ['Tropical', 'Sidereal'],
  house_systems: [],
  aspects: [],
})

const showPreferencesDialog = ref(false)
const preferencesDraft = ref(null)
const loadingPreferences = ref(false)
const savingPreferences = ref(false)

const initialFormData = {
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
  zodiac_type: '',
  houses_system: '',
}

const formData = ref({ ...initialFormData })

const chartData = ref()
const loading = ref(false)
const svgUrl = ref()
const showSidebar = ref(false)
const showFullScreen = ref(false)
const showMagnifier = ref(false)
const magnifierScale = 1.4
const recentFiles = ref([])
const toast = useToast()

const toPlainPayload = (value) => {
  if (value === null || value === undefined) {
    return value
  }

  return JSON.parse(JSON.stringify(value))
}

// Helper to call backend via IPC
const apiCall = async (method, endpoint, body = null) => {
  if (!window.electronAPI) {
    console.error('electronAPI not available - falling back?')
    throw new Error('Electron API not loaded. Restart the app.')
  }
  return window.electronAPI.apiRequest({
    method,
    endpoint,
    body: toPlainPayload(body),
  })
}

const normalizePreferences = (source = {}) => {
  const zodiacType = source.zodiac_type || 'Tropical'
  const houseSystem = source.houses_system || 'P'
  const aspectKeys = preferencesOptions.value.aspects.map((aspect) => aspect.key)

  const normalizedAspects = Object.fromEntries(aspectKeys.map((key) => [key, false]))
  if (typeof source.aspects_enabled === 'boolean') {
    aspectKeys.forEach((key) => {
      normalizedAspects[key] = source.aspects_enabled
    })
  } else if (source.aspects_enabled && typeof source.aspects_enabled === 'object') {
    for (const [key, enabled] of Object.entries(source.aspects_enabled)) {
      if (Object.prototype.hasOwnProperty.call(normalizedAspects, key)) {
        normalizedAspects[key] = !!enabled
      }
    }
  }

  return {
    zodiac_type: zodiacType,
    houses_system: houseSystem,
    aspects_enabled: normalizedAspects,
  }
}

const loadPreferenceOptions = async () => {
  try {
    const options = await apiCall('GET', '/preferences/options')
    preferencesOptions.value = {
      zodiac_types: options.zodiac_types || ['Tropical', 'Sidereal'],
      house_systems: options.house_systems || [],
      aspects: options.aspects || [],
    }
  } catch (e) {
    console.error('Failed to load preferences options:', e)
    toast.add({
      severity: 'warn',
      summary: 'Preferences options unavailable',
      detail: 'Using fallback preferences values.',
      life: 3000,
    })
  }
}

const loadPreferences = async () => {
  loadingPreferences.value = true
  try {
    const loaded = await apiCall('GET', '/preferences')
    preferences.value = normalizePreferences(loaded)
  } catch (e) {
    console.error('Failed to load preferences:', e)
    preferences.value = normalizePreferences(preferences.value)
  } finally {
    loadingPreferences.value = false
  }
}

const openPreferencesDialog = () => {
  preferencesDraft.value = normalizePreferences(preferences.value)
  showPreferencesDialog.value = true
}

const cancelPreferences = () => {
  showPreferencesDialog.value = false
  preferencesDraft.value = null
}

const persistPreferences = async (
  nextPreferences,
  { suppressErrorToast = false, regenerateChart = true } = {},
) => {
  savingPreferences.value = true
  try {
    const saved = await apiCall('PUT', '/preferences', nextPreferences)
    preferences.value = normalizePreferences(saved)

    if (preferencesDraft.value) {
      preferencesDraft.value = normalizePreferences(saved)
    }

    if (regenerateChart && chartData.value) {
      await generateChart({ notifySuccess: false })
      return { ok: true, regenerated: true }
    }

    return { ok: true, regenerated: false }
  } catch (e) {
    if (!suppressErrorToast) {
      toast.add({
        severity: 'error',
        summary: 'Save failed',
        detail: e.message || 'Could not save preferences',
        life: 5000,
      })
    }
    return { ok: false }
  } finally {
    savingPreferences.value = false
  }
}

const savePreferences = async () => {
  if (!preferencesDraft.value) return

  const result = await persistPreferences(preferencesDraft.value)
  if (!result.ok) {
    return
  }

  showPreferencesDialog.value = false
  preferencesDraft.value = null

  if (result.regenerated) {
    toast.add({
      severity: 'success',
      summary: 'Preferences saved',
      detail: 'Chart regenerated with updated preferences.',
      life: 3000,
    })
  } else {
    toast.add({ severity: 'success', summary: 'Preferences saved', life: 2500 })
  }
}

const updateAspectPreference = async (aspectKey, enabled) => {
  const previousPreferences = normalizePreferences(preferences.value)
  const nextPreferences = normalizePreferences({
    ...preferences.value,
    aspects_enabled: {
      ...preferences.value.aspects_enabled,
      [aspectKey]: enabled,
    },
  })

  preferences.value = nextPreferences
  if (preferencesDraft.value) {
    preferencesDraft.value = normalizePreferences(nextPreferences)
  }

  const result = await persistPreferences(nextPreferences, {
    suppressErrorToast: true,
    regenerateChart: true,
  })

  if (!result.ok) {
    preferences.value = previousPreferences
    if (preferencesDraft.value) {
      preferencesDraft.value = normalizePreferences(previousPreferences)
    }
    toast.add({
      severity: 'error',
      summary: 'Update failed',
      detail: 'Could not update aspect preferences.',
      life: 4000,
    })
  }
}

const generateChart = async ({ notifySuccess = true } = {}) => {
  console.log('Generating chart with data:', formData.value)
  loading.value = true
  chartData.value = null
  svgUrl.value = null
  showFullScreen.value = false

  try {
    const res = await apiCall('POST', '/chart', {
      data: { ...formData.value },
      data2: preferences.value,
    })

    chartData.value = res

    let svgPath = res.svg_path
    if (svgPath && svgPath.startsWith('/charts_output')) {
      svgUrl.value = `http://127.0.0.1:8080${svgPath}?t=${Date.now()}` // Cache-bust to always show latest SVG
    } else {
      const joiner = svgPath && svgPath.includes('?') ? '&' : '?'
      svgUrl.value = svgPath ? `${svgPath}${joiner}t=${Date.now()}` : svgPath
    }

    if (notifySuccess) {
      toast.add({ severity: 'success', summary: 'Chart Generated', life: 3000 })
    }
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

const resetForm = () => {
  formData.value = { ...initialFormData }
  chartData.value = null
  svgUrl.value = null
  showFullScreen.value = false
  showMagnifier.value = false
}

// Provide to child components (AppMenuBar)
provide('saveChart', saveChartToFile)
provide('openChart', openChartFromFile)
provide('openPreferences', openPreferencesDialog)
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
  await loadPreferenceOptions()
  await loadPreferences()
  await loadRecentFiles()
})
</script>
