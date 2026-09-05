const modelTimes = ["08:45","09:45","10:45","11:45","12:45","13:45","15:45"];
const labels = ["Pre-open","Anchor","Reaction","Follow-through","Midday","Afternoon","Pre-close"];
const timezone = "America/New_York";

// DEMO SESSION: this is sample data used to make the rule engine visible.
// Replace it with validated historical OHLC data in the backtest pipeline.
const demoMarket = {
  anchor: { high: 19842.0, low: 19782.0, close: 19830.0 },
  price: 19858.0,
  recentHigh: 19872.0,
  recentLow: 19755.0,
  structure: "bullish",
  displacement: true,
  liquidity: "buy-side nearby"
};

function minutes(hhmm){const [h,m]=hhmm.split(":").map(Number);return h*60+m;}

function getNewYorkTime(){
  const now = new Date();
  return new Intl.DateTimeFormat("en-US",{
    timeZone: timezone,
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(now);
}

function setText(id, value){
  const element = document.querySelector(id);
  if (element) element.textContent = value;
}

function priceState(price, anchor){
  if (price > anchor.high) return "Above anchor";
  if (price < anchor.low) return "Below anchor";
  return "Inside anchor";
}

function evaluateDemo(){
  const state = priceState(demoMarket.price, demoMarket.anchor);
  const bullishConfirmed = state === "Above anchor" && demoMarket.structure === "bullish" && demoMarket.displacement;
  const bearishConfirmed = state === "Below anchor" && demoMarket.structure === "bearish" && demoMarket.displacement;

  setText("#anchor", `${demoMarket.anchor.high.toFixed(2)} / ${demoMarket.anchor.low.toFixed(2)}`);
  setText("#anchorRange", `${(demoMarket.anchor.high - demoMarket.anchor.low).toFixed(2)} pts`);
  setText("#priceState", `${state} · ${demoMarket.price.toFixed(2)}`);
  setText("#structure", demoMarket.structure.toUpperCase());
  setText("#displacement", demoMarket.displacement ? "Confirmed" : "Not confirmed");
  setText("#liquidity", `${demoMarket.liquidity} · H ${demoMarket.recentHigh.toFixed(2)} / L ${demoMarket.recentLow.toFixed(2)}`);

  if (bullishConfirmed) {
    const entry = demoMarket.price;
    const invalidation = demoMarket.anchor.low;
    const risk = entry - invalidation;
    const target = entry + risk * 2;
    setText("#decision", "DEMO: CONFIRMED LONG SETUP");
    setText("#direction", "LONG");
    setText("#entry", entry.toFixed(2));
    setText("#invalidation", invalidation.toFixed(2));
    setText("#target", target.toFixed(2));
  } else if (bearishConfirmed) {
    const entry = demoMarket.price;
    const invalidation = demoMarket.anchor.high;
    const risk = invalidation - entry;
    const target = entry - risk * 2;
    setText("#decision", "DEMO: CONFIRMED SHORT SETUP");
    setText("#direction", "SHORT");
    setText("#entry", entry.toFixed(2));
    setText("#invalidation", invalidation.toFixed(2));
    setText("#target", target.toFixed(2));
  } else {
    setText("#decision", "DEMO: WAIT FOR CONFIRMATION");
    ["#direction","#entry","#invalidation","#target"].forEach(id => setText(id, "--"));
  }
}

function updateClock(){
  const current = getNewYorkTime();
  setText("#clock", `${current} ET`);
  const currentMinutes = minutes(current);
  let active = -1;
  modelTimes.forEach((t,i)=>{if(currentMinutes>=minutes(t)) active=i;});
  setText("#window", active>=0 ? `${modelTimes[active]} ET — ${labels[active]}` : "Before model window");
  document.querySelectorAll(".time").forEach((el,i)=>{
    el.classList.toggle("active",i===active);
    el.classList.toggle("past",i<active);
  });
}

document.querySelector("#timeline").innerHTML=modelTimes.map((t,i)=>
  `<div class="time"><strong>${t}</strong><span>${labels[i]}</span></div>`
).join("");

updateClock();
evaluateDemo();
setInterval(updateClock,15000);
