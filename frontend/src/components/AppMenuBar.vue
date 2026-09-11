<template>
<div class="astro-menu-hover-guard" @mouseenter.capture.stop>
  <Menubar :model="items" breakpoint="640px" :pt="pt" :ptOptions="{ mergeProps: true }" />
  <AppStatusMessage />
</div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import Menubar from 'primevue/menubar'
import AppStatusMessage from './AppStatusMessage.vue'

const pt = {
  root: {
    class:
      'astro-menubar m-0 w-full rounded-none border-x-0 border-t-0 border-b border-[rgba(239,232,220,0.16)] bg-[#17191a] p-0 shadow-none',
    style: {
      borderRadius: '0',
      borderColor: 'rgba(239, 232, 220, 0.16)',
      backgroundColor: '#17191a',
      boxShadow: 'none',
    },
  },
  button: {
    class: 'astro-menu-button',
  },
  buttonicon: {
    class: 'astro-menu-button-icon',
  },
  rootList: {
    class: 'astro-menu-list m-0 flex w-full list-none bg-transparent p-0',
  },

  item: ({ context }) => ({
    class: [
      'astro-menu-item relative m-0 p-0 transition-colors duration-150',
      context.focused && 'outline-none',
    ],
  }),

  itemContent: ({ context }) => ({
    class: [
      'astro-menu-item-content flex w-full cursor-pointer items-center rounded-none bg-transparent',
      context.active && context.level === 0 && 'shadow-[inset_0_-2px_0_#c9a467]',
      context.level > 0 && 'hover:bg-[#2b302d]',
    ],
  }),

  itemLink: ({ context }) => ({
    class: [
      'astro-menu-link flex flex-1 items-center gap-x-2 rounded-none! no-underline transition-colors',
      context.level === 0 &&
        'text-[#bdb4a7] hover:text-[#f4eee4]',
      context.level > 0 &&
        'text-[#bdb4a7]',
      (context.active || context.focused) && 'text-[#f4eee4]',
    ],
    style:
      context.level === 0
        ? {
            padding: 'var(--astro-menu-root-padding-y) var(--astro-menu-root-padding-x)',
            color: context.active || context.focused ? '#f4eee4' : '#bdb4a7',
            fontSize: '0.7rem',
            fontWeight: '600',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
          }
        : {
            padding: 'var(--astro-menu-submenu-padding-y) var(--astro-menu-submenu-padding-x)',
            color: context.active || context.focused ? '#f4eee4' : '#bdb4a7',
            fontSize: 'var(--astro-menu-submenu-font-size)',
            fontWeight: '500',
          },
  }),

  itemIcon: {
    class: 'text-sm',
  },

  itemLabel: {
    class: 'whitespace-nowrap',
  },

  submenu: {
    class:
      'astro-submenu min-w-[196px] rounded-none border border-[#5c625e] bg-[#222625] py-0.5 shadow-xl',
    style: {
      minWidth: '210px',
      borderRadius: '0',
      borderColor: '#5c625e',
      backgroundColor: '#222625',
      boxShadow: '0 12px 30px rgba(0, 0, 0, 0.45)',
    },
  },

  submenuIcon: ({ context }) => ({
    class: ['ml-auto text-sm transition-transform', context.active && 'rotate-180'],
  }),

  // Separators
  separator: {
    class: 'astro-menu-separator my-1 border-t border-[#5c625e] mx-3',
  },
}

// Injected from App.vue
const doSaveChart = inject('saveChart', () => {})
const doSaveChartAs = inject('saveChartAs', () => {})
const doOpenChart = inject('openChart', () => {})
const doNewChart = inject('newChart', () => {})
const doOpenPreferences = inject('openPreferences', () => {})
const doOpenAbout = inject('openAbout', null)
const doPrintChart = inject('printChart', null)
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
  doNewChart()
}
const openChart = () => doOpenChart()
const saveChart = () => doSaveChart()
const saveChartAs = () => doSaveChartAs()

// In App.vue or your Menu Component
const handlePrint = async () => {
  if (doPrintChart) {
    doPrintChart()
    return
  }

  const img = document.querySelector('.print-chart-image')
  if (!img) return
  const printNow = () => window.setTimeout(() => window.print(), 100)
  if (img.complete) {
    printNow()
    return
  }
  img.onload = printNow
  img.onerror = printNow
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
  if (doOpenAbout) {
    doOpenAbout()
    return
  }
  if (window.electronAPI?.showAbout) {
    window.electronAPI.showAbout()
  }
}
</script>
