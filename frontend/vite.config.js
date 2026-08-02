import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import Components from 'unplugin-vue-components/vite'
import { PrimeVueResolver } from '@primevue/auto-import-resolver'
import tailwindcss from '@tailwindcss/vite'
import electron from 'vite-plugin-electron/simple' // Simple preset from docs

// https://vite.dev/config/
export default defineConfig(({ command }) => {
  const isServe = command === 'serve'

  return {
    plugins: [
      vue(),
      tailwindcss(),
      Components({
        resolvers: [PrimeVueResolver()],
      }),
      vueDevTools(),
      electron({
        main: {
          // Main process entry (create this file next)
          entry: 'electron/main.js',
          onstart({ startup }) {
            if (isServe) {
              startup() // Auto-start Electron in dev
            }
          },
        },
        // Preload optional for secure IPC (recommended for backend communication)
        preload: {
          input: 'electron/preload.js',
        },
        // Renderer polyfills (Node.js APIs if needed, but prefer IPC for backend)
        renderer: {},
      }),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      watch: {
        ignored: ['**/public/charts_output/**'],
      },
    },
    // Build output for Electron
    build: {
      outDir: 'dist-renderer',
    },
  }
})
