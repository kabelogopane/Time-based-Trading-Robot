const modelTimes = ["08:45","09:45","10:45","11:45","12:45","13:45","15:45"];
const labels = ["Pre-open","Anchor","Reaction","Follow-through","Midday","Afternoon","Pre-close"];
const timezone = "America/New_York";

function minutes(hhmm) {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
}

function getNewYorkTime() {
  return new Intl.DateTimeFormat("en-US", {
    timeZone: timezone,
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(new Date());
}

function setText(id, value) {
  const element = document.querySelector(id);
  if (element) element.textContent = value;
}

function renderSummary(data) {
  const stats = data.summary || {};
  setText("#dataSource", `Python engine · ${data.source_file || "research dataset"}`);
  setText("#tradeCount", String(stats.trades ?? 0));
  setText("#winRate", `${Number(stats.win_rate ?? 0).toFixed(2)}%`);
  setText("#netR", `${Number(stats.net_r ?? 0).toFixed(2)}R`);
  setText("#sessionCount", String((data.sessions || []).length));

  const rows = (data.sessions || []).map((item) => `
    <tr>
      <td>${item.date}</td>
      <td>${item.first_break}</td>
      <td>${item.first_confirmation}</td>
      <td>${item.entry ?? "--"}</td>
      <td>${item.target ?? "--"}</td>
      <td>${item.outcome}</td>
      <td>${Number(item.r_multiple ?? 0).toFixed(2)}R</td>
    </tr>
  `).join("");
  const table = document.querySelector("#sessionRows");
  if (table) table.innerHTML = rows || `<tr><td colspan="7">No research sessions found.</td></tr>`;

  const eventRows = (data.market_events || []).map((event) => `
    <tr>
      <td>${event.time}</td>
      <td>${event.label}</td>
      <td>${event.liquidity_reference}</td>
      <td>${event.liquidity_event}</td>
      <td>${event.break_direction}</td>
      <td>${event.structure}</td>
      <td>${event.displacement ? "yes" : "no"}</td>
      <td>${event.confirmation}</td>
      <td>${event.status}</td>
    </tr>
  `).join("");
  const eventTable = document.querySelector("#eventRows");
  if (eventTable) eventTable.innerHTML = eventRows || `<tr><td colspan="9">No market events found.</td></tr>`;

  const firstTrade = (data.sessions || []).find(item => item.outcome !== "no_setup");
  if (firstTrade) {
    setText("#decision", `RESEARCH: ${firstTrade.outcome.toUpperCase()} · ${firstTrade.first_confirmation.toUpperCase()} SETUP`);
    setText("#direction", firstTrade.first_confirmation.toUpperCase());
    setText("#entry", firstTrade.entry?.toFixed(2) ?? "--");
    setText("#invalidation", firstTrade.invalidation?.toFixed(2) ?? "--");
    setText("#target", firstTrade.target?.toFixed(2) ?? "--");
  } else {
    setText("#decision", "RESEARCH: NO CONFIRMED SETUP");
  }
}

async function loadResearchResults() {
  try {
    const response = await fetch("data/demo-results.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    renderSummary(data);
  } catch (error) {
    setText("#dataSource", "Research data could not be loaded");
    setText("#decision", "RESEARCH DATA ERROR");
    console.error(error);
  }
}

function updateClock() {
  const current = getNewYorkTime();
  setText("#clock", `${current} ET`);
  const currentMinutes = minutes(current);
  let active = -1;
  modelTimes.forEach((t, i) => {
    if (currentMinutes >= minutes(t)) active = i;
  });
  setText("#window", active >= 0 ? `${modelTimes[active]} ET — ${labels[active]}` : "Before model window");
  document.querySelectorAll(".time").forEach((el, i) => {
    el.classList.toggle("active", i === active);
    el.classList.toggle("past", i < active);
  });
}

document.querySelector("#timeline").innerHTML = modelTimes.map((t, i) =>
  `<div class="time"><strong>${t}</strong><span>${labels[i]}</span></div>`
).join("");

updateClock();
loadResearchResults();
setInterval(updateClock, 15000);
