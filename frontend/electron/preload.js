const { contextBridge, shell, ipcRenderer } = require('electron')

console.log('Preload script running...')

contextBridge.exposeInMainWorld('electronAPI', {
  // Backend control
  startBackend: () => ipcRenderer.invoke('start-backend'),
  stopBackend: () => ipcRenderer.invoke('stop-backend'),

  // API proxy
  apiRequest: (options) => ipcRenderer.invoke('api-request', options),

  // Convenience methods
  savePerson: (data) =>
    ipcRenderer.invoke('api-request', { method: 'POST', endpoint: '/persons', body: data }),
  generateChart: (data) =>
    ipcRenderer.invoke('api-request', { method: 'POST', endpoint: '/chart', body: data }),
  listPersons: () => ipcRenderer.invoke('api-request', { method: 'GET', endpoint: '/persons' }),

  showAbout: () => ipcRenderer.send('show-about'),
  quitApp: () => ipcRenderer.send('app-quit'),

  // Open link in default browser
  openExternal: (url) => shell.openExternal(url),
})
