import { readFileSync } from 'fs'
import { mkdir, writeFile } from 'fs/promises'
import { fileURLToPath } from 'url'
import { app, shell, BrowserWindow, ipcMain, clipboard } from 'electron'
import { join, dirname } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const scriptCatalog = [
  {
    id: 'setup',
    title: 'Setup Script',
    description: 'Label key UI targets and save a gaze profile for this page.',
    filename: 'setup.js',
    steps: [
      'Open the target page in a Chromium-based browser.',
      'Launch DevTools (F12) and switch to the Console tab.',
      'Paste the script and press Enter.',
      'Hold Alt and click elements you want to rank, then choose 1–5.',
      'Press Esc when you are done to save the profile locally.'
    ]
  },
  {
    id: 'play',
    title: 'Play Script',
    description: 'Load the saved profile and record gaze hits for its selectors.',
    filename: 'play.js',
    steps: [
      'Open the same page after you already ran the setup script.',
      'Open the DevTools Console and paste the script.',
      'Feed gaze coordinates by calling __gazePlay.record or enable Alt+Click sampling.',
      'Call __gazePlay.end() when finished to review counts per selector.'
    ]
  }
]

const PROFILE_LOG_PREFIX = '__GAZE_PROFILE_SAVED__'

const scriptCache = new Map()
let mainWindow = null
let sessionCounter = 0
const sessionRegistry = new Map()
let profileDirPath = null

const ensureProfileDir = async () => {
  if (profileDirPath) {
    return profileDirPath
  }
  profileDirPath = join(app.getPath('userData'), 'gaze-profiles')
  await mkdir(profileDirPath, { recursive: true })
  return profileDirPath
}

const sanitizeSegment = (input) => {
  const value = (input || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
  return value || 'profile'
}

const buildProfileFilename = (profile) => {
  const candidateUrl = profile?.url || (profile?.origin ? `${profile.origin}${profile.path || ''}` : '')
  try {
    const parsed = new URL(candidateUrl)
    const host = sanitizeSegment(parsed.hostname)
    const rawPath = parsed.pathname && parsed.pathname !== '/' ? parsed.pathname.replace(/\//g, '-') : 'root'
    const pathSegment = sanitizeSegment(rawPath)
    return `${host}-${pathSegment}.json`
  } catch {
    const originSegment = sanitizeSegment(profile?.origin)
    return `${originSegment}.json`
  }
}

const saveProfileToDisk = async (profile) => {
  const dir = await ensureProfileDir()
  const fileName = buildProfileFilename(profile)
  const filePath = join(dir, fileName)
  await writeFile(filePath, JSON.stringify(profile, null, 2), 'utf-8')
  return filePath
}

const getResourcesRoot = () => {
  if (app.isPackaged) {
    return join(process.resourcesPath, 'resources')
  }
  return join(__dirname, '../../resources')
}

const loadScript = (id) => {
  const cached = scriptCache.get(id)
  if (cached) {
    return cached
  }

  const entry = scriptCatalog.find((item) => item.id === id)
  if (!entry) {
    return null
  }

  try {
    const scriptPath = join(getResourcesRoot(), 'scripts', entry.filename)
    const code = readFileSync(scriptPath, 'utf-8')
    const payload = { ...entry, code }
    scriptCache.set(id, payload)
    return payload
  } catch (error) {
    console.error(`[gaze] Failed to load script ${id}:`, error)
    return null
  }
}

const broadcast = (channel, payload) => {
  if (!mainWindow || mainWindow.isDestroyed()) {
    return
  }
  mainWindow.webContents.send(channel, payload)
}

const normaliseUrl = (rawUrl) => {
  try {
    const parsed = new URL(rawUrl)
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      throw new Error('Only http and https URLs are supported.')
    }
    return parsed.toString()
  } catch {
    throw new Error('Please enter a valid URL (http/https).')
  }
}

const openSessionWindow = ({ url, mode, durationSeconds }) => {
  const sessionId = ++sessionCounter
  const sessionWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    show: true,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  const contents = sessionWindow.webContents

  const handleConsoleMessage = (_event, level, message) => {
    if (typeof message !== 'string' || !message.startsWith(PROFILE_LOG_PREFIX)) {
      return
    }
    const payload = message.slice(PROFILE_LOG_PREFIX.length)
    if (!payload) {
      return
    }

    try {
      const profile = JSON.parse(payload)
      ;(async () => {
        try {
          const profilePath = await saveProfileToDisk(profile)
          broadcast('gaze:session-event', {
            sessionId,
            type: 'profile-saved',
            mode,
            profile,
            profilePath
          })
        } catch (error) {
          console.error('[gaze] Failed to persist profile to disk:', error)
          broadcast('gaze:session-event', {
            sessionId,
            type: 'error',
            mode,
            message: error?.message || 'Unable to save the profile to disk.'
          })
        }
      })()
    } catch (error) {
      console.error('[gaze] Failed to parse saved profile payload:', error)
    }
  }

  contents.on('console-message', handleConsoleMessage)

  sessionRegistry.set(sessionId, { window: sessionWindow, mode })

  sessionWindow.once('closed', () => {
    try {
      if (!contents.isDestroyed()) {
        contents.removeListener('console-message', handleConsoleMessage)
      }
    } catch (error) {
      console.warn('[gaze] Failed to remove console listener:', error)
    }
    sessionRegistry.delete(sessionId)
    broadcast('gaze:session-event', {
      sessionId,
      type: 'closed',
      mode
    })
  })

  const run = async () => {
    const script = loadScript(mode)
    if (!script) {
      throw new Error(`Script "${mode}" not found.`)
    }

    try {
      await contents.executeJavaScript(script.code, true)
    } catch (error) {
      if (sessionWindow.isDestroyed() || contents.isDestroyed()) {
        return
      }
      throw error
    }

    broadcast('gaze:session-event', {
      sessionId,
      type: 'script-ready',
      mode
    })

    if (mode !== 'play') {
      return
    }

    const durationMs = Math.max(1, Number(durationSeconds) || 0) * 1000
    broadcast('gaze:session-event', {
      sessionId,
      type: 'running',
      mode,
      durationMs
    })

    if (sessionWindow.isDestroyed() || contents.isDestroyed()) {
      return
    }

    let result = null
    try {
      result = await contents.executeJavaScript(
        `(() => {
          if (!window.__gazePlay?.runFor) {
            throw new Error('Play runtime did not initialise.');
          }
          return window.__gazePlay.runFor(${durationMs}, false);
        })();`,
        true
      )
    } catch (error) {
      if (sessionWindow.isDestroyed() || contents.isDestroyed()) {
        return
      }
      throw error
    }

    broadcast('gaze:session-event', {
      sessionId,
      type: 'completed',
      mode,
      result
    })
  }

  contents.once('did-finish-load', async () => {
    if (sessionWindow.isDestroyed()) {
      return
    }

    try {
      await run()
    } catch (error) {
      console.error('[gaze] Session failed:', error)
      broadcast('gaze:session-event', {
        sessionId,
        type: 'error',
        mode,
        message: error?.message || 'Unable to run the script.'
      })
    }
  })

  contents.once('did-fail-load', (_event, errorCode, errorDescription) => {
    broadcast('gaze:session-event', {
      sessionId,
      type: 'error',
      mode,
      message: `Failed to load page: ${errorDescription || errorCode}`
    })
  })

  sessionWindow
    .loadURL(url)
    .then(() => {
      broadcast('gaze:session-event', {
        sessionId,
        type: 'navigated',
        mode,
        url
      })
    })
    .catch((error) => {
      console.error('[gaze] Unable to load URL', error)
      broadcast('gaze:session-event', {
        sessionId,
        type: 'error',
        mode,
        message: error?.message || 'Unable to open the requested URL.'
      })
    })

  broadcast('gaze:session-event', {
    sessionId,
    type: 'created',
    mode,
    url
  })

  return { sessionId }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

app.whenReady().then(async () => {
  electronApp.setAppUserModelId('com.electron')

  try {
    await ensureProfileDir()
  } catch (error) {
    console.error('[gaze] Unable to prepare profile directory:', error)
  }

  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  ipcMain.on('ping', () => console.log('pong'))

  ipcMain.handle('gaze:listScripts', () =>
    scriptCatalog.map((item) => {
      const entry = { ...item }
      delete entry.filename
      return entry
    })
  )

  ipcMain.handle('gaze:getScript', (_, id) => {
    const payload = loadScript(id)
    if (!payload) {
      throw new Error(`Script "${id}" not found.`)
    }
    const { code } = payload
    const meta = { ...payload }
    delete meta.filename
    delete meta.code
    return { ...meta, code }
  })

  ipcMain.handle('gaze:copyScript', (_, id) => {
    const payload = loadScript(id)
    if (!payload) {
      throw new Error(`Script "${id}" not found.`)
    }
    clipboard.writeText(payload.code)
    return { success: true }
  })

  ipcMain.handle('gaze:runScript', (_, options = {}) => {
    const mode = options.mode === 'play' ? 'play' : 'setup'
    const url = normaliseUrl(options.url || '')
    if (mode === 'play' && (!options.durationSeconds || Number(options.durationSeconds) <= 0)) {
      throw new Error('Please provide a positive duration for play sessions.')
    }
    return openSessionWindow({ url, mode, durationSeconds: options.durationSeconds })
  })

  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
