const setupSteps = [
  {
    title: "Opna orugga uppsetningu",
    text: "Starfsmadur faer QR koda eda stuttan tengikoda fra admin. Kodinn er demo-only her.",
    status: "Otengt"
  },
  {
    title: "Stadfesta sima",
    text: "Siminn tengist starfsmanni, taeki og vinnustad an thess ad birta lykla eda private config.",
    status: "Stadfesting"
  },
  {
    title: "Velja lagmarksheimildir",
    text: "MVP tharf bara atburdi: inn, ut, leidrettingarbeidni og samthykki. Ekki stodugt eftirlit.",
    status: "Heimildir"
  },
  {
    title: "Tilbuid ad stimpla",
    text: "Starfsmadur getur nu profad innstimplun og sed nuverandi stodu strax a simanum.",
    status: "Tengt"
  }
];

let setupIndex = 0;
let isClockedIn = false;
let apiMode = false;
let activeDeviceId = null;
let activePairingCode = null;

function two(value) {
  return String(value).padStart(2, "0");
}

function currentTime() {
  const now = new Date();
  return `${two(now.getHours())}:${two(now.getMinutes())}`;
}

function getCookie(name) {
  return document.cookie
    .split(";")
    .map((item) => item.trim())
    .find((item) => item.startsWith(`${name}=`))
    ?.split("=")
    .slice(1)
    .join("=") || "";
}

async function apiRequest(path, options = {}) {
  const headers = {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...(options.headers || {})
  };
  const csrfToken = getCookie("csrftoken");
  if (csrfToken) {
    headers["X-CSRFToken"] = csrfToken;
  }
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.villa || error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

function updateSetup() {
  const step = setupSteps[setupIndex];
  document.getElementById("phoneStepTitle").textContent = step.title;
  document.getElementById("phoneStepText").textContent = step.text;
  document.getElementById("phoneStatus").textContent = step.status;

  const pill = document.getElementById("setupPill");
  pill.textContent = `Skref ${setupIndex + 1} af ${setupSteps.length}`;
  pill.classList.toggle("green", setupIndex === setupSteps.length - 1);
  pill.classList.toggle("amber", setupIndex !== setupSteps.length - 1);

  document.querySelectorAll(".setup-step").forEach((item) => {
    item.classList.toggle("active", Number(item.dataset.step) === setupIndex);
  });
}

function pushHistory(event, state) {
  const root = document.getElementById("historyList");
  const card = document.createElement("article");
  const time = document.createElement("time");
  const label = document.createElement("span");
  const meta = document.createElement("small");
  time.textContent = currentTime();
  label.textContent = event;
  meta.textContent = `${apiMode ? "API" : "Demo takki"} - ${state}`;
  card.append(time, label, meta);
  root.prepend(card);
}

function renderHistory(rows) {
  const root = document.getElementById("historyList");
  root.innerHTML = "";
  rows.forEach((row) => {
    const timestamp = row.timestamp ? new Date(row.timestamp) : new Date();
    pushHistory(row.event_type || "Atburdur", row.source || "API");
    root.firstElementChild.querySelector("time").textContent = `${two(timestamp.getHours())}:${two(timestamp.getMinutes())}`;
  });
}

function setClockState(nextState) {
  const status = document.getElementById("clockState");
  const time = document.getElementById("clockTime");
  const note = document.getElementById("clockNote");
  const panel = document.querySelector(".current-status");

  isClockedIn = nextState === "in";
  panel.classList.toggle("active", isClockedIn);
  status.textContent = isClockedIn ? "I vinnu nuna" : "Ekki stimplad inn";
  time.textContent = currentTime();
  if (apiMode) {
    note.textContent = isClockedIn
      ? "API: innstimplun vistud i starfsmannahaldi."
      : "API: utstimplun vistud i starfsmannahaldi.";
  } else {
    note.textContent = isClockedIn
      ? "Demo: innstimplun birtist strax. Engin faersla vistast."
      : "Demo: utstimplun birtist strax. Engin faersla vistast.";
  }
}

async function loadApiState() {
  try {
    const current = await apiRequest("/api/starfsfolk/maetingar/current_status/");
    apiMode = true;
    setClockState(current.is_clocked_in ? "in" : "out");
    document.getElementById("clockNote").textContent = "API tengt: raunstada lesin ur starfsmannahaldi.";

    const history = await apiRequest("/api/starfsfolk/maetingar/history/");
    renderHistory(history);
  } catch (error) {
    apiMode = false;
  }
}

async function ensureApiDevice() {
  if (activeDeviceId && activePairingCode) {
    return;
  }
  const device = await apiRequest("/api/starfsfolk/timaklukku-taeki/", {
    method: "POST",
    body: JSON.stringify({ device_label: "Browser mobile setup" })
  });
  activeDeviceId = device.id;
  activePairingCode = device.pairing_code;
  await apiRequest(`/api/starfsfolk/timaklukku-taeki/${activeDeviceId}/connect/`, {
    method: "POST",
    body: JSON.stringify({ pairing_code: activePairingCode })
  });
}

async function clockViaApi(direction) {
  await ensureApiDevice();
  const endpoint = direction === "in"
    ? "/api/starfsfolk/maetingar/stimplast_inn/"
    : "/api/starfsfolk/maetingar/stimplast_ut/";
  await apiRequest(endpoint, {
    method: "POST",
    body: JSON.stringify({ taeki: activeDeviceId })
  });
  setClockState(direction);
  const history = await apiRequest("/api/starfsfolk/maetingar/history/");
  renderHistory(history);
}

document.getElementById("nextSetup").addEventListener("click", () => {
  setupIndex = Math.min(setupIndex + 1, setupSteps.length - 1);
  updateSetup();
});

document.getElementById("prevSetup").addEventListener("click", () => {
  setupIndex = Math.max(setupIndex - 1, 0);
  updateSetup();
});

document.getElementById("clockIn").addEventListener("click", async () => {
  if (apiMode) {
    await clockViaApi("in").catch((error) => {
      document.getElementById("clockNote").textContent = `API villa: ${error.message}`;
    });
    return;
  }
  setClockState("in");
  pushHistory("Stimplad inn", "Skrad i demo");
});

document.getElementById("clockOut").addEventListener("click", async () => {
  if (apiMode) {
    await clockViaApi("out").catch((error) => {
      document.getElementById("clockNote").textContent = `API villa: ${error.message}`;
    });
    return;
  }
  setClockState("out");
  pushHistory("Stimplad ut", "Bidur yfirferdar i demo");
});

updateSetup();
loadApiState();
