import { contextBridge, ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

const api = {
  gaze: {
    listScripts: () => ipcRenderer.invoke('gaze:listScripts'),
    getScript: (id) => ipcRenderer.invoke('gaze:getScript', id),
    copyScript: (id) => ipcRenderer.invoke('gaze:copyScript', id),
    runScript: (options) => ipcRenderer.invoke('gaze:runScript', options),
    onSessionEvent: (handler) => {
      if (typeof handler !== 'function') return () => {};
      const listener = (_event, payload) => handler(payload)
      ipcRenderer.on('gaze:session-event', listener)
      return () => ipcRenderer.removeListener('gaze:session-event', listener)
    }
  }
}

if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  window.electron = electronAPI
  window.api = api
}
