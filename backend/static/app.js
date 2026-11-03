
let company="All", customers=[], expiryView="all", searchTimer=null;
const $=id=>document.getElementById(id);
const months=window.MONTH_LIST;
$("cycleLabel").textContent=months[3][1]+" "+months[3][0].slice(0,4);
function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}

function highlight(value){
 const text=String(value??""); const query=$("search").value.trim(); if(!query)return esc(text);
 const tokens=query.split(/\s+/).filter(Boolean).slice(0,6); let html=esc(text);
 for(const token of tokens){const escaped=token.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");try{html=html.replace(new RegExp("("+escaped+")","ig"),'<mark class="search-hit">$1</mark>');}catch(e){}}
 return html;
}
function renderTabs(){
 const all=["All",...window.COMPANY_LIST];
 $("tabs").innerHTML=all.map(x=>`<button class="tab ${x===company?"active":""}" data-company="${esc(x)}">${esc(x)}</button>`).join("");
 document.querySelectorAll(".tab").forEach(b=>b.onclick=()=>{company=b.dataset.company;load();});
}
async function load(){
 renderTabs();
 const params=new URLSearchParams({company,q:$("search").value,sort:$("sort").value,payment:$("payfilter").value,expiry:expiryView});
 const res=await fetch("/api/customers?"+params); customers=await res.json();
 const viewNames={today:"Packs expiring today",expired:"Expired · Not recharged",tomorrow:"Packs expiring tomorrow",week:"Packs expiring within 7 days"};
 $("listTitle").textContent=(viewNames[expiryView]|| (company==="All"?"All customers":company+" customers"))+(company!=="All"?" · "+company:"");
 $("listCount").textContent=customers.length+" customers shown"+(expiryView!=="all"?" · expiry filter active":"");
 drawRows(); loadSummary();
 const back=$("backMain"); if(back) back.classList.toggle("hidden", expiryView==="all");
}
function monthButton(c,p){return `<button class="month ${p.paid?"":"pending"}" onclick="togglePayment(${c.id},'${p.key}',${!p.paid})">${p.label} ${p.paid?"✓ Paid":"Pending"}</button>`;}
function normalizeIndianPhone(phone){
 const raw=String(phone||"").trim();
 if(!raw) return "";
 let digits=raw.replace(/\\D/g,"");
 if(digits.length===10) return "+91"+digits;
 if(digits.length===11 && digits.startsWith("0")) return "+91"+digits.slice(1);
 if(digits.length===12 && digits.startsWith("91")) return "+"+digits;
 if(raw.startsWith("+")) return "+"+digits;
 return "+91"+digits;
}
function displayPhone(phone){
 const normalized=normalizeIndianPhone(phone);
 return normalized ? esc(normalized) : "—";
}
function callLink(phone){
 const number=String(phone||"").trim();
 if(!number) return '<button class="callbtn disabled" type="button" disabled title="Add a phone number to this customer first">☎ Call</button>';
 const tel=normalizeIndianPhone(number);
 const digits=tel.replace(/\\D/g,"");
 if(digits.length<11 || digits.length>15) return '<button class="callbtn disabled" type="button" disabled title="Enter a valid phone number">☎ Call</button>';
 return `<a class="callbtn" href="tel:${esc(tel)}" aria-label="Call ${esc(tel)}">☎ Call</a>`;
}
function expiryText(c){
 if(!c.pack_expiry)return "Not set";
 const d=new Date(c.pack_expiry+"T00:00:00");
 const dateLabel=d.toLocaleDateString("en-IN",{day:"2-digit",month:"short",year:"numeric"});
 if(c.days_to_expiry<0)return `Expired ${Math.abs(c.days_to_expiry)} ${Math.abs(c.days_to_expiry)===1?"day":"days"} ago · ${dateLabel}`;
 if(c.days_to_expiry===0)return `Expires today · ${dateLabel}`;
 if(c.days_to_expiry===1)return `Expires tomorrow · ${dateLabel}`;
 return `Expires in ${c.days_to_expiry} days · ${dateLabel}`;
}
function setExpiryView(view){expiryView=view;load().then(()=>$ ("register").scrollIntoView({behavior:"smooth",block:"start"}));}
function returnToMain(){expiryView="all";company="All";$("search").value="";$("payfilter").value="all";load().then(()=>$ ("expiryDashboard").scrollIntoView({behavior:"smooth",block:"start"}));}
function drawRows(){
 const rows=customers.map(c=>`<tr>
 <td class="person"><b>${highlight(c.name)}</b><small>${highlight(c.area||"Area not set")}</small></td><td class="phone-cell"><span>${highlight(displayPhone(c.phone))}</span>${callLink(c.phone)}</td><td>${highlight(c.connection_id||"—")}</td><td><span class="provider">${highlight(c.company)}</span></td>
 ${c.payments.map(p=>`<td>${monthButton(c,p)}</td>`).join("")}
 <td class="expiry ${c.days_to_expiry!==null&&c.days_to_expiry<=2?"soon":""}">${expiryText(c)}</td>
 <td><button class="recharge ${c.recharged?"done":""}" onclick="markRecharge(${c.id},${c.recharged})">${c.recharged?"↶ Rollback recharge":"Not recharged"}</button></td>
 <td class="action-cell"><div class="actionbar">${callLink(c.phone)}<button class="actionbtn" onclick="editCustomer(${c.id})">Edit</button><button class="actionbtn" onclick="deleteCustomer(${c.id})">Delete</button></div></td></tr>`).join("");
 $("rows").innerHTML=rows||`<tr><td colspan="11" class="empty">No customers found.</td></tr>`;
 $("mobileRows").innerHTML=customers.map(c=>`<article class="customer-card"><div class="customer-top"><div><b>${highlight(c.name)}</b><small>${displayPhone(c.phone)==="—"?"Phone not set":highlight(displayPhone(c.phone))} · ${highlight(c.company)}</small></div><div class="mobile-actions">${callLink(c.phone)}<button class="actionbtn" onclick="editCustomer(${c.id})">Edit</button><button class="actionbtn" onclick="deleteCustomer(${c.id})">Delete</button></div></div><div class="meta-line">Connection ID: <b>${highlight(c.connection_id||"Not set")}</b> · ${highlight(c.area||"Area not set")}</div><div class="monthsline">${c.payments.map(p=>monthButton(c,p)).join("")}</div><div class="recharge-line"><span>Pack expiry: <b>${expiryText(c)}</b></span><button class="recharge ${c.recharged?"done":""}" onclick="markRecharge(${c.id},${c.recharged})">${c.recharged?"↶ Rollback recharge":"Not recharged"}</button></div></article>`).join("")||`<div class="empty">No customers found.</div>`;
}
async function togglePayment(id,key,paid){
 const r=await fetch("/api/payment",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({customer_id:id,month_key:key,paid})});
 if(!r.ok){alert("Could not update payment status.");return;} load();
}
async function markRecharge(id,already){
 if(already){
   if(!confirm("Roll back this recharge? The pack expiry will return to the exact date saved before the recharge."))return;
   const rollback=await fetch("/api/recharge/reset",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({customer_id:id})});
   const rollbackData=await rollback.json();
   if(!rollback.ok){alert(rollbackData.error||"Could not roll back recharge.");return;}
   alert("Recharge rolled back. Original expiry restored: "+(rollbackData.pack_expiry||"Not set"));
 }else{
   if(!confirm("Mark as recharged and extend the pack expiry by 30 days?"))return;
   const r=await fetch("/api/recharge",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({customer_id:id})});
   const d=await r.json();if(!r.ok){alert(d.error||"Recharge update failed.");return;}
   alert("Recharge saved. New pack expiry: "+d.pack_expiry);
 }
 load();
}
async function loadSummary(){
 const [s,r]=await Promise.all([fetch("/api/summary").then(x=>x.json()),fetch("/api/reminders").then(x=>x.json())]);
 $("total").textContent=s.total;$("pending").textContent=s.pending;$("expires").textContent=s.expiring_tomorrow;
 const ec=s.expiry_counts||{};
 $("countToday").textContent=ec.today||0;$("countExpired").textContent=ec.expired||0;
 $("countTomorrow").textContent=ec.tomorrow||0;$("countWeek").textContent=ec.week||0;
 $("remExp").textContent=r.expiring_tomorrow.length+" customers";$("remPay").textContent=r.long_pending.length+" customers";
}
async function showReminder(kind){
 const r=await fetch("/api/reminders").then(x=>x.json());const list=r[kind]||[];
 $("reminderList").classList.remove("hidden");
 $("reminderList").innerHTML=`<div class="heading"><div><label>REMINDER RECIPIENTS</label><h2>${kind==="expiring_tomorrow"?"Packs expiring tomorrow":"Pending 3+ months"}</h2></div><button class="btn ghost" onclick="selectAllReminders('${kind}')">Select all</button></div><div id="remRows">${list.map(x=>`<label class="remrow"><span><input type="checkbox" class="remcheck" data-id="${x.id}" data-phone="${esc(x.phone)}" data-name="${esc(x.name)}" data-company="${esc(x.company)}"> <b>${esc(x.name)}</b> · ${esc(x.company)} · ${esc(x.phone||"No phone")}</span><small>${kind==="long_pending"?x.pending_months+" months pending":"Expires tomorrow"}</small></label>`).join("")||"<p>No customers currently match this reminder.</p>"}</div><div class="modalactions"><button class="btn ghost" onclick="sendSelected('sms','${kind}')">Send SMS</button><button class="btn primary" onclick="sendSelected('wa','${kind}')">WhatsApp selected</button></div>`;
}
function selectAllReminders(){document.querySelectorAll(".remcheck").forEach(x=>x.checked=true);}
function sendSelected(mode,kind){
 const selected=[...document.querySelectorAll(".remcheck:checked")];
 if(!selected.length){alert("Select at least one customer.");return;}
 const message=kind==="expiring_tomorrow"?"Reminder: your cable pack expires tomorrow. Please recharge to continue your service.":"Reminder: your cable payment has been pending for 3 or more months. Please contact us to update your payment.";
 if(mode==="wa"){
   if(selected.length>1){alert("WhatsApp opens one chat at a time. We'll open the first selected customer; repeat for the others.");}
   const x=selected[0];if(!x.dataset.phone){alert("This customer has no phone number saved.");return;}
   window.open("https://wa.me/91"+x.dataset.phone.replace(/\D/g,"")+"?text="+encodeURIComponent(message),"_blank");
 }else{
   const x=selected[0];if(!x.dataset.phone){alert("This customer has no phone number saved.");return;}
   window.location.href="sms:"+x.dataset.phone+"?body="+encodeURIComponent(message);
 }
}
function openModal(title,c=null){
 $("modalTitle").textContent=title;$("fid").value=c?.id||"";$("fname").value=c?.name||"";$("fphone").value=c?.phone||"";$("fconn").value=c?.connection_id||"";$("fcompany").value=c?.company||window.COMPANY_LIST[0];$("farea").value=c?.area||"";$("famount").value=c?.monthly_amount||"";$("fexpiry").value=c?.pack_expiry||"";$("fnotes").value=c?.notes||"";$("modal").classList.remove("hidden");
}
function editCustomer(id){const c=customers.find(x=>x.id===id);if(c)openModal("Edit customer",c);}
$("add").onclick=()=>openModal("Add customer");$("close").onclick=$("cancel").onclick=()=>$("modal").classList.add("hidden");
$("customerForm").onsubmit=async e=>{
 e.preventDefault();
 const save=$("saveCustomer"); if(save.disabled)return;
 const id=$("fid").value;
 const d={name:$("fname").value.trim(),phone:$("fphone").value.trim(),connection_id:$("fconn").value.trim(),company:$("fcompany").value,area:$("farea").value.trim(),monthly_amount:$("famount").value,pack_expiry:$("fexpiry").value,notes:$("fnotes").value.trim()};
 if(!d.name){alert("Please enter the customer name.");$("fname").focus();return;}
 save.disabled=true; save.textContent="Saving…";
 try{
  const r=await fetch(id?"/api/customers/"+id:"/api/customers",{method:id?"PUT":"POST",headers:{"Content-Type":"application/json","Accept":"application/json"},body:JSON.stringify(d)});
  const out=await r.json().catch(()=>({error:"The server returned an unreadable response."}));
  if(!r.ok)throw new Error(out.error||`Save failed (${r.status}).`);
  $("modal").classList.add("hidden");
  await load();
  alert(id?"Customer details updated successfully.":"Customer added successfully.");
 }catch(err){alert(err.message||"Could not save customer. Check your connection and try again.");}
 finally{save.disabled=false;save.textContent="Save customer";}
};
async function deleteCustomer(id){if(!confirm("Remove this customer from the active register?"))return;await fetch("/api/customers/"+id,{method:"DELETE"});load();}
$("sort").onchange=load;$("payfilter").onchange=load;$("refreshRem").onclick=loadSummary;
$("search").oninput=()=>{clearTimeout(searchTimer);searchTimer=setTimeout(load,180);$("clearSearch").classList.toggle("visible",!!$("search").value);};
$("clearSearch").onclick=()=>{$("search").value="";$("clearSearch").classList.remove("visible");load();$("search").focus();};
$("search").addEventListener("keydown",e=>{if(e.key==="Escape")$("clearSearch").click();});
$("backMain").onclick=returnToMain;
load();
