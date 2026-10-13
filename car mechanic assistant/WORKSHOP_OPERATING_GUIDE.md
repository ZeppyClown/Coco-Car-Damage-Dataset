# Workshop local operating and recovery guide

Last updated: 12 October 2026. This describes the **local fictional demonstration**, protected by one configured operator account. Company pilot approval, actual access policy, hosting and retention remain pending; external destination mapping is optional under standalone scope. The [master plan](WORKSHOP_MASTER_PLAN.md) records each feature and its exact evidence.

Current user scope: standalone workshop records; old financial/GST software is assumed gone. External mapping is optional, not a setup prerequisite. F13 invoicing/GST is implemented; use the [billing guide](WORKSHOP_INVOICING_GUIDE.md). Real issuance is disabled pending supplier settings; general accounting is separate. [Inspect the saved record/export and fresh verification](WORKSHOP_VERIFICATION_REPORT.md): initial217 clean workshop tests and final326 full tests passed, with actual invoice/PostgreSQL recovery and live HTTP/Chrome billing checks.

## What is available

`/workshop` supports JPEG/PNG source attachment, manual drafts, optional proposed AI fields, explicit review, immutable history, corrections, per-version demo CSV, latest-reviewed lookup and separate SGD invoice/GST preview/issue/print output. Jobs are separate UUID records even when customer/vehicle text matches. Nothing writes to the company's financial software. PDF/archive scanning, automatic diagram meanings and accounting mapping are not implemented.

The existing automotive API and separate manual RAG assistant are independent applications. Their historical evidence/results must not be relabelled as this new workshop workflow. Company visit records and runtime artifacts stay private and ignored by Git.

## Prepare an isolated local environment

Use Python 3.12 and an already provisioned local development PostgreSQL database. The checked environment used PostgreSQL 14.20; PostgreSQL client tools are needed for recovery tests. Docker execution was not checked on this machine. Do not connect to a live company/default automotive database for these steps.

On a fresh checkout, create an API-only environment once:

```sh
python3.12 -m venv 'car mechanic assistant/runtime/workshop-api-venv'
'car mechanic assistant/runtime/workshop-api-venv/bin/python' -m pip install -r requirements.txt
'car mechanic assistant/runtime/workshop-api-venv/bin/python' -m pip check
```

The runtime directory is ignored. An existing usable environment can be reused. This API-only requirements set includes the workshop, not the separate Chroma/RAG application's dependencies. The workspace's shared `.venv` has unrelated audio/telemetry conflicts; the isolated API environment was installed and checked successfully.

Set the **actual separately provisioned local** connection. Replace these role/port/database placeholders; keep real credentials in a permitted local environment file, never in public docs/chat/Git:

```sh
export DATABASE_URL='postgresql://YOUR_LOCAL_ROLE@127.0.0.1:5432/yap_test_workshop'
export WORKSHOP_ENABLED=true
export WORKSHOP_AUTH_USERNAME='fictional-local-operator'
export WORKSHOP_ORIGIN='http://127.0.0.1:8000'
export WORKSHOP_AI_ENABLED=false
export USE_GOOGLE_CSE=false
export USE_EBAY_API=false
export DEBUG=false
'car mechanic assistant/runtime/workshop-api-venv/bin/python' -m alembic upgrade head
'car mechanic assistant/runtime/workshop-api-venv/bin/python' -m alembic check
```

Check the target before migration. Startup does not create tables automatically. Current workshop head is `20261012_invoices`, following draft/review-guard/export/authentication revisions. The invoice migration adds immutable billing rows without rewriting existing records/exports. The additive authentication migration labels existing snapshots `self_reported` without changing their contents, reviewer, timestamp or CSV bytes. New API confirmations use `authenticated`. Future changes need a new migration. Stop this task's server with Ctrl-C in its terminal.

Generate a password hash interactively; the password is hidden, entered twice and never passed on the command line:

```sh
'car mechanic assistant/runtime/workshop-api-venv/bin/python' -m scripts.workshop_password
```

Use 16–1024 printable ASCII password characters and a printable ASCII account name (no colon, surrounding whitespace or more than200 characters). This is an account identifier, not evidence of a person's legal name. Store the resulting hash in `WORKSHOP_AUTH_PASSWORD_HASH` in an ignored permitted private environment file with mode0600. Use single quotes around the hash when setting it in a shell: its `$` characters are literal. Do not commit the hash/password or paste it into chat. The hash uses a random16-byte salt and standard-library scrypt; no plaintext password is configured in the application. Then start Uvicorn with your private environment file:

```sh
'car mechanic assistant/runtime/workshop-api-venv/bin/python' -m uvicorn app.main:app --env-file 'PATH_TO_PRIVATE_ENV_FILE' --host 127.0.0.1 --port 8000
```

Open the **exact configured origin** plus `/workshop` and enter the account/password in the browser's native HTTP Basic prompt. `localhost` and `127.0.0.1` are different hosts. Wrong/missing credentials return401; enabled routes with missing/invalid configuration return503; disabled routes return404. Page, workshop API, preview, CSV download and invoice read/print/issuance are protected before body parsing. Protected responses use `Cache-Control: no-store`. Requests to a different host/origin or marked cross-site/same-site are rejected403, including authenticated writes; ordinary same-origin browser requests and authenticated CLI calls without Origin are supported. The existing seven automotive endpoints are outside this boundary. `/docs` exposes API schemas with HTTP Basic authorisation, not stored workshop records.

`WORKSHOP_ENABLED` defaults false and remains a separate feature gate. The single operator can access all workshop records; there are no per-customer permissions or roles. Close the dedicated browser context to clear its cached Basic credentials; there is no application logout/session manager. Rotate the hash and restart to revoke the old password. Keep HTTP restricted to loopback; non-loopback configured origins require HTTPS. Actual TLS/proxy configuration, brute-force/rate limiting, credential custody and company access policy have not been deployed/verified. Do not expose this prototype publicly. A future shared pilot needs those operating decisions and checks first.

## Complete one fictional job

1. Start a new record, use **Fictional demonstration** origin and attach `tests/fixtures/workshop/synthetic-sheet.png`. Only JPEG/PNG is accepted, with 8 MiB/6000-pixels-per-side/20MP limits. Upload preserves original bytes; zoom/rotation change only the view. Duplicate identical bytes reuse a source, not a job/customer.
2. Enter a unique fictional job reference, explicit stage and work items. Copy literal wording and amount notes separately from clarified values. A missing amount remains empty/null; enter 0.00 only if zero is known. Do not infer currency, year, repairs or totals from context.
3. Keep crossed-out rows and mark them cancelled. Raw diagram/shorthand notes can remain uninterpreted. An area alone does not define an active repair item. For clarified diagram meaning, state the source of clarification and applicable vehicle direction convention in manual provenance; the software checks text presence, not its truth.
4. Choose review states deliberately. Editing an interpreted value makes it proposed again. Optional truly missing fields can stay missing. Ambiguous interpretations remain unclear until someone establishes meaning. Unresolved interpretations block confirmation but do not prevent saving a draft.
5. Save. Copy the job UUID/bookmark URL. Check the displayed read-only signed-in account, explicitly acknowledge checking values and confirm. The server binds the reviewer to that account regardless of a client-supplied name and uses its current UTC clock; clients cannot backdate reviews. A reviewed quote remains a quote. History distinguishes authenticated attribution from older self-reported identities; it does not retroactively verify them.
6. Expand a reviewed version in history and download its demo CSV. `workshop-demo-v1` is not a company import mapping. It repeats snapshot fields per line, preserves unknown/zero distinction and marks cancelled literal rows without interpreted values. Formula-like cells get an apostrophe prefix; signed negatives are textual under this demo rule. Stored values remain unchanged.
7. Reopen/search the job. Lookup returns latest reviewed records, excludes draft-only jobs, shows unknown references and flags newer unreviewed changes. Search raw/unknown/cancelled text does not establish its meaning. Date filters use inclusive UTC review dates; results open the current editable draft plus immutable history.
8. To correct, edit/save a new draft version, resolve proposed fields and confirm again. Earlier snapshots/CSVs stay unchanged. Repeated unchanged confirmation/export returns the original identity/time. This works within the standalone system. Only a later selected external integration needs F09 mapping/correction agreement.

For a manual entry without an image, state manual provenance. Older reviewed snapshots lacking the newer diagram-context rule remain readable/exportable and are labelled in history; add context in a new review to supersede them.

## Optional AI drafting

Manual entry needs no provider credentials. AI is default-off. On11October2026, the existing separate assistant's local key was explicitly supplied to a temporary authenticated localhost process using `gemini-3.1-flash-lite` and SDK2.29.0. The full **printed fictional** image→unsaved proposed draft→source-checked manual quote review→CSV API smoke passed, and the record reopened in the browser. This proves integration for that fixture/model, not real handwriting, independent accuracy or company acceptance. The root/manual demo still has AI off and does not automatically load the assistant's credential file. Standard unit/browser scenarios still mock provider responses.

For another **fictional-source** check, configure a permitted Gemini key in the workshop's private environment using `GOOGLE_API_KEY`, set an explicit `WORKSHOP_AI_MODEL` (the tested selection was `gemini-3.1-flash-lite`) and `WORKSHOP_AI_ENABLED=true`, then restart that local process with the correct origin. No automatic cross-application credential loading or default model is added. Read current official [SDK](https://github.com/googleapis/python-genai) and [model](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite) documentation; aliases can change and the configured/requested model is recorded, not an immutable provider snapshot version.

To reproduce the acceptance check, use only `tests/fixtures/workshop/synthetic-sheet.png`: compare preview bytes, explicitly request suggestions from a new empty draft, check source/model/proposed states, and verify it has not saved a job. A proposed/unknown-stage version must not confirm. Compare the printed fields/item/25.10 with the image, explicitly choose quote and resolve states, save and confirm a new reviewed version. Download/repeat the CSV and verify its recorded checksum/identity, then reopen the record and initial AI provenance. Record actual errors/time/model and any corrections; do not substitute this author-known printed example for a held-out handwriting benchmark. The last live proposal took3.871 seconds on the local authenticated request, a single observation rather than a performance guarantee.

The tested model returned400 for the nested provider `maxItems:50` schema while the same item schema without that cap succeeded. The provider copy omits that cap; the application still validates at most50 rows and rejects51 without saving. Explicit serializer return types make money's provider schema string/null; local precision/range/non-float validation and existing output bytes remain unchanged. Token/response/time bounds continue to apply. Other provider errors stay generic and preserve the manual fallback.

Attach a fictional image to a new empty unsaved draft, explicitly acknowledge sending it to Google Gemini and request suggestions. Entered/saved fields are preserved by refusing replacement. The route does not save/confirm/export. All interpretations are proposed, unclear literal amounts remain unknown, stage remains unknown and diagram meaning must be supplied by a human. Correct/check ordinary fields and choose stage before the normal save/review flow. Initial source/model/prompt/time provenance survives edits/reopen; it is not signed evidence.

There is one 60-second attempt, no automatic retry and no configured tools. Invalid/schema/oversized/provider responses fail without a saved draft. A valid shape can still contain invented text; review is required. Private-source AI returns403 while Q07 processing permission is unresolved and has no bypass setting. Do not declare a company image fictional. Do not count the mocked browser pipeline as model quality.

## Handle failures without losing work

| Result | Operator action | What is preserved |
|---|---|---|
|401 missing/wrong account | Re-enter the configured account in the dedicated browser; preserve unsaved work, then retry deliberately | No request reaches the workshop parser/service; form values remain visible |
|403 origin rejected /503 account misconfigured | Use the exact configured origin or have the local operator fix configuration; do not disable the boundary | No workshop write occurs |
|422 invalid draft/review | Correct the indicated value/state/context; save/review deliberately | Current form values and earlier stored versions |
|409 stale version | Keep current unsaved values visible, reopen/compare the latest job in a separate view if needed, then apply intended corrections to the current version | Other person's save is not overwritten; no automatic merge |
|503 source/output missing or corrupt | Investigate storage/restore the corresponding verified file; retry explicitly | Database identity/history; broken bytes are not silently regenerated/reused |
|502/504 AI invalid/provider/timeout | Enter manually or retry explicitly after checking configuration/source | No draft/review/output was created by extraction |
| Save succeeds but history read fails | Treat save as successful; reopen to reload history | Saved draft version; history failure is labelled separately |
| Lookup fails | Retry; the page labels any retained results as from the prior successful search | Prior results/query/pagination and current editable draft |

The page warns before discarding unsaved edits for new/open/navigation or item removal. A detach/remove UI action does not delete stored source/history. Preview integrity checks can fail if someone changes files outside the application. Do not repair this by editing checksums or immutable rows. There is no authorised deletion/retention workflow yet.

## Run workshop checks

Only use an isolated local DB with a name beginning `yap_test`; tests create/drop their own random schemas. PostgreSQL and source-file checks must actually run before claiming them passed:

```sh
YAP_TEST_POSTGRES_URL="$DATABASE_URL" \
  'car mechanic assistant/runtime/workshop-api-venv/bin/python' -m pytest -q \
  tests/unit/test_workshop*.py tests/integration/test_workshop_postgres.py
```

Without the explicit URL, PG checks skip. The recovery case also skips if `pg_dump`/`pg_restore` is unavailable; a skip is not recovery evidence. The whole repository suite additionally needs `requirements-dev.txt`/the separate assistant dependencies.

For an installed Chrome and Node, the isolated browser harness creates fictional records on the local demo DB:

```sh
npm install --prefix 'car mechanic assistant/runtime/workshop-browser-tests' playwright@1.64.0
node tests/browser/workshop.cjs 'car mechanic assistant/runtime/workshop-browser-tests/node_modules/playwright' http://127.0.0.1:8000 'PATH_TO_PRIVATE_FICTIONAL_CREDENTIAL_JSON'
```

The private mode0600 JSON file contains `username` and `password` for the fictional local account only. Keep it under ignored runtime, never Git. It is a test-harness convenience, not approved company credential storage. The harness uses a fresh authenticated browser context, never the user's profile, and checks anonymous page/upload rejection. Screenshots/downloads stay ignored under runtime. API provider checks and browser AI proposal responses are mocked; no live AI request occurs. See the [evaluation guide](WORKSHOP_EVALUATION_GUIDE.md) for the no-network comparator and future actual trial protocol.

## Local recovery rehearsal and its limits

Repeat the implemented disposable test:

```sh
YAP_TEST_POSTGRES_URL="$DATABASE_URL" \
  'car mechanic assistant/runtime/workshop-api-venv/bin/python' -m pytest -q \
  tests/integration/test_workshop_postgres.py::test_disposable_dump_restore_recovers_history_sources_outputs_and_guards
```

The test creates a random schema, one fictional source, two reviewed versions, two private CSVs and one issued fictional invoice. With no writers to that schema, it takes a custom-format namespace dump and copies source/output files. It renames only its own disposable namespace, restores it using `pg_restore --exit-on-error --no-owner --no-acl`, restores files to a fresh directory and checks draft/history identity, source bytes, repeat export identities/checksums, canonical invoice JSON/HTML/retry identity, migration/model alignment, restored invoice/review mutation guards and reviewed-source FK. It explicitly proves a DB-only restore leaves preview unavailable. Temporary schemas are cleaned by the test; pytest may retain its fictional temporary files under its own retention policy. The test does not rename/drop the application's public schema or restore over company records. Connection credentials pass through subprocess environment, not command arguments/logs. Dumps/source copies remain temporary private fixtures.

For a future real backup, agree owner/host/storage/retention/access first. Freeze workshop writes or establish a coordinated database/files snapshot; a database dump and later uncoordinated file copy are not automatically a consistent pair. Back up the actual DB and referenced original source/CSV files, record schema/mapping versions and verify SHA-256. A source UUID/checksum is not a file backup. Keep permitted backups private with agreed access/encryption and verify restore into a fresh isolated target before relying on them. Do not blindly replay `--clean`, drop a DB, rewrite checksums or overwrite existing storage.

The current rehearsal verifies a namespace restore on the same local PostgreSQL server plus a new file directory. It does not prove offsite/encrypted backup, disaster recovery on another host, retention/deletion, ownership/role restoration, production scale or an unattended backup schedule. Source/export write crashes can leave unreferenced files; reconciliation still needs an implementation selected with operating/retention decisions. Never delete an orphan candidate solely because its filename looks unfamiliar.

## Before company use

Usefulness is assumed by the user as of 12 October; demand interviews, baseline timing and adoption measurements are optional. Remaining technical decisions/evidence from master Q01–Q11:

- Exact invoice supplier name/address/GST number and IRAS InvoiceNow implementation date (Q11); GST-registered/inclusive prices supplied by user.
- Reviewer meanings, diagram convention, stage and independently checked examples.
- External destination format/chain/correction rules only if an integration is later selected; not required for standalone capture/export.
- Operator/decision owner for the selected operating scope.
- Source/external-provider permission and independently labelled cases; baseline timing is not required.
- Named user identity, access/roles, permitted host, origin/session/CSRF controls, storage, retention/deletion, backup/restore and support owner.

No real company pilot has been deployed. The local account/origin boundary, guide and fictional recovery evidence are development parts of F12; company approval, real account policy, hosting and retention remain unresolved. Actual data/use/outcome claims require actual evidence; the résumé targets remain separate from these tests.

## Invoicing/GST extension

Use [WORKSHOP_INVOICING_GUIDE.md](WORKSHOP_INVOICING_GUIDE.md) for the completed-work→preview→issue→print workflow, Decimal rules and private billing profile. Inclusive is the UI default per user answer. Keep real issuance off until exact supplier settings/selected company operation are established. There is no InvoiceNow transmission, payment receipt, credit-note handling or GST-return preparation. Source record CSV v1 remains unchanged.

Final F13 checks are recorded in the master and verification report: full326-test regression including18 workshop PG cases, fresh Chrome invoice/old-workflow checks and actual browser PDF output; the final UTC fix is covered by JSON equality across PostgreSQL issue/read/retry/restore and fresh restarted HTTP verification.

## Print a job sheet in the paper layout

Each reviewed version in the history has a **Print job sheet (paper layout)** link. It opens the workshop's own form with the checked values filled in; use the browser's Print / Save as PDF.

To show the real form, save a PNG or JPEG of the blank job sheet in the private `car mechanic assistant/runtime/workshop/` folder and set `WORKSHOP_SHEET_TEMPLATE` to its full path, then restart. Without it the values still print, on a plain page with a notice. Keep the form image out of Git. If the workshop changes its printed form, the field positions at the top of `app/services/workshop_sheet.py` need adjusting.

An issued invoice has the same option: **Print invoice on the workshop form**. Work lines fill the numbered rows and Total, GST 9% and Grand total fill the last rows. The plain invoice print is still available and is the stored copy.

## New screen (13 October 2026)

The numbered walk-through under “Complete one fictional job” above describes the earlier screen. The current screen has a step bar along the top and its own guide: open `/workshop` and click **How to use**. In short: New job → 1 Car & customer → 2 Knock → 3 Repair & parts → 4 Spray (add lines, click the car to mark damage) → 5 Check & save (Save, then tick and confirm) → 6 Print & invoice. The car picture needs `WORKSHOP_SHEET_TEMPLATE` set; without it a plain box is shown and marks still work.

## Books, payments and the paper guide (13 October 2026)

Run `python -m alembic upgrade head` once to add the payments table (`20261013_payments`). **Books** in the top bar lists each month's invoices with GST, paid and balance, and downloads them for Excel. Record payments on step 6 or from a Books row; a refund is a minus amount. To show reference pictures in the **Paper guide** pop-up, put PNG/JPEG files in a private folder (for example `car mechanic assistant/runtime/workshop/guide/`, named `01 …`, `02 …` for order) and set `WORKSHOP_GUIDE_DIR` to its full path. Keep that folder out of Git.
