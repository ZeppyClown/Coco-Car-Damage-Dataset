"use strict";
const api = document.querySelector('meta[name="workshop-api"]').content;
const reviewerAccount = document.querySelector('meta[name="workshop-user"]').content;
const $ = id => document.getElementById(id);
const JSON_POST = body => ({ method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

// Fields typed on step 1. The record keeps a review state for each of these.
const headerFields = ["job_reference", "vehicle_reference", "make", "model", "customer_reference", "quotation_date", "date_in", "date_out"];
// Older records may carry these; the simple screen keeps them untouched.
const keptFields = ["diagram_notes", "written_total", "written_adjustment", "written_grand_total", "date_note_raw", "diagram_notes_raw", "written_totals_raw"];
const fuelLevels = ["empty", "1/5", "2/5", "3/5", "4/5", "full"];
const sections = {
  knock: { title: "2 · Knock", hint: "One line for each knocking job, as written on the sheet. Then click the car on the right to show where.", next: ["repair", "Next: Repair & parts →"] },
  repair: { title: "3 · Repair & parts", hint: "Servicing, repairs and parts to change, for example radiator, fan motor or front oil seal.", next: ["spray", "Next: Spray →"] },
  spray: { title: "4 · Spray", hint: "Spray painting lines, as written on the sheet. Click the car to show which panels.", next: ["check", "Next: Check & save →"] },
};
const panels = ["Front bumper", "Bonnet", "Front left fender", "Front right fender", "Front left door", "Front right door",
  "Rear left door", "Rear right door", "Rear left fender", "Rear right fender", "Boot", "Rear bumper", "Roof", "Rocker panel"];
const quickLines = {
  knock: panels.map(name => "Knock " + name.toLowerCase()),
  repair: ["Servicing", "Engine oil", "Radiator", "Coolant", "Fan motor", "Front oil seal", "Windscreen replace", "Headlight", "Rear lamp", "Side mirror", "Labour"],
  spray: [...panels.map(name => "Spray " + name.toLowerCase()), "Spray rim", "Polish"],
};
const accidentFields = ["claim_type", "accident_date", "accident_place", "insurer", "policy_number", "report_number", "other_vehicle", "other_party", "other_insurer", "excess", "notes"];
const claimNames = { own_damage: "claim own insurance", third_party: "claim the other party's insurance", private_settlement: "private settlement", report_only: "report for record only" };
const expenseTypes = [["parts", "Parts"], ["paint", "Paint & materials"], ["subcontract", "Outside work"], ["wages", "Wages"], ["rent", "Rent"], ["utilities", "Utilities"], ["tools", "Tools & equipment"], ["other", "Other"]];
const stageNames = { quote: "Quotation", approved_scope: "Agreed job", completed_work: "Finished job" };

let step = "car", job = null, sourceId = null, aiProvenance = null, kept = {}, marks = [], fuel = null;
let dirty = false, zoom = 1, rotation = 0, reviewed = [];
let lookupParams = new URLSearchParams(), lookupOffset = 0;
let billingRevision = null, billingPreview = null, billingIssued = null, billingAllowed = false, billingDirty = false, billingSupplier = null;

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function status(message, error = false) { $("status").textContent = message; $("status").classList.toggle("error", error); }
function markDirty() { dirty = true; $("dirty-label").textContent = "Unsaved changes"; updateIssueButton(); }

// ---- steps -----------------------------------------------------------------
function showStep(name) {
  step = name;
  const panel = sections[name] ? "lines" : name;
  for (const node of document.querySelectorAll("[data-panel]")) node.hidden = node.dataset.panel !== panel;
  for (const button of document.querySelectorAll("#steps button, .tools [data-step]")) button.classList.toggle("active", button.dataset.step === name);
  $("draft-form").hidden = ["find", "help", "books", "setup"].includes(name);
  $("side").hidden = name === "print";
  if (sections[name]) {
    $("lines-title").textContent = sections[name].title; $("lines-hint").textContent = sections[name].hint;
    $("lines-next").textContent = sections[name].next[1]; showRows(); showQuick();
  }
  if (name === "check") renderSummary();
  if (name === "books") loadBooks();
  viewImage(); window.scrollTo(0, 0);
}
for (const button of document.querySelectorAll("[data-step]")) button.addEventListener("click", () => showStep(button.dataset.step));
$("lines-next").addEventListener("click", () => showStep(sections[step].next[0]));

// ---- fuel gauge ------------------------------------------------------------
for (const level of fuelLevels) {
  const button = element("button", level === "empty" ? "Empty" : level === "full" ? "Full" : level); button.type = "button"; button.dataset.level = level;
  button.addEventListener("click", () => { fuel = fuel === level ? null : level; showFuel(); markDirty(); });
  $("fuel").append(button);
}
function showFuel() { for (const button of $("fuel").querySelectorAll("button")) button.classList.toggle("active", button.dataset.level === fuel); }

// ---- work lines ------------------------------------------------------------
function parseAmount(text) {
  const cleaned = text.replace(/[$,\s]|\/-|sgd/gi, "");
  return /^\d{1,10}(\.\d{1,2})?$/.test(cleaned) ? cleaned : null;
}
function addRow(item = {}, section = step) {
  const row = element("div", "", "row"); row.dataset.section = item.section || section;
  row.dataset.raw = item.description_raw || ""; row.dataset.loaded = item.description || item.description_raw || "";
  const number = element("span", "", "number");
  const text = element("input"); text.maxLength = 2000; text.className = "text"; text.value = row.dataset.loaded; text.setAttribute("aria-label", "Comments or remarks / items");
  const amount = element("input"); amount.maxLength = 200; amount.className = "amount"; amount.inputMode = "decimal"; amount.setAttribute("aria-label", "Amount");
  amount.value = item.amount ?? item.amount_raw ?? "";
  const unsure = element("input"); unsure.type = "checkbox"; unsure.className = "unsure"; unsure.setAttribute("aria-label", "Not sure");
  unsure.checked = item.description_state === "unclear" || item.amount_state === "unclear";
  const crossed = element("input"); crossed.type = "checkbox"; crossed.className = "crossed"; crossed.setAttribute("aria-label", "Crossed out"); crossed.checked = Boolean(item.cancelled);
  const remove = element("button", "✕"); remove.type = "button"; remove.title = "Remove this line";
  remove.addEventListener("click", () => { if (!text.value.trim() || window.confirm("Remove this line?")) { row.remove(); markDirty(); showRows(); } });
  crossed.addEventListener("change", () => row.classList.toggle("cancelled", crossed.checked));
  row.classList.toggle("cancelled", crossed.checked);
  row.append(number, text, amount, unsure, crossed, remove); $("items").append(row); return row;
}
function showRows() {
  let shown = 0;
  for (const row of $("items").children) {
    row.hidden = row.dataset.section !== step;
    if (!row.hidden) row.querySelector(".number").textContent = ++shown;
  }
  $("no-lines").hidden = shown > 0; $("add-item").disabled = $("items").children.length >= 50;
}
$("add-item").addEventListener("click", () => { addRow().querySelector(".text").focus(); markDirty(); showRows(); });
function showQuick() {
  $("quick").replaceChildren(...quickLines[step].map(text => {
    const chip = element("button", text, "chip"); chip.type = "button";
    chip.addEventListener("click", () => { const row = addRow({ description: text }); markDirty(); showRows(); row.querySelector(".amount").focus(); });
    return chip;
  }));
}
function readRows(confirmed) {
  return [...$("items").children].map(row => {
    const text = row.querySelector(".text").value.trim(), typed = row.querySelector(".amount").value.trim();
    const unsure = row.querySelector(".unsure").checked, amount = parseAmount(typed), done = confirmed ? "confirmed" : "proposed";
    return {
      section: row.dataset.section, cancelled: row.querySelector(".crossed").checked,
      description_raw: text === row.dataset.loaded && row.dataset.raw ? row.dataset.raw : text,
      description: text || null, description_state: !text ? "missing" : unsure ? "unclear" : done,
      amount_raw: typed, amount, amount_state: amount === null ? (typed ? "unclear" : "missing") : unsure ? "unclear" : done,
    };
  }).filter(item => item.description_raw || item.amount_raw);
}

// ---- car marks -------------------------------------------------------------
function showMarks() {
  for (const old of $("car").querySelectorAll(".mark")) old.remove();
  $("marks").replaceChildren();
  marks.forEach((mark, index) => {
    const dot = element("span", String(index + 1), "mark"); dot.style.left = mark.x + "%"; dot.style.top = mark.y + "%"; $("car").append(dot);
    const line = element("li"); const note = element("input"); note.maxLength = 200; note.value = mark.note; note.placeholder = "What is it? e.g. rear bumper dent";
    note.addEventListener("input", () => { mark.note = note.value; });
    const remove = element("button", "✕"); remove.type = "button"; remove.title = "Remove this mark";
    remove.addEventListener("click", () => { marks.splice(index, 1); showMarks(); markDirty(); });
    line.append(note, remove); $("marks").append(line);
  });
}
$("car").addEventListener("click", event => {
  if (event.target.classList.contains("mark")) return;
  if (marks.length >= 30) return status("30 marks is the most one sheet can hold.", true);
  const box = $("car").getBoundingClientRect();
  marks.push({ x: Math.round((event.clientX - box.left) / box.width * 1000) / 10, y: Math.round((event.clientY - box.top) / box.height * 1000) / 10, note: "" });
  showMarks(); markDirty(); $("marks").lastChild.querySelector("input").focus();
});
$("car-outline").addEventListener("error", () => { $("car-outline").hidden = true; $("car").classList.add("blank"); });
$("car-outline").src = api + "/sheet-diagram";

// ---- car seen before: fill in what is empty, never overwrite typed values ---
async function lookUpCar() {
  const number = $("vehicle_reference").value.trim(), box = $("car-history"); box.hidden = true;
  if (!number) return;
  let car;
  try { car = await request("/vehicles?number=" + encodeURIComponent(number)); } catch (error) { return; }
  const others = car.jobs.filter(entry => entry.job_id !== job?.id); if (!others.length) return;
  let filled = false;
  for (const [id, value] of [["customer_reference", car.owner], ["contact", car.contact], ["make", car.make], ["model", car.model]]) {
    if (value && !$(id).value.trim()) { $(id).value = value; filled = true; }
  }
  if (filled) markDirty();
  box.replaceChildren(element("strong", `This car has been here ${others.length} time${others.length > 1 ? "s" : ""} before.` + (filled ? " Empty boxes were filled in from last time; check them." : "")));
  const list = element("ul");
  for (const entry of others.slice(0, 10)) {
    const line = element("li", `${entry.date} · ${entry.job_reference} · ${entry.work.slice(0, 4).join(", ") || "no lines"} · $${entry.invoice_total ?? entry.amount}${entry.invoice_total ? " invoiced" : ""} `);
    const open = element("button", "Open"); open.type = "button"; open.addEventListener("click", () => openJob(entry.job_id)); line.append(open); list.append(line);
  }
  box.append(list); box.hidden = false;
}
$("vehicle_reference").addEventListener("change", lookUpCar);

// ---- photo of the paper sheet ---------------------------------------------
function viewImage() {
  const image = $("source-image"); if (image.hidden || !image.naturalWidth) return;
  const fit = Math.min(1, (document.querySelector(".viewer").clientWidth - 24) / image.naturalWidth);
  const width = image.naturalWidth * fit * zoom, height = image.naturalHeight * fit * zoom;
  image.style.width = width + "px"; image.style.height = height + "px";
  image.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`;
  $("image-stage").style.width = (rotation % 180 ? height : width) + "px";
  $("image-stage").style.height = (rotation % 180 ? width : height) + "px";
  $("zoom-label").textContent = Math.round(zoom * 100) + "%";
}
function showSource() {
  const image = $("source-image"); zoom = 1; rotation = 0;
  image.hidden = !sourceId; $("photo").hidden = !sourceId;
  $("source-identity").textContent = sourceId ? "Photo attached." : "No photo attached.";
  if (sourceId) image.src = api + "/documents/" + encodeURIComponent(sourceId) + "/preview"; else image.removeAttribute("src");
}

// ---- record <-> screen -----------------------------------------------------
function readAccident() {
  if (!$("accident-claim_type").value) return null;
  const accident = {};
  for (const name of accidentFields) accident[name] = $("accident-" + name).value.trim() || (name === "notes" ? "" : null);
  if (accident.excess !== null) accident.excess = parseAmount(accident.excess) ?? accident.excess;
  return accident;
}
function render(record = { data_origin: "private_source", items: [] }) {
  resetBilling();
  $("reviewer").textContent = reviewerAccount;
  aiProvenance = record.ai_provenance || null;
  for (const name of accidentFields) $("accident-" + name).value = record.accident?.[name] ?? "";
  $("accident-box").open = Boolean(record.accident);
  $("ai-provenance").textContent = aiProvenance ? `First draft suggested by AI (${aiProvenance.model}). Check every value.` : "";
  sourceId = record.source_document_id || null; $("data-origin").value = record.data_origin; $("data-origin").disabled = Boolean(job);
  $("record-stage").value = stageNames[record.record_stage] ? record.record_stage : "quote";
  $("manual-provenance").value = record.manual_provenance || "";
  for (const name of headerFields) $(name).value = record[name] ?? "";
  $("contact").value = record.contact ?? "";
  kept = { states: {} };
  for (const name of keptFields) kept[name] = record[name] ?? (name.endsWith("_raw") ? "" : null);
  for (const name of keptFields.slice(0, 4)) if (record.field_states?.[name]) kept.states[name] = record.field_states[name];
  kept.currency = record.currency ?? null;
  fuel = record.fuel_level || null; showFuel();
  marks = (record.diagram_marks || []).map(mark => ({ ...mark })); showMarks();
  $("items").replaceChildren(); for (const item of record.items || []) addRow(item, "repair");
  showRows(); dirty = false; $("dirty-label").textContent = "No unsaved changes"; $("source-file").value = "";
  $("record-identity").textContent = job ? `${record.job_reference || "Job without a number"} · saved version ${job.draft_version}` : "New job, not saved yet";
  $("open-id").value = job?.id || ""; showSource(); $("review-ack").checked = false; $("car-history").hidden = true;
}
function readDraft(confirmed = false) {
  const done = confirmed ? "confirmed" : "proposed", items = readRows(confirmed);
  const draft = {
    data_origin: $("data-origin").value, source_document_id: sourceId, ai_provenance: aiProvenance,
    record_stage: $("record-stage").value, items, field_states: {},
    manual_provenance: $("manual-provenance").value.trim() || (sourceId ? null : "Typed in by workshop staff; no photo attached."),
    contact: $("contact").value.trim() || null, fuel_level: fuel, diagram_marks: marks.map(mark => ({ ...mark, note: mark.note.trim() })),
    accident: readAccident(),
  };
  for (const name of headerFields) { draft[name] = $(name).value.trim() || null; draft.field_states[name] = draft[name] ? done : "missing"; }
  for (const name of keptFields) draft[name] = kept[name];
  for (const [name, state] of Object.entries(kept.states)) draft.field_states[name] = confirmed && state === "proposed" ? "confirmed" : state;
  const priced = items.some(item => item.amount !== null) || kept.written_total !== null || kept.written_grand_total !== null;
  draft.currency = priced ? "SGD" : kept.currency; draft.field_states.currency = draft.currency ? done : "missing";
  return draft;
}
function renderSummary() {
  const draft = readDraft(), box = $("summary"); box.replaceChildren();
  const head = [["Job no.", draft.job_reference], ["Vehicle", [draft.vehicle_reference, draft.make, draft.model].filter(Boolean).join(" · ")],
    ["Owner", [draft.customer_reference, draft.contact].filter(Boolean).join(" · ")], ["Date in / out", [draft.date_in, draft.date_out].filter(Boolean).join(" → ")],
    ["Fuel", draft.fuel_level]];
  const top = element("p"); top.textContent = head.map(([label, value]) => `${label}: ${value || "—"}`).join("   |   "); box.append(top);
  const table = element("table"); let total = 0, problems = [];
  for (const [name, label] of [["knock", "Knock"], ["repair", "Repair & parts"], ["spray", "Spray"]]) {
    const rows = draft.items.filter(item => item.section === name); if (!rows.length) continue;
    const title = table.insertRow(); title.className = "group"; title.insertCell().textContent = label; title.insertCell();
    for (const item of rows) {
      const line = table.insertRow(); if (item.cancelled) line.className = "cancelled";
      line.insertCell().textContent = item.description_raw + (item.cancelled ? " (crossed out)" : "");
      line.insertCell().textContent = item.cancelled ? "" : item.amount ?? (item.amount_raw ? item.amount_raw + " ?" : "—");
      if (item.cancelled) continue;
      if (item.amount !== null) total += Number(item.amount);
      if (item.description_state === "unclear" || item.amount_state === "unclear") problems.push(item.description_raw || item.amount_raw);
    }
  }
  const sum = table.insertRow(); sum.className = "group"; sum.insertCell().textContent = "Total of the amounts typed in"; sum.insertCell().textContent = total.toFixed(2);
  box.append(table);
  if (draft.diagram_marks.length) box.append(element("p", "Car marks: " + draft.diagram_marks.map((mark, index) => `${index + 1} ${mark.note || "(no note)"}`).join("; ")));
  if (draft.accident) box.append(element("p", "Accident job: " + [claimNames[draft.accident.claim_type], draft.accident.insurer && "insurer " + draft.accident.insurer,
    draft.accident.report_number && "report " + draft.accident.report_number, draft.accident.other_vehicle && "other vehicle " + draft.accident.other_vehicle,
    draft.accident.excess && "excess $" + draft.accident.excess].filter(Boolean).join(" · ")));
  if (!draft.job_reference) problems.unshift("Job no. is empty");
  if (!draft.items.some(item => !item.cancelled && item.description)) problems.unshift("No work lines yet");
  if (problems.length) box.append(element("p", "Clear up before confirming: " + problems.join("; "), "notice"));
}

// ---- server calls ----------------------------------------------------------
async function request(path, options = {}) {
  const response = await fetch(api + path, options);
  if (response.status === 401) { location.href = "/workshop/login"; throw new Error("Please sign in again."); }
  const data = await response.json();
  if (!response.ok) {
    const detail = Array.isArray(data.detail) ? data.detail.slice(0, 20).map(error => error.msg.replace(/^Value error, /, "")).join("\n") : data.detail || data.error;
    throw new Error(detail || "That did not work. What you typed is still on screen.");
  }
  return data;
}
async function action(task) {
  const controls = [...document.querySelectorAll("button,input,select,textarea")].map(node => [node, node.disabled]);
  controls.forEach(([node]) => node.disabled = true);
  try { await task(); } catch (error) { status(error.message || "That did not work. What you typed is still on screen.", true); }
  finally { controls.forEach(([node, disabled]) => node.disabled = disabled); $("data-origin").disabled = Boolean(job); showRows(); updateIssueButton(); }
}
async function save(confirmed = false) {
  const draft = readDraft(confirmed);
  job = await request(job ? "/jobs/" + job.id : "/jobs", { ...JSON_POST(job ? { expected_version: job.draft_version, draft } : draft), method: job ? "PATCH" : "POST" });
  render(job.draft); history.replaceState(null, "", "/workshop?job=" + encodeURIComponent(job.id));
}
$("draft-form").addEventListener("submit", event => {
  event.preventDefault();
  if (billingDirty && !window.confirm("Discard the invoice details you typed and save the job?")) return;
  action(async () => { await save(); showStep(step); await historyStatus("Saved. Not confirmed yet."); });
});
$("confirm-record").addEventListener("click", () => {
  if (!$("review-ack").checked) return status("Tick the box to say you checked it first.", true);
  const draft = readDraft(true), active = draft.items.filter(item => !item.cancelled);
  const unsure = active.filter(item => item.description_state === "unclear" || item.amount_state === "unclear");
  if (!draft.job_reference) return status("Type the job no. on step 1 before confirming.", true);
  if (!active.some(item => item.description)) return status("Add at least one work line before confirming.", true);
  if (unsure.length) return status("Clear up these lines before confirming (untick “Not sure” or fix the amount): " + unsure.map(item => item.description_raw || item.amount_raw).join("; "), true);
  if (active.some(item => !item.description)) return status("A line has an amount but no words. Type what it is, or cross it out.", true);
  action(async () => {
    await save(true);
    const revision = await request("/jobs/" + job.id + "/confirm", JSON_POST({ expected_version: job.draft_version, reviewer: reviewerAccount, acknowledged: true }));
    await historyStatus(`Confirmed as checked (version ${revision.version}). You can print it now.`); showStep("print");
  });
});
function draftChanged(event) { if (!event.target.closest('.review-controls,[data-panel="print"],#photo-box')) markDirty(); }
$("draft-form").addEventListener("input", draftChanged);
$("draft-form").addEventListener("change", draftChanged);
$("data-origin").addEventListener("change", markDirty);
$("new-record").addEventListener("click", () => {
  if ((dirty || billingDirty) && !window.confirm("Discard unsaved changes and start a new job?")) return;
  job = null; render(); refreshHistory(); history.replaceState(null, "", "/workshop"); showStep("car"); status("New job. Nothing saved was deleted.");
});
function openJob(id) {
  if ((dirty || billingDirty) && !window.confirm("Discard unsaved changes and open another job?")) return;
  action(async () => { job = await request("/jobs/" + encodeURIComponent(id)); render(job.draft); showStep("check"); await historyStatus("Job opened."); });
}
$("open-record").addEventListener("click", () => { const id = $("open-id").value.trim(); if (id) openJob(id); else status("Paste a job ID first.", true); });
$("attach-source").addEventListener("click", () => {
  const file = $("source-file").files[0]; if (!file) return status("Choose a JPEG or PNG photo first.", true);
  const data = new FormData(); data.append("file", file); data.append("data_origin", $("data-origin").value);
  action(async () => { const source = await request("/documents", { method: "POST", body: data }); sourceId = source.id; showSource(); markDirty(); status("Photo attached. Save the job to keep it."); });
});
$("detach-source").addEventListener("click", () => { sourceId = null; showSource(); markDirty(); status("Photo removed from this job. The stored photo was not deleted."); });

// ---- history, printing and CSV --------------------------------------------
function link(text, href) { const node = element("a", text, "button"); node.href = href; node.target = "_blank"; node.rel = "noopener"; return node; }
function renderHistory() {
  const container = $("reviewed-history"); container.replaceChildren();
  const current = reviewed.find(revision => revision.version === job?.draft_version);
  $("review-state").textContent = !job ? "No job opened." : current ? "The saved job is confirmed. To correct it, change it, save and confirm again; older versions stay as they were."
    : reviewed.length ? "The job was changed after it was last confirmed. Confirm again on step 5 to print the new version." : "This job is not confirmed yet. Confirm it on step 5 to print or invoice.";
  for (const revision of reviewed) {
    const record = revision.record, card = element("section", "", "version");
    card.append(element("h3", `Version ${revision.version} · ${stageNames[record.record_stage]} · ${record.job_reference}`));
    card.append(element("p", `Checked by ${revision.reviewer} on ${new Date(revision.reviewed_at).toLocaleString()} · ${record.items.filter(item => !item.cancelled).length} work lines`, "hint"));
    card.append(link("Print job sheet", api + "/revisions/" + revision.id + "/sheet"));
    if (record.record_stage === "completed_work") {
      const bill = element("button", "Make invoice"); bill.type = "button"; bill.addEventListener("click", () => action(() => prepareInvoice(revision))); card.append(bill);
    }
    const download = element("button", "Download CSV"); download.type = "button";
    download.addEventListener("click", () => action(async () => {
      const exported = await request("/revisions/" + revision.id + "/exports", { method: "POST" });
      const response = await fetch(api + "/exports/" + exported.id + "/download");
      if (!response.ok) throw new Error("CSV download failed. The job is still saved.");
      const url = URL.createObjectURL(await response.blob()), anchor = element("a"); anchor.href = url; anchor.download = `job-${record.job_reference}-v${revision.version}.csv`;
      document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 60000);
      status("CSV downloaded: one row for each line of this job.");
    }));
    card.append(download);
    if (record.source_document_id) card.append(link("Open photo", api + "/documents/" + encodeURIComponent(record.source_document_id) + "/preview"));
    container.append(card);
  }
}
async function refreshHistory(append = false) {
  if (!job) { reviewed = []; $("more-history").hidden = true; renderHistory(); return; }
  let rows;
  try { rows = await request("/jobs/" + job.id + "/revisions?limit=20&offset=" + (append ? reviewed.length : 0)); }
  catch (error) { $("review-state").textContent = "History could not load. Open the job again to retry."; throw error; }
  if (!append) await loadJobInvoice();
  reviewed = append ? reviewed.concat(rows) : rows; $("more-history").hidden = rows.length < 20; renderHistory();
}
async function historyStatus(message) {
  try { await refreshHistory(); status(message); } catch (error) { status(message + " History could not load: " + error.message, true); }
}
$("more-history").addEventListener("click", () => action(() => refreshHistory(true)));

// ---- find job --------------------------------------------------------------
async function runLookup(offset, filters = lookupParams) {
  const params = new URLSearchParams(filters); params.set("limit", "20"); params.set("offset", offset);
  let data;
  try { data = await request("/jobs?" + params); }
  catch (error) { $("lookup-state").textContent = "Search failed. Results below are from the last search that worked."; throw error; }
  lookupParams = new URLSearchParams(filters); lookupOffset = offset;
  const container = $("lookup-results"); container.replaceChildren();
  $("lookup-state").textContent = data.results.length ? `Showing ${offset + 1}–${offset + data.results.length}.` : "Nothing found.";
  $("lookup-previous").hidden = offset === 0; $("lookup-next").hidden = !data.has_more;
  for (const result of data.results) {
    const record = result.record, card = element("section", "", "version");
    card.append(element("h3", `${record.job_reference} · ${stageNames[record.record_stage]}`));
    card.append(element("p", `Owner: ${record.customer_reference || "—"} · Vehicle: ${record.vehicle_reference || "—"} · confirmed ${new Date(result.reviewed_at).toLocaleDateString()}`));
    if (result.has_unreviewed_changes) card.append(element("p", "Changed since it was last confirmed.", "hint"));
    const open = element("button", "Open job"); open.type = "button"; open.addEventListener("click", () => openJob(result.job_id)); card.append(open);
    container.append(card);
  }
}
$("lookup-form").addEventListener("submit", event => {
  event.preventDefault(); const filters = new URLSearchParams();
  for (const name of ["q", "customer", "vehicle", "reference", "stage", "reviewed_from", "reviewed_to"]) {
    const value = $("lookup-" + name).value.trim(); if (value) filters.set(name, value);
  }
  action(() => runLookup(0, filters));
});
$("lookup-next").addEventListener("click", () => action(() => runLookup(lookupOffset + 20)));
$("lookup-previous").addEventListener("click", () => action(() => runLookup(Math.max(0, lookupOffset - 20))));
$("zoom-in").addEventListener("click", () => { zoom = Math.min(3, zoom + .25); viewImage(); });
$("zoom-out").addEventListener("click", () => { zoom = Math.max(.25, zoom - .25); viewImage(); });
$("rotate-source").addEventListener("click", () => { rotation = (rotation + 90) % 360; viewImage(); });
$("source-image").addEventListener("load", viewImage);
$("source-image").addEventListener("error", () => status("The photo could not load. The job can still be edited.", true));

// ---- invoice ---------------------------------------------------------------
function resetBilling() {
  billingRevision = null; billingPreview = null; billingIssued = null; billingAllowed = false; billingDirty = false;
  $("invoice-form").hidden = true; $("issued-invoice").replaceChildren(); $("invoice-preview").textContent = "";
  $("invoice-ack").checked = false; $("billing-state").textContent = "Choose “Make invoice” on a finished job above.";
  $("invoice-payment").replaceChildren();
  updateIssueButton();
}
function updateIssueButton() {
  $("issue-invoice").disabled = !billingPreview || !billingAllowed || Boolean(billingIssued) || !$("invoice-ack").checked || dirty;
}
function showIssuedInvoice(invoice) {
  billingIssued = invoice; billingPreview = null; billingDirty = false; $("invoice-form").hidden = true;
  const container = $("issued-invoice"); container.replaceChildren();
  container.append(element("p", `${invoice.number} · total $${invoice.preview.total} · GST $${invoice.preview.gst} · issued by ${invoice.issued_by}`));
  container.append(link("Print invoice on the workshop form", api + "/invoices/" + invoice.id + "/sheet"), link("Plain copy", api + "/invoices/" + invoice.id + "/print"));
  $("billing-state").textContent = "Invoice issued. Record the payment below when the customer pays.";
  updateIssueButton(); paymentBox(invoice.id, $("invoice-payment")).catch(() => {});
}
async function loadJobInvoice() {
  if (!job) return;
  const response = await fetch(api + "/jobs/" + job.id + "/invoice");
  if (response.status === 404) return;
  if (!response.ok) throw new Error("The invoice could not load. Open the job again before issuing.");
  showIssuedInvoice(await response.json());
}
function singaporeDate() {
  const parts = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Singapore", year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date());
  const part = type => parts.find(value => value.type === type).value;
  return `${part("year")}-${part("month")}-${part("day")}`;
}
async function prepareInvoice(revision) {
  if (dirty) throw new Error("Save and confirm your changes before making an invoice.");
  if (billingIssued) return showIssuedInvoice(billingIssued);
  if (revision.version !== job.draft_version) throw new Error("Use the newest confirmed version of this job.");
  const config = await request("/billing-settings");
  billingRevision = revision; billingPreview = null; billingDirty = false; $("invoice-ack").checked = false;
  billingSupplier = config.supplier; billingAllowed = Boolean(billingSupplier);
  $("invoice-from").textContent = billingSupplier ? `Invoice from ${billingSupplier.name}` + (billingSupplier.gst_registration_number ? ` · GST reg. no. ${billingSupplier.gst_registration_number}` : " · not GST-registered, so no GST is added") : "";
  $("invoice-customer-name").value = revision.record.customer_reference || ""; $("invoice-customer-address").value = "";
  $("invoice-date").value = singaporeDate(); $("invoice-basis").value = "inclusive"; $("invoice-discount").value = "0.00";
  $("invoice-preview").textContent = ""; $("invoice-form").hidden = false;
  $("billing-state").textContent = billingAllowed ? "Fill in the boxes, then work out the totals." : "Fill in “Workshop details” (top bar) first. The invoice needs the workshop's name and address.";
  updateIssueButton(); $("billing-heading").scrollIntoView();
}
function invoiceRequest() {
  return { supplier: billingSupplier,
    customer: { name: $("invoice-customer-name").value.trim(), address: $("invoice-customer-address").value.trim() },
    invoice_date: $("invoice-date").value, pricing_basis: $("invoice-basis").value, discount: $("invoice-discount").value.trim() };
}
function billingChanged(event) {
  if (event.target.id !== "invoice-ack") { billingDirty = true; billingPreview = null; $("invoice-preview").textContent = "Details changed. Work out the totals again."; $("invoice-ack").checked = false; }
  updateIssueButton();
}
$("invoice-form").addEventListener("input", billingChanged);
$("invoice-form").addEventListener("change", billingChanged);
$("preview-invoice").addEventListener("click", () => {
  if (!billingRevision || billingIssued) return;
  billingPreview = null; $("invoice-ack").checked = false; updateIssueButton();
  action(async () => {
    billingPreview = await request("/revisions/" + billingRevision.id + "/invoice-preview", JSON_POST(invoiceRequest()));
    $("invoice-preview").textContent = `Not issued yet\nAmounts typed in (${billingPreview.request.pricing_basis} of GST): ${billingPreview.subtotal}\nDiscount: ${billingPreview.request.discount}\nTotal before GST: ${billingPreview.net}\nGST (${billingPreview.gst_rate}): ${billingPreview.gst}\nGrand total: ${billingPreview.total}`;
  });
});
$("issue-invoice").addEventListener("click", () => {
  if (!billingPreview || !billingAllowed || billingIssued || dirty || !$("invoice-ack").checked) return;
  const preview = billingPreview;
  action(async () => { showIssuedInvoice(await request("/revisions/" + preview.revision_id + "/invoice", JSON_POST({ invoice: preview.request, acknowledged: true }))); status("Invoice issued. Print it on the workshop form."); });
});

// ---- payments --------------------------------------------------------------
async function paymentBox(invoiceId, container, changed) {
  const state = await request("/invoices/" + invoiceId + "/payments");
  container.replaceChildren(element("h3", "Payment"));
  container.append(element("p", `Grand total $${state.total} · paid $${state.paid} · ` + (Number(state.balance) > 0 ? `still owing $${state.balance}` : Number(state.balance) < 0 ? `overpaid $${state.balance.slice(1)}` : "fully paid")));
  for (const entry of state.payments) container.append(element("p", `${entry.paid_on} · $${entry.amount} · ${entry.method}${entry.note ? " · " + entry.note : ""} · entered by ${entry.recorded_by}`, "hint"));
  const amount = element("input"); amount.inputMode = "decimal"; amount.placeholder = "Amount"; amount.value = Number(state.balance) > 0 ? state.balance : ""; amount.setAttribute("aria-label", "Payment amount");
  const method = element("select"); method.setAttribute("aria-label", "How it was paid");
  for (const [value, label] of [["cash", "Cash"], ["nets", "NETS"], ["paynow", "PayNow"], ["bank", "Bank transfer"], ["other", "Other"]]) { const option = element("option", label); option.value = value; method.append(option); }
  const paidOn = element("input"); paidOn.type = "date"; paidOn.value = singaporeDate(); paidOn.setAttribute("aria-label", "Date paid");
  const note = element("input"); note.maxLength = 500; note.placeholder = "Note (optional)"; note.setAttribute("aria-label", "Note");
  const add = element("button", "Record payment"); add.type = "button";
  add.addEventListener("click", () => action(async () => {
    const value = parseAmount(amount.value.replace(/^-/, "")); if (!value) throw new Error("Type the amount paid, for example 327.00. For a refund put a minus in front.");
    await request("/invoices/" + invoiceId + "/payments", JSON_POST({ amount: (amount.value.trim().startsWith("-") ? "-" : "") + value, method: method.value, paid_on: paidOn.value, note: note.value.trim() }));
    await paymentBox(invoiceId, container, changed); status("Payment recorded."); if (changed) await changed();
  }));
  const form = element("div", "", "pay"); form.append(amount, method, paidOn, note, add); container.append(form);
}

// ---- books -----------------------------------------------------------------
const bookColumns = [["date", "Date"], ["number", "Invoice no."], ["job_reference", "Job no."], ["vehicle", "Vehicle"], ["customer", "Customer"],
  ["knock", "Knock"], ["repair", "Repair"], ["spray", "Spray"], ["net", "Before GST"], ["gst", "GST"], ["total", "Grand total"], ["paid", "Paid"], ["balance", "Balance"]];
async function loadBooks() {
  const month = $("books-month").value || singaporeDate().slice(0, 7); $("books-month").value = month;
  $("books-download").href = api + "/books?format=csv&month=" + month; $("books-payment").hidden = true;
  const table = $("books-table"); table.replaceChildren();
  let sheet;
  try { sheet = await request("/books?month=" + month); } catch (error) { $("books-state").textContent = "The books could not load: " + error.message; return; }
  $("books-state").textContent = sheet.rows.length ? `${sheet.rows.length} invoice${sheet.rows.length > 1 ? "s" : ""} in ${month}.` : `No invoices in ${month}.`;
  const head = table.insertRow(); for (const [, label] of bookColumns) head.append(element("th", label)); head.append(element("th", ""));
  for (const row of sheet.rows) {
    const line = table.insertRow();
    for (const [name] of bookColumns) { const cell = line.insertCell(); cell.textContent = name === "number" ? row.number.slice(0, 13) + (row.number.length > 13 ? "…" : "") : row[name]; if (name === "number") cell.title = row.number; }
    const pay = element("button", Number(row.balance) > 0 ? "Pay" : "View"); pay.title = "Payments for this invoice"; pay.type = "button";
    pay.addEventListener("click", () => { $("books-payment").hidden = false; paymentBox(row.invoice_id, $("books-payment"), loadBooks).then(() => $("books-payment").scrollIntoView()).catch(error => status(error.message, true)); });
    line.insertCell().append(pay);
  }
  const foot = table.insertRow(); foot.className = "group";
  for (const [name] of bookColumns) foot.insertCell().textContent = name === "date" ? "TOTAL" : sheet.totals[name] ?? "";
  foot.insertCell();
  await loadExpenses(month);
}

// ---- money paid out, and profit and loss ------------------------------------
for (const [value, label] of expenseTypes) { const option = element("option", label); option.value = value; $("expense-category").append(option); }
const expenseColumns = [["date", "Date"], ["supplier", "Paid to"], ["category", "Type"], ["description", "What for"], ["supplier_invoice", "Supplier invoice"], ["job_reference", "Job no."],
  ["amount", "Paid"], ["gst", "GST in it"], ["net", "Before GST"]];
async function loadExpenses(month) {
  $("expenses-download").href = api + "/expenses?format=csv&month=" + month;
  if (!$("expense-date").value.startsWith(month)) $("expense-date").value = month === singaporeDate().slice(0, 7) ? singaporeDate() : month + "-01";
  const table = $("expenses-table"), profitTable = $("profit-table"); table.replaceChildren(); profitTable.replaceChildren(); $("job-profit-table").replaceChildren();
  let sheet, profit;
  try { [sheet, profit] = await Promise.all([request("/expenses?month=" + month), request("/profit?month=" + month)]); }
  catch (error) { table.insertRow().insertCell().textContent = "Expenses could not load: " + error.message; return; }
  const head = table.insertRow(); for (const [, label] of expenseColumns) head.append(element("th", label));
  for (const row of sheet.rows) {
    const line = table.insertRow();
    for (const [name] of expenseColumns) line.insertCell().textContent = name === "category" ? Object.fromEntries(expenseTypes)[row.category] : row[name];
  }
  const foot = table.insertRow(); foot.className = "group";
  for (const [name] of expenseColumns) foot.insertCell().textContent = name === "date" ? "TOTAL" : sheet.totals[name] ?? "";
  const line = (label, value, className) => { const row = profitTable.insertRow(); if (className) row.className = className; row.insertCell().textContent = label; row.insertCell().textContent = value; };
  line("Sales (invoices, before GST)", profit.sales);
  for (const cost of profit.costs) line("Less " + cost.label.toLowerCase(), cost.amount);
  line("Total costs (before GST)", profit.total_costs);
  line(Number(profit.profit) < 0 ? "LOSS for the month" : "PROFIT for the month", profit.profit, Number(profit.profit) < 0 ? "group loss" : "group");
  line("GST collected on invoices", profit.gst_collected); line("GST paid on expenses", profit.gst_paid); line("GST difference (collected less paid)", profit.gst_owed);
  line("Money received from customers this month", profit.money_in); line("Money paid out this month", profit.money_out);
  line("Still owed by customers on this month's invoices", profit.unpaid_invoices);
  const jobs = $("job-profit-table"); jobs.replaceChildren();
  const jobHead = jobs.insertRow(); for (const label of ["Job no.", "Invoice no.", "Vehicle", "Customer", "Charged (before GST)", "Spent on the job", "Profit on the job"]) jobHead.append(element("th", label));
  for (const entry of profit.jobs) {
    const row = jobs.insertRow(); if (Number(entry.profit) < 0) row.className = "loss";
    for (const name of ["job_reference", "number", "vehicle", "customer", "charged", "cost", "profit"]) row.insertCell().textContent = entry[name];
  }
}
$("add-expense").addEventListener("click", () => action(async () => {
  const typed = $("expense-amount").value.trim(), amount = parseAmount(typed.replace(/^-/, "")), gst = $("expense-gst").value.trim() ? parseAmount($("expense-gst").value) : "0";
  if (!$("expense-supplier").value.trim()) throw new Error("Type who was paid.");
  if (!amount || gst === null) throw new Error("Type the amount paid, for example 250.00, and the GST in it if the bill shows GST.");
  await request("/expenses", JSON_POST({ spent_on: $("expense-date").value, supplier: $("expense-supplier").value.trim(), category: $("expense-category").value,
    description: $("expense-description").value.trim(), supplier_invoice: $("expense-bill").value.trim(), job_reference: $("expense-job").value.trim(),
    amount: (typed.startsWith("-") ? "-" : "") + amount, gst }));
  for (const name of ["supplier", "description", "bill", "job", "amount", "gst"]) $("expense-" + name).value = "";
  const month = $("expense-date").value.slice(0, 7); $("books-month").value = month; await loadBooks(); status("Expense recorded.");
}));
$("books-show").addEventListener("click", loadBooks);
$("books-month").addEventListener("change", loadBooks);

// ---- pop-up paper guide ----------------------------------------------------
let guideNames = null, guideIndex = 0;
function showGuide() {
  const name = guideNames[guideIndex]; $("guide-empty").hidden = Boolean(name); $("guide-picture").hidden = !name;
  $("guide-previous").disabled = guideIndex === 0; $("guide-next").disabled = guideIndex >= guideNames.length - 1;
  if (!name) return;
  $("guide-picture").src = api + "/guide/" + encodeURIComponent(name);
  $("guide-title").textContent = `${name.replace(/^\d+[ _-]*/, "").replace(/\.[a-z]+$/i, "")} (${guideIndex + 1} of ${guideNames.length})`;
}
$("open-guide").addEventListener("click", async () => {
  try { guideNames = guideNames || await request("/guide"); } catch (error) { guideNames = []; }
  showGuide(); $("guide").showModal();
});
$("guide-previous").addEventListener("click", () => { guideIndex--; showGuide(); });
$("guide-next").addEventListener("click", () => { guideIndex++; showGuide(); });
$("guide-close").addEventListener("click", () => $("guide").close());

window.addEventListener("resize", viewImage);
window.addEventListener("beforeunload", event => { if (dirty || billingDirty) { event.preventDefault(); event.returnValue = ""; } });
// ---- first-time setup ------------------------------------------------------
function showSetup(state) {
  const company = state.company;
  for (const [id, name] of [["company-name", "name"], ["company-phone", "phone"], ["company-gst", "gst_registration_number"], ["company-address", "address"]]) $(id).value = company?.[name] ?? "";
  $("company-state").textContent = company ? "Saved." : "Not saved yet.";
  $("add-examples").disabled = !company || state.jobs > 0;
  $("example-state").textContent = state.jobs > 0 ? `The app already has ${state.jobs} job${state.jobs > 1 ? "s" : ""}, so examples cannot be added.` : company ? "" : "Save the workshop details first.";
  $("setup-hint").hidden = Boolean(company) && state.jobs > 0;
  $("form-state").textContent = state.form === "uploaded" ? "A picture is saved." : state.form === "file" ? "Using the picture stored on this computer; upload one here to keep it with the books." : "No picture yet: print-outs will be plain until one is added.";
}
function showUsers(account) {
  $("signed-in").textContent = `Signed in as ${account.me}` + (account.role === "owner" ? " (owner)" : "");
  const owner = account.role === "owner", table = $("users-table"); table.replaceChildren();
  for (const id of ["save-company", "upload-form", "add-user", "add-examples"]) if (!owner) $(id).disabled = true;
  if (!owner) { $("company-state").textContent = "Only an owner login can change this page."; $("users-step").hidden = true; return; }
  const head = table.insertRow(); for (const label of ["Login", "Kind", "", ""]) head.append(element("th", label));
  for (const user of account.users) {
    const row = table.insertRow(); row.insertCell().textContent = user.username; row.insertCell().textContent = user.role === "owner" ? "Owner" : "Staff";
    row.insertCell().textContent = user.built_in ? "main login" : user.active ? "on" : "switched off";
    const cell = row.insertCell(); if (user.built_in) continue;
    const toggle = element("button", user.active ? "Switch off" : "Switch on"); toggle.type = "button";
    toggle.addEventListener("click", () => action(async () => {
      const list = await request("/users/" + encodeURIComponent(user.username) + "/active", JSON_POST({ active: !user.active }));
      status(`${user.username} ${user.active ? "can no longer sign in" : "can sign in again"}.`); setTimeout(() => showUsers({ ...account, users: list }));
    }));
    cell.append(toggle);
  }
}
async function loadSetup() {
  const [state, account] = await Promise.all([request("/setup"), request("/users")]);
  showSetup(state); showUsers(account); return state;
}
$("upload-form").addEventListener("click", () => {
  const file = $("form-file").files[0]; if (!file) return status("Choose the picture of the blank job sheet first.", true);
  const data = new FormData(); data.append("file", file);
  action(async () => { const state = await request("/setup/form", { method: "PUT", body: data }); $("form-file").value = ""; $("car-outline").hidden = false; $("car").classList.remove("blank"); $("car-outline").src = api + "/sheet-diagram?" + Date.now();
    status("Blank job sheet saved. Print-outs will use it."); setTimeout(() => showSetup(state)); });
});
$("add-user").addEventListener("click", () => action(async () => {
  const name = $("user-name").value.trim(), password = $("user-password").value;
  if (!name || password.length < 10) throw new Error("Type a login name and a password of 10 or more characters.");
  const list = await request("/users", JSON_POST({ username: name, password, role: $("user-role").value }));
  $("user-name").value = ""; $("user-password").value = ""; status(`${name} can now sign in. Give them the password in person.`);
  setTimeout(async () => showUsers(await request("/users")));
}));
$("save-company").addEventListener("click", () => action(async () => {
  if (!$("company-name").value.trim() || !$("company-address").value.trim()) throw new Error("Type the workshop name and address first.");
  const state = await request("/setup", { ...JSON_POST({ name: $("company-name").value.trim(), address: $("company-address").value.trim(),
    phone: $("company-phone").value.trim(), gst_registration_number: $("company-gst").value.trim() || null }), method: "PUT" });
  status("Workshop details saved. They will be printed on every invoice from now on."); setTimeout(() => showSetup(state));
}));
$("add-examples").addEventListener("click", () => {
  if (!window.confirm("Add three months of made-up jobs, invoices, payments and expenses? They cannot be removed afterwards.")) return;
  action(async () => { const state = await request("/setup/example-jobs", { method: "POST" }); status(`${state.jobs} example jobs added. Open “Books” or “Find job” to see them.`); setTimeout(() => showSetup(state)); });
});
$("setup-start").addEventListener("click", () => { showStep("car"); $("job_reference").focus(); });
document.querySelector('.tools [data-step="setup"]').addEventListener("click", () => loadSetup().catch(error => status(error.message, true)));

render(); renderHistory(); showStep("car");
const initialJob = new URLSearchParams(location.search).get("job");
if (initialJob) openJob(initialJob);
loadSetup().then(state => { if (initialJob) return; if (!state.company) { showStep("setup"); status("Welcome. Fill in the workshop details to begin."); } }).catch(() => {});
