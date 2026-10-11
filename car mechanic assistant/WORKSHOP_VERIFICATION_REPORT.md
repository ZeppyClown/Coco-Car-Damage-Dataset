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

The user assumes usefulness and that the old financial/GST software is gone. Target: **standalone workshop capture/review/history/export**. The old application's import format is not a prerequisite. Specific external integrations are optional if later selected. Invoicing/GST/accounting is a separate conditional extension; no tax treatment, registration status or calculation rules are inferred.

The CSV remains an explicitly labelled demonstration record export, not a GST invoice or tax return. Saving/corrections/access/recovery are developer-verifiable software behavior and have now been checked; they do not need a usefulness interview.

Real handwriting/source interpretation still needs independently established expected values. Company deployment is separate: access checks use one configured local account; recovery uses a quiescent local disposable schema and fictional files. These checks do not prove multi-user roles, remote TLS/hosting, consistent backups during arbitrary writes, offsite recovery, adoption or historical résumé figures.
