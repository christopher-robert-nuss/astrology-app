<template>
  <Menubar
    :model="items"
    breakpoint="100px"
    :pt="pt"
    :ptOptions="{ mergeProps: true }"
  />
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import Menubar from 'primevue/menubar'

const pt = {
  root: {
    class:
      'm-0 w-full rounded-none border-x-0 border-t-0 border-b border-[rgba(168,176,214,0.45)] bg-[rgba(247,249,255,0.72)] p-0 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] backdrop-blur-[8px]',
  },
  rootList: {
    class: 'm-0 flex w-full list-none bg-transparent p-0',
  },

  item: ({ context }) => ({
    class: [
      'relative m-0 p-0 transition-colors duration-150',
      context.focused && 'outline-none',
    ],
  }),

  itemContent: ({ context }) => ({
    class: [
      'flex w-full cursor-pointer items-center gap-x-2 rounded-none bg-transparent',
      context.active && context.level === 0 && 'shadow-[inset_0_-2px_0_#8a95d4]',
      context.level > 0 && 'hover:bg-[rgba(225,231,255,0.42)]',
    ],
  }),

  itemLink: ({ context }) => ({
    class: [
      'flex flex-1 items-center gap-x-2 rounded-none! no-underline transition-colors',
      context.level === 0 &&
        'px-[1.1rem] py-[0.42rem] text-[0.73rem] font-semibold uppercase tracking-[0.09em] text-[#4a5577] hover:text-[#2f3a5a]',
      context.level > 0 &&
        'px-[0.86rem] py-[0.52rem] text-[0.84rem] font-medium normal-case tracking-normal text-[#455170]',
      (context.active || context.focused) && 'text-[#2f3a5a]',
    ],
  }),

  itemIcon: {
    class: 'text-sm',
  },

  itemLabel: {
    class: 'whitespace-nowrap',
  },

  submenu: {
    class: 'min-w-[210px] rounded-md border border-[#d3d8ef] bg-[rgba(252,253,255,0.98)] py-1 shadow-xl',
  },

  submenuIcon: ({ context }) => ({
    class: [
      'ml-auto text-sm transition-transform',
      context.active && 'rotate-180',
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
