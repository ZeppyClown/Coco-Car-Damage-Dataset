> Historical prototype snapshot. The October 2026 rebuild changes behaviour and commands; see [BUILD_STATUS.md](BUILD_STATUS.md) and [QUICKSTART.md](QUICKSTART.md) for the current verified state.

# Car Mechanic Assistant (Gemini RAG) — Project Summary

**Last updated:** 2026-10-02 (written from a full read of the code; project files are dated 2026-01-02)
**Location:** `car mechanic assistant/` inside the `Coco-Car-Damage-Dataset` repo
(moved here from `/Volumes/T9/Kaggle/` on 2026-10-02; folder name typo fixed)

> The "Problems found" section comes from **reading** the code. Nothing was run to
> produce this document. The only measured numbers are the ones in section 6, which
> come from the saved `test_results.json`.

---

## 1. What this project is

A question-and-answer assistant for a working car mechanic. The mechanic types a
question ("2008 BMW 335i hard to start when hot, loses power under boost"), and can
attach a photo. The assistant looks up the most relevant pages in a small library of
workshop notes, then asks Google Gemini to write an answer **based on those pages**,
and shows which pages it used.

This is a RAG pipeline (retrieval-augmented generation): find the right documents
first, then let the language model answer from them, so it relies on workshop notes
instead of guessing.

### How it relates to the FastAPI app in the parent folder

They are two separate attempts at the same idea and share no code.

| | Parent repo (`app/`) | This project |
|---|---|---|
| Written | Dec 2025 – 1 Jan 2026 | 2 Jan 2026 |
| How answers are produced | Fixed templates filled from lookup tables | Gemini writes the answer from retrieved documents |
| Language model | None | Gemini (text and image) |
| Knowledge | 5 fault codes, 7 makes, in Python dictionaries | 14 Markdown documents, searchable |
| Storage | PostgreSQL | ChromaDB (local vector database) |
| Web framework | FastAPI | Flask |
| Size | ~9,100 lines of Python | ~1,700 lines of Python |

The last commit message in the parent repo — "problems faced, as lack of actual
information and static information" — is the problem this project was built to solve.

---

## 2. Current state at a glance

| Part | State |
|---|---|
| Knowledge base | 14 documents (~3,800 lines) across 10 topic folders |
| Vector database | Built: **108 chunks** stored in `chroma_db/` (3.7 MB) |
| Text questions | Working (per saved test results) |
| Photo questions | Built, using Gemini's image understanding |
| Web page | Built (Flask, port 8080) |
| Command-line chat | Built, but likely fails to start (see section 7) |
| Evaluation | 8 test questions, 8 passed — see section 6 for what that does and doesn't show |
| Version control | **Not committed.** Most of it would be skipped by git as things stand (see section 7) |

---

## 3. How a question flows through the system

```
Question (+ optional photo)
        │
        ▼
1. Pick out vehicle details        make, year, model, engine code (keyword/regex)
        │
        ▼
2. Turn the question into numbers  Gemini gemini-embedding-001 → 3,072 numbers
        │
        ▼
3. Search ChromaDB                 fetch 15 closest chunks (3× the 5 needed),
        │                          limited to chunks matching the vehicle details
        ▼
4. Re-rank                         similarity + folder priority + exact-match bonuses
        │                          → keep top 5
        ▼
5. Always add workshop rules       prepended if not already in the top 5
        │
        ▼
6. Build the prompt                system rules + retrieved documents + question (+ photo)
        │
        ▼
7. Gemini writes the answer        temperature 0.3, up to 8,192 tokens
        │
        ▼
Answer + list of source documents with scores
```

---

## 4. The pieces in detail

### 4.1 Knowledge base — `knowledge_base/`

Hand-written Markdown notes, organised by topic. Each file ends with a small JSON
block of tags (make, model, engine, fault codes) that becomes searchable metadata.

| Folder | Documents | Chunks |
|---|---|---|
| 01 Vehicle specs | BMW E90 328i (2007), BMW N52 torque specs | 6 |
| 02 Diagnostic procedures | No-start (cranks fine), rough idle | 12 |
| 03 Fault codes | P0300 random misfire, BMW 30D8 | 13 |
| 04 Repair procedures | BMW N54 injector replacement | 6 |
| 05 Parts catalogue | Spark plug cross-reference | 9 |
| 06 Diagnostic software | BMW INPA injector coding | 10 |
| 07 Paint codes | BMW paint codes | 9 |
| 08 Pricing | Common repair labour guide | 9 |
| 09 Workshop rules | Workshop standards (always included) | 9 |
| 10 Troubleshooting | BMW N54 fuel pump failure, Honda VTC rattle | 25 |

**7 of the 14 documents are BMW-specific, 1 is Honda, 6 are general.** Many
sub-folders (flowcharts, recalls, market values, mixing formulas…) exist but are empty.

### 4.2 Document processing — `src/document_processor.py`

- Reads every `.md` file except `README.md`.
- Splits on `##` headings so each section stays whole, packing sections together up
  to about 1,000 characters, with a 200-character overlap between chunks.
- Tags each chunk with its folder, file name, section title and vehicle details
  (from the JSON block, the file name, or `**Make**:` style lines in the text).
- Only Markdown is handled. PDF and Word support is listed in the requirements but
  no code reads those formats.

### 4.3 Embeddings — `src/embeddings.py`

- Uses Gemini `gemini-embedding-001` (3,072 numbers per chunk). The original model,
  `text-embedding-004`, has been retired by Google and now returns a 404, so the
  database was rebuilt with the new model on 2026-10-02. The old database is kept in
  `chroma_db.backup-text-embedding-004/` (git-ignored).
- Documents and questions are embedded with different task settings
  (`retrieval_document` vs `retrieval_query`), which is the recommended way.
- Waits 1 second between batches to stay inside the free rate limit.

### 4.4 Vector store and ranking — `src/vector_store.py`

ChromaDB, stored on disk in `chroma_db/`. The ranking score for each chunk is:

| Factor | Points |
|---|---|
| Similarity to the question | 0–100 |
| Folder priority (known issues 10 → paint/pricing 3) | 3–10 |
| Fault code in both question and chunk (P0300, P0171, P0420, P0087) | +20 |
| Make in the question matches the chunk's make | +15 |
| Symptom phrase in both (rough idle, no start, misfire, rattle…) | +10 |

The idea behind folder priority: real-world "known issue" notes should beat generic
theory when both match.

### 4.5 Answer generation — `src/rag_system.py`

- A long system prompt sets the behaviour: act as a workshop assistant, rank causes
  with probabilities, suggest quick checks first, at most 3 follow-up questions,
  never invent part numbers or specs, say so when unsure, give price ranges not
  single numbers, treat photo-based colour and part identification as approximate.
- The retrieved documents are pasted into the prompt with their source and score.
- **Photo questions:** the photo goes to Gemini together with the prompt. The
  document search uses only the typed text, not the photo.
- Model: `gemini-3-flash-preview` (set in `.env`; the code default is
  `gemini-3-pro-preview`).

### 4.6 Front ends

| File | What it is |
|---|---|
| `web_app.py` + `templates/index.html` + `static/style.css` | Flask web page on port 8080 with a question box, photo upload, answer and source list. `POST /query`, `GET /health` |
| `app.py` | Command-line chat with `help`, `verbose on/off`, `clear`, `exit` |
| `setup.py` | Guided setup: installs packages, creates `.env`, offers to build the database |

---

## 5. Setup

```bash
cd "car mechanic assistant"
pip install -r requirements.txt
# put your Gemini key in .env as GOOGLE_API_KEY=...
python src/vector_store.py            # build the database (add --reset to rebuild)
python src/test_rag.py                # run the 8 test questions
python web_app.py                     # then open http://localhost:8080
```

The database only needs rebuilding when documents are added or changed.

---

## 6. Evaluation

**What exists:** `src/test_rag.py` runs 8 fixed questions and saves the outcome to
`test_results.json`. The saved result is **8 out of 8 passed**.

| Test | Keywords found | Right folder retrieved |
|---|---|---|
| BMW N54 fuel pump failure | 2 of 4 | Yes |
| P0300 misfire code | 4 of 4 | Yes |
| Rough idle diagnosis | 3 of 3 | Yes |
| Oil specification | 2 of 2 | Yes |
| Paint code lookup | 2 of 2 | Yes |
| Repair procedure | 4 of 4 | Yes |
| Labour time estimate | 3 of 3 | Yes |
| Honda VTC rattle | 4 of 4 | Yes |

A test passes when at least half the expected keywords appear in the answer **and**
a document from the expected folder was among the sources.

The saved run dates from January 2026, **before** the embedding model was switched,
so it has not been re-run against the current database.

**What this shows:** the pipeline runs end to end, retrieval finds the intended
document for questions written about that document, and the answer mentions the
expected terms.

**What it does not show:**

- **Whether the answers are correct.** Mentioning "misfire" and "coil" is not the
  same as giving the right diagnosis. No answer was checked against a trusted source.
- **How it handles questions outside the 14 documents.** Every test question was
  written to match a document that exists. There are no tests for a Toyota, a fault
  code that isn't covered, or a question it should decline to answer.
- **Whether it makes things up.** There is no check that part numbers and specs in
  the answer actually appear in the retrieved documents.
- **Anything about photos.** No image tests.
- **A reliable percentage.** 8 questions is too few; one failure would move the
  score by 12.5 points. The pass bar is also lenient (the fuel pump test passed with
  2 of 4 keywords), and the "Oil specification" test's folder check can never fail
  because workshop rules are always added to the sources.

`README_RAG_SYSTEM.md` states "Retrieval: >90% relevant docs in top 5" and "Response
quality: Expert-level". **Neither figure is backed by a measurement in this folder**
and they should not be quoted. The honest claim is: "8 of 8 smoke-test questions
passed a keyword-and-source check."

---

## 7. Problems found

**Before committing to git**

1. ~~Real API key in `.env.example`~~ — **fixed 2026-10-02.** The example file now
   holds a placeholder and is tracked; the real key lives only in `.env`, which is
   git-ignored.
2. ~~Git would skip the knowledge base~~ — **fixed 2026-10-02.** The parent
   `.gitignore` now makes an exception for Markdown in this folder. `chroma_db/`
   and `test_results.json` are still ignored, so the database must be rebuilt after
   a fresh clone (`python src/vector_store.py`).
3. **The Gemini library is end-of-life.** `google-generativeai` prints a warning
   that it no longer receives updates; Google's replacement is `google-genai`.

**Likely to fail**

4. **`python app.py` (command-line chat).** It imports `src.rag_system`, which in
   turn imports `config` by its bare name. That only resolves when `src/` is on the
   Python path, which `web_app.py` sets up and `app.py` does not.

**Runs but can give weaker answers**

5. **Naming a vehicle can hide the best document.** When the question mentions a
   make, model, year or engine, the search is limited to chunks tagged with one of
   those. General documents have no vehicle tags, so "P0300 code on Honda Accord"
   would search only Honda-tagged chunks and miss the generic P0300 guide. A make
   with no documents at all (e.g. Toyota) would return nothing except workshop rules.
6. **Workshop rules are only partly included.** The rules document is 9 chunks, but
   the "always include" step adds just the first one.
7. **Embedding failures are silent.** If a Gemini embedding call fails, the chunk is
   stored with an all-zero vector and can never be found. Only a console message
   reports it.
8. **Exact-match bonuses are hard-coded** to four fault codes and six makes.
9. **No conversation memory.** Each question is answered on its own; the chat
   history kept by `app.py` is never sent to the model.

**Housekeeping**

10. Unused packages in `requirements.txt`: LangChain, sentence-transformers, pypdf,
   python-docx, BeautifulSoup, FastAPI, Jupyter — none are imported.
11. The Flask app runs in debug mode and listens on all network interfaces; fine on
    a laptop, not for anything shared.
12. No unit tests for chunking, metadata extraction or ranking — only the
    end-to-end script, which needs a live API key to run.

---

## 8. Suggested next steps

1. Move from `google-generativeai` to `google-genai` before the old library stops
   working.
2. Change the vehicle filter so untagged (general) documents are always eligible —
   use the vehicle match as a ranking bonus instead of a hard filter.
3. Fix the `app.py` import so the command-line chat starts.
4. Grow the knowledge base beyond BMW. This is the main limit on usefulness, the
   same way 5 fault codes limits the parent app.
5. Build a real evaluation: 50–100 questions written the way mechanics ask them,
   each with a known correct answer, including questions the system should **not**
   be able to answer. Score retrieval (was the right document in the top 5?) and
   answers (correct, and supported by the sources?) separately.
6. Include all workshop-rule chunks, and fail loudly when an embedding call fails.

---

## 9. Technology

- **Python 3.8+**
- **Google Gemini** (`google-generativeai`): `gemini-embedding-001` for search,
  `gemini-3-flash-preview` for answers and image understanding
- **ChromaDB** for the local vector database
- **Flask** for the web page
- Settings in `.env`: 5 documents per answer, 1,000-character chunks, 200 overlap,
  temperature 0.3

## 10. File map

```
car mechanic assistant/
├── web_app.py              Flask web app (port 8080)
├── app.py                  Command-line chat
├── setup.py                Guided setup
├── requirements.txt
├── .env / .env.example     Settings and API key (git-ignored)
├── src/
│   ├── config.py           Settings, folder priorities
│   ├── document_processor.py  Read and chunk Markdown
│   ├── embeddings.py       Gemini embeddings
│   ├── vector_store.py     ChromaDB, search, re-ranking; run to build the database
│   ├── rag_system.py       Retrieval + prompt + Gemini answer (text and photo)
│   └── test_rag.py         8-question test script
├── knowledge_base/         14 Markdown documents in 10 topic folders
├── chroma_db/              Built vector database (108 chunks, git-ignored)
├── templates/index.html    Web page
├── static/style.css
├── test_results.json       Saved result of the last test run (8/8)
└── README_RAG_SYSTEM.md, QUICKSTART.md, WEB_APP_README.md, IMAGE_UPLOAD_GUIDE.md
```
