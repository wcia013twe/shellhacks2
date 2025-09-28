(() => {
  // ===== utils =====
  const INTERNAL_PREFIX = "__gaze_";
  const isInternalClass = (c) => c && c.startsWith(INTERNAL_PREFIX);
  const hasDigits = (s) => /\d/.test(s);
  const stableClass = (c) => c && c.length <= 32 && !hasDigits(c) && !isInternalClass(c); // skip hashed & internal
  const unique = (sel) => { try { return document.querySelectorAll(sel).length === 1; } catch { return false; } };

  const attrCandidates = (el) => {
    const out = [];
    for (const a of el.attributes || []) {
      const k = a.name;
      if (k.startsWith("data-") || k === "aria-label" || k === "name" || k === "role") {
        out.push(`[${CSS.escape ? CSS.escape(k) : k}="${a.value}"]`);
      }
    }
    return out;
  };

  // Temporarily remove ALL internal classes from a node, run fn(), then restore
  const withoutInternalClasses = (el, fn) => {
    if (!(el instanceof Element)) return fn();
    const removed = [];
    el.classList.forEach((c) => { if (isInternalClass(c)) { el.classList.remove(c); removed.push(c); } });
    try { return fn(); } finally { removed.forEach((c) => el.classList.add(c)); }
  };

  // Build a selector for one element (never html/body; never internal classes)
  const selectorFor = (el) => withoutInternalClasses(el, () => {
    if (!(el instanceof Element)) return null;

    // 1) Unique ID
    if (el.id && unique(`#${CSS.escape ? CSS.escape(el.id) : el.id}`)) {
      return `#${CSS.escape ? CSS.escape(el.id) : el.id}`;
    }

    // 2) Stable attributes
    for (const a of attrCandidates(el)) {
      const sel = `${el.tagName.toLowerCase()}${a}`;
      if (unique(sel)) return sel;
    }

    // 3) Tag + stable classes (up to 2), if unique (ignore internal classes)
    const classes = [...(el.classList || [])].filter(stableClass).slice(0, 2);
    if (classes.length) {
      const sel = `${el.tagName.toLowerCase()}` + classes.map(c => `.${CSS.escape ? CSS.escape(c) : c}`).join("");
      if (unique(sel)) return sel;
    }

    // 4) Fallback: tag with :nth-of-type if needed
    const tag = el.tagName.toLowerCase();
    let sibIndex = 1, sib = el;
    while ((sib = sib.previousElementSibling)) if (sib.tagName === el.tagName) sibIndex++;
    let base = `${tag}:nth-of-type(${sibIndex})`;
    if (unique(base)) return base;

    // 5) Climb minimal chain until unique (stop at body, but don't include it)
    const cleanParentSel = (p) => withoutInternalClasses(p, () => {
      if (p.id && unique(`#${CSS.escape ? CSS.escape(p.id) : p.id}`)) {
        return `#${CSS.escape ? CSS.escape(p.id) : p.id}`;
      }
      for (const a of attrCandidates(p)) {
        const s = `${p.tagName.toLowerCase()}${a}`;
        if (unique(s)) return s;
      }
      const pcs = [...(p.classList || [])].filter(stableClass).slice(0,2);
      if (pcs.length) return p.tagName.toLowerCase() + pcs.map(c=>`.`+(CSS.escape?CSS.escape(c):c)).join("");
      let n=1, x=p; while ((x = x.previousElementSibling)) if (x.tagName===p.tagName) n++;
      return `${p.tagName.toLowerCase()}:nth-of-type(${n})`;
    });

    const chain = [base];
    let p = el.parentElement;
    while (p && p !== document.body) {
      const pSel = cleanParentSel(p);
      const candidate = `${pSel} > ${chain.join(" > ")}`;
      if (unique(candidate)) return candidate;
      chain.unshift(pSel);
      p = p.parentElement;
    }

    // 6) If still not unique, return the chain (no html/body)
    return chain.join(" > ");
  });

  // ===== styles =====
  const ensureStyle = () => {
    if (document.getElementById("__gazeSetupNoRoot")) return;
    const s = document.createElement("style");
    s.id = "__gazeSetupNoRoot";
    s.textContent = `
      .${INTERNAL_PREFIX}glow{ outline:3px solid #1e90ff!important; outline-offset:2px!important; box-shadow:0 0 10px #1e90ff,0 0 20px rgba(30,144,255,.6)!important; border-radius:6px!important; transition:box-shadow .15s }
      .${INTERNAL_PREFIX}toast{ position:fixed; z-index:2147483647; left:50%; top:12px; transform:translateX(-50%); background:rgba(20,22,26,.92); color:#e6f0ff; padding:8px 12px; border-radius:8px; font:13px/1.45 system-ui; box-shadow:0 6px 18px rgba(0,0,0,.35); pointer-events:none }
      .${INTERNAL_PREFIX}hud{ position:fixed; z-index:2147483647; background:#0b1220; color:#e6f0ff; padding:6px; border-radius:10px; box-shadow:0 10px 30px rgba(0,0,0,.45); display:flex; gap:6px; align-items:center; }
      .${INTERNAL_PREFIX}btn{ min-width:28px; min-height:28px; border-radius:8px; border:1px solid #2b3652; background:#121b2f; color:#cfe1ff; cursor:pointer; font:600 13px/1 system-ui }
      .${INTERNAL_PREFIX}btn:hover{ background:#1a2540 }
      .${INTERNAL_PREFIX}small{ opacity:.8; font:12px/1.2 system-ui; margin-left:6px }
    `;
    document.head.appendChild(s);
  };

  const toast = (msg, ms=1400) => {
    const el = document.createElement("div");
    el.className = `${INTERNAL_PREFIX}toast`; el.textContent = msg;
    document.documentElement.appendChild(el);
    setTimeout(() => el.remove(), ms);
  };

  // ===== session (Alt+Click → rank 1–5, Esc to finish) =====
  if (window.__gazeSetup?.end) window.__gazeSetup.end(true);
  ensureStyle();

  const selByRank = new Map();
  let pendingEl = null, hud = null;

  const glowOn  = (el) => el && el.classList.add(`${INTERNAL_PREFIX}glow`);
  const glowOff = (el) => el && el.classList.remove(`${INTERNAL_PREFIX}glow`);

  const hideHUD = () => { hud?.remove(); hud = null; };
  const showHUD = (x, y, onPick) => {
    hideHUD();
    hud = document.createElement("div"); hud.className=`${INTERNAL_PREFIX}hud`; hud.tabIndex=-1;
    const mk = (n)=>{ const b=document.createElement("button"); b.className=`${INTERNAL_PREFIX}btn`; b.textContent=n; b.onclick=(e)=>{e.stopPropagation(); onPick(n); hideHUD();}; return b; };
    for(let i=1;i<=5;i++) hud.appendChild(mk(i));
    const tip=document.createElement("span"); tip.className=`${INTERNAL_PREFIX}small`; tip.textContent="Press 1–5 or click • Esc to finish"; hud.appendChild(tip);
    const pad=8, w=220, h=40, left=Math.min(Math.max(x-w/2,pad), innerWidth-w-pad), top=Math.min(Math.max(y+12,pad), innerHeight-h-pad);
    Object.assign(hud.style,{left:left+"px", top:top+"px", position:"fixed"}); document.documentElement.appendChild(hud); hud.focus({preventScroll:true});
  };

  const assignRank = (el, rank) => {
    const prev = selByRank.get(rank);
    if (prev?.el && prev.el !== el) glowOff(prev.el);

    // Build selector WITHOUT internal classes (temporarily strip them)
    const selector = selectorFor(el);
    selByRank.set(rank, { el, selector, tag: el.tagName.toLowerCase(), rank });
    glowOn(el); // keep glow only for ranked
    pendingEl = null;
    toast(`Assigned rank ${rank} to <${el.tagName.toLowerCase()}>`);
    // console.log(`rank ${rank} selector:`, selector);
  };

  const onKeyDown = (e) => {
    if (e.key === "Escape") { e.preventDefault(); end(); return; }
    const num = Number(e.key);
    if (pendingEl && Number.isInteger(num) && num>=1 && num<=5) {
      e.preventDefault(); assignRank(pendingEl, num); hideHUD();
    }
  };

  const onPointerDown = (e) => {
    const inHUD = e.target.closest(`.${INTERNAL_PREFIX}hud`);
    if (!(e.altKey && e.button === 0)) { if (!inHUD) { if (pendingEl) glowOff(pendingEl); pendingEl=null; hideHUD(); } return; }
    e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
    if (pendingEl) glowOff(pendingEl);
    const el = document.elementFromPoint(e.clientX, e.clientY);
    if (!el) return;
    pendingEl = el; glowOn(el); showHUD(e.clientX, e.clientY, (rank)=>assignRank(el, rank));
  };

  const saveProfile = () => {
    const ranks = {};
    for (const [rank, item] of selByRank.entries()) {
      ranks[String(rank)] = { selector: item.selector, tag: item.tag };
    }
    const profile = { version:1, url:location.href, origin:location.origin, path:location.pathname, saved_at:Date.now(), ranks };

    let serializedProfile = '';
    try {
      serializedProfile = JSON.stringify(profile);
      localStorage.setItem(`__gaze_profile__${location.origin}${location.pathname}`, serializedProfile);
    } catch (error) {
      console.error('Failed to cache profile in localStorage.', error);
    }

    try {
      const bridgeSaver = window.__gazeElectron?.saveProfile;
      if (typeof bridgeSaver === 'function') {
        const maybePromise = bridgeSaver(profile);
        if (maybePromise?.catch) {
          maybePromise.catch((err) => console.error('Electron bridge could not persist the profile.', err));
        }
      }
    } catch (error) {
      console.error('Error while invoking the Electron bridge to save the profile.', error);
    }

    if (serializedProfile) {
      try {
        console.log('__GAZE_PROFILE_SAVED__' + serializedProfile);
      } catch (error) {
        console.error('Failed to broadcast saved profile to the console.', error);
      }
    }

    return profile;
  };

  const end = (silent=false) => {
    removeEventListener("pointerdown", onPointerDown, true);
    removeEventListener("keydown", onKeyDown, true);
    hideHUD();
    if (pendingEl) glowOff(pendingEl);
    for (const {el} of selByRank.values()) glowOff(el);
    const profile = saveProfile();
    if (!silent) {
      toast('Profile saved for this URL');
      console.log('Profile saved for this URL.', profile);
    }
    window.__gazeSetup=undefined;
  };

  addEventListener("pointerdown", onPointerDown, true);
  addEventListener("keydown", onKeyDown, true);
  window.__gazeSetup = { end };
  console.log('Setup ready (selectors never include internal glow class). Alt+Click to rank 1-5. Esc to save.');
})();









