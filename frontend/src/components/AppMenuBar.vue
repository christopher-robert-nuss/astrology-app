<template>
  <Menubar :model="items" breakpoint="100px" :pt="pt" :ptOptions="{ mergeProps: true }" />
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import Menubar from 'primevue/menubar'

const pt = {
  root: {
    class: 'm-0 p-0 border-b border-surface-300 bg-surface-50 shadow-none rounded-none w-full',
  },
  rootList: {
    class: 'm-0 p-0 flex list-none bg-surface-50 w-full',
  },

  // Menu item container - removed relative positioning
  item: ({ context }) => ({
    class: [
      'm-0 p-0 text-xs transition-colors duration-150',
      context.focused && 'outline-none ring-2 ring-primary-500 ring-offset-1',
    ],
  }),

  // Content wrapper
  itemContent: ({ context }) => ({
    class: [
      'flex items-center gap-x-2 w-full cursor-pointer',
      context.active ? 'bg-primary-100 text-primary-700' : 'hover:bg-surface-100',
      context.focused && !context.active && 'bg-surface-100',
    ],
  }),

  // Link element
  itemLink: ({ context }) => ({
    class: [
      'flex-1 flex items-center gap-x-2 no-underline text-sm font-medium rounded-none!',
      context.active ? 'text-primary-700' : 'text-surface-700 hover:text-surface-900',
      context.focused && 'text-surface-900',
    ],
  }),

  // Icons
  itemIcon: ({ context }) => ({
    class: [
      'text-base',
      context.active ? 'text-primary-600' : 'text-surface-500 group-hover:text-surface-700',
      context.focused && 'text-surface-700',
    ],
  }),

  // Label
  itemLabel: ({ context }) => ({
    class: [
      'text-xs whitespace-nowrap',
      context.active ? 'text-primary-700 font-medium' : 'text-surface-700',
    ],
  }),

  // Submenu container - removed absolute + z-index; PrimeVue handles positioning
  submenu: {
    class: 'bg-surface-0 border border-surface-200 shadow-xl rounded-md py-1 min-w-[200px]',
  },

  submenuIcon: ({ context }) => ({
    class: [
      'ml-auto text-sm transition-transform',
      context.active && 'rotate-180 text-primary-600',
    ],
  }),

  // Separators
  separator: {
    class: 'my-1 border-t border-surface-200 mx-4',
  },
}

// Injected from App.vue
const doSaveChart = inject('saveChart', () => {})
const doOpenChart = inject('openChart', () => {})
const doOpenPreferences = inject('openPreferences', () => {})
const recentFiles = inject('recentFiles', ref([]))
const doOpenRecentFile = inject('openRecentFile', () => {})

// Menu items relevant to the Astrological Birth Chart app
const items = computed(() => [
  {
    label: 'File',
    items: [
      { label: 'New Chart', icon: 'pi pi-plus', command: () => newChart() },
      { label: 'Open...', icon: 'pi pi-folder-open', command: () => openChart() },
      {
        label: 'Recent Files',
        icon: 'pi pi-history',
        items:
          recentFiles.value.length > 0
            ? recentFiles.value.map((f) => ({
                label: f.name,
                icon: 'pi pi-file',
                command: () => doOpenRecentFile(f.filePath),
              }))
            : [{ label: 'No Recent Files', disabled: true }],
      },
      { separator: true },
      { label: 'Save', icon: 'pi pi-save', command: () => saveChart() },
      { label: 'Save As...', icon: 'pi pi-save', command: () => saveChartAs() },
      { separator: true },
      { label: 'Print...', icon: 'pi pi-print', command: () => handlePrint() },
      { separator: true },
      { label: 'Exit', icon: 'pi pi-power-off', command: () => exitApp() },
    ],
  },
  {
    label: 'Edit',
    items: [{ label: 'Preferences...', icon: 'pi pi-cog', command: () => openPreferences() }],
  },
  {
    label: 'Help',
    items: [
      { label: 'Documentation', icon: 'pi pi-book', command: () => showDocs() },
      { label: 'About Simple Astro Chart', icon: 'pi pi-info-circle', command: () => showAbout() },
    ],
  },
])

// Menu command handlers
const newChart = () => {
  // Reset form
  window.location.reload() // temporary
}
const openChart = () => doOpenChart()
const saveChart = () => doSaveChart()
const saveChartAs = () => doSaveChart()

// In App.vue or your Menu Component
const handlePrint = async () => {
  const img = document.querySelector('.print-chart-image')

  if (!img) {
    console.error('Target image not found')
    return
  }

  // Wait for image to be fully loaded
  const ensureLoaded = new Promise((resolve) => {
    if (img.complete) {
      resolve()
    } else {
      img.onload = resolve
      img.onerror = () => {
        console.warn('Image failed to load, proceeding anyway')
        resolve()
      }
    }
  })

  await ensureLoaded

  // Small delay to ensure DOM paints before print dialog opens
  setTimeout(() => {
    window.print()
  }, 100)
}

const exitApp = () => {
  console.log('Exit requested via menu')

  if (window.electronAPI?.quitApp) {
    window.electronAPI.quitApp()
  } else if (window.electron?.ipcRenderer) {
    window.electron.ipcRenderer.send('app-quit')
  } else {
    console.warn('Electron quit API not available, falling back to window.close()')
    window.close()
  }
}

const undo = () => {}
const redo = () => {}
const openPreferences = () => doOpenPreferences()

const setTheme = (theme) => {
  const root = document.documentElement

  if (theme === 'dark') {
    root.classList.add('dark')
    root.classList.remove('light', 'gtk')
  } else if (theme === 'light') {
    root.classList.add('light')
    root.classList.remove('dark', 'gtk')
  } else if (theme === 'gtk') {
    root.classList.add('gtk')
    root.classList.remove('dark', 'light')
  }

  // Optional: persist choice
  localStorage.setItem('app-theme', theme)
}

const zoomIn = () => {}
const zoomOut = () => {}
const resetZoom = () => {}
const calculateChart = () => {}
const toggleAspects = () => {}
const managePersons = () => {}
const manageLocations = () => {}
const showDocs = () => {
  const repoUrl = 'https://github.com/christopher-robert-nuss/astrology-app'

  if (window.electronAPI?.openExternal) {
    window.electronAPI.openExternal(repoUrl)
  } else {
    window.open(repoUrl, '_blank', 'noopener,noreferrer')
  }
}
const showAbout = () => {
  console.log('Showing About dialog')

  if (window.electronAPI?.showAbout) {
    window.electronAPI.showAbout()
  } else {
    // Fallback for development / non-Electron
    const aboutInfo = `
Kerykeion Chart
Version 1.0.0

A simple, standalone offline astrological birth chart application.

Built with:
• Vue 3 + PrimeVue + Tailwind
• Kerykeion (Swiss Ephemeris)
• Python FastAPI + Electron

© 2026 - All Rights Reserved
    `.trim()

    alert(aboutInfo)
  }
}
</script>
