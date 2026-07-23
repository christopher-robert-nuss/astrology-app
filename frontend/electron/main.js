import { app, BrowserWindow, ipcMain, Menu, nativeTheme } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import { spawn } from 'child_process'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
process.env.NODE_ENV = process.env.NODE_ENV || 'development'

let mainWindow
let backendProcess = null

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
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.webContents.openDevTools() // Optional: Open DevTools for debugging

  // Remove default Electron menu (already present, kept for clarity)
  Menu.setApplicationMenu(null)

  // Optional: Send theme to renderer
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.send('theme-changed', nativeTheme.shouldUseDarkColors)
  })
}

// Start Python FastAPI backend
function startBackend() {
  if (backendProcess) return backendProcess

  const backendPath = path.join(__dirname, '../../backend/run_backend.py')
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3'

  backendProcess = spawn(pythonCmd, [backendPath], {
    cwd: path.join(__dirname, '../../backend'),
    env: { ...process.env, PORT: '8080' },
  })

  backendProcess.stdout.on('data', (data) => console.log(`[Backend] ${data}`))
  backendProcess.stderr.on('data', (data) => console.error(`[Backend] ${data}`))
  backendProcess.on('close', (code) => {
    console.log(`[Backend] Exited with code ${code}`)
    backendProcess = null
  })

  return new Promise((resolve) => setTimeout(resolve, 1500))
}

// IPC Handlers (unchanged)
ipcMain.handle('start-backend', async () => {
  await startBackend()
  return { success: true, url: 'http://127.0.0.1:8080' }
})

ipcMain.handle('stop-backend', () => {
  if (backendProcess) {
    backendProcess.kill()
    backendProcess = null
  }
  return { success: true }
})

ipcMain.handle('api-request', async (event, { method, endpoint, body }) => {
  const baseUrl = 'http://127.0.0.1:8080'
  try {
    const response = await fetch(`${baseUrl}${endpoint}`, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
})

ipcMain.on('app-quit', () => {
  if (backendProcess) backendProcess.kill()
  app.quit()
})

ipcMain.on('show-about', () => {
  const aboutWin = new BrowserWindow({
    width: 460,
    height: 420,
    parent: mainWindow,
    modal: true,
    resizable: false,
    minimizable: false,
    maximizable: false,
    frame: true, // GTK-style title bar
    title: 'About Kerykeion Chart',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  // Simple inline HTML for GTK-like About dialog
  const aboutHTML = `
    <html><head><style>
      body { font-family: system-ui, sans-serif; padding: 32px; text-align: center; background: #f8f9fa; }
      h1 { margin: 0 0 8px; font-size: 28px; }
      .version { color: #666; margin-bottom: 24px; }
      .info { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style></head><body>
      <h1>Kerykeion Chart</h1>
      <p class="version">Version 1.0.0 • Linux Edition</p>
      
      <div class="info">
        <p><strong>Simple, standalone astrological birth chart tool.</strong></p>
        <p>Powered by Kerykeion (Swiss Ephemeris) + Vue 3 + Electron</p>
      </div>
      
      <p style="color:#555; margin-top: 20px;">
        © 2026 • Built for accurate offline chart calculation.
      </p>
    </body></html>`

  aboutWin.loadURL(`data:text/html,${encodeURIComponent(aboutHTML)}`)
})

app.whenReady().then(async () => {
  await startBackend()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill()
  if (process.platform !== 'darwin') app.quit()
})
