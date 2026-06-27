const MODES = [
  "Random",
  "Fantasy Tavern",
  "Village Weird",
  "Quest Giver Gone Wrong",
  "Villain Contact",
  "Shopkeeper With A Problem",
];

const TUNE_PRESETS = [
  {
    id: "grounded",
    label: "Grounded",
    chaos: 25,
    light: "green",
    body: "Useful contact, one odd detail, low table risk.",
  },
  {
    id: "trouble",
    label: "Trouble",
    chaos: 55,
    light: "amber",
    body: "Stronger contradiction, immediate problem, easy to drop in.",
  },
  {
    id: "wild",
    label: "Wild Hook",
    chaos: 82,
    light: "red",
    body: "Big pressure, stranger collision, use when the scene needs a shove.",
  },
];

const MODE_HINTS = {
  Random: "Lets the box choose a scene shape.",
  "Fantasy Tavern": "Good for first meetings, gossip, jobs, and messy introductions.",
  "Village Weird": "Turns local drama into a playable problem.",
  "Quest Giver Gone Wrong": "Makes the job useful but bent.",
  "Villain Contact": "Creates a clue-bearer, informant, or dangerous middle step.",
  "Shopkeeper With A Problem": "Makes a practical NPC with a problem attached to trade.",
};

const SEED_KEYS = [
  "names",
  "epithets",
  "roles",
  "places",
  "factions",
  "wants",
  "secrets",
  "contradictions",
  "problems",
  "objects",
  "hooks",
  "knowledge",
  "offers",
  "complications",
  "quotes",
  "use_cases",
  "chaos_rules",
];

const SEED_GROUPS = [
  { title: "Core", keys: ["names", "roles", "places", "factions"] },
  { title: "Motives", keys: ["wants", "secrets", "contradictions", "problems"] },
  { title: "At The Table", keys: ["hooks", "knowledge", "offers", "complications"] },
  { title: "Voice", keys: ["objects", "quotes", "epithets", "use_cases", "chaos_rules"] },
];

const SEED_HELP = {
  names: "People the box can pull from the crowd.",
  epithets: "Short odd tags that make names memorable.",
  roles: "Jobs, archetypes, and table-facing functions.",
  places: "Where the NPC belongs or first appears.",
  factions: "Groups that can apply pressure.",
  wants: "What the NPC is trying to make happen.",
  secrets: "What makes them useful, risky, or funny.",
  contradictions: "The human twist that stops them feeling flat.",
  problems: "The immediate trouble they bring into play.",
  objects: "Props, clues, and strange leverage.",
  hooks: "How they enter the scene.",
  knowledge: "What they can tell the players.",
  offers: "What they can do for the players.",
  complications: "The catch attached to their help.",
  quotes: "Voice lines worth reading aloud.",
  use_cases: "When this NPC is useful at the table.",
  chaos_rules: "How traces bend the result.",
};

let appState = {};
let doctor = {};
let currentNpc = null;
let currentSeedTab = "names";
let lastExport = null;
let favouritesCache = [];

const el = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "content-type": "application/json",
      ...(options.headers || {}),
    },
  });
  const data = await response.json();
  if (!data.ok) {
    throw new Error(data.error || "NPC Chaos Box request failed");
  }
  return data;
}

async function init() {
  bindNavigation();
  bindControls();
  populateModes();
  await loadState();
  showPage(location.hash.replace("#", "") || "generate");
}

function bindNavigation() {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => {
      location.hash = button.dataset.page;
      showPage(button.dataset.page);
    });
  });
  window.addEventListener("hashchange", () => showPage(location.hash.replace("#", "") || "generate"));
}

function bindControls() {
  el("generateButton").addEventListener("click", () => generateNpc(false));
  el("sameSeedButton").addEventListener("click", () => generateNpc(true));
  el("chaosInput").addEventListener("input", () => {
    el("chaosValue").textContent = el("chaosInput").value;
    renderTuneStrip();
    renderTunePreview();
  });
  el("modeSelect").addEventListener("change", renderTunePreview);
  el("roleSelect").addEventListener("change", renderTunePreview);
  el("seedInput").addEventListener("input", renderTunePreview);
  el("lockSeedInput").addEventListener("change", () => {
    renderTuneStrip();
    renderTunePreview();
  });
  el("copyButton").addEventListener("click", copyCurrentNpc);
  el("saveButton").addEventListener("click", saveFavourite);
  el("goExportsButton").addEventListener("click", goToExports);
  el("exportTxtButton").addEventListener("click", () => exportNpc("txt"));
  el("exportHtmlButton").addEventListener("click", () => exportNpc("html"));
  el("openExportsButton").addEventListener("click", openExports);
  el("saveSeedsButton").addEventListener("click", saveSeeds);
  el("resetSeedsButton").addEventListener("click", resetSeeds);
  el("seedEditor").addEventListener("input", () => {
    syncSeedEditor();
    renderSeedHealth();
    renderReadiness();
    setSeedMessage("Unsaved seed edits. Save when this list feels useful.", "amber");
  });
  el("saveFromFavouritesButton").addEventListener("click", saveFavourite);
  el("refreshFavouritesButton").addEventListener("click", loadFavourites);
}

function populateModes() {
  el("modeSelect").innerHTML = MODES.map((mode) => `<option>${escapeHtml(mode)}</option>`).join("");
  renderTunePresets();
}

function renderTunePresets() {
  const currentChaos = Number(el("chaosInput")?.value || 55);
  el("tunePresets").innerHTML = TUNE_PRESETS.map((preset) => `
    <button class="preset-button ${nearestPreset(currentChaos)?.id === preset.id ? "active" : ""}" data-preset="${escapeHtml(preset.id)}">
      <span class="preset-title"><span class="light ${preset.light}"></span>${escapeHtml(preset.label)}</span>
      <span class="preset-body">${escapeHtml(preset.body)}</span>
    </button>
  `).join("");
  document.querySelectorAll("[data-preset]").forEach((button) => {
    button.addEventListener("click", () => applyTunePreset(button.dataset.preset));
  });
}

function nearestPreset(chaos) {
  return TUNE_PRESETS.reduce((best, preset) => {
    const bestDistance = Math.abs(chaos - best.chaos);
    const nextDistance = Math.abs(chaos - preset.chaos);
    return nextDistance < bestDistance ? preset : best;
  }, TUNE_PRESETS[0]);
}

function applyTunePreset(id) {
  const preset = TUNE_PRESETS.find((item) => item.id === id) || TUNE_PRESETS[1];
  el("chaosInput").value = String(preset.chaos);
  el("chaosValue").textContent = String(preset.chaos);
  renderTuneStrip();
  renderTunePreview();
  setMessage(`${preset.label} feel selected.`);
}

async function loadState() {
  const data = await api("/api/state");
  appState = data.state;
  doctor = data.doctor;
  el("versionText").textContent = `v${data.version} - local`;
  renderStorageStatus();
  renderRoleOptions();
  renderSeedTabs();
  renderSeedEditor();
  renderSeedHealth();
  renderReadiness();
  renderTuneStrip();
  renderTunePreview();
  renderDoctor(data.version);
  renderResultActions();
  renderExportSummary();
  setSeedMessage("Edits stay local and save only when you press Save Seeds.", "amber");
  await loadFavourites();
}

function showPage(page) {
  const safePage = page || "generate";
  document.querySelectorAll(".page").forEach((node) => node.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach((node) => node.classList.toggle("active", node.dataset.page === safePage));
  const target = el(`page-${safePage}`) || el("page-generate");
  target.classList.add("active");
  const titles = {
    generate: ["Generate", "Make an NPC you can use now"],
    tune: ["Tune", "Set the next pull"],
    seeds: ["Seed Packs", "Keep the ingredients healthy"],
    favourites: ["Favourites", "Bring back the useful ones"],
    exports: ["Exports", "Export the current NPC"],
    doctor: ["Doctor", "Check the local setup"],
  };
  const [label, title] = titles[safePage] || titles.generate;
  el("pageLabel").textContent = label;
  el("pageTitle").textContent = title;
  if (safePage === "exports") {
    renderExportSummary();
  }
  if (safePage === "favourites") {
    renderFavouritesStatus();
  }
}

async function generateNpc(sameSeed) {
  try {
    const seedInput = el("seedInput");
    let seed = seedInput.value.trim();
    if (sameSeed && currentNpc) {
      seed = String(currentNpc.seed);
    }
    if (!seed && el("lockSeedInput").checked && currentNpc) {
      seed = String(currentNpc.seed);
    }
    const payload = {
      mode: el("modeSelect").value,
      role: el("roleSelect").value,
      chaos: Number(el("chaosInput").value),
    };
    if (seed) {
      payload.seed = seed;
    }
    const data = await api("/api/generate", { method: "POST", body: JSON.stringify(payload) });
    currentNpc = data.scene;
    seedInput.value = String(currentNpc.seed);
    renderNpcCard();
    renderResultActions();
    renderExportSummary();
    renderFavouritesStatus();
    renderReadiness();
    renderNextSteps();
    setMessage(sameSeed ? "Seed repeated." : "NPC generated.");
    showPage("generate");
  } catch (error) {
    setMessage(error.message);
  }
}

function renderNpcCard() {
  if (!currentNpc) {
    return;
  }
  const npc = currentNpc.npc;
  const traceLines = currentNpc.trace_lines || [];
  el("npcCard").innerHTML = `
    <div class="npc-sheet">
      <header class="npc-sheet-head">
        <div>
          <p class="npc-kicker">${escapeHtml(currentNpc.mode)} | Chaos ${escapeHtml(currentNpc.chaos)} | Seed ${escapeHtml(currentNpc.seed)}</p>
          <h3 class="npc-title">${escapeHtml(currentNpc.title)}</h3>
          <p class="npc-subtitle">${escapeHtml(npc.role)} from ${escapeHtml(npc.home)}.</p>
        </div>
        <div class="npc-ready-badge">
          <span>Table Role</span>
          <strong>${escapeHtml(npc.role)}</strong>
        </div>
      </header>

      <section class="npc-table-callout">
        <span>Use Now</span>
        <p>${escapeHtml(npc.use_in_play)}</p>
      </section>

      <section class="npc-quote-block">
        <span>Read Aloud</span>
        <p>"${escapeHtml(npc.quote)}"</p>
      </section>

      <div class="npc-priority-grid">
        ${npcSpotlight("Problem Now", npc.problem_now)}
        ${npcSpotlight("First Move", npc.first_move)}
      </div>

      <div class="npc-section-grid">
        <section class="npc-section">
          <h4>Pressure</h4>
          ${npcMiniField("Wants", npc.wants)}
          ${npcMiniField("Contradiction", npc.contradiction)}
          ${npcMiniField("Secret", npc.secret)}
        </section>
        <section class="npc-section">
          <h4>Table Levers</h4>
          ${npcMiniField("What They Know", npc.what_they_know)}
          ${npcMiniField("Wants From Players", npc.wants_from_players)}
          ${npcMiniField("Object", npc.object)}
        </section>
        <section class="npc-section">
          <h4>Context</h4>
          ${npcMiniField("Home", npc.home)}
          ${npcMiniField("Faction", npc.faction)}
        </section>
      </div>

      <details class="trace-details">
        <summary>Chaos Trace</summary>
        ${traceLines.length ? `<ol>${traceLines.map((line) => `<li>${escapeHtml(line)}</li>`).join("")}</ol>` : "<p>No trace lines returned.</p>"}
      </details>
    </div>
  `;
}

function renderResultActions() {
  el("resultActions").hidden = !currentNpc;
  el("repeatSeedPanel").hidden = !currentNpc;
  if (currentNpc) {
    el("repeatSeedValue").textContent = String(currentNpc.seed || "auto");
  }
}

function npcSpotlight(label, value) {
  return `
    <section class="npc-spotlight">
      <span>${escapeHtml(label)}</span>
      <p>${escapeHtml(value || "")}</p>
    </section>
  `;
}

function npcMiniField(label, value) {
  return `
    <div class="npc-mini-field">
      <span>${escapeHtml(label)}</span>
      <p>${escapeHtml(value || "")}</p>
    </div>
  `;
}

function renderStorageStatus() {
  const status = doctor.state_ok ? "green" : "red";
  el("storageStatus").innerHTML = `<span class="light ${status}"></span>${doctor.state_ok ? "Ready" : "Needs seeds"}`;
}

function renderReadiness() {
  const items = seedStatusItems();
  el("readinessStrip").innerHTML = items.slice(0, 4).map(statusPill).join("");
  renderNextSteps();
}

function renderTuneStrip() {
  const chaos = Number(el("chaosInput").value || 0);
  const light = chaos > 75 ? "red" : chaos > 45 ? "amber" : "green";
  const text = chaos > 75 ? "High pressure NPC" : chaos > 45 ? "Table-ready complication" : "Grounded contact";
  el("tuneStrip").innerHTML = [
    statusPill({ light, label: text }),
    statusPill({ light: el("lockSeedInput").checked ? "green" : "amber", label: el("lockSeedInput").checked ? "Seed locked" : "Seed will move" }),
  ].join("");
  renderTunePresets();
}

function renderTunePreview() {
  const mode = el("modeSelect").value || "Random";
  const role = el("roleSelect").value || "Any Role";
  const chaos = Number(el("chaosInput").value || 0);
  const seedText = el("seedInput").value.trim();
  const locked = el("lockSeedInput").checked;
  const chaosLight = chaos > 75 ? "red" : chaos > 45 ? "amber" : "green";
  const chaosLabel = chaos > 75 ? "Loud and risky" : chaos > 45 ? "Playable trouble" : "Grounded and steady";
  const seedLine = seedText
    ? `Seed ${seedText}${locked ? " will repeat exactly." : " is set for the next pull."}`
    : locked && currentNpc
      ? `Locks the current seed ${currentNpc.seed}.`
      : "No seed set, so each pull can surprise you.";
  el("tunePreview").innerHTML = `
    <div class="preview-lede ${chaosLight}">
      <span class="light ${chaosLight}"></span>
      <strong>${escapeHtml(chaosLabel)}</strong>
      <p>${escapeHtml(MODE_HINTS[mode] || MODE_HINTS.Random)}</p>
    </div>
    <div class="preview-row">
      <span>Mode</span>
      <strong>${escapeHtml(mode)}</strong>
    </div>
    <div class="preview-row">
      <span>Role</span>
      <strong>${escapeHtml(role === "Any Role" ? "Box chooses" : role)}</strong>
    </div>
    <div class="preview-row">
      <span>Seed</span>
      <strong>${escapeHtml(seedLine)}</strong>
    </div>
  `;
}

function renderNextSteps() {
  const cards = [];
  const overall = overallSeedStatus();
  if (!currentNpc) {
    cards.push({ light: overall.light, title: "Generate", body: overall.light === "red" ? "Fix the red seed categories first." : "Press Generate NPC. The first useful card is one click away." });
  } else {
    cards.push({ light: "green", title: "Use", body: currentNpc.guidance?.next_step || "Drop this NPC into the next scene." });
    cards.push({ light: "amber", title: "Tune", body: "Change mode, role, chaos, or seed if the NPC is nearly right." });
    cards.push({ light: "green", title: "Keep", body: "Copy it, save it, or open Exports when the card works." });
  }
  if (overall.light !== "green") {
    cards.push({ light: overall.light, title: "Seed Pack", body: overall.body });
  }
  el("nextStepList").innerHTML = cards.map((card) => `
    <div class="next-card ${card.light}">
      <strong>${escapeHtml(card.title)}</strong>
      <p>${escapeHtml(card.body)}</p>
    </div>
  `).join("");
}

function seedStatusItems() {
  const counts = countCategories();
  return Object.entries(counts).map(([key, count]) => ({
    light: count >= 8 ? "green" : count >= 4 ? "amber" : "red",
    label: `${labelFor(key)} ${count}`,
  }));
}

function overallSeedStatus() {
  const statuses = seedStatusItems();
  if (statuses.some((item) => item.light === "red")) {
    return { light: "red", body: "One seed category is too thin for varied NPCs." };
  }
  if (statuses.some((item) => item.light === "amber")) {
    return { light: "amber", body: "The pack works, but some categories will repeat sooner." };
  }
  return { light: "green", body: "The pack is ready for varied NPCs." };
}

function statusPill(item) {
  return `<div class="traffic-item"><span class="light ${item.light}"></span>${escapeHtml(item.label)}</div>`;
}

function countCategories() {
  const required = ["names", "roles", "places", "wants", "secrets", "problems", "hooks", "knowledge", "offers", "quotes"];
  return Object.fromEntries(required.map((key) => [key, Array.isArray(appState[key]) ? appState[key].length : 0]));
}

function renderRoleOptions() {
  const roles = ["Any Role", ...(appState.roles || [])];
  el("roleSelect").innerHTML = roles.map((role) => `<option>${escapeHtml(role)}</option>`).join("");
}

function renderSeedTabs() {
  el("seedTabs").innerHTML = SEED_GROUPS.map((group) => `
    <div class="tab-group">
      <strong>${escapeHtml(group.title)}</strong>
      <div class="tab-row">
        ${group.keys.map((key) => `<button class="tab ${key === currentSeedTab ? "active" : ""}" data-key="${key}">${escapeHtml(labelFor(key))}</button>`).join("")}
      </div>
    </div>
  `).join("");
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      syncSeedEditor();
      currentSeedTab = button.dataset.key;
      renderSeedTabs();
      renderSeedEditor();
    });
  });
}

function renderSeedEditor() {
  el("seedPackTitle").textContent = appState.world_name || "Seed Pack";
  el("seedPackNote").textContent = appState.world_note || "Edit one item per line.";
  el("seedEditor").value = (appState[currentSeedTab] || []).join("\n");
  renderCurrentSeedStatus();
}

function renderSeedHealth() {
  el("seedHealth").innerHTML = seedStatusItems().map(statusPill).join("");
  renderCurrentSeedStatus();
}

function renderCurrentSeedStatus() {
  const count = Array.isArray(appState[currentSeedTab]) ? appState[currentSeedTab].length : 0;
  const light = count >= 8 ? "green" : count >= 4 ? "amber" : "red";
  el("currentSeedLabel").textContent = `${labelFor(currentSeedTab)} (${count})`;
  el("currentSeedHelp").textContent = SEED_HELP[currentSeedTab] || "Edit one item per line.";
  el("currentSeedStatus").innerHTML = `<span class="light ${light}"></span>${count >= 8 ? "Healthy" : count >= 4 ? "Thin but usable" : "Needs more"}`;
  renderSeedGuide();
}

function renderSeedGuide() {
  const guide = el("seedGuide");
  if (!guide) {
    return;
  }
  const count = Array.isArray(appState[currentSeedTab]) ? appState[currentSeedTab].length : 0;
  const label = labelFor(currentSeedTab);
  const currentLight = count >= 8 ? "green" : count >= 4 ? "amber" : "red";
  const overall = overallSeedStatus();
  const cards = [
    {
      light: currentLight,
      title: "Current List",
      body: count >= 8
        ? `${label} has enough variety for clean pulls.`
        : count >= 4
          ? `${label} works, but a few more lines will reduce repeats.`
          : `${label} needs more lines before the pack feels healthy.`,
    },
    {
      light: overall.light,
      title: overall.light === "green" ? "Ready To Generate" : "Add Variety",
      body: overall.body,
    },
    {
      light: "amber",
      title: "Save Then Test",
      body: "Save the pack, then generate once to feel whether the new ingredients land.",
    },
  ];
  guide.innerHTML = cards.map((card) => `
    <div class="next-card ${card.light}">
      <strong>${escapeHtml(card.title)}</strong>
      <p>${escapeHtml(card.body)}</p>
    </div>
  `).join("");
}

function setSeedMessage(message, tone = "amber") {
  const node = el("seedActionMessage");
  if (!node) {
    return;
  }
  node.textContent = message;
  node.dataset.tone = tone;
}

async function saveSeeds() {
  syncSeedEditor();
  try {
    const data = await api("/api/state", { method: "POST", body: JSON.stringify({ state: appState }) });
    appState = data.state;
    doctor = data.doctor;
    renderRoleOptions();
    renderSeedHealth();
    renderReadiness();
    renderStorageStatus();
    renderDoctor();
    setSeedMessage("Seed pack saved locally.", "green");
    setMessage("Seed pack saved.");
  } catch (error) {
    setSeedMessage(error.message, "red");
    setMessage(error.message);
  }
}

function syncSeedEditor() {
  appState[currentSeedTab] = el("seedEditor").value.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
}

async function resetSeeds() {
  try {
    const data = await api("/api/state", { method: "POST", body: JSON.stringify({ reset: true }) });
    appState = data.state;
    doctor = data.doctor;
    currentSeedTab = "names";
    renderRoleOptions();
    renderSeedTabs();
    renderSeedEditor();
    renderSeedHealth();
    renderReadiness();
    renderStorageStatus();
    renderDoctor();
    setSeedMessage("Default Crooked Lantern pack restored locally.", "green");
    setMessage("Crooked Lantern restored.");
  } catch (error) {
    setSeedMessage(error.message, "red");
    setMessage(error.message);
  }
}

async function copyCurrentNpc() {
  if (!currentNpc) {
    setMessage("Generate an NPC first.");
    return;
  }
  await copyText(currentNpc.card_text || "");
}

async function saveFavourite() {
  if (!currentNpc) {
    setMessage("Generate an NPC first.");
    return;
  }
  try {
    await api("/api/favourites", { method: "POST", body: JSON.stringify({ scene: currentNpc }) });
    await loadFavourites();
    renderFavouritesStatus();
    setMessage("Favourite saved.");
  } catch (error) {
    setMessage(error.message);
  }
}

function goToExports() {
  if (!currentNpc) {
    setMessage("Generate an NPC first.");
    return;
  }
  location.hash = "exports";
  showPage("exports");
}

async function loadFavourites() {
  const data = await api("/api/favourites");
  const favourites = data.favourites || [];
  favouritesCache = favourites;
  renderFavouritesStatus();
  el("favouritesList").innerHTML = favourites.length ? favourites.map((item) => {
    const npc = item.scene?.npc || {};
    return `
      <article class="list-item favourite-card">
        <div>
          <h4>${escapeHtml(item.title)}</h4>
          <p>${escapeHtml(npc.role || "Saved NPC")} | Seed ${escapeHtml(item.seed)} | ${escapeHtml(item.mode)}</p>
        </div>
        <div class="favourite-card-foot">
          <span>${escapeHtml(formatLocalDate(item.created_at))}</span>
          <button data-fav="${escapeHtml(item.id)}">Load NPC</button>
        </div>
      </article>
    `;
  }).join("") : `
    <div class="list-item empty-list">
      <h4>No favourites yet</h4>
      <p>Generate an NPC, then save the ones worth keeping. This shelf stays local on this machine.</p>
      <div class="button-row">
        <button data-go-page="generate">Go Generate</button>
      </div>
    </div>
  `;
  document.querySelectorAll("[data-fav]").forEach((button) => {
    button.addEventListener("click", () => {
      const item = favourites.find((fav) => fav.id === button.dataset.fav);
      if (item?.scene) {
        currentNpc = item.scene;
        el("seedInput").value = String(currentNpc.seed || "");
        renderNpcCard();
        renderResultActions();
        renderExportSummary();
        renderFavouritesStatus();
        renderNextSteps();
        showPage("generate");
        setMessage("Favourite loaded.");
      }
    });
  });
  document.querySelectorAll("[data-go-page]").forEach((button) => {
    button.addEventListener("click", () => {
      const page = button.dataset.goPage || "generate";
      location.hash = page;
      showPage(page);
    });
  });
}

function renderFavouritesStatus() {
  const count = favouritesCache.length;
  const hasCurrent = Boolean(currentNpc);
  const saveButton = el("saveFromFavouritesButton");
  saveButton.disabled = !hasCurrent;
  el("favouritesSummary").innerHTML = `
    <div class="traffic-strip compact">
      ${statusPill({ light: count ? "green" : "amber", label: count ? `${count} saved` : "No saved NPCs yet" })}
      ${statusPill({ light: hasCurrent ? "green" : "amber", label: hasCurrent ? "Current NPC ready" : "Generate before saving" })}
    </div>
    ${hasCurrent ? `
      <div class="shelf-current">
        <span>Current NPC</span>
        <strong>${escapeHtml(currentNpc.title)}</strong>
      </div>
    ` : ""}
  `;
  const cards = [];
  if (!hasCurrent) {
    cards.push({ light: "amber", title: "Generate", body: "Make an NPC first, then this page can save it." });
  } else {
    cards.push({ light: "green", title: "Save", body: "Save the current NPC when it earns a place at the table." });
  }
  if (count) {
    cards.push({ light: "green", title: "Load", body: "Load any saved NPC back onto the Generate page." });
  } else {
    cards.push({ light: "amber", title: "Build Shelf", body: "Keep only the useful ones so the list stays easy to scan." });
  }
  el("favouritesGuide").innerHTML = cards.map((card) => `
    <div class="next-card ${card.light}">
      <strong>${escapeHtml(card.title)}</strong>
      <p>${escapeHtml(card.body)}</p>
    </div>
  `).join("");
}

async function exportNpc(format) {
  if (!currentNpc) {
    setMessage("Generate an NPC first.");
    return;
  }
  try {
    const data = await api("/api/export", { method: "POST", body: JSON.stringify({ scene: currentNpc, format }) });
    lastExport = data.export;
    el("lastExportText").textContent = `${data.export.format.toUpperCase()} saved in your exports folder.`;
    el("lastExportPath").textContent = data.export.path;
    renderExportSummary();
    renderExportsStrip();
    setMessage(`${data.export.format.toUpperCase()} exported.`);
  } catch (error) {
    setMessage(error.message);
  }
}

async function openExports() {
  try {
    const data = await api("/api/open-exports", { method: "POST", body: JSON.stringify({}) });
    const result = data.export_folder;
    el("lastExportText").textContent = result.opened ? "Exports folder opened." : "Exports folder is ready.";
    el("lastExportPath").textContent = result.path;
    renderExportsStrip(result);
    renderExportsGuide(result);
  } catch (error) {
    el("lastExportText").textContent = error.message;
  }
}

function renderExportsStrip(result = null) {
  const item = result?.error
    ? { light: "amber", label: "Folder not opened" }
    : { light: lastExport ? "green" : "amber", label: lastExport ? "Export ready" : "No export yet" };
  el("exportsStrip").innerHTML = statusPill(item);
}

function renderExportSummary() {
  const txtButton = el("exportTxtButton");
  const htmlButton = el("exportHtmlButton");
  txtButton.disabled = !currentNpc;
  htmlButton.disabled = !currentNpc;

  if (!currentNpc) {
    el("exportCurrentCard").innerHTML = `
      <h4>No NPC ready yet</h4>
      <p>Generate an NPC first. Then choose TXT for notes or HTML for a browser-friendly copy.</p>
    `;
    el("lastExportPath").textContent = lastExport?.path || "Exports stay local on this machine.";
    renderExportsStrip();
    renderExportsGuide();
    return;
  }

  el("exportCurrentCard").innerHTML = `
    <h4>${escapeHtml(currentNpc.title)}</h4>
    <p>${escapeHtml(currentNpc.npc?.role || "NPC")} | Seed ${escapeHtml(currentNpc.seed)} | ${escapeHtml(currentNpc.mode)} | Chaos ${escapeHtml(currentNpc.chaos)}</p>
    <div class="export-format-note">
      <span>TXT is best for notes.</span>
      <span>HTML is best for a clean saved card.</span>
    </div>
  `;
  el("lastExportPath").textContent = lastExport?.path || "No file exported from this session yet.";
  renderExportsStrip();
  renderExportsGuide();
}

function renderExportsGuide(result = null) {
  const cards = [];
  if (!currentNpc) {
    cards.push({ light: "amber", title: "Generate", body: "Make or load an NPC before exporting." });
  } else {
    cards.push({ light: "green", title: "Choose Format", body: "TXT for notes, HTML for a readable saved card." });
  }
  if (lastExport) {
    cards.push({ light: "green", title: "Find File", body: "Open the exports folder when you want the saved file." });
  } else {
    cards.push({ light: "amber", title: "Export Once", body: "Pick one format. You can export the other later." });
  }
  if (result?.error) {
    cards.push({ light: "amber", title: "Folder", body: "The file was saved, but Windows did not open the folder." });
  }
  el("exportsGuide").innerHTML = cards.map((card) => `
    <div class="next-card ${card.light}">
      <strong>${escapeHtml(card.title)}</strong>
      <p>${escapeHtml(card.body)}</p>
    </div>
  `).join("");
}

function renderDoctor(version = null) {
  const counts = doctor.category_counts || countCategories();
  const rows = [
    ["App", `NPC Chaos Box ${version || ""}`.trim()],
    ["Storage", doctor.data_dir || ""],
    ["Exports", doctor.exports_dir || ""],
    ["Seed Pack", doctor.state_ok ? "Ready" : "Needs attention"],
    ["Portable Default", doctor.portable_default || ""],
    ["Internet", "Not required"],
    ["Categories", Object.entries(counts).map(([key, count]) => `${labelFor(key)} ${count}`).join(", ")],
  ];
  el("doctorPanel").innerHTML = rows.map(([name, value]) => `
    <div class="doctor-row">
      <strong>${escapeHtml(name)}</strong>
      <span>${escapeHtml(value)}</span>
    </div>
  `).join("");
  renderExportsStrip();
}

async function copyText(text) {
  const fallback = el("copyFallback");
  fallback.hidden = true;
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      setMessage("Copied.");
      return;
    }
  } catch {
    // Fall through to the selection fallback.
  }
  fallback.value = text;
  fallback.hidden = false;
  fallback.focus();
  fallback.select();
  try {
    document.execCommand("copy");
    setMessage("Copied.");
  } catch {
    setMessage("Clipboard blocked. Text is selected below.");
  }
}

function setMessage(message) {
  el("actionMessage").textContent = message;
}

function labelFor(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatLocalDate(value) {
  if (!value) {
    return "Local save";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }
  return date.toLocaleString([], {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

init().catch((error) => {
  document.body.innerHTML = `<pre>${escapeHtml(error.message)}</pre>`;
});
