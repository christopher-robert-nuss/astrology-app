import { app, BrowserWindow, dialog, ipcMain, Menu, nativeTheme, shell } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import { spawn } from 'child_process'
import net from 'net'
import { existsSync, readFileSync, writeFileSync } from 'fs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const isPlaywright = process.env.PLAYWRIGHT === '1'
const useMockBackend = process.env.PLAYWRIGHT_ELECTRON_MOCK === '1'

let mainWindow
let backendProcess = null
let backendPort = 8080
let backendStartupPromise = null
let backendShutdownPromise = null
let isQuitting = false

function getMockApiResponse(method, endpoint) {
  if (method === 'GET' && endpoint === '/preferences/options') {
    return {
      zodiac_types: ['Tropical', 'Sidereal'],
      house_systems: [],
      aspects: [
        { key: 'conjunction', label: 'Conjunction', default_orb: 8 },
        { key: 'opposition', label: 'Opposition', default_orb: 8 },
        { key: 'trine', label: 'Trine', default_orb: 8 },
        { key: 'square', label: 'Square', default_orb: 8 },
        { key: 'sextile', label: 'Sextile', default_orb: 6 },
        { key: 'quincunx', label: 'Quincunx', default_orb: 3 },
        { key: 'semisextile', label: 'Semi-Sextile', default_orb: 2 },
        { key: 'semisquare', label: 'Semi-Square', default_orb: 2 },
        { key: 'sesquisquare', label: 'Sesquisquare', default_orb: 2 },
      ],
    }
  }

  if (method === 'GET' && endpoint === '/preferences') {
    return {
      zodiac_type: 'Tropical',
      houses_system: 'P',
      aspects_enabled: {
        conjunction: true,
        opposition: true,
        trine: true,
        square: true,
        sextile: true,
      },
    }
  }

  if (method === 'GET' && endpoint === '/ephemeris/status') {
    return {
      ephe_dir: '',
      exists: true,
      files: [],
    }
  }

  if (method === 'POST' && endpoint.startsWith('/ephemeris/ensure')) {
    return { ok: true }
  }

  if (method === 'POST' && endpoint === '/chart') {
    return {
      svg_path: '/mock-chart.svg',
    }
  }

  throw new Error(`No mock API response defined for ${method} ${endpoint}`)
}

function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer()

    server.once('error', () => resolve(false))
    server.once('listening', () => {
      server.close(() => resolve(true))
    })

    server.listen(port, '127.0.0.1')
  })
}

async function waitForBackendReady(port, { attempts = 50, delayMs = 200 } = {}) {
  const healthUrl = `http://127.0.0.1:${port}/preferences`

  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      const response = await fetch(healthUrl)
      if (response.ok) return
    } catch {
      // Backend not ready yet; keep polling.
    }

    await new Promise((resolve) => setTimeout(resolve, delayMs))
  }

  throw new Error(`Backend did not become ready on port ${port}`)
}

async function findAvailablePort(startPort = 8080, maxAttempts = 25) {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const port = startPort + attempt
    if (await isPortAvailable(port)) return port
  }

  throw new Error(`No available backend port found from ${startPort}`)
}

function getBackendLaunchConfig() {
  const isDev = !app.isPackaged

  if (isDev) {
    return {
      command: process.platform === 'win32' ? 'python' : 'python3',
      args: [path.join(__dirname, '../../backend/run_backend.py')],
      cwd: path.join(__dirname, '../../backend'),
    }
  }

  const backendDir = path.join(process.resourcesPath, 'backend')
  const backendBinary = path.join(
    backendDir,
    process.platform === 'win32' ? 'astrology-backend.exe' : 'astrology-backend',
  )

  if (existsSync(backendBinary)) {
    return {
      command: backendBinary,
      args: [],
      cwd: backendDir,
    }
  }

  throw new Error(`Packaged backend binary not found: ${backendBinary}`)
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
    },
    roundedCorners: false,
    frame: true, // Keep native window controls (GTK style)
  })

  // 🔥 Load Vite dev server during development
  const isDev = !app.isPackaged
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    if (!isPlaywright) {
      mainWindow.webContents.openDevTools()
    }
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist-renderer/index.html'))
  }

  // Remove default Electron menu (already present, kept for clarity)
  Menu.setApplicationMenu(null)

  // Optional: Send theme to renderer
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.send('theme-changed', nativeTheme.shouldUseDarkColors)
  })
}

// Start FastAPI backend
async function startBackend() {
  if (useMockBackend) return
  if (isQuitting) throw new Error('Cannot start backend while the app is quitting')
  if (backendStartupPromise) return backendStartupPromise
  if (backendProcess) return

  backendStartupPromise = (async () => {
    const launch = getBackendLaunchConfig()
    backendPort = await findAvailablePort(8080)
    if (isQuitting) throw new Error('Backend startup cancelled because the app is quitting')

    await new Promise((resolve, reject) => {
      backendProcess = spawn(launch.command, launch.args, {
        cwd: launch.cwd,
        env: {
          ...process.env,
          PORT: String(backendPort),
          ASTROLOGY_APP_DATA_DIR: app.getPath('userData'),
          ASTROLOGY_APP_PREFERENCES_PATH: path.join(app.getPath('userData'), 'preferences.json'),
        },
      })

      let settled = false

      backendProcess.once('error', (error) => {
        backendProcess = null
        if (!settled) reject(error)
      })

      backendProcess.once('close', (code) => {
        if (!settled) {
          reject(new Error(`Backend exited before startup completed (code ${code})`))
        }
        console.log(`[Backend] Exited with code ${code}`)
        backendProcess = null
      })

      backendProcess.stdout.on('data', (data) => console.log(`[Backend] ${data}`))
      backendProcess.stderr.on('data', (data) => console.error(`[Backend] ${data}`))

      waitForBackendReady(backendPort)
        .then(() => {
          settled = true
          resolve()
        })
        .catch((error) => {
          if (!settled) {
            backendProcess?.kill()
            backendProcess = null
            reject(error)
          }
        })
    })
  })()

  try {
    await backendStartupPromise
  } finally {
    backendStartupPromise = null
  }
}

function waitForProcessExit(processToStop) {
  if (processToStop.exitCode !== null || processToStop.signalCode !== null) {
    return Promise.resolve()
  }

  return new Promise((resolve) => {
    processToStop.once('close', resolve)
  })
}

async function stopBackend() {
  if (backendShutdownPromise) return backendShutdownPromise

  backendShutdownPromise = (async () => {
    if (!backendProcess && backendStartupPromise) {
      await backendStartupPromise.catch(() => {})
    }

    const processToStop = backendProcess
    backendProcess = null
    if (!processToStop) return

    const processExit = waitForProcessExit(processToStop)
    if (process.platform === 'win32' && processToStop.pid) {
      await new Promise((resolve, reject) => {
        const taskkill = spawn('taskkill', ['/pid', String(processToStop.pid), '/T', '/F'], {
          windowsHide: true,
        })
        taskkill.once('error', reject)
        taskkill.once('close', (code) => {
          if (code === 0 || code === 128) {
            resolve()
          } else {
            reject(new Error(`taskkill exited with code ${code}`))
          }
        })
      })
    } else {
      processToStop.kill()
    }

    await processExit
  })()

  try {
    await backendShutdownPromise
  } finally {
    backendShutdownPromise = null
  }
}

// IPC Handlers
ipcMain.handle('start-backend', async () => {
  await startBackend()
  return { success: true, url: `http://127.0.0.1:${backendPort}` }
})

ipcMain.handle('stop-backend', () => {
  return stopBackend().then(() => ({ success: true }))
})

ipcMain.handle('api-request', async (event, { method, endpoint, body }) => {
  if (useMockBackend) {
    return getMockApiResponse(method, endpoint)
  }

  await startBackend()
  const baseUrl = `http://127.0.0.1:${backendPort}`
  try {
    const response = await fetch(`${baseUrl}${endpoint}`, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    })
    const responseText = await response.text()
    let responseBody = null
    try {
      responseBody = responseText ? JSON.parse(responseText) : null
    } catch {
      responseBody = null
    }

    if (!response.ok) {
      const detail = responseBody?.detail || responseText || `HTTP ${response.status}`
      throw new Error(`HTTP ${response.status}: ${detail}`)
    }

    return responseBody
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
})

ipcMain.on('app-quit', () => {
  app.quit()
})

// ====================== FILE OPERATIONS ======================

function getRecentFilesPath() {
  return path.join(app.getPath('userData'), 'recent-files.json')
}

function readRecentFiles() {
  try {
    const filePath = getRecentFilesPath()
    if (existsSync(filePath)) {
      return JSON.parse(readFileSync(filePath, 'utf8'))
    }
  } catch (err) {
    console.warn('Could not read recent files:', err.message)
  }
  return []
}

function saveRecentFile(filePath, name) {
  try {
    let recent = readRecentFiles()
    recent = recent.filter((f) => f.filePath !== filePath)
    recent.unshift({ filePath, name })
    recent = recent.slice(0, 10)
    writeFileSync(getRecentFilesPath(), JSON.stringify(recent, null, 2), 'utf8')
  } catch (err) {
    console.warn('Could not save recent file:', err.message)
  }
}

ipcMain.handle('save-chart-file', async (event, data, suggestedName) => {
  const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
    title: 'Save Chart',
    defaultPath: `${suggestedName || 'chart'}.json`,
    filters: [{ name: 'Chart Files', extensions: ['json'] }],
  })
  if (canceled || !filePath) return { success: false }

  try {
    writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8')
    saveRecentFile(filePath, path.basename(filePath, '.json'))
    return { success: true, filePath }
  } catch (err) {
    console.error('Save chart failed:', err)
    throw new Error(`Failed to save file: ${err.message}`)
  }
})

ipcMain.handle('open-chart-file', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    title: 'Open Chart',
    filters: [{ name: 'Chart Files', extensions: ['json'] }],
    properties: ['openFile'],
  })
  if (canceled || !filePaths.length) return null

  try {
    const filePath = filePaths[0]
    const content = readFileSync(filePath, 'utf8')
    const data = JSON.parse(content)
    saveRecentFile(filePath, path.basename(filePath, '.json'))
    return { ...data, filePath }
  } catch (err) {
    console.error('Open chart failed:', err)
    throw new Error(`Failed to open file: ${err.message}`)
  }
})

ipcMain.handle('open-recent-file', async (event, filePath) => {
  try {
    if (!existsSync(filePath)) throw new Error('File not found')
    const content = readFileSync(filePath, 'utf8')
    const data = JSON.parse(content)
    saveRecentFile(filePath, path.basename(filePath, '.json'))
    return { ...data, filePath }
  } catch (err) {
    console.error('Open recent file failed:', err)
    throw new Error(`Failed to open file: ${err.message}`)
  }
})

ipcMain.handle('get-recent-files', () => {
  return readRecentFiles()
})

ipcMain.on('show-about', () => {
  let version = '1.0.0'
  let edition = 'Desktop Edition'

  try {
    const packageJson = JSON.parse(readFileSync(path.join(__dirname, '../package.json'), 'utf8'))
    version = packageJson.version || version
  } catch (err) {
    console.warn('Could not read package.json version:', err.message)
  }

  // Detect OS for edition label
  switch (process.platform) {
    case 'win32':
      edition = 'Windows Edition'
      break
    case 'darwin':
      edition = 'macOS Edition'
      break
    case 'linux':
      edition = 'Linux Edition'
      break
  }

  const aboutWindow = new BrowserWindow({
    width: 460,
    height: 420,
    parent: mainWindow,
    modal: true,
    resizable: false,
    minimizable: false,
    maximizable: false,
    frame: true,
    title: 'About Kerykeion Chart',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  const githubUrl = 'https://github.com/christopher-robert-nuss/astrology-app'

  const aboutHTML = `
    <html><head><meta charset="UTF-8"><style>
      body { font-family: system-ui, sans-serif; padding: 32px; text-align: center; background: #f8f9fa; }
      h1 { margin: 0 0 8px; font-size: 28px; }
      .version { color: #666; margin-bottom: 24px; }
      .info { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
      p {font-size: 14px; margin: 8px 0; color: #666;}
      .github-link {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #24292e;
        text-decoration: none;
        margin-top: 24px;
        font-size: 14px;
      }
      .github-link:hover { color: #0366d6; }
      .github-icon { width: 20px; height: 20px; }
    </style></head><body>
      <h1>Simple Astro Chart</h1>
      <p class="version">Version ${version} • ${edition}</p>

      <div class="info">
        <p class="text-xs"><strong>Simple, standalone and opensource astrological birth chart tool.</strong></p>
        <p>Powered by Kerykeion (Swiss Ephemeris) + Vue 3 + Python + Electron</p>
      </div>

      <p style="color:#555; margin-top: 20px;">
        2026 • Christopher Robert Nuss • <a href="mailto:chris@crn.net.au">chris@crn.net.au</a>
      </p>

      <!-- GitHub Link -->
      <a href="${githubUrl}" target="_blank" class="github-link">
        <svg class="github-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="#24292e" viewBox="0 0 24 24">
          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577 0-.285-.01-1.044-.015-2.049-3.338.726-4.042-1.416-4.042-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.652 1.652.242 2.873.118 3.176.77.84 1.235 1.91 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222 0 1.604-.015 2.896-.015 3.286 0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
        View on GitHub
      </a>
    </body></html>`

  // Intercept link clicks that open new windows
  aboutWindow.webContents.setWindowOpenHandler(({ url }) => {
    // Check if the URL is external (starts with http/https)
    if (url.startsWith('http://') || url.startsWith('https://')) {
      shell.openExternal(url)
      return { action: 'deny' } // Prevent Electron from opening a new window
    }
    return { action: 'allow' } // Allow internal navigation
  })

  aboutWindow.loadURL(`data:text/html,${encodeURIComponent(aboutHTML)}`)
})

app.whenReady().then(async () => {
  // Use a stable working directory so packaged child processes do not inherit stale/deleted cwd paths.
  try {
    process.chdir(app.getPath('home'))
  } catch (error) {
    console.warn('[App] Failed to update cwd:', error)
  }

  createWindow()
  startBackend().catch((error) => {
    console.error('[Backend] Failed to start:', error)
  })

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('before-quit', (event) => {
  if (isQuitting) return

  isQuitting = true
  event.preventDefault()
  stopBackend()
    .catch((error) => {
      console.error('[Backend] Failed to stop:', error)
    })
    .finally(() => {
      app.quit()
    })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
