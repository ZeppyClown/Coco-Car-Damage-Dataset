# Workshop record, export and software verification

Checked 12 October 2026 against the authenticated local API and isolated PostgreSQL 14.20 test database. Examples are **fictional**, not company records or a handwriting benchmark. See the [master plan](WORKSHOP_MASTER_PLAN.md) for scope.

## Inspect the saved example

- [Actual stored record and reviewed history screenshot](workshop_demo/captured-record.png)
- [Complete reviewed record as JSON](workshop_demo/captured-record.json)
- [Actual 32-column CSV download](workshop_demo/export.csv)
- [Authored source image](../tests/fixtures/workshop/synthetic-sheet.png)

The JSON was read from the saved reviewed snapshot. The CSV preserves the original download bytes, including UTF-8 BOM and CRLF records. Chrome opened that same stored job for the screenshot. No new model call was made. This example came from the earlier live printed-fictional Gemini proposal and explicit human source check.

An exact-path `.gitattributes` rule keeps Git from normalising this CSV's line endings, so its recorded checksum survives publication/cloning.

| Field | Stored value |
|---|---|
| Job reference | DEMO-JOB-001 |
| Customer | Fictional Example Person |
| Vehicle | DEMO-VEHICLE-A |
| Stage | Quote |
| Description | Example filter replacement |
| Amount/currency | 25.10 SGD |
| Reviewed version | 2 |
| Attribution | Authenticated fictional local operator |
| Unknown values | Make/model/dates/written totals remain null |

Selected fields from the full CSV row:

| output_kind | revision | record_stage | job_reference | description | amount | currency |
|---|---|---|---|---|---|---|
| DEMO_ONLY | 2 | quote | DEMO-JOB-001 | Example filter replacement | 25.10 | SGD |

The file also contains source/revision IDs, literal text, review time/provenance and mapping version `workshop-demo-v1`. SHA-256: `d0a175808168e5a8b4ddfb9b257d8267b61897acba0464e07864d7ae31802638`. Repeating the export returned the same identity/bytes. No GST, inferred total or invoice was generated.

## Executed checks

| Area | Actual check | Result |
|---|---|---|
| Stored capture | Read saved snapshot; source bytes equal authored fixture; fields equal downloaded CSV | Passed |
| Saving | New fictional manual draft saved/read; corrected version reopened through fresh HTTP client | Passed |
| Corrections | Authored manual amount 25.10→30.10 in version 2; stale save/confirm returned409; new review preserved original snapshot | Passed |
| Output history | Old CSV unchanged; corrected version has distinct output; repeat review/export reuse identities | Passed |
| Access | Anonymous page/job/image/CSV401; wrong password401; authenticated cross-origin write403; static bypass404; no-store | Passed |
| Attribution | Client reviewer text could not replace authenticated account | Passed |
| Browser | Stored source/quote/25.10/history reopened in fresh Chrome; reviewer readonly; no page errors | Passed |
| PostgreSQL | Fresh/older-head migration, concurrent saves/reviews/exports, rollback, source retention and immutable snapshot guards | Passed in suite |
| Recovery | Actual `pg_dump`/`pg_restore` in owned disposable schema plus source/CSV file restore; record/history/identities/bytes/checksums/schema/guards preserved | Passed in suite |
| Incomplete recovery | DB-only restore correctly lacked source bytes until files were restored | Passed in suite |

Fresh command:

```sh
YAP_TEST_POSTGRES_URL='postgresql://workshop_test@127.0.0.1:55441/yap_test_workshop_f02' \
  'car mechanic assistant/runtime/workshop-api-venv/bin/python' -m pytest -q \
  --disable-warnings tests/unit/test_workshop*.py tests/integration/test_workshop_postgres.py
```

**217 passed, no skips, 51 warnings in 146.30 seconds.** All 15 workshop PostgreSQL cases ran, including actual recovery. Warnings are dependency/deprecation notices. Live HTTP/Chrome checks above are additional to pytest.

## Scope and limits

The user assumes usefulness and that the old financial/GST software is gone. Target: **standalone workshop capture/review/history/export**, now with explicitly requested F13 invoicing/GST. The old application's import format is not a prerequisite. Specific external integrations are optional if later selected. The user supplied GST-registered/inclusive pricing; exact company billing identity/number and InvoiceNow date remain pending.

The CSV remains an explicitly labelled demonstration record export, not a GST invoice or tax return. Saving/corrections/access/recovery are developer-verifiable software behavior and have now been checked; they do not need a usefulness interview.

Real handwriting/source interpretation still needs independently established expected values. Company deployment is separate: access checks use one configured local account; recovery uses a quiescent local disposable schema and fictional files. These checks do not prove multi-user roles, remote TLS/hosting, consistent backups during arbitrary writes, offsite recovery, adoption or historical résumé figures.

## F13: inspect the actual fictional invoice

- [One-page browser-generated PDF](workshop_demo/invoice.pdf)
- [Exact issued printable HTML](workshop_demo/invoice.html)
- [Stored invoice response as JSON](workshop_demo/invoice.json)
- [Billing workflow, configuration and company questions](WORKSHOP_INVOICING_GUIDE.md)

This is a separate, manually authored **fictional completed-work** record `DEMO-INVOICE-001`, not the earlier quote or a real company bill. It has explicit fictional supplier/customer details and a deliberately non-real GST-number placeholder. The browser PDF came from the stored protected print route. It was not manually assembled or backdated. No AI/provider call was used.

| Amount | Value (SGD) |
|---|---:|
| Active line subtotal, GST-inclusive |109.00|
| Explicit discount |0.00|
| Total excluding GST |100.00|
| GST at9% |9.00|
| Total payable, including GST |109.00|

Invoice number: `DEMO-INV-3F15CB475D534DEC88992E9C672D57C4`. Exact issued HTML SHA-256: `48563a7d09b5494ec6b256b2ea0456c8e557a0dfe8385492e2fde7aa4a1cd49a`. The JSON was reread after server restart; exact-request retry returned the same JSON/number/time, canonical UTC timestamp and printable bytes. Normal local demo remains real-issuance-disabled, supplier-unset and AI-off.

## F13 executed verification

Final regression after the UTC correction:

```sh
YAP_TEST_POSTGRES_URL='postgresql://workshop_test@127.0.0.1:55441/yap_test_workshop_f02' \
  .venv/bin/python -m pytest -q --disable-warnings tests
```

**326 passed, no skips, 137 warnings in136.34 seconds.** All18 workshop PostgreSQL cases ran. The earlier217-test result above is the pre-invoice clean-API baseline, not this final run. Targeted initial billing unit/API file:33 passed/8 warnings. PostgreSQL file:18 passed/34 warnings. Dependencies were unchanged; the billing profile JSON setting was separately parsed successfully and a registered profile missing its number rejected.

| Area | Actual check/result |
|---|---|
| Calculation | Inclusive/exclusive, subtotal versus line rounding, half-cent half-up, discount, explicit zero/non-registration and range/invalid-money rejection passed |
| Billing eligibility | Quote/approved scope, foreign currency, unknown price, stale review, wrong date and extra client totals rejected |
| Identity/corrections | Repeat reuses one invoice; changed inputs/new reviewed correction conflict409; original issued output unchanged |
| PostgreSQL concurrency | Simultaneous same inputs return one ID; differing inputs produce one issue and one409 |
| Migration | Fresh/old heads aligned with metadata; prior-auth-head reviews/CSV preserved; dev-only Alembic upgrade/check passed |
| Immutability/recovery | Actual DB dump/restore recovers invoice snapshot/HTML/identity; restored invoice UPDATE/DELETE guard rejects mutation; existing source/CSV recovery retained |
| Failed commit | No partial invoice row; deliberate retry succeeds; internal values not exposed |
| Access/print | Protected read/print/issue, anonymous/wrong account401, cross-origin403/default-disabled404 and corrupt HTML503 passed; print CSP/no-store/nosniff/escaping checked |
| Browser | Existing record/CSV/mocked-AI/diagram/lookup flows and new preview/basis/discount/invalidation/unsaved-discard/failure-retry/issue/reopen/print-PDF passed in fresh Chrome; no page errors |
| Fresh runtime reread | After restart, canonical UTC issue/read/retry JSON equal and original HTML checksum unchanged |

Two issues were found and corrected before delivery: the browser harness matched an old confirmation status while the newly added invoice lookup was pending (history-ready ordering and response wait fixed); fresh PostgreSQL reads serialized the same timestamp with a different timezone offset (responses now canonicalise UTC; recovery assertions compare JSON). The initial failing checks are retained in the master work log rather than counted as passes.

This verifies the local invoice software. Real issuance awaits the exact supplier profile/selected company operation. Credit notes, payments, input tax/GST returns/general ledger and InvoiceNow submission are not implemented. Current treatment/rounding/layout were checked against [IRAS invoicing guidance](https://www.iras.gov.sg/taxes/goods-services-tax-(gst)/basics-of-gst/invoicing-price-display-and-record-keeping/invoicing-customers); a printable artifact is not evidence of InvoiceNow submission or blanket tax compliance.
