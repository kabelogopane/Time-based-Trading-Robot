const modelTimes = ["08:45","09:45","10:45","11:45","12:45","13:45","15:45"];
const labels = ["Pre-open","Anchor","Reaction","Follow-through","Midday","Afternoon","Pre-close"];

function minutes(hhmm){const [h,m]=hhmm.split(":").map(Number);return h*60+m;}
function updateClock(){
  const now=new Date();
  const formatter=new Intl.DateTimeFormat("en-ZA",{timeZone:"Africa/Johannesburg",hour:"2-digit",minute:"2-digit",hour12:false});
  const current=formatter.format(now);
  document.querySelector("#clock").textContent=current;
  const currentMinutes=minutes(current);
  let active=-1;
  modelTimes.forEach((t,i)=>{if(currentMinutes>=minutes(t))active=i;});
  document.querySelector("#window").textContent=active>=0?`${modelTimes[active]} — ${labels[active]}`:"Before model window";
  document.querySelectorAll(".time").forEach((el,i)=>{el.classList.toggle("active",i===active);el.classList.toggle("past",i<active);});
}

document.querySelector("#timeline").innerHTML=modelTimes.map((t,i)=>`<div class="time"><strong>${t}</strong><span>${labels[i]}</span></div>`).join("");
updateClock();
setInterval(updateClock,15000);
