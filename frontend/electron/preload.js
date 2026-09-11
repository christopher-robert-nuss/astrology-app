const { contextBridge, shell, ipcRenderer } = require('electron')

console.log('Preload script running...')

contextBridge.exposeInMainWorld('electronAPI', {
  // Backend control
  startBackend: () => ipcRenderer.invoke('start-backend'),
  stopBackend: () => ipcRenderer.invoke('stop-backend'),

  // API proxy
  apiRequest: (options) => ipcRenderer.invoke('api-request', options),

  // File operations
  saveChartFile: (data, suggestedName, existingPath) =>
    ipcRenderer.invoke('save-chart-file', data, suggestedName, existingPath),
  openChartFile: () => ipcRenderer.invoke('open-chart-file'),
  openRecentFile: (filePath) => ipcRenderer.invoke('open-recent-file', filePath),
  getRecentFiles: () => ipcRenderer.invoke('get-recent-files'),

  showAbout: () => ipcRenderer.send('show-about'),
  quitApp: () => ipcRenderer.send('app-quit'),

  // Open link in default browser
  openExternal: (url) => shell.openExternal(url),
})
