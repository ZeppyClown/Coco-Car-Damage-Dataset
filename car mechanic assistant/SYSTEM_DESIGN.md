> Historical prototype snapshot. The October 2026 rebuild changes behaviour and commands; see [BUILD_STATUS.md](BUILD_STATUS.md) and [QUICKSTART.md](QUICKSTART.md) for the current verified state.

# Car Mechanic Assistant — System Design (as built)

**Last updated:** 2026-10-02

A mechanic types a question and can attach a photo. The app finds the most relevant
workshop notes, then asks Google Gemini to write an answer from those notes and lists
which ones it used.

---

## 1. The whole system on one page

`[LAPTOP]` = runs on the laptop. `[GEMINI]` = call to Google Gemini (needs internet
and the API key). `[DISK]` = database stored on disk.

```
  LANE A: BUILDING THE LIBRARY                 LANE B: ANSWERING A QUESTION
  (run once, repeat when notes change)         (every question)

  ┌──────────────────────────────┐             ┌──────────────────────────────┐
  │ A1  Workshop notes  [LAPTOP] │             │ B1  Question + optional      │
  │ 14 Markdown files,           │             │     photo           [LAPTOP] │
  │ 10 topic folders             │             │ Flask web page, port 8080    │
  │ knowledge_base/              │             │ web_app.py                   │
  └──────────────┬───────────────┘             └──────────────┬───────────────┘
                 ▼                                            ▼
  ┌──────────────────────────────┐             ┌──────────────────────────────┐
  │ A2  Cut into chunks [LAPTOP] │             │ B2  Pick out the vehicle     │
  │ Split at ## headings,        │             │                     [LAPTOP] │
  │ ~1,000 characters each,      │             │ make, model, year, engine    │
  │ 200 overlap → 108 chunks     │             │ src/rag_system.py            │
  │ src/document_processor.py    │             └──────────────┬───────────────┘
  └──────────────┬───────────────┘                            ▼
                 ▼                             ┌──────────────────────────────┐
  ┌──────────────────────────────┐             │ B3  Turn the question into   │
  │ A3  Tag each chunk  [LAPTOP] │             │     numbers         [GEMINI] │
  │ folder, file, section, make, │             │ gemini-embedding-001         │
  │ model, engine, fault codes   │             │ src/embeddings.py            │
  │ src/document_processor.py    │             └──────────────┬───────────────┘
  └──────────────┬───────────────┘                            ▼
                 ▼                             ┌──────────────────────────────┐
  ┌──────────────────────────────┐             │ B4  Search the database      │
  │ A4  Turn each chunk into     │             │                       [DISK] │
  │     numbers         [GEMINI] │   ┌────────▶│ fetch 15 closest chunks,     │
  │ 3,072 numbers per chunk      │   │         │ limited to the vehicle in B2 │
  │ gemini-embedding-001         │   │         │ src/vector_store.py          │
  │ src/embeddings.py            │   │         └──────────────┬───────────────┘
  └──────────────┬───────────────┘   │                        ▼
                 ▼                   │         ┌──────────────────────────────┐
  ╔══════════════════════════════╗   │         │ B5  Re-rank, keep 5 [LAPTOP] │
  ║ A5  ChromaDB          [DISK] ║   │         │ score each chunk (section 2) │
  ║ 108 chunks + tags + numbers  ║───┘         │ + always add workshop rules  │
  ║ 3.7 MB, chroma_db/           ║  same       │ src/vector_store.py          │
  ╚══════════════════════════════╝  database   └──────────────┬───────────────┘
                                                              ▼
                                               ┌──────────────────────────────┐
                                               │ B6  Build the prompt         │
                                               │                     [LAPTOP] │
                                               │ behaviour rules + 5 chunks   │
                                               │ + question + photo           │
                                               │ src/rag_system.py            │
                                               └──────────────┬───────────────┘
                                                              ▼
                                               ┌──────────────────────────────┐
                                               │ B7  Gemini writes the answer │
                                               │                     [GEMINI] │
                                               │ gemini-3-flash-preview       │
                                               │ temperature 0.3,             │
                                               │ up to 8,192 tokens           │
                                               └──────────────┬───────────────┘
                                                              ▼
                                               ┌──────────────────────────────┐
                                               │ B8  Answer + sources         │
                                               │                     [LAPTOP] │
                                               │ shown with each source file  │
                                               │ and its score                │
                                               └──────────────────────────────┘
```

Lane A command: `python src/vector_store.py --reset`
Lane B entry point: `POST /query` (and `GET /health` to check the app is up)

---

## 2. How a chunk is scored in step B5

| Factor | Points |
|---|---|
| How close its meaning is to the question | 0 to 100 |
| Which folder it came from (known issues highest, paint and pricing lowest) | 3 to 10 |
| Same fault code in question and chunk | +20 |
| Same make in question and chunk | +15 |
| Same symptom phrase, such as rough idle or rattle | +10 |

The top 5 by total score go into the prompt.

---

## 3. What leaves the laptop

| Step | Sent to Google |
|---|---|
| A4 | The text of every note, once per rebuild |
| B3 | The typed question |
| B7 | The question, the 5 chosen chunks and the photo |

Everything else, including the database and the search, stays on the laptop. Nothing
is saved between questions, so each one is answered on its own.

---

## 4. The parts

| Part | File | Job |
|---|---|---|
| Web page | `web_app.py`, `templates/index.html`, `static/style.css` | Question box, photo upload, shows answer and sources |
| Settings | `src/config.py`, `.env` | Model names, chunk size, how many chunks to keep, folder priorities |
| Note reader | `src/document_processor.py` | Reads Markdown, cuts into chunks, tags them |
| Number converter | `src/embeddings.py` | Calls Gemini to turn text into 3,072 numbers |
| Database and ranking | `src/vector_store.py` | Stores chunks in ChromaDB, searches, re-ranks |
| Answer writer | `src/rag_system.py` | Finds the vehicle, builds the prompt, calls Gemini |
| Test script | `src/test_rag.py` | Runs 8 fixed questions and saves the result |

About 1,500 lines of Python in total.

---

## 5. Weak points in this design

| Step | Problem |
|---|---|
| B4 | Naming a vehicle limits the search to chunks tagged with it. General notes have no vehicle tag, so "P0300 on a Honda Accord" skips the general P0300 guide. A make with no notes, such as Toyota, gets only the workshop rules. |
| B3 | The photo is not used to find notes. Only the typed text is searched; Gemini sees the photo at B7. |
| B5 | The workshop rules are 9 chunks, but only the first one is added. |
| A4 | If Gemini fails on a chunk, it is stored as all zeros and can never be found. Only a console message reports it. |
| A4, B3, B7 | All three Gemini calls use the `google-generativeai` library, which Google no longer updates. The replacement is `google-genai`. |
| Testing | 8 of 8 test questions passed in January 2026, but that run was before the switch to `gemini-embedding-001` and has not been repeated. |

See `PROJECT_SUMMARY.md` in this folder for the full list of problems and next steps.
