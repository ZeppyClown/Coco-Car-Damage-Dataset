# Yap Motor automotive assistant

Two applications share this repository: a structured FastAPI/PostgreSQL service and a Gemini/ChromaDB manual assistant. The current rebuild is dated October 2026; internship history and business-use claims require separate evidence.

The new workshop job-sheet capture/review project is specified in the [master plan and implementation ledger](car%20mechanic%20assistant/WORKSHOP_MASTER_PLAN.md). It gives the build order, feature acceptance checks, missing company prerequisites and Claude handoff. Every implementation part must update that ledger. F01–F04 are verified: schemas, fixtures, persistence, image handling and the manual screen at `/workshop`. F05 confirmation/history is next. Workshop routes are disabled by default (`WORKSHOP_ENABLED=false`); the master includes local API instructions. Confirmation, export and AI extraction remain pending.

## Run the automotive API

Use Python 3.12. Install `requirements.txt`, supply `DATABASE_URL`, and run:

```sh
python -m alembic upgrade head
python scripts/generate_training_data.py
python scripts/train_intent_simple.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Training uses template-generated questions; its accuracy is not a workshop-quality result. The model is rebuilt inside the Docker image. Keep an existing model/data backup before deliberately regenerating it locally.

With Docker available, `docker compose up --build` starts PostgreSQL, runs migrations once, then starts the API on localhost. Use a dedicated Compose project when testing; do not remove existing database volumes. The Compose recipe is not a production access-control setup.

The seven automotive routes are query routing, parts identification, diagnostics, valuation, paint guidance, VIN specifications, and parts compatibility. `/docs` contains their actual schemas. Query and parts requests use form data; the remaining POST routes use JSON.

```sh
curl -X POST http://127.0.0.1:8000/api/v1/query -F 'text=How much is my 2018 Toyota Camry with 75k km worth?'
```

Parts retrieval uses PostgreSQL full-text search, eligible-result filtering, optional independent provider fallback, and cache keys covering all result-affecting inputs. Catalogue fit does not verify physical installation. Unknown prices are null. Valuation is a rule-based estimate with no verified comparable listings. Diagnostic and paint knowledge remain small static libraries.

Google Custom Search needs eligible existing account credentials; it is closed to new customers and ends January 1, 2027 ([Google documentation](https://developers.google.com/custom-search/v1/overview)). eBay uses Browse OAuth: set `EBAY_APP_ID`, `EBAY_CLIENT_SECRET`, `EBAY_MARKETPLACE` and `USE_EBAY_API=true`. Neither provider is required for startup. A supplier URL does not prove shipping or fit. [Search replacement research](car%20mechanic%20assistant/PUBLIC_REFERENCE_RESEARCH.md) recommends Brave for a direct web-search adapter replacement; accounts and live integration remain pending.

## Manual assistant and implementation record

Going to the workshop: use the detailed [fill-in interview workbook](car%20mechanic%20assistant/WORKSHOP_VISIT_WORKBOOK.md), starting with its essential checklist and five-question script. Keep completed company answers in a private copy.

See [assistant quickstart](car%20mechanic%20assistant/QUICKSTART.md), [build status](car%20mechanic%20assistant/BUILD_STATUS.md), and [full implementation/evidence plan](car%20mechanic%20assistant/RESUME_DELIVERY_PLAN.md).

The [résumé verification report](car%20mechanic%20assistant/RESUME_VERIFICATION.md) distinguishes working code from unverified business claims. [Company questions](car%20mechanic%20assistant/COMPANY_QUESTIONS.md) retain all missing evidence requests. A separate [public EN/CN/JP reference demo](car%20mechanic%20assistant/public_reference_corpus/README.md) uses attributed company summaries while authorised manuals are pending. It is not a repair corpus or evidence of Yap Motor adoption.

## Tests

Install both applications' requirements and `requirements-dev.txt`, then run `python -m pytest -q`. Unit fixtures use isolated databases, mocked providers, temporary Chroma directories and test embeddings. Tests do not use the workshop database or assert 90% retrieval precision. For the PostgreSQL integration test, create a disposable local database whose name starts with `yap_test`, then set `YAP_TEST_POSTGRES_URL` to its connection URL. Without that variable, this integration check is skipped.

Manual originals, keys, built vector indexes and feedback remain private and untracked. A real 500-page corpus, 24 mechanic users, independent precision labels and sustained adoption are pending evidence.
