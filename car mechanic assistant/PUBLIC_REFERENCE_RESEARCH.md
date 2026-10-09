# Public industry references and replacement search options

Checked 9 October 2026 against primary sources. These are examples and proposed choices, not Yap Motor achievements or independently established vendor performance. The corresponding [placeholder library](public_reference_corpus/README.md) contains 12 short authored summaries in EN/CN/JP, with source URLs and explicit provenance. No proprietary manuals or full articles were copied.

## What relevant companies provide

| Source | Publicly described workflow | Implication for this project (our recommendation) |
|---|---|---|
| [BMW Factory Genius](https://www.press.bmwgroup.com/canada/article/detail/T0451181EN/%E2%80%9Cjust-ask-factory-genius-%E2%80%9D%3A-how-ai-helps-maintain-manufacturing-equipment?language=en), 2 July 2025 | Searches internal manufacturing-maintenance material, displays source links and supports translation | Use authorised internal material, maintain source provenance and distinguish factory maintenance from vehicle repair |
| [TEXA IDC6](https://www.texa.com/idc6-software/) | AI Global Search and AI Intelligent Diagnosis use TEXA diagnostic information and repair solutions | Collect reviewed fault-code cases with vehicle context; avoid unsupported diagnostic statistics |
| [Toyota TIS](https://techinfo.toyota.com/) | North American service information, repair manuals and wiring diagrams with subscription levels | Check region, edition and permission; access to a website does not grant RAG redistribution rights |
| [Bosch ESI[tronic]](https://www.boschaftermarket.com/me/en/equipment/ecu-diagnosis/esitronic-software/esitronic/) | Structured diagnostic/repair information, component tests and wiring diagrams | Preserve procedure structure, tables and vehicle applicability during extraction |

These examples support the product direction, not the numbers 24, 500 or 90%. Product information is no substitute for a manufacturer procedure for the actual vehicle. Development translations need native-speaker review.

## What can replace Google Custom Search?

Google’s [official overview](https://developers.google.com/custom-search/v1/overview) says Custom Search JSON API is closed to new customers and existing customers must migrate by 1 January 2027. It should not be the default for a new deployment.

| Option | Current official terms/capability | Fit here |
|---|---|---|
| [Brave Search API](https://brave.com/search/api/) | Search plan: $5 per 1,000 requests, $5 monthly credits; independent web index | Recommended direct replacement for URL/snippet search behind the existing adapter contract |
| [Tavily](https://docs.tavily.com/documentation/api-credits) | 1,000 free credits/month; basic search uses one credit, advanced uses two; pay-as-you-go $0.008/credit | Convenient prototype option; return attributed sources and keep search depth explicit |
| [Gemini grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search) | A Gemini tool for web-grounded answers with grounding metadata | Alternative for cited explanatory answers using Gemini; not a drop-in structured parts-listing API |
| [Google’s suggested alternative](https://developers.google.com/custom-search/v1/overview) | Vertex AI Search for up to 50 domains; separate full-web-search enquiry | Consider if the requirement is a fixed set of authorised supplier domains |

Brave’s [web endpoint](https://api-dashboard.search.brave.com/api-reference/web/search/get) uses a subscription-token header and returns web results. Its FAQ requires an appropriate plan for storing results. Confirm caching/storage terms before persisting provider responses; search access does not license third-party pages. Tavily’s [search endpoint](https://docs.tavily.com/documentation/api-reference/endpoint/search) supports source results and domain controls.

Recommendation: keep PostgreSQL catalogue retrieval first, replace the Google web-discovery adapter with Brave when an account is available, and retain eBay Browse or an authorised supplier catalogue for structured price/currency/shipping data. Tavily is a reasonable alternative for a free prototype. Web-search snippets must leave unknown price, fit and shipping fields unknown. Search replacements do not replace Docker, which is a separate deployment runtime.

No new account, paid plan or replacement adapter was created in this audit. Google/eBay contract tests exist, but live provider credentials remain absent. Recheck pricing and terms when selecting a provider.

## Working placeholder and later replacement

The public demo is deliberately a separate Chroma collection, `public_reference_demo`, built from `public_reference_corpus`. The checked build has 12 chunks and zero PDF manual pages. It does not add material to the repair-library benchmark.

```sh
# From the assistant directory, use a new output name for each build.
COLLECTION_NAME=public_reference_demo python -m src.vector_store --knowledge-base public_reference_corpus --output runtime/releases/public-reference-demo-new
COLLECTION_NAME=public_reference_demo CHROMA_PERSIST_DIRECTORY=runtime/releases/public-reference-demo-new gunicorn --workers 1 --threads 4 --bind 127.0.0.1:8080 'web_app:create_app()'
```

An actual Gemini embedding build and three live EN/CN/JP answers passed source-ID validation. These are demonstration checks, not expert diagnostic labels or translation-quality scores. Source payloads retain original URL, language and placeholder kind; the UI displays that provenance.

When Q06–Q09 in [COMPANY_QUESTIONS.md](COMPANY_QUESTIONS.md) are answered:

1. Keep authorised originals privately, with checksums, edition/region and vehicle applicability.
2. Extract text, reject scans until OCR/review is supplied, and count unique accepted pages.
3. Review metadata and procedures with a qualified mechanic; generic scope must actually be generic.
4. Build a new company release under the normal repair collection. Keep the public demo separate for traceability.
5. Review answer support and then evaluate a frozen, independently labelled diagnostic set. Preserve raw rankings and release/model identity.
6. Only update résumé page counts, precision, users or adoption from the corresponding evidence, not from this placeholder demo.
