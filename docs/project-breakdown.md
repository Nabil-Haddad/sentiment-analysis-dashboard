# Sentiment Analysis Dashboard — Technical Breakdown

## What This Project Is

A full-stack web application that takes free-text comments, runs them through a transformer-based sentiment model, and presents the results in a structured, interactive dashboard. The project was built end-to-end: from model experimentation in Jupyter notebooks, to a standalone inference pipeline, to a production FastAPI backend, to a React frontend.

---

## How It Was Built — The Engineering Process

This project followed a proper ML engineering workflow rather than jumping straight to an application. The work happened in three distinct phases.

### Phase 1 — Research and Experimentation (Notebooks)

Before writing any application code, the model and pipeline logic were validated in notebooks:

- **`01_basic_sentiment_analysis.ipynb`** — Explored the `cardiffnlp/twitter-roberta-base-sentiment` model from HuggingFace. Tested single-input inference, verified label mappings, and confirmed the model's output format.
- **`02_aspect_based_splitting.ipynb`** — Experimented with how to split compound sentences (e.g. *"The design is beautiful but the price is too high"*) into independent phrases before classification, so each aspect gets its own sentiment score rather than one collapsed result for the whole sentence.
- **`03_batch_inference_optimization.ipynb`** — Benchmarked single-call inference vs. batched inference. Batching all phrases from a request into a single forward pass significantly reduces latency and is the approach used in production.
- **`04_aspect_based_analysing_SpaCy.ipynb`** — Evaluated spaCy as a replacement for the keyword-based aspect detection used in earlier notebooks. Compared three approaches side by side: substring keyword matching, spaCy lemma matching, and dependency-based opinion extraction. This notebook drove the decision to adopt spaCy lemma matching in production.

This research-first approach means every decision in the production code has a reason behind it.

---

### Phase 2 — Standalone Python Pipeline

Once the experiments were validated, the logic was extracted into clean, importable Python modules under `Models piplines/Sentimental Analysis/src/`:

| Module | Responsibility |
|---|---|
| `model_loader.py` | Loads tokenizer and model from HuggingFace Hub |
| `preprocessing.py` | Cleans text (normalises URLs, masks @mentions) and splits compound sentences |
| `aspect_extraction.py` | Detects product/service aspects using spaCy lemma matching |
| `inference.py` | Runs single and batched sentiment prediction with proper `torch.no_grad()` and `softmax` |

A `test_pipeline.py` script validated the full pipeline end-to-end across 19 real-world comment types: straightforward, compound, double-aspect, edge cases, and no-aspect inputs.

This phase produced a standalone, testable pipeline — completely independent of any web framework.

---

### Phase 3 — Production API and Frontend

The validated pipeline was integrated into a production-grade application.

#### Backend — FastAPI

The backend follows a strict 4-layer architecture:

```
routers/       ← HTTP layer, input validation, routing
services/      ← Business logic, orchestrates inference + storage
repositories/  ← All database access, isolated from business logic
models/        ← SQLAlchemy ORM definitions
schemas/       ← Pydantic request/response contracts
```

**Key engineering decisions:**

**Model loaded once at startup, not per request.**
Using FastAPI's `lifespan` context, the model is loaded into memory when the server starts and stored in a shared `model_state` dict. Every subsequent request reuses the same loaded model. Loading a transformer model on every request would add several seconds of latency.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_temp_user()
    load_model()  # ← runs once
    yield
```

**Batched inference across all phrases in a request.**
When a user submits multiple comments, every comment is first split into phrases, then all phrases are collected and passed to the model in a single batched forward pass. This is more efficient than running one inference call per phrase.

```python
all_phrases = []
for comment in comments:
    phrases = split_into_phrases(preprocess_text(comment))
    all_phrases.extend(phrases)

predictions = predict_batch(all_phrases)  # ← one forward pass for all
```

**spaCy lemma matching for aspect extraction.**
The initial aspect detection approach used substring keyword matching — checking whether a word like `"price"` appeared anywhere in a phrase string. This was replaced with spaCy's lemma-based token matching after notebook experimentation revealed two concrete failure modes:

- **False positives** from substrings: `"priceless"` would match the aspect `price`, `"staffroom"` would match `staff`.
- **Missed inflections**: `"prices"` and `"deliveries"` would not match because the exact keyword strings `"price"` and `"delivery"` were not present.

The production implementation loads spaCy once at the module level, tokenizes each phrase, and matches each token's lemma against the aspect list:

```python
doc = nlp(text)
for token in doc:
    if token.lemma_.lower() in aspects_set:
        detected_aspects.append(token.lemma_.lower())
```

Using a `set` for the aspect lookup keeps the check O(1) regardless of how many aspects are defined.

**User-defined aspects managed through the database.**
The initial implementation used a hardcoded array of aspect keywords in `aspect_extraction.py`. This was replaced with a database-backed system where aspects are stored in an `aspects` table, scoped per user, with an `is_active` flag. Several decisions drove the design:

- **Why a database table, not a config file.** Config files require a server restart to take effect. A DB table means changes are live immediately and the REST API can expose full CRUD operations without touching the filesystem.
- **`is_active` flag instead of hard delete.** Deactivating an aspect preserves the word in the table so the user can re-enable it later. Hard delete is also available for permanent removal.
- **`UniqueConstraint("name", "user_id")`.** Enforced at the database level, not only in Python. The service layer catches the resulting `IntegrityError` and converts it to a clean `400` response with a human-readable message.
- **Idempotent seeding.** On startup, `seed_default_aspects()` checks whether the user already has any aspects before inserting defaults. Running it on every server restart is safe — it becomes a no-op after the first run.
- **`DEFAULT_ASPECTS` in `core/constants.py`.** The defaults are defined once and imported by the service layer for seeding. `aspect_extraction.py` no longer contains any fallback list — callers must always pass the aspect list explicitly, making the absence of aspects a visible failure rather than a silent one.
- **Aspects fetched once per request, at the orchestrator level.** `analysis_service.analyse_and_save_comments` fetches the user's active aspects from the database and passes them down to `predict_comments` and then to `extract_aspects`. Neither `inference.py` nor `aspect_extraction.py` knows the database exists — they receive a plain `list[str]`.

**Correct inference setup.**
`model.eval()` disables dropout layers (which are active during training). `torch.no_grad()` prevents the model from building a computation graph, saving memory and computation during inference. Both are required for correct, efficient production inference.

**Cascade deletes on relationships.**
SQLAlchemy relationships use `cascade="all, delete-orphan"`, meaning deleting an analysis automatically removes all its child phrase results — no orphaned rows, no manual cleanup.

**Input validated at two levels.**
At the router level via FastAPI (`Path(gt=0)`, empty list checks). At the schema level via Pydantic (`Field(min_length=1)`, `ge=0`, `le=1`). Both layers work together to reject malformed input before it reaches business logic.

**Environment variables for configuration.**
All runtime configuration is loaded from a `.env` file via `python-dotenv`. No values are hardcoded in source files. A `.env.example` template is committed to the repository so the required variables are documented without exposing actual values.

#### Database Schema

Four tables with proper foreign key relationships:

```
users
  ├── aspects (user_id FK)               ← user-defined aspect vocabulary
  └── analyses (user_id FK)
        ├── aspect_based_analyses (analysis_id FK)
        └── without_aspect_analyses (analysis_id FK)
```

The `aspects` table carries a `UniqueConstraint` on `(name, user_id)` and an `is_active` boolean so users can disable aspects without losing them.

SQLite is used for simplicity — the session is configured with `check_same_thread=False` to handle FastAPI's async request handling correctly.

#### Frontend — React + Vite + Tailwind

The frontend is structured around a clean API abstraction layer and component separation:

- **API layer** (`src/api/`) — All HTTP calls go through a single Axios client instance. API functions are named after intent (`submitAnalysis`, `getAllAnalyses`, `toggleAspect`), not HTTP verbs.
- **Pages** (`src/pages/`) — Each route is a self-contained page component that manages its own loading and error states.
- **Components** (`src/components/`) — Reusable components (`StatCard`, `SentimentBadge`, `LoadingSpinner`) encapsulate display logic.

The UI is fully responsive, handles empty states gracefully, and includes a confirm step before destructive actions (delete).

The **Aspects page** (`src/pages/Aspects.jsx`) exposes the full aspect management workflow:
- **Optimistic toggle** — the switch flips immediately in the UI; if the API call fails the state is reverted. This avoids the latency of waiting for a server round-trip on a simple boolean change.
- **Two-step delete** — clicking Delete reveals Confirm / Cancel buttons rather than executing immediately. Accidental deletion of an aspect would silently affect all future analyses, so the extra confirmation step is intentional.
- **Inline add error** — duplicate aspect names are rejected by the database constraint and surfaced as an inline error below the input field, not as a page-level banner, because the error is scoped to that form only.
- **Zero-active warning** — an amber banner appears when all aspects are disabled, informing the user that the next analysis will produce no aspect-level results before they run it.

---

## The Inference Pipeline — Step by Step

Given this input:
```
"The design is beautiful but the price is too high."
"The staff and service are amazing."
"I really loved the overall experience."
```

The pipeline does the following:

1. **Preprocess** — Normalise URLs and @mentions in each comment.
2. **Split into phrases** — Split on `.`, `but`, `however`:
   - `"The design is beautiful"`
   - `"the price is too high"`
   - `"The staff and service are amazing"`
   - `"I really loved the overall experience"`
3. **Batch inference** — All 4 phrases are tokenised together (padded to the same length) and passed through RoBERTa in a single forward pass. Softmax is applied to the logits to get confidence scores.
4. **Aspect extraction** — The user's active aspects are fetched from the database once at the start of the request. Each phrase is then processed by spaCy, and every token's lemma is checked against that list. This correctly handles inflected forms (`"prices"` → lemma `"price"`) and avoids substring false positives (`"priceless"` is a single token whose lemma is `"priceless"`, not `"price"`). Because aspects are fetched at the service layer and passed down as a plain list, the NLP function itself has no dependency on the database.
5. **Route results** — Phrases with a detected aspect go to `aspect_based_analyses`. Phrases with no detected aspect go to `without_aspect_analyses`.
6. **Persist** — The analysis record and all phrase-level results are saved in a single database transaction.
7. **Return** — The full result set is returned to the frontend immediately.

---

## Model

**`cardiffnlp/twitter-roberta-base-sentiment`**

- Architecture: RoBERTa-base fine-tuned on ~58M tweets for 3-class sentiment classification
- Labels: `negative`, `neutral`, `positive`
- Chosen because it was pre-trained on short, informal social-media text — the same register as product reviews and customer comments
- Max token length: 128 (sufficient for phrase-level inputs after splitting)

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML model | HuggingFace Transformers, PyTorch, SciPy |
| NLP | spaCy (`en_core_web_sm`) |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2, SQLite |
| Configuration | python-dotenv |
| Frontend | React, Vite, Tailwind CSS, Axios, React Router |
| Experimentation | Jupyter Notebooks, Pandas |

---

## Project Structure

```
AI Multi-Tool Dashboard/
├── Models piplines/
│   └── Sentimental Analysis/
│       ├── notebooks/          ← experimentation phase
│       │   ├── 01_basic_sentiment_analysis.ipynb
│       │   ├── 02_aspect_based_splitting.ipynb
│       │   ├── 03_batch_inference_optimization.ipynb
│       │   └── 04_aspect_based_analysing_SpaCy.ipynb
│       └── src/                ← standalone pipeline
│           ├── model_loader.py
│           ├── preprocessing.py
│           ├── aspect_extraction.py
│           ├── inference.py
│           └── test_pipeline.py
├── App/
│   ├── Backend/
│   │   ├── core/               ← configuration + env loading
│   │   ├── db/                 ← session, base, seed
│   │   ├── models/             ← ORM definitions
│   │   ├── schemas/            ← Pydantic schemas
│   │   ├── repositories/       ← database queries
│   │   ├── services/           ← business logic + inference + spaCy extraction
│   │   ├── routers/            ← HTTP endpoints
│   │   ├── main.py
│   │   ├── .env.example        ← configuration template
│   │   └── requirements.txt
│   └── Frontend/
│       └── src/
│           ├── api/            ← Axios client + functions (analysis, aspects)
│           ├── components/     ← reusable UI components
│           └── pages/          ← Dashboard, History, NewAnalysis, AnalysisDetail, Aspects
└── docs/
    └── project-breakdown.md
```
