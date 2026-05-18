# Sentiment Analysis Dashboard

A full-stack AI application that performs **aspect-based sentiment analysis** on customer comments using a fine-tuned RoBERTa transformer model. Built end-to-end — from research notebooks to a production-grade REST API and an interactive React dashboard.

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)
![PyTorch](https://img.shields.io/badge/PyTorch-2.11-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-3.8-09A3D5?style=flat&logo=spacy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)

---

## What It Does

Given a set of customer comments, the pipeline:

1. **Splits** compound sentences on conjunctions (`but`, `however`, `.`) so each opinion is analysed independently
2. **Classifies** each phrase as `positive`, `neutral`, or `negative` using a RoBERTa model fine-tuned on 58M tweets
3. **Extracts aspects** (price, design, quality, service…) using spaCy's lemma matching — correctly handling plurals, verb forms, and avoiding substring false positives
4. **Stores** every result in a structured SQLite database linked to the originating analysis
5. **Displays** everything in a clean dashboard with stat cards, history, and per-analysis drill-downs

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

**Research-first workflow.** Four progressive notebooks validated every decision before production code was written — model selection, phrase splitting strategy, batch optimization, and NLP-based aspect extraction.

**Batch inference.** All phrases from a request are collected and passed to the model in a single forward pass, reducing inference time from ~70s (sequential) to ~6s (batched) on the same test set.

**spaCy lemma matching.** Aspect detection was migrated from substring keyword matching to spaCy token-level lemma matching after notebook experiments exposed two concrete failure modes: substring false positives (`"priceless"` matching `price`) and missed inflections (`"deliveries"` not matching `delivery`).

**Layered backend architecture.** The FastAPI backend is organized in four strict layers — routers, services, repositories, and models — keeping HTTP logic, business logic, and database access completely separated.

**Model loaded once at startup.** The transformer model is loaded into a shared state during FastAPI's lifespan event and reused across all requests. Loading it per-request would add 3–5 seconds of latency to every call.

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML Model | `cardiffnlp/twitter-roberta-base-sentiment` via HuggingFace Transformers |
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
│       │   └── 04_aspect_based_analysing_SpaCy.ipynb
│       └── src/                                ← validated standalone pipeline
│           ├── model_loader.py
│           ├── preprocessing.py
│           ├── aspect_extraction.py
│           ├── inference.py
│           └── test_pipeline.py
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
│           ├── api/         ← Axios client
│           ├── components/  ← StatCard, SentimentBadge, Sidebar…
│           └── pages/       ← Dashboard, History, NewAnalysis, AnalysisDetail
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

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/sentiment-analysis/` | Submit a list of comments for analysis |
| `GET` | `/sentiment-analysis/all` | Retrieve all analyses with results |
| `GET` | `/sentiment-analysis/results/{id}` | Retrieve a single analysis by ID |
| `GET` | `/sentiment-analysis/stats/summary` | Get aggregate stats (total, positive, negative counts) |
| `DELETE` | `/sentiment-analysis/{id}` | Delete an analysis and all its results |

---

## Documentation

A full technical breakdown of every engineering decision, the inference pipeline step-by-step, and the architecture is available in [`docs/project-breakdown.md`](docs/project-breakdown.md).
