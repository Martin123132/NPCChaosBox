const MODES = [
  "Random",
  "Fantasy Tavern",
  "Village Weird",
  "Quest Giver Gone Wrong",
  "Villain Contact",
  "Shopkeeper With A Problem",
];

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
  });
  el("lockSeedInput").addEventListener("change", renderTuneStrip);
  el("copyButton").addEventListener("click", copyCurrentNpc);
  el("saveButton").addEventListener("click", saveFavourite);
  el("goExportsButton").addEventListener("click", goToExports);
  el("exportTxtButton").addEventListener("click", () => exportNpc("txt"));
  el("exportHtmlButton").addEventListener("click", () => exportNpc("html"));
  el("openExportsButton").addEventListener("click", openExports);
  el("saveSeedsButton").addEventListener("click", saveSeeds);
  el("resetSeedsButton").addEventListener("click", resetSeeds);
  el("refreshFavouritesButton").addEventListener("click", loadFavourites);
}

function populateModes() {
  el("modeSelect").innerHTML = MODES.map((mode) => `<option>${escapeHtml(mode)}</option>`).join("");
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
  renderDoctor(data.version);
  renderResultActions();
  renderExportSummary();
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
    renderReadiness();
    renderNextSteps();
    setMessage("NPC generated.");
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
  el("npcCard").innerHTML = `
    <h3 class="npc-title">${escapeHtml(currentNpc.title)}</h3>
    <p class="npc-subtitle">${escapeHtml(npc.role)} from ${escapeHtml(npc.home)}.</p>
    <div class="field-grid">
      ${field("Wants", npc.wants)}
      ${field("Secret", npc.secret)}
      ${field("Contradiction", npc.contradiction)}
      ${field("Problem Now", npc.problem_now)}
      ${field("Faction", npc.faction)}
      ${field("Object", npc.object)}
      ${field("First Move", npc.first_move, true)}
      ${field("What They Know", npc.what_they_know)}
      ${field("Wants From Players", npc.wants_from_players)}
      <div class="field wide"><span>Quote</span><p class="quote">"${escapeHtml(npc.quote)}"</p></div>
      ${field("Use In Play", npc.use_in_play, true)}
      ${field("Chaos Trace", (currentNpc.trace_lines || []).join(" "), true)}
    </div>
  `;
}

function renderResultActions() {
  el("resultActions").hidden = !currentNpc;
}

function field(label, value, wide = false) {
  return `<div class="field ${wide ? "wide" : ""}"><span>${escapeHtml(label)}</span><p>${escapeHtml(value || "")}</p></div>`;
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
    setMessage("Seed pack saved.");
  } catch (error) {
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
    setMessage("Crooked Lantern restored.");
  } catch (error) {
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
  el("favouritesList").innerHTML = favourites.length ? favourites.map((item) => `
    <article class="list-item">
      <h4>${escapeHtml(item.title)}</h4>
      <p>Seed ${escapeHtml(item.seed)} | ${escapeHtml(item.mode)} | ${escapeHtml(item.created_at || "")}</p>
      <div class="button-row">
        <button data-fav="${escapeHtml(item.id)}">Load</button>
      </div>
    </article>
  `).join("") : `<div class="list-item"><h4>No favourites yet</h4><p>Generate an NPC, then save the ones worth keeping.</p></div>`;
  document.querySelectorAll("[data-fav]").forEach((button) => {
    button.addEventListener("click", () => {
      const item = favourites.find((fav) => fav.id === button.dataset.fav);
      if (item?.scene) {
        currentNpc = item.scene;
        el("seedInput").value = String(currentNpc.seed || "");
        renderNpcCard();
        renderResultActions();
        renderExportSummary();
        renderNextSteps();
        showPage("generate");
        setMessage("Favourite loaded.");
      }
    });
  });
}

async function exportNpc(format) {
  if (!currentNpc) {
    setMessage("Generate an NPC first.");
    return;
  }
  try {
    const data = await api("/api/export", { method: "POST", body: JSON.stringify({ scene: currentNpc, format }) });
    lastExport = data.export;
    el("lastExportText").textContent = `${data.export.format.toUpperCase()} saved: ${data.export.path}`;
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
    el("lastExportText").textContent = result.opened ? `Opened: ${result.path}` : `Exports folder: ${result.path}`;
    renderExportsStrip(result);
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
      <p>Generate an NPC first, then come back here to choose TXT or HTML.</p>
    `;
    return;
  }

  el("exportCurrentCard").innerHTML = `
    <h4>${escapeHtml(currentNpc.title)}</h4>
    <p>Seed ${escapeHtml(currentNpc.seed)} | ${escapeHtml(currentNpc.mode)} | Chaos ${escapeHtml(currentNpc.chaos)}</p>
  `;
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
