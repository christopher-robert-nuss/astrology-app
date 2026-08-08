<template>
  <Menubar
    :model="items"
    breakpoint="100px"
    class="app-menubar"
    :pt="pt"
    :ptOptions="{ mergeProps: true }"
  />
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import Menubar from 'primevue/menubar'

const pt = {
  root: {
    class: 'app-menubar-root m-0 p-0 border-none bg-transparent shadow-none rounded-none w-full',
  },
  rootList: {
    class: 'app-menubar-root-list m-0 p-0 flex list-none bg-transparent w-full',
  },

  item: ({ context }) => ({
    class: [
      'app-menubar-item m-0 p-0 transition-colors duration-150',
      context.focused && 'outline-none',
    ],
  }),

  itemContent: ({ context }) => ({
    class: [
      'app-menubar-item-content flex items-center gap-x-2 w-full cursor-pointer',
      context.active && 'app-menubar-item-content-active',
    ],
  }),

  itemLink: ({ context }) => ({
    class: [
      'app-menubar-item-link flex-1 flex items-center gap-x-2 no-underline rounded-none!',
      context.active && 'app-menubar-item-link-active',
    ],
  }),

  itemIcon: ({ context }) => ({
    class: [
      'app-menubar-item-icon text-sm',
      context.active && 'app-menubar-item-icon-active',
    ],
  }),

  itemLabel: ({ context }) => ({
    class: [
      'app-menubar-item-label whitespace-nowrap',
      context.active && 'app-menubar-item-label-active',
    ],
  }),

  submenu: {
    class: 'app-menubar-submenu border shadow-xl rounded-md py-1 min-w-[210px]',
  },

  submenuIcon: ({ context }) => ({
    class: [
      'ml-auto text-sm transition-transform app-menubar-submenu-icon',
      context.active && 'rotate-180 app-menubar-submenu-icon-active',
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
      { label: 'Project docs', icon: 'pi pi-book', command: () => showDocs() },
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

const openPreferences = () => doOpenPreferences()

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
