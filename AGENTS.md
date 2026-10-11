# Workshop project contributor instructions

Read `car mechanic assistant/WORKSHOP_MASTER_PLAN.md` before workshop implementation. It is the master specification, feature ledger and handoff state. The next ready task and actual status belong there, not only in chat.

For every implemented feature **or partial implementation**, update the master with delivered behaviour, files/routes/schema/config, actual verification results, limitations, unanswered company prerequisites and the next task. Update relevant run instructions and `car mechanic assistant/BUILD_STATUS.md` when behaviour changes. Commit implementation, meaningful tests and master updates together; the user has authorised committing and pushing intended changes to the existing repository.

Preserve unrelated user changes. Inspect Git status and stage explicit paths; do not use `git add .`. Keep `company visit/`, completed company-answer documents, real samples/labels and generated private artifacts out of Git. Use clearly labelled fictional fixtures for public tests. Confirm the permitted processing path before sending real company records to an external provider.

Continue independent ready work while company answers remain pending. Do not invent meanings, mappings, approvals, accuracy or adoption. Begin with the manual source/draft/review/output workflow; AI is an optional drafting step. Existing API/RAG functionality and historical evidence are separate from this project.

No public deployment, live financial-system writes or irreversible data changes are authorised merely by this plan. Use isolated development/test storage and databases. Record unfinished/failed checks candidly so the next contributor can resume.
