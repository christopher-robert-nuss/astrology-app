import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import Components from 'unplugin-vue-components/vite'
import { PrimeVueResolver } from '@primevue/auto-import-resolver'
import tailwindcss from '@tailwindcss/vite'
import electron from 'vite-plugin-electron/simple'

export default defineConfig(({ command }) => {
  const isServe = command === 'serve'
  const webOnlyMode = process.env.VITE_WEB_ONLY === '1'

  return {
    plugins: [
      vue(),
      tailwindcss(),
      Components({
        resolvers: [PrimeVueResolver()],
      }),
      vueDevTools(),
      ...(!webOnlyMode
        ? [
            electron({
              main: {
                entry: 'electron/main.js',
                onstart({ startup }) {
                  if (isServe) {
                    startup()
                  }
                },
              },
              preload: {
                input: 'electron/preload.js',
              },
              renderer: {},
            }),
          ]
        : []),
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
    build: {
      outDir: 'dist-renderer',
    },
    test: {
      environment: 'jsdom',
      globals: true,
      setupFiles: './src/test/setup.js',
      include: ['src/**/*.spec.{js,ts,jsx,tsx}'],
    },
  }
})
