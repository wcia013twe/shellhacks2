(() => {
  // ========= utils (coords + deep hit-test) =========
  const PROFILE_KEY = (u = location) => `__gaze_profile__${u.origin}${u.pathname}`
  const toClient = (x, y, kind = 'client') => {
    const vv = window.visualViewport
    if (kind === 'client') return { x, y }
    if (kind === 'page') {
      return {
        x: x - (vv?.pageLeft ?? window.scrollX),
        y: y - (vv?.pageTop ?? window.scrollY)
      }
    }
    if (kind === 'normalized') return { x: x * window.innerWidth, y: y * window.innerHeight }
    if (kind === 'device') {
      const dpr = window.devicePixelRatio || 1
      return { x: x / dpr, y: y / dpr }
    }
    throw new Error('unknown coord kind')
  }
  const deepEl = (clientX, clientY, rootDoc = document) => {
    let el = rootDoc.elementFromPoint(clientX, clientY)
    if (!el) return null
    while (el && el.shadowRoot?.elementFromPoint) {
      const deeper = el.shadowRoot.elementFromPoint(clientX, clientY)
      if (!deeper || deeper === el) break
      el = deeper
    }
    if (el?.tagName === 'IFRAME') {
      const r = el.getBoundingClientRect()
      try {
        const d = el.contentDocument
        if (d) {
          const inside = deepEl(clientX - r.left, clientY - r.top, d)
          if (inside) return inside
        }
      } catch (error) {
        console.warn('Skipping cross-origin iframe during deep element lookup.', error)
      }
    }
    return el
  }

  // ========= load profile =========
  const profile = (() => {
    try {
      return JSON.parse(localStorage.getItem(PROFILE_KEY()) || 'null')
    } catch {
      return null
    }
  })()
  console.log('🗂️ Loaded gaze profile:', profile)
  if (!profile?.ranks) {
    console.warn('No saved gaze profile for this URL.')
  }

  // ========= build rank records (rank -> {selector, resolve()}) =========
  const ranks = new Map()
  if (profile?.ranks) {
    for (const [rankStr, info] of Object.entries(profile.ranks)) {
      const rank = Number(rankStr)
      const selector = info.selector
      const resolve = () => {
        try {
          return document.querySelector(selector)
        } catch {
          return null
        }
      }
      ranks.set(rank, { selector, resolve })
    }
  }

  // ========= selector maps =========
  const ranksBySelector = {}
  for (const [rank, rec] of ranks.entries()) {
    const s = rec.selector
    if (!(s in ranksBySelector) || rank < ranksBySelector[s]) ranksBySelector[s] = rank
  }

  const occurrencesBySelector = {}
  Object.keys(ranksBySelector).forEach((sel) => {
    occurrencesBySelector[sel] = 0
  })

  const byRankCounts = { r1: 0, r2: 0, r3: 0, r4: 0, r5: 0, unmatched: 0 }

  const isWithinRankElement = (candidate, rec) => {
    const target = rec.resolve()
    if (!candidate || !target) return false
    let node = candidate instanceof Element ? candidate : candidate?.parentElement
    while (node) {
      if (node === target) return true
      if (node.parentElement) {
        node = node.parentElement
        continue
      }
      const root = node.getRootNode?.()
      if (root?.host) {
        node = root.host
        continue
      }
      const frameEl = node.ownerDocument?.defaultView?.frameElement
      if (frameEl) {
        node = frameEl
        continue
      }
      break
    }
    return false
  }

  const record = (x, y, kind = 'client') => {
    const { x: cx, y: cy } = toClient(x, y, kind)
    const el = deepEl(cx, cy)

    let hitRank = null
    let hitSelector = null
    for (const [rank, rec] of ranks.entries()) {
      if (isWithinRankElement(el, rec)) {
        hitRank = rank
        hitSelector = rec.selector
        break
      }
    }

    if (hitRank) {
      byRankCounts[`r${hitRank}`] += 1
      occurrencesBySelector[hitSelector] = (occurrencesBySelector[hitSelector] || 0) + 1
      return hitRank
    }
    byRankCounts.unmatched += 1
    return null
  }

  let clickHandler = null
  const clickOn = () => {
    if (clickHandler) return
    clickHandler = (event) => {
      if (!event.altKey || event.button !== 0) return
      event.preventDefault()
      event.stopPropagation()
      event.stopImmediatePropagation()
      const rank = record(event.clientX, event.clientY, 'client')
      console.log('sample →', rank ? `rank ${rank}` : 'unmatched', {
        byRankCounts,
        occurrencesBySelector
      })
    }
    addEventListener('click', clickHandler, true)
    console.log('🟦 Play test: Alt+Click to sample points (Esc to stop)')
    const keyHandler = (event) => {
      if (event.key === 'Escape') {
        clickOff()
        removeEventListener('keydown', keyHandler, true)
      }
    }
    addEventListener('keydown', keyHandler, true)
  }

  const clickOff = () => {
    if (!clickHandler) return
    removeEventListener('click', clickHandler, true)
    clickHandler = null
    console.log('🟦 Play test OFF')
  }

  const end = () => {
    clickOff()
    console.log('🏷️ ranksBySelector =', JSON.stringify(ranksBySelector, null, 2))
    console.log('🔢 occurrencesBySelector =', JSON.stringify(occurrencesBySelector, null, 2))
    return { ranksBySelector, occurrencesBySelector, countsByRank: byRankCounts }
  }

  const runFor = async (ms = 10000, autoClick = true) => {
    if (autoClick) clickOn()
    console.log(`⏱️ Running gaze session for ${ms}ms`)
    await new Promise((resolve) => {
      setTimeout(resolve, ms)
    })
    const result = end()
    console.log('✅ Session finished:', result)
    return result
  }

  window.__gazePlay = {
    record,
    clickOn,
    clickOff,
    end,
    runFor,
    countsByRank: byRankCounts,
    ranksBySelector,
    occurrencesBySelector,
    profile,
    ranks
  }

  console.log(
    profile
      ? '✅ Loaded profile. Call __gazePlay.runFor(ms) or feed __gazePlay.record(x,y,kind).'
      : '⚠️ No profile found for this URL. Run the setup script first.'
  )
})()
