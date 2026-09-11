import { flushPromises, shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App.vue'

describe('App', () => {
  beforeEach(() => {
    window.electronAPI = {
      startBackend: vi.fn().mockResolvedValue({ url: 'http://127.0.0.1:8080' }),
      apiRequest: vi.fn(async ({ endpoint }) => {
        if (endpoint === '/preferences/options') {
          return {
            zodiac_types: ['Tropical', 'Sidereal'],
            house_systems: [],
            aspects: [],
          }
        }

        if (endpoint === '/preferences') {
          return {
            zodiac_type: 'Tropical',
            houses_system: 'P',
            aspects_enabled: {},
          }
        }

        if (endpoint === '/ephemeris/status') {
          return {
            ephe_dir: '',
            exists: true,
            files: [],
          }
        }

        throw new Error(`Unhandled endpoint: ${endpoint}`)
      }),
      getRecentFiles: vi.fn().mockResolvedValue([]),
      saveChartFile: vi.fn(),
      openChartFile: vi.fn(),
      openRecentFile: vi.fn(),
    }
  })

  it('shows the empty chart state before any chart is generated', async () => {
    const wrapper = shallowMount(App)
    await flushPromises()

    expect(wrapper.text()).toContain('Natal chart workspace')
  })

  it('shows the loading overlay while a chart generation is in progress', async () => {
    const wrapper = shallowMount(App)
    await flushPromises()

    wrapper.vm.loading = true
    wrapper.vm.loadingStage = 'chart'
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Generating birth chart…')
  })
})
