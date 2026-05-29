# Sentiment Analysis Dashboard

A full-stack AI application that performs **aspect-based sentiment analysis** on customer comments using a fine-tuned RoBERTa transformer model. Built end-to-end — from research notebooks to a production-grade REST API and an interactive React dashboard.

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)
![PyTorch](https://img.shields.io/badge/PyTorch-2.11-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-3.8-09A3D5?style=flat&logo=spacy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-DeBERTa-FFD21E?style=flat&logo=huggingface&logoColor=black)

---

## What It Does

Given a set of customer comments, the pipeline:

1. **Splits** compound sentences on conjunctions (`but`, `however`, `.`) so each opinion is analysed independently
2. **Classifies** each phrase as `positive`, `neutral`, or `negative` using a RoBERTa model fine-tuned on 58M tweets
3. **Extracts aspects** (user-defined topics such as price, design, quality…) using spaCy's lemma matching — correctly handling plurals, verb forms, and avoiding substring false positives
4. **Stores** every result in a structured SQLite database linked to the originating analysis
5. **Displays** everything in a clean dashboard with stat cards, history, per-analysis drill-downs, and a dedicated aspect management page

**Example input:**
```
The design is beautiful but the price is too high.
The staff and service are amazing.
I really loved the overall experience.
```

**Example output:**

| Phrase | Aspect | Sentiment | Confidence |
|---|---|---|---|
| The design is beautiful | design | ✅ Positive | 98% |
| the price is too high | price | ❌ Negative | 92% |
| The staff and service are amazing | staff, service | ✅ Positive | 98% |
| I really loved the overall experience | — | ✅ Positive | 97% |

---

## Engineering Highlights

**Research-first workflow.** Five progressive notebooks validated every decision before production code was written — model selection, phrase splitting strategy, batch optimization, NLP-based aspect extraction, and DeBERTa fine-tuning investigation.

**Fine-tuned DeBERTa-v3-base for ABSA.** The cardiffnlp RoBERTa model was established as a baseline (macro F1: 0.687) on the SemEval-2014 restaurant dataset, then `microsoft/deberta-v3-base` was fine-tuned specifically for aspect-based sentiment classification. The fine-tuned model reached **macro F1: 0.7847** — a **+14.22% improvement** over the baseline — with the largest gains on minority classes (negative +13.34%, neutral +12.40%). A `compare_models.py` script loads both metric files, prints a side-by-side comparison, and writes a `decision.json` file that encodes which model the backend should load.

**Batch inference.** All phrases from a request are collected and passed to the model in a single forward pass, reducing inference time from ~70s (sequential) to ~6s (batched) on the same test set.

**spaCy lemma matching.** Aspect detection was migrated from substring keyword matching to spaCy token-level lemma matching after notebook experiments exposed two concrete failure modes: substring false positives (`"priceless"` matching `price`) and missed inflections (`"deliveries"` not matching `delivery`).

**User-defined aspects stored in the database.** Aspects are persisted in a dedicated `aspects` table rather than a hardcoded array. Each aspect is scoped to a user and carries an `is_active` flag. The dashboard lets users add, enable, disable, and delete aspects at any time — only active aspects are used in the next analysis run. Defaults are seeded once at startup using an idempotency check, so restarting the server never creates duplicates.

**Layered backend architecture.** The FastAPI backend is organized in four strict layers — routers, services, repositories, and models — keeping HTTP logic, business logic, and database access completely separated.

**Model loaded once at startup.** The transformer model is loaded into a shared state during FastAPI's lifespan event and reused across all requests. Loading it per-request would add 3–5 seconds of latency to every call.

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML Model (baseline) | `cardiffnlp/twitter-roberta-base-sentiment` via HuggingFace Transformers |
| ML Model (fine-tuned) | `microsoft/deberta-v3-base` fine-tuned on SemEval-2014 Restaurant ABSA |
| NLP | spaCy `en_core_web_sm` |
| Inference | PyTorch, SciPy (softmax) |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | SQLite |
| Frontend | React 18, Vite, Tailwind CSS, Axios |
| Configuration | python-dotenv |

---

## Project Structure

```
AI Multi-Tool Dashboard/
│
├── Models piplines/
│   └── Sentimental Analysis/
│       ├── notebooks/                          ← research & experimentation
│       │   ├── 01_basic_sentiment_analysis.ipynb
│       │   ├── 02_aspect_based_splitting.ipynb
│       │   ├── 03_batch_inference_optimization.ipynb
│       │   ├── 04_aspect_based_analysing_SpaCy.ipynb
│       │   └── 05_deberta_absa_investigation.ipynb
│       ├── src/
│       │   ├── roberta/                        ← original RoBERTa pipeline
│       │   │   ├── model_loader.py
│       │   │   ├── preprocessing.py
│       │   │   ├── aspect_extraction.py
│       │   │   ├── inference.py
│       │   │   └── test_pipeline.py
│       │   └── deberta_absa/                   ← fine-tuning pipeline
│       │       ├── data_preprocessing.py
│       │       ├── baseline_eval.py
│       │       ├── train_absa.py
│       │       └── compare_models.py
│       ├── models/
│       │   └── deberta-absa/                   ← saved fine-tuned weights
│       └── reports/
│           └── Metrics/                        ← baseline, finetuned, decision JSON
│
├── App/
│   ├── Backend/
│   │   ├── core/            ← config + env loading
│   │   ├── db/              ← session, base, seed
│   │   ├── models/          ← SQLAlchemy ORM
│   │   ├── schemas/         ← Pydantic schemas
│   │   ├── repositories/    ← all DB queries
│   │   ├── services/        ← business logic, inference, spaCy extraction
│   │   ├── routers/         ← HTTP endpoints
│   │   ├── main.py
│   │   ├── .env.example
│   │   └── requirements.txt
│   │
│   └── Frontend/
│       └── src/
│           ├── api/         ← Axios client (analysis + aspects)
│           ├── components/  ← StatCard, SentimentBadge, Sidebar…
│           └── pages/       ← Dashboard, History, NewAnalysis, AnalysisDetail, Aspects
│
└── docs/
    └── project-breakdown.md   ← full technical breakdown
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A virtual environment (recommended)

### 1 — Backend

```bash
cd App/Backend

# install dependencies
pip install -r requirements.txt

# download the spaCy language model
python -m spacy download en_core_web_sm

# set up environment variables
cp .env.example .env

# start the API (the model downloads automatically on first run)
uvicorn main:app --reload
```

### (Optional) Re-run the fine-tuning pipeline

```bash
cd "Models piplines /Sentimental Analysis"

pip install -r requirements.txt

# 1. Evaluate the cardiffnlp baseline
python src/deberta_absa/baseline_eval.py

# 2. Fine-tune DeBERTa-v3-base (requires a GPU for reasonable training time)
python src/deberta_absa/train_absa.py

# 3. Compare both models and write decision.json
python src/deberta_absa/compare_models.py
```

The API will be available at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

### 2 — Frontend

```bash
cd App/Frontend

npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy database connection string | `sqlite:///./database.db` |
| `MODEL_NAME` | HuggingFace model identifier | `cardiffnlp/twitter-roberta-base-sentiment` |

---

## The Research Notebooks

The notebooks document the full thinking process behind the production pipeline.  
Each one builds on the previous and ends with a conclusion that motivates the next step.

| Notebook | What it explores |
|---|---|
| `01` | Basic inference with RoBERTa — label mapping, single predictions, first observations on ambiguous sentences |
| `02` | Phrase splitting — how splitting on `but` / `however` isolates mixed opinions before classification |
| `03` | Batch optimization — benchmarking sequential vs. batched inference (~70s → ~6s on 19 comments) |
| `04` | spaCy evaluation — comparing keyword matching vs. lemma matching vs. dependency-based opinion extraction |
| `05` | DeBERTa ABSA investigation — dataset exploration (SemEval-2014), class imbalance analysis, hyperparameter rationale, and the aspect-prefix input format (`"aspect: {aspect} [SEP] {text}"`) that makes the model aspect-aware |

---

## API Endpoints

**Sentiment Analysis**

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/sentiment-analysis/` | Submit a list of comments for analysis |
| `GET` | `/sentiment-analysis/all` | Retrieve all analyses with results |
| `GET` | `/sentiment-analysis/results/{id}` | Retrieve a single analysis by ID |
| `GET` | `/sentiment-analysis/stats/summary` | Get aggregate stats (total, positive, negative counts) |
| `DELETE` | `/sentiment-analysis/{id}` | Delete an analysis and all its results |

**Aspect Management**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/aspects/` | List all aspects for the current user |
| `GET` | `/aspects/active` | List only active aspects |
| `POST` | `/aspects/` | Add a new aspect |
| `PATCH` | `/aspects/{id}` | Enable or disable an aspect |
| `DELETE` | `/aspects/{id}` | Permanently delete an aspect |

---

## Documentation

A full technical breakdown of every engineering decision, the inference pipeline step-by-step, and the architecture is available in [`docs/project-breakdown.md`](docs/project-breakdown.md).
