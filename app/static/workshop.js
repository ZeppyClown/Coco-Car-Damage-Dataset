"use strict";
const api = document.querySelector('meta[name="workshop-api"]').content;
const $ = id => document.getElementById(id);
const states = ["missing", "unclear", "proposed", "confirmed"];
const scalarFields = [
  ["job_reference", "Job reference"], ["customer_reference", "Customer reference"],
  ["vehicle_reference", "Vehicle reference"], ["make", "Make"], ["model", "Model"],
  ["quotation_date", "Quotation date", "date"], ["date_in", "Date in", "date"], ["date_out", "Date out", "date"],
  ["currency", "Currency (three uppercase letters)"], ["diagram_notes", "Clarified diagram meaning", "textarea"],
  ["written_total", "Written total", "money"], ["written_adjustment", "Written adjustment", "money"],
  ["written_grand_total", "Written grand total", "money"],
];
const rawFields = [["date_note_raw", "Literal date note"], ["diagram_notes_raw", "Literal diagram / panel notes"], ["written_totals_raw", "Literal total / adjustment notes"]];
let job = null, sourceId = null, aiProvenance = null, dirty = false, zoom = 1, rotation = 0, reviewed = [];
let lookupParams = new URLSearchParams(), lookupOffset = 0;

function element(tag, text) { const node = document.createElement(tag); if (text) node.textContent = text; return node; }
function control(parent, id, labelText, type = "text", limit = 200) {
  const label = element("label", labelText);
  const input = element(type === "textarea" ? "textarea" : "input");
  input.id = id; input.maxLength = limit;
  if (type !== "textarea") input.type = type === "money" ? "text" : type;
  if (type === "money") input.inputMode = "decimal";
  label.append(input); parent.append(label); return input;
}
function stateControl(parent, id, labelText) {
  const label = element("label", labelText); label.className = "field-state";
  const select = element("select"); select.id = id;
  select.setAttribute("aria-label", labelText);
  for (const state of states) { const option = element("option", state); option.value = state; select.append(option); }
  label.append(select); parent.append(label); return select;
}
function markDirty() {
  dirty = true; $("dirty-label").textContent = "Unsaved changes";
  $("confirm-record").disabled = true; $("review-ack").checked = false;
}
function watchValue(input, state) {
  input.addEventListener("input", () => { state.value = input.value.trim() ? "proposed" : "missing"; markDirty(); });
}
for (const [name, label, type] of scalarFields) {
  const group = element("div");
  const primary = ["job_reference", "customer_reference", "vehicle_reference", "currency"].includes(name);
  $(primary ? "scalar-fields" : "optional-fields").append(group);
  const input = control(group, name, label, type, type === "textarea" ? 2000 : 200);
  const state = stateControl(group, name + "-state", label + " review state"); watchValue(input, state);
}
for (const [name, label] of rawFields) control($("raw-fields"), name, label, "textarea", 10000);

function addItem(item = {}) {
  const rows = $("items"); if (rows.children.length >= 50) return;
  const index = crypto.randomUUID(); const card = element("section"); card.className = "item";
  card.append(element("h4", "Item"));
  control(card, index + "-raw", "Literal item description", "textarea", 10000).value = item.description_raw || "";
  const description = control(card, index + "-description", "Clarified description", "textarea", 2000); description.value = item.description || "";
  const descriptionState = stateControl(card, index + "-description-state", "Description review state"); descriptionState.value = item.description_state || "missing";
  control(card, index + "-amount-raw", "Literal amount text").value = item.amount_raw || "";
  const amount = control(card, index + "-amount", "Parsed amount (empty means unknown)", "money"); amount.value = item.amount ?? "";
  const amountState = stateControl(card, index + "-amount-state", "Amount review state"); amountState.value = item.amount_state || "missing";
  const cancelled = control(card, index + "-cancelled", "Cancelled / crossed out", "checkbox"); cancelled.checked = item.cancelled || false;
  card.classList.toggle("cancelled", cancelled.checked);
  cancelled.addEventListener("change", () => card.classList.toggle("cancelled", cancelled.checked));
  watchValue(description, descriptionState); watchValue(amount, amountState);
  const remove = element("button", "Remove item"); remove.type = "button";
  remove.addEventListener("click", () => { if (window.confirm("Remove this item from the draft?")) { card.remove(); markDirty(); $("add-item").disabled = false; } });
  card.append(remove); card.dataset.key = index; rows.append(card); $("add-item").disabled = rows.children.length >= 50;
}
function readDraft() {
  const draft = { data_origin: $("data-origin").value, source_document_id: sourceId, record_stage: $("record-stage").value,
    manual_provenance: $("manual-provenance").value.trim() || null, ai_provenance: aiProvenance, field_states: {}, items: [] };
  for (const [name] of scalarFields) { draft[name] = $(name).value.trim() || null; draft.field_states[name] = $(name + "-state").value; }
  for (const [name] of rawFields) draft[name] = $(name).value;
  for (const card of $("items").children) {
    const key = card.dataset.key;
    draft.items.push({ description_raw: $(key + "-raw").value, description: $(key + "-description").value.trim() || null,
      description_state: $(key + "-description-state").value, amount_raw: $(key + "-amount-raw").value,
      amount: $(key + "-amount").value.trim() || null, amount_state: $(key + "-amount-state").value, cancelled: $(key + "-cancelled").checked });
  }
  return draft;
}
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
  image.hidden = !sourceId; $("source-identity").textContent = sourceId ? "Source ID: " + sourceId : "No source attached. Manual entry is available.";
  if (sourceId) image.src = api + "/documents/" + encodeURIComponent(sourceId) + "/preview";
  else { image.removeAttribute("src"); $("image-stage").style.height = "0px"; }
}
function render(record = { data_origin: "synthetic_demo", items: [] }) {
  aiProvenance = record.ai_provenance || null; $("ai-send-ack").checked = false;
  $("ai-provenance").textContent = aiProvenance ? `Initial AI proposal: ${aiProvenance.model} · ${aiProvenance.prompt_version} · source ${aiProvenance.source_document_id}. Review every value; this is not an accuracy result.` : "";
  sourceId = record.source_document_id || null; $("data-origin").value = record.data_origin; $("data-origin").disabled = Boolean(job);
  $("record-stage").value = record.record_stage || "unknown"; $("manual-provenance").value = record.manual_provenance || "";
  for (const [name] of scalarFields) { $(name).value = record[name] ?? ""; $(name + "-state").value = record.field_states?.[name] || (record[name] == null ? "missing" : "proposed"); }
  for (const [name] of rawFields) $(name).value = record[name] || "";
  $("items").replaceChildren(); for (const item of record.items || []) addItem(item);
  $("add-item").disabled = $("items").children.length >= 50; dirty = false; $("dirty-label").textContent = "No unsaved changes";
  $("source-file").value = "";
  $("record-identity").textContent = job ? `Job ID: ${job.id} · editable draft version ${job.draft_version}` : "New, unsaved draft";
  $("open-id").value = job?.id || ""; showSource();
  $("review-ack").checked = false; $("confirm-record").disabled = !job;
}
function renderHistory() {
  const container = $("reviewed-history"); container.replaceChildren();
  const current = reviewed.find(revision => revision.version === job?.draft_version);
  $("review-state").textContent = !job ? "No record opened." : current ? "This saved draft version has been reviewed. Edit and save to create a correction; earlier snapshots remain unchanged." : "This draft version has not been reviewed.";
  for (const revision of reviewed) {
    const details = element("details"); const record = revision.record;
    const stages = { quote: "Quote", approved_scope: "Approved scope", completed_work: "Completed work" };
    details.append(element("summary", `Reviewed version ${revision.version} · ${stages[record.record_stage]} · ${record.job_reference}`));
    details.append(element("p", `Reviewer: ${revision.reviewer} (self-reported) · ${new Date(revision.reviewed_at).toLocaleString()}`));
    if (record.ai_provenance) details.append(element("p", `Initial AI proposal: ${record.ai_provenance.model} · ${record.ai_provenance.prompt_version} · source ${record.ai_provenance.source_document_id}`));
    if (record.diagram_notes && !record.manual_provenance) details.append(element("p", "This older version has no stated diagram clarification context. Add it to a new draft and review again."));
    for (const [name, label] of scalarFields) if (record[name] != null) details.append(element("p", label + ": " + record[name]));
    for (const [name, label] of rawFields) if (record[name]) details.append(element("pre", label + ": " + record[name]));
    for (const item of record.items) {
      details.append(element("pre", (item.cancelled ? "Cancelled row" : "Reviewed item") + ": " + (item.description || "Unknown description") +
        "\nLiteral text: " + item.description_raw + "\nAmount: " + (item.amount ?? "Unknown") + (record.currency ? " " + record.currency : "") + "\nLiteral amount: " + item.amount_raw));
    }
    if (record.source_document_id) {
      const source = element("a", "Open this version's original source");
      source.href = api + "/documents/" + encodeURIComponent(record.source_document_id) + "/preview"; source.target = "_blank"; source.rel = "noopener"; details.append(source);
    } else details.append(element("p", "Manual provenance: " + record.manual_provenance));
    const download = element("button", `Download demo CSV · version ${revision.version}`); download.type = "button";
    download.addEventListener("click", () => action(async () => {
      const exported = await request("/revisions/" + revision.id + "/exports", { method: "POST" });
      const response = await fetch(api + "/exports/" + exported.id + "/download");
      if (!response.ok) throw new Error("Demo CSV download failed. The reviewed version remains saved.");
      const url = URL.createObjectURL(await response.blob());
      const link = element("a"); link.href = url; link.download = `workshop-demo-${job.id}-v${revision.version}.csv`;
      document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 60000);
      status(`Demo CSV generated for reviewed version ${revision.version}. It has not been imported into accounting software.`);
    }));
    details.append(element("p", "Demo output only. Unknown amounts stay empty; cancelled rows contain literal text without interpreted values."));
    details.append(download);
    container.append(details);
  }
}
async function refreshHistory(append = false) {
  if (!job) { reviewed = []; $("more-history").hidden = true; renderHistory(); return; }
  if (!append) { reviewed = []; $("reviewed-history").replaceChildren(); $("review-state").textContent = "Loading reviewed history…"; }
  let rows;
  try { rows = await request("/jobs/" + job.id + "/revisions?limit=20&offset=" + (append ? reviewed.length : 0)); }
  catch (error) { $("review-state").textContent = "Reviewed history could not load. Reopen the record to retry."; throw error; }
  reviewed = append ? reviewed.concat(rows) : rows; $("more-history").hidden = rows.length < 20; renderHistory();
}
async function historyStatus(message) {
  try { await refreshHistory(); status(message); }
  catch (error) { status(message + " Reviewed history could not load: " + error.message, true); }
}
function status(message, error = false) { $("status").textContent = message; $("status").classList.toggle("error", error); }
async function request(path, options = {}) {
  const response = await fetch(api + path, options);
  const data = await response.json();
  if (!response.ok) {
    const detail = Array.isArray(data.detail) ? data.detail.slice(0, 20).map(error => error.loc.join(".") + ": " + error.msg).join("\n") : data.detail || data.error;
    throw new Error(detail || "Request failed. Your draft remains on screen.");
  }
  return data;
}
async function action(task) {
  const controls = [...document.querySelectorAll("button,input,select,textarea")].map(node => [node, node.disabled]);
  controls.forEach(([node]) => node.disabled = true);
  try { await task(); } catch (error) { status(error.message || "Request failed. Your draft remains on screen.", true); }
  finally { controls.forEach(([node, disabled]) => node.disabled = disabled); $("data-origin").disabled = Boolean(job); $("add-item").disabled = $("items").children.length >= 50; $("confirm-record").disabled = !job || dirty; }
}
function draftChanged(event) { if (!event.target.closest(".review-controls")) markDirty(); }
$("draft-form").addEventListener("input", draftChanged);
$("draft-form").addEventListener("change", draftChanged);
$("data-origin").addEventListener("change", markDirty);
$("add-item").addEventListener("click", () => { addItem(); markDirty(); });
$("new-record").addEventListener("click", () => { if (!dirty || window.confirm("Discard unsaved changes and start a new record?")) { job = null; render(); refreshHistory(); history.replaceState(null, "", "/workshop"); status("New draft. No saved record was deleted."); } });
$("open-record").addEventListener("click", () => {
  if (dirty && !window.confirm("Discard unsaved changes and open another record?")) return;
  const id = $("open-id").value.trim(); if (!id) return status("Enter a saved job ID.", true);
  action(async () => { const loaded = await request("/jobs/" + encodeURIComponent(id)); job = loaded; render(job.draft); await historyStatus("Loaded editable draft version " + job.draft_version + "."); });
});
$("draft-form").addEventListener("submit", event => {
  event.preventDefault(); const draft = readDraft();
  action(async () => {
    const payload = job ? { expected_version: job.draft_version, draft } : draft;
    const saved = await request(job ? "/jobs/" + job.id : "/jobs", { method: job ? "PATCH" : "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload) });
    job = saved; render(job.draft); history.replaceState(null, "", "/workshop?job=" + encodeURIComponent(job.id));
    await historyStatus("Draft saved. Copy the job ID to reopen it. It has not been reviewed.");
  });
});
$("attach-source").addEventListener("click", () => {
  const file = $("source-file").files[0]; if (!file) return status("Choose a JPEG/PNG source first.", true);
  const data = new FormData(); data.append("file", file); data.append("data_origin", $("data-origin").value);
  action(async () => { const source = await request("/documents", { method: "POST", body: data }); sourceId = source.id; showSource(); markDirty(); status(source.duplicate ? "These bytes already exist; reused the source. Jobs were not merged. Save the draft to retain this attachment." : "Source attached. Save the draft to retain this attachment."); });
});
$("detach-source").addEventListener("click", () => { sourceId = null; showSource(); markDirty(); status("Detached from this draft; the stored source was not deleted."); });
$("extract-source").addEventListener("click", () => {
  const draft = readDraft();
  if (!sourceId) return status("Attach a fictional image first.", true);
  if (job || draft.items.length || draft.manual_provenance || draft.record_stage !== "unknown" ||
      scalarFields.some(([name]) => draft[name] != null) || rawFields.some(([name]) => draft[name])) {
    return status("AI suggestions require a new empty draft. Your entered or saved values were kept.", true);
  }
  if (Object.values(draft.field_states).some(state => state !== "missing")) return status("Your review states were kept. Start a new empty draft for AI suggestions.", true);
  if (!$("ai-send-ack").checked) return status("Acknowledge sending this fictional image to Gemini first.", true);
  action(async () => {
    const proposed = await request("/documents/" + sourceId + "/extract", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ send_to_gemini: true }) });
    render(proposed); markDirty(); status("AI proposal loaded without saving. Check literal text, resolve unclear values, choose the stage and review all interpretations.");
  });
});
$("confirm-record").addEventListener("click", () => {
  if (!job || dirty) return status("Save the draft before confirming.", true);
  const reviewer = $("reviewer").value.trim();
  if (!reviewer || !$("review-ack").checked) return status("Enter your reviewer name and acknowledge checking the values.", true);
  action(async () => {
    const revision = await request("/jobs/" + job.id + "/confirm", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ expected_version: job.draft_version, reviewer, acknowledged: true }) });
    $("review-ack").checked = false;
    await historyStatus(`Saved reviewed version ${revision.version}. This preserves its selected stage; it does not create an invoice or completed repair.`);
  });
});
$("more-history").addEventListener("click", () => action(() => refreshHistory(true)));
async function runLookup(offset, filters = lookupParams) {
  const params = new URLSearchParams(filters); params.set("limit", "20"); params.set("offset", offset);
  let data;
  try { data = await request("/jobs?" + params); }
  catch (error) { $("lookup-state").textContent = "Search failed. Any results below belong to the previous successful search."; throw error; }
  lookupParams = new URLSearchParams(filters); lookupOffset = offset;
  const container = $("lookup-results"); container.replaceChildren();
  $("lookup-state").textContent = data.results.length ? `Showing ${offset + 1}–${offset + data.results.length} reviewed jobs.` : "No reviewed records match.";
  $("lookup-previous").hidden = offset === 0; $("lookup-next").hidden = !data.has_more;
  for (const result of data.results) {
    const card = element("section"); card.className = "lookup-result";
    card.append(element("h3", result.record.job_reference));
    card.append(element("p", `Customer: ${result.record.customer_reference || "Unknown"} · Vehicle: ${result.record.vehicle_reference || "Unknown"}`));
    card.append(element("p", `Reviewed version ${result.version} · ${result.record.record_stage} · ${new Date(result.reviewed_at).toLocaleString()}`));
    card.append(element("p", result.has_unreviewed_changes ? `Editable draft version ${result.draft_version} has newer unreviewed changes.` : "Editable draft matches this reviewed version."));
    const open = element("button", "Open job and history"); open.type = "button";
    open.addEventListener("click", () => { $("open-id").value = result.job_id; $("open-record").click(); }); card.append(open);
    if (result.record.source_document_id) {
      const source = element("a", "Open reviewed source"); source.href = api + "/documents/" + result.record.source_document_id + "/preview";
      source.target = "_blank"; source.rel = "noopener"; card.append(source);
    }
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
$("source-image").addEventListener("error", () => status("Source preview could not load. The draft remains editable; check its source before review.", true));
window.addEventListener("resize", viewImage);
window.addEventListener("beforeunload", event => { if (dirty) { event.preventDefault(); event.returnValue = ""; } });
render();
renderHistory();
const initialJob = new URLSearchParams(location.search).get("job");
if (initialJob) { $("open-id").value = initialJob; $("open-record").click(); }
