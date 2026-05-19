# AI Semantic Resume & Job Matching Engine

# Project Goal

Build a production-style AI-powered resume intelligence and job recommendation backend that:

* uploads and parses resumes
* extracts structured technical skills
* generates semantic embeddings
* performs hybrid AI matching
* recommends relevant jobs
* highlights matched and missing skills
* uses scalable vector retrieval
* simulates real-world AI backend architecture

The project is designed to:

* strengthen practical AI/ML engineering skills
* focus on backend AI system design
* remain interview-friendly and production-oriented
* teach semantic search and recommendation systems
* avoid unnecessary research-level complexity

---

# Current Tech Stack

## Backend

* Python
* FastAPI
* Pydantic

## AI / NLP

* sentence-transformers
* all-MiniLM-L6-v2
* scikit-learn

## Vector Search

* FAISS

## Parsing

* PyMuPDF

## Database / Storage (Current + Planned)

* JSON datasets
* PostgreSQL (used in previous AI project experience)

## Frontend (Planned Later)

* React
* TailwindCSS

## Utilities

* NumPy
* pandas
* regex

---

# Current Project Structure

```text
AI_Job_Matcher/
│
├── Backend/
│   │
│   ├── app/
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── embedding_service.py
│   │   │   ├── parser_service.py
│   │   │   ├── recommendation_service.py
│   │   │   ├── similarity_service.py
│   │   │   ├── skill_extractor_service.py
│   │   │   └── matching_engine.py   (planned improvement)
│   │   │
│   │   ├── utils/
│   │   │   └── helpers.py
│   │   │
│   │   ├── __init__.py
│   │   │
│   │   └── main.py
│   │
│   ├── data/
│   │   │
│   │   ├── jobs/
│   │   │   └── jobs.json
│   │   │
│   │   ├── uploads/
│   │   │
│   │   └── skills.py
│   │
│   ├── hf_cache/
│   │
│   ├── requirements.txt
│   │
│   └── venv/
│
├── Frontend/
│
├── Memory.md
│
├── .gitignore
│
└── requirements.txt
```

---

# Completed Features

# 1. Modular Backend Architecture

Built a clean FastAPI backend architecture using:

* API layer
* services layer
* models layer
* utility layer

Goal:

keep AI logic separated from API logic.

---

# 2. FastAPI Backend Setup

Implemented:

* FastAPI initialization
* API routing
* Swagger documentation
* endpoint testing workflow
* modular route structure

Server command:

```bash
uvicorn app.main:app --reload
```

---

# 3. Embedding Generation Pipeline

Created:

```text
embedding_service.py
```

Implemented:

* transformer model loading
* semantic embedding generation
* vector conversion pipeline

Embedding model:

```text
all-MiniLM-L6-v2
```

Output size:

```text
384-dimensional vectors
```

---

# 4. HuggingFace Windows Issues Solved

Problems faced:

* permission errors
* XET backend issue
* cache corruption

Solutions:

* disabled HuggingFace XET backend
* configured local hf_cache folder
* stabilized model loading workflow

---

# 5. Semantic Similarity Engine

Created:

```text
similarity_service.py
```

Implemented:

* cosine similarity
* vector comparison
* semantic scoring

Core formula:

genui{"math_block_widget_always_prefetch_v2":{"content":"\cos(\theta)=\frac{A\cdot B}{|A||B|}"}}

Enabled:

* semantic text comparison
* meaning-based job matching
* AI-powered ranking logic

---

# 6. Match API Built

Endpoint:

```text
/match
```

Features:

* accepts resume text
* accepts job description
* generates embeddings
* returns similarity score

Example output:

```json
{
  "match_score": 49.5
}
```

---

# 7. Pydantic Schema Integration

Implemented:

* request validation
* structured API responses
* cleaner backend architecture

Concepts learned:

* BaseModel
* request models
* response models
* schema validation

---

# 8. Resume PDF Upload System

Created:

```text
parser_service.py
```

Implemented:

* PDF uploads
* text extraction using PyMuPDF
* async file handling
* multipart/form-data processing

Endpoint:

```text
/upload-resume
```

Concepts learned:

* UploadFile
* Form(...)
* async uploads
* binary file saving

---

# 9. End-to-End Resume Matching Pipeline

Created endpoint:

```text
/resume-match
```

Workflow:

```text
Resume PDF
↓
PDF Upload
↓
Text Extraction
↓
Embedding Generation
↓
Semantic Similarity
↓
Final Match Score
```

---

# 10. Skill Extraction Engine

Created:

* skill_extractor_service.py
* data/skills.py

Implemented:

* keyword-based skill extraction
* technical skill matching
* structured NLP extraction

Example:

```json
[
  "python",
  "fastapi",
  "scikit-learn"
]
```

---

# 11. Hybrid AI Matching System

Major upgrade:

moved from pure semantic similarity to hybrid ranking.

Current scoring combines:

* semantic embeddings
* skill overlap scoring

Formula:

genui{"math_block_widget_always_prefetch_v2":{"content":"Final\ Score=(semantic_score\times0.7)+(skill_match_score\times0.3)"}}

Benefits:

* improved technical accuracy
* ATS-like behavior
* better role alignment
* more realistic recommendation quality

Observed improvement:

```text
~43 → ~62 score improvement
```

---

# 12. Multi-Job Recommendation Engine Completed

Created:

* recommendation_service.py
* jobs/jobs.json

Implemented:

* compare one resume against multiple jobs
* rank jobs by score
* hybrid AI recommendation pipeline
* matched skills detection
* missing skills detection
* sorted recommendation responses

Current endpoint:

```text
/job-recommendations
```

Current response includes:

```json
{
  "filename": "AI_Resume.pdf",
  "total_jobs_compared": 3,
  "recommendations": [
    {
      "title": "Backend Python Developer",
      "match_score": 45.95,
      "semantic_score": 22.79,
      "skill_match_score": 100,
      "matched_skills": ["fastapi"],
      "missing_skills": []
    }
  ]
}
```

This transitioned the project from:

```text
single similarity system
```

into:

```text
AI recommendation system architecture
```

---

# Current Active APIs

```text
/embedding
/resume-match
/job-recommendations
```

---

# Current Working Pipeline

```text
Resume PDF
↓
Upload API
↓
PyMuPDF Parser
↓
Text Extraction
↓
Skill Extraction
↓
Embedding Generation
↓
Semantic Similarity
↓
Hybrid AI Scoring
↓
Multi-Job Comparison
↓
Ranked Recommendations
```

---

# Important Concepts Learned

# 1. Embeddings

Text converted into numerical vectors.

Example:

```text
"Machine Learning Engineer"
↓
[0.23, -0.51, ...]
```

---

# 2. Semantic Similarity

Meaning-based comparison instead of exact keyword matching.

---

# 3. Cosine Similarity

Main vector similarity metric used for semantic comparison.

genui{"math_block_widget_always_prefetch_v2":{"content":"\cos(\theta)=\frac{A\cdot B}{|A||B|}"}}

---

# 4. Hybrid Ranking Systems

Real-world AI systems combine:

* embeddings
* keyword matching
* rule systems
* structured extraction
* ranking logic

Pure embeddings alone are insufficient.

---

# 5. Recommendation Systems

Learned:

* ranking pipelines
* top-k retrieval
* recommendation scoring
* multi-job comparison
* recommendation sorting

---

# 6. Resume Intelligence Pipelines

Real workflow:

```text
Resume PDF
↓
Raw Text
↓
Clean Text
↓
Skill Extraction
↓
Embeddings
↓
Recommendation Engine
```

---

# Problems Faced And Solved

# 1. HuggingFace Cache Errors

Solved using:

* local cache
* disabling XET backend

---

# 2. FastAPI Method Not Allowed Error

Problem:

opening POST endpoint directly in browser.

Solution:

used Swagger docs testing:

```text
/docs
```

---

# 3. Multipart Form Upload Handling

Problem:

could not send file + JSON together.

Solution:

used:

* UploadFile
* Form(...)

---

# 4. Low Semantic Scores

Problem:

pure embeddings produced weak recommendation quality.

Understanding gained:

* embeddings alone are insufficient
* hybrid systems perform better

Solution:

added skill extraction + hybrid scoring.

---

# Current Project Status

# COMPLETED

✅ FastAPI backend
✅ Modular backend architecture
✅ Embedding generation pipeline
✅ Semantic similarity engine
✅ Cosine similarity scoring
✅ Resume PDF upload system
✅ PDF parsing pipeline
✅ Skill extraction engine
✅ Hybrid AI matching system
✅ Multi-job recommendation engine
✅ Ranked recommendation responses
✅ Missing skill detection
✅ Multipart form handling
✅ End-to-end AI recommendation pipeline

---

# NEXT PHASE

# PHASE 6 — FAISS Semantic Retrieval

Goal:

replace brute-force job comparison with scalable vector retrieval.

Current system:

```python
for job in jobs:
```

Next system:

```text
FAISS nearest-neighbor retrieval
```

---

# Planned FAISS Workflow

```text
All Job Descriptions
↓
Generate Job Embeddings
↓
Store Vectors In FAISS Index
↓
Resume Embedding Query
↓
Nearest Neighbor Search
↓
Retrieve Top Matching Jobs
```

---

# Next Files To Build

## matching_engine.py

Purpose:

centralize reusable hybrid scoring logic.

Responsibilities:

* semantic similarity
* skill overlap scoring
* final weighted scoring
* matched skills
* missing skills

This will be reused by:

* /resume-match
* /job-recommendations
* FAISS retrieval pipeline

---

## faiss_service.py

Purpose:

* generate job embeddings
* build FAISS index
* perform nearest-neighbor search
* retrieve top matching jobs efficiently

---

# Upcoming Improvements

## 1. Skill Normalization

Examples:

```text
postgres → postgresql
ml → machine learning
rest api → rest apis
```

Goal:

improve ATS-style matching quality.

---

## 2. Top-K Recommendations

Return:

```text
Top 5 Best Matching Jobs
```

instead of all jobs.

---

## 3. Match Strength Labels

Examples:

```text
Strong Match
Moderate Match
Low Match
```

---

## 4. Resume Role Prediction

Predict:

```text
Best Career Role
```

using highest-ranked recommendation.

---

# Future Planned Phases

# PHASE 7 — Frontend Dashboard

Planned pages:

* resume upload
* top recommendations
* skill analysis
* missing skills dashboard
* recommendation score visualization

---

# Development Rules

## DO

* build step-by-step
* test every module individually
* understand every concept
* keep architecture modular
* focus on practical AI engineering
* reuse services instead of duplicating logic

---

## DO NOT

* blindly follow tutorials
* overcomplicate architecture
* jump into frontend too early
* focus only on model training
* ignore backend engineering concepts

---

# Final Target

Build a production-style AI recommendation backend demonstrating:

* NLP engineering
* embeddings
* semantic search
* hybrid ranking systems
* recommendation engines
* FAISS vector retrieval
* AI backend architecture
* scalable search systems
* practical AI workflows

without going unnecessarily deep into research-level ML.
