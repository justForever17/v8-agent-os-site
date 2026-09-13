/* Progressive enhancements: content and navigation also work without JavaScript. */
(() => {
  "use strict";
  const root = document.documentElement;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const panels = [...document.querySelectorAll("[data-tab-panel]")];
  const menuButton = document.querySelector(".menu-button");
  const navigation = document.querySelector(".navigation");
  const motionButton = document.querySelector(".motion-toggle");
  let manuallyPaused = false;
  try { manuallyPaused = localStorage.getItem("v8-site-motion") === "paused"; } catch { /* Storage is optional. */ }
  const motionPaused = () => manuallyPaused || reducedMotion.matches;

  document.querySelectorAll("[data-tab-group]").forEach(group => {
  const tabs = [...group.querySelectorAll("[data-tab]")];
  const groupPanels = [...group.querySelectorAll("[data-tab-panel]")];
  const tabList = group.querySelector("[data-tab-list]");
  function choosePanel(id, moveFocus = false, updateHash = false, animate = true) {
    const selected = tabs.find(tab => tab.dataset.tab === id);
    if (!selected) return;
    tabs.forEach(tab => {
      const active = tab === selected;
      tab.classList.toggle("is-active", active);
      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    groupPanels.forEach(panel => {
      const active = panel.id === id;
      panel.classList.toggle("is-active", active);
      panel.hidden = !active;
      panel.getAnimations().forEach(animation => animation.cancel());
      if (active && animate && !motionPaused()) {
        panel.animate([{ opacity: .35, transform: "translateY(7px)" }, { opacity: 1, transform: "translateY(0)" }], { duration: 280, easing: "cubic-bezier(.22,1,.36,1)" });
      }
    });
    if (moveFocus) selected.focus({ preventScroll: true });
    if (updateHash) history.replaceState(null, "", `#${id}`);
  }
  tabList?.setAttribute("role", "tablist");
  tabs.forEach((tab, index) => {
    tab.setAttribute("role", "tab");
    tab.setAttribute("aria-controls", tab.dataset.tab);
    tab.addEventListener("click", event => { event.preventDefault(); choosePanel(tab.dataset.tab, false, true); });
    tab.addEventListener("keydown", event => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); choosePanel(tabs[next].dataset.tab, true, true, false); }
    });
  });
  groupPanels.forEach(panel => { panel.setAttribute("role", "tabpanel"); panel.tabIndex = 0; });
  function readPanelHash() {
    const id = location.hash.slice(1);
    if (tabs.some(tab => tab.dataset.tab === id)) choosePanel(id, false, false, false);
  }
  choosePanel(tabs[0]?.dataset.tab, false, false, false);
  readPanelHash();
  window.addEventListener("hashchange", readPanelHash);
  });

  function closeMenu(restoreFocus = false) {
    navigation?.classList.remove("is-open");
    menuButton?.setAttribute("aria-expanded", "false");
    if (restoreFocus) menuButton?.focus();
  }
  menuButton?.addEventListener("click", () => {
    const open = menuButton.getAttribute("aria-expanded") !== "true";
    navigation.classList.toggle("is-open", open);
    menuButton.setAttribute("aria-expanded", String(open));
  });
  navigation?.querySelectorAll("a").forEach(link => link.addEventListener("click", () => closeMenu()));
  document.addEventListener("click", event => {
    if (!navigation?.contains(event.target) && !menuButton?.contains(event.target)) closeMenu();
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && navigation?.classList.contains("is-open")) closeMenu(true);
  });
  window.matchMedia("(max-width: 760px)").addEventListener("change", () => closeMenu());

  const revealObserver = "IntersectionObserver" in window ? new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.remove("is-reveal-pending");
      entry.target.classList.add("is-revealed");
      revealObserver.unobserve(entry.target);
    });
  }, { threshold: .08, rootMargin: "0px 0px -24px 0px" }) : null;
  if (!motionPaused() && revealObserver) {
    document.querySelectorAll("[data-reveal]").forEach(element => {
      if (element.getBoundingClientRect().top > window.innerHeight) {
        element.classList.add("is-reveal-pending");
        revealObserver.observe(element);
      }
    });
  }
  function syncMotion() {
    root.classList.toggle("motion-paused", motionPaused());
    motionButton?.setAttribute("aria-pressed", String(motionPaused()));
    const label = motionButton?.querySelector("[data-motion-label]");
    if (label) label.textContent = motionPaused() ? motionButton.dataset.resume : motionButton.dataset.pause;
    if (motionPaused()) {
      revealObserver?.disconnect();
      document.querySelectorAll(".is-reveal-pending").forEach(element => element.classList.remove("is-reveal-pending"));
      panels.forEach(panel => panel.getAnimations().forEach(animation => animation.cancel()));
    }
    motionButton.disabled = reducedMotion.matches;
    if (reducedMotion.matches && label) label.textContent = document.body.dataset.locale === "zh" ? "已遵循系统减少动态效果设置" : "System reduced motion is on";
  }
  motionButton?.addEventListener("click", () => {
    manuallyPaused = !manuallyPaused;
    try { localStorage.setItem("v8-site-motion", manuallyPaused ? "paused" : "enabled"); } catch { /* Preference still applies to this visit. */ }
    syncMotion();
  });
  reducedMotion.addEventListener("change", syncMotion);
  syncMotion();
  let heroVisible = true;
  let scrollFrame = 0;
  const stage = document.querySelector(".orbit-stage");
  const precisePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  const pointerEnabled = () => precisePointer.matches && !motionPaused() && !document.hidden;
  const orbitPointer = { x: 0, y: 0, targetX: 0, targetY: 0, previousTime: 0 };
  const clamp = value => Math.max(-1, Math.min(1, value));
  function updateStage(time = 0) {
    scrollFrame = 0;
    if (motionPaused() || window.innerWidth <= 760 || document.hidden) {
      stage.style.transform = "";
      orbitPointer.x = orbitPointer.y = orbitPointer.targetX = orbitPointer.targetY = 0;
      return;
    }
    const alpha = 1 - Math.exp(-Math.min(64, time - orbitPointer.previousTime || 16) / 100);
    orbitPointer.previousTime = time;
    orbitPointer.x += (orbitPointer.targetX - orbitPointer.x) * alpha;
    orbitPointer.y += (orbitPointer.targetY - orbitPointer.y) * alpha;
    const progress = Math.min(1, Math.max(0, window.scrollY / window.innerHeight));
    stage.style.transform = `translateX(calc(-50% + ${orbitPointer.x * 18}px)) translateY(${-progress * 45 + orbitPointer.y * 8}px) perspective(1200px) rotateX(${-orbitPointer.y * 4}deg) rotateY(${orbitPointer.x * 6}deg) scale(${1 + progress * .055})`;
    if (heroVisible && Math.abs(orbitPointer.targetX - orbitPointer.x) + Math.abs(orbitPointer.targetY - orbitPointer.y) > .002) scheduleStage();
  }
  function scheduleStage() { if (!scrollFrame) scrollFrame = requestAnimationFrame(updateStage); }
  const updateAmbient = () => { root.classList.toggle("motion-offscreen", !heroVisible || document.hidden); if (heroVisible) scheduleStage(); };
  window.addEventListener("scroll", () => { if (heroVisible && !document.hidden) scheduleStage(); }, { passive: true });
  window.addEventListener("resize", scheduleStage);
  reducedMotion.addEventListener("change", scheduleStage);
  motionButton?.addEventListener("click", scheduleStage);
  if ("IntersectionObserver" in window) {
    const heroObserver = new IntersectionObserver(entries => { heroVisible = entries[0].isIntersecting; updateAmbient(); });
    heroObserver.observe(document.querySelector(".hero"));
  }
  document.addEventListener("visibilitychange", updateAmbient);
  const hero = document.querySelector(".hero");
  hero.addEventListener("pointermove", event => {
    if (!pointerEnabled() || event.pointerType !== "mouse" || window.innerWidth <= 760) return;
    const rect = hero.getBoundingClientRect();
    orbitPointer.targetX = clamp((event.clientX - rect.left) / rect.width * 2 - 1);
    orbitPointer.targetY = clamp((event.clientY - rect.top) / rect.height * 2 - 1);
    scheduleStage();
  });
  const releaseOrbit = () => { orbitPointer.targetX = orbitPointer.targetY = 0; scheduleStage(); };
  hero.addEventListener("pointerleave", releaseOrbit);
  precisePointer.addEventListener("change", releaseOrbit);

  // Animate only the surface under the mouse, then stop the frame loop once settled.
  // Hit targets stay in place; button light moves inside the existing button bounds.
  const pointerResets = [];
  document.querySelectorAll(".media-frame, .builder-tile, .button-primary, .header-cta").forEach(surface => {
    const tilt = surface.matches(".media-frame, .builder-tile");
    const baseTransform = getComputedStyle(surface).transform;
    const glow = document.createElement("span");
    glow.className = "pointer-glow";
    glow.setAttribute("aria-hidden", "true");
    surface.append(glow);
    let frame = 0, x = 0, y = 0, targetX = 0, targetY = 0, previousTime = 0, bounds;
    function paint(time) {
      frame = 0;
      if (!pointerEnabled()) { reset(); return; }
      const alpha = 1 - Math.exp(-Math.min(64, time - previousTime || 16) / 75);
      previousTime = time;
      x += (targetX - x) * alpha;
      y += (targetY - y) * alpha;
      if (tilt) surface.style.transform = `perspective(1100px) rotateX(${-y * 2.5}deg) rotateY(${x * 3.5}deg) ${baseTransform === "none" ? "" : baseTransform}`;
      if (Math.abs(targetX - x) + Math.abs(targetY - y) > .003) frame = requestAnimationFrame(paint);
      else if (!surface.classList.contains("pointer-active")) surface.style.transform = "";
    }
    function reset() {
      cancelAnimationFrame(frame); frame = 0;
      x = y = targetX = targetY = 0;
      surface.style.transform = "";
      surface.classList.remove("pointer-active");
    }
    surface.addEventListener("pointerenter", event => {
      if (!pointerEnabled() || event.pointerType !== "mouse") return;
      bounds = surface.getBoundingClientRect();
      surface.classList.add("pointer-active");
    });
    surface.addEventListener("pointermove", event => {
      if (!pointerEnabled() || event.pointerType !== "mouse" || !bounds) return;
      targetX = clamp((event.clientX - bounds.left) / bounds.width * 2 - 1);
      targetY = clamp((event.clientY - bounds.top) / bounds.height * 2 - 1);
      glow.style.transform = `translate(${event.clientX - bounds.left - 160}px,${event.clientY - bounds.top - 160}px)`;
      if (tilt && !frame) frame = requestAnimationFrame(paint);
    });
    surface.addEventListener("pointerleave", () => {
      surface.classList.remove("pointer-active");
      targetX = targetY = 0;
      if (tilt && !frame && pointerEnabled()) frame = requestAnimationFrame(paint);
    });
    pointerResets.push(reset);
  });
  const resetPointers = () => { pointerResets.forEach(reset => reset()); releaseOrbit(); };
  reducedMotion.addEventListener("change", resetPointers);
  precisePointer.addEventListener("change", resetPointers);
  motionButton?.addEventListener("click", resetPointers);
  document.addEventListener("visibilitychange", () => { if (document.hidden) resetPointers(); });

  const dialog = document.querySelector(".image-dialog");
  document.querySelectorAll(".capture-open").forEach(button => button.addEventListener("click", () => {
    if (!dialog?.showModal) return;
    dialog.querySelector("img").src = button.dataset.image;
    dialog.querySelector("img").alt = button.querySelector("img").alt;
    dialog.querySelector(".dialog-original").href = button.dataset.image;
    dialog.showModal();
    document.body.classList.add("dialog-open");
  }));
  dialog?.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
  dialog?.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
  dialog?.addEventListener("close", () => {
    document.body.classList.remove("dialog-open");
    dialog.querySelector("img").removeAttribute("src");
    dialog.querySelector(".dialog-original").removeAttribute("href");
  });
  const video = document.querySelector("video");
  const videoError = document.querySelector(".video-error");
  const showVideoError = () => { if (videoError) videoError.hidden = false; };
  video?.addEventListener("error", showVideoError);
  video?.querySelector("source")?.addEventListener("error", showVideoError);
  const showCaptionError = () => {
    const captionError = document.querySelector(".caption-error");
    if (captionError) captionError.hidden = false;
  };
  video?.querySelectorAll("track").forEach(track => {
    track.addEventListener("error", showCaptionError);
    // Default captions can fail while the deferred application script is loading.
    if (track.readyState === HTMLTrackElement.ERROR) showCaptionError();
  });
  if (video?.error) showVideoError();
  video?.addEventListener("playing", () => { if (videoError) videoError.hidden = true; });
  root.classList.add("has-js");
})();
