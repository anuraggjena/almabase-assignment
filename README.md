# Structured Questionnaire AI Engine

A Retrieval-Augmented Compliance Questionnaire System

----------

## 🚀 Live Demo

Frontend: `https://almabase-assignment-nine.vercel.app/`

Backend API: `https://almabase-assignment.onrender.com`

----------

# 1️⃣ Industry & Context Setup (Assignment Requirement)

### Industry Chosen

Enterprise SaaS – Compliance & Security Governance

### Fictional Company

**SecureVault Systems** is a mid-sized SaaS company that provides AI-powered workflow automation tools for financial institutions. The company handles sensitive customer data and must comply with strict security, governance, and resilience standards.

SecureLayer AI undergoes periodic vendor security assessments and must complete structured compliance questionnaires using official internal policy documents as the source of truth.

----------

# 2️⃣ Problem Statement

Manually answering compliance questionnaires is:

-   Time-consuming
    
-   Error-prone
    
-   Repetitive
    
-   Difficult to keep consistent with updated policy documents
    

This system automates structured questionnaire completion using reference documents as the single source of truth.

----------

# 3️⃣ What This System Does

-   Accepts structured questionnaires (PDF, DOCX, TXT)
    
-   Accepts multiple reference documents (PDF, DOCX, TXT)
    
-   Extracts and normalizes text
    
-   Splits documents into semantic chunks
    
-   Retrieves the most relevant chunk per question
    
-   Generates structured answers strictly grounded in references
    
-   Returns confidence scores
    
-   Exports final questionnaire in TXT, DOCX, or PDF
    
-   Supports session management and regeneration
    

----------

# 4️⃣ Assignment Requirements — Explicitly Covered

## ✅ Industry & Context Setup

Included above.

## ✅ 8–15 Realistic Questions

A 12-question compliance questionnaire was created.

## ✅ 3–8 Reference Documents

Multiple fictional governance and security documents were created in:

-   PDF
    
-   DOCX
    
-   TXT
    

## ✅ README Includes:

-   Industry
    
-   Fictional company description
    
-   System explanation
    
-   Design decisions
    
-   Tradeoffs
    
-   Deployment instructions
    

----------

# 5️⃣ System Architecture

``` mermaid

flowchart TB

%% ================================
%% USER LAYER
%% ================================
User[User Browser]

%% ================================
%% FRONTEND LAYER
%% ================================
subgraph Frontend [Frontend - Next.js (Vercel)]
    UI[UI Components]
    AuthClient[JWT Auth Handling]
    ExportClient[Export Format Selector]
end

%% ================================
%% BACKEND LAYER
%% ================================
subgraph Backend [Backend - FastAPI (Render)]
    AuthAPI[Auth Routes]
    QuestionnaireAPI[Questionnaire Routes]
    ReferenceAPI[Reference Upload Routes]
    AnswerAPI[Answer Generation Routes]
    
    Extraction[File Extraction Service\n(PDF / DOCX / TXT)]
    Normalization[Text Normalization Layer]
    Chunking[Chunking Engine\n(250 size / 50 overlap)]
    Retrieval[Retrieval Engine\n(Token Overlap + Coverage)]
    PromptBuilder[Strict Prompt Builder]
    LLM[LLM Generation]
    Confidence[Confidence Scoring Logic]
    ExportService[Export Engine\n(TXT / DOCX / PDF)]
end

%% ================================
%% DATABASE
%% ================================
subgraph Database [Neon PostgreSQL]
    Users[(Users)]
    References[(Reference Documents)]
    Chunks[(Document Chunks)]
    Questionnaires[(Questionnaires)]
    Questions[(Questions)]
    Sessions[(Generation Sessions)]
    Answers[(Generated Answers)]
end

%% ================================
%% CONNECTIONS
%% ================================

User --> UI
UI --> AuthClient
UI --> ExportClient

AuthClient --> AuthAPI
UI --> QuestionnaireAPI
UI --> ReferenceAPI
UI --> AnswerAPI

ReferenceAPI --> Extraction
Extraction --> Normalization
Normalization --> Chunking
Chunking --> Chunks

QuestionnaireAPI --> Questions

AnswerAPI --> Retrieval
Retrieval --> PromptBuilder
PromptBuilder --> LLM
LLM --> Confidence
Confidence --> Answers

AnswerAPI --> ExportService

AuthAPI --> Users
ReferenceAPI --> References
QuestionnaireAPI --> Questionnaires
AnswerAPI --> Sessions
AnswerAPI --> Answers
Chunks --> References
Answers --> Sessions
Questions --> Questionnaires

%% ================================
%% DEPLOYMENT LAYER
%% ================================
Frontend ---|Deployed on| Vercel[(Vercel)]
Backend ---|Deployed on| Render[(Render)]
Database ---|Hosted on| Neon[(Neon DB)]
```    

----------

# 6️⃣ Architecture Flow

``` mermaid

flowchart TD

%% =============================
%% USER INTERACTION
%% =============================
A[User Uploads Questionnaire] --> B[Frontend - Next.js]
A2[User Uploads Reference Document] --> B

%% =============================
%% API CALLS
%% =============================
B --> C[FastAPI Backend]

%% =============================
%% REFERENCE PROCESSING FLOW
%% =============================
C --> D[File Extraction Service]
D --> E[Text Normalization Layer]
E --> F[Chunking Engine\n(250 words / 50 overlap)]
F --> G[Store Chunks in PostgreSQL]

%% =============================
%% QUESTION PROCESSING FLOW
%% =============================
C --> H[Question Parser]
H --> I[Store Structured Questions in DB]

%% =============================
%% ANSWER GENERATION FLOW
%% =============================
J[User Clicks Generate Answers] --> B
B --> C

C --> K[Retrieve Relevant Chunks]
K --> L[Coverage-Based Confidence Calculation]

L -->|If Confidence < 35%| M[Return: Not found in references]
L -->|If Confidence ≥ 35%| N[Build Strict Prompt]

N --> O[LLM Generation]
O --> P[Structured Answer Output]

P --> Q[Save Answer + Confidence in DB]

%% =============================
%% EXPORT FLOW
%% =============================
R[User Selects Export Format] --> B
B --> C
C --> S[Export Service]
S -->|TXT| T1[Generate TXT]
S -->|DOCX| T2[Generate DOCX]
S -->|PDF| T3[Generate PDF]
T1 --> U[Download to User]
T2 --> U
T3 --> U

%% =============================
%% DATABASE
%% =============================
subgraph PostgreSQL (Neon)
    G
    I
    Q
end
```

----------

# 7️⃣ Why Each Major Decision Was Made

## 7.1 Why PostgreSQL Instead of SQLite

SQLite is suitable for local testing but:

-   Not scalable
    
-   Not production-ready
    
-   Limited concurrency
    

Neon PostgreSQL was used because:

-   Serverless
    
-   Scalable
    
-   Secure
    
-   Free tier available
    
-   Production-grade
    

----------

## 7.2 Why Chunking Is Required

Large documents cannot be sent fully to an LLM.

Chunking allows:

-   Efficient retrieval
    
-   Reduced token usage
    
-   Improved answer grounding
    
-   Controlled context injection
    

Chunk size: 250 words  
Overlap: 50 words

This balances:

-   Context preservation
    
-   Avoiding duplication
    
-   Maintaining retrieval accuracy
    

----------

## 7.3 Why Overlap Is Necessary

Without overlap:

-   Information split between chunks may be lost
    

With overlap:

-   Boundary information is preserved
    
-   Reduces retrieval miss errors
    

----------

## 7.4 Why Only Top 1 Chunk Is Returned

Initially multiple chunks were shown.

Problem:

-   Inconsistent chunk order
    
-   Confusing evidence display
    
-   Redundant citations
    

Final decision:  
Return only the most relevant chunk

This improves:

-   Clarity
    
-   Determinism
    
-   Confidence reliability
    

----------

## 7.5 Why Confidence Scoring Exists

Confidence is calculated based on token overlap coverage.

This allows:

-   Deterministic fallback
    
-   "Not found in references." when confidence is low
    
-   Prevents hallucination
    

Threshold logic:  
If coverage < 35% → return Not found.

----------

## 7.6 Why Strict Prompt Constraints Were Added

LLMs hallucinate by default.

To prevent this:

-   Prompt forces answer strictly from references
    
-   Explicit "Not found in references." rule
    
-   No inference allowed
    
-   No source mentions allowed
    

This enforces compliance-safe behavior.

----------

## 7.7 Why Normalization Layer Was Required

PDFs and DOCX often contain:

-   Broken line breaks
    
-   Collapsed numbering
    
-   Section headers mixed into questions
    

Normalization ensures:

-   Clean parsing
    
-   Proper question extraction
    
-   Prevents split-question bug
    

----------

## 7.8 Why Section Headers Were Removed in Parser

Section headers were merging into questions, causing:

-   Retrieval failure
    
-   False negative matches
    

Solution:  
Explicit removal of section patterns before parsing.

----------

## 7.9 Why Duplicate Reference Prevention Was Added

If two references contain outdated and updated versions:

-   Retrieval may pull older policy
    

Solution implemented:  
Filename-based replacement.

If same filename uploaded:

-   Old document deleted
    
-   New version inserted
    
-   Old chunks cascade deleted
    

This ensures latest version is always authoritative.

----------

# 8️⃣ File Format Support

Supported formats:

-   PDF (pdfplumber)
    
-   DOCX (XML parsing for numbering preservation)
    
-   TXT
    

Extraction handles:

-   Multi-page PDFs
    
-   Numbered DOCX lists
    
-   Broken formatting
    
-   Encoding errors
    

----------

# 9️⃣ Export System

Supports:

-   TXT
    
-   DOCX
    
-   PDF
    

Frontend dropdown allows selecting format dynamically.

Backend endpoint:  
`/answers/export/{session_id}/{format}`

Why this was required:  
Assignment requires structured output.

----------

# 🔟 Security Considerations

-   JWT authentication
    
-   User-scoped data
    
-   Reference documents isolated per user
    
-   CORS restricted in production
    
-   Environment variables used for secrets
    
-   .gitignore prevents secret leakage
    

----------

# 1️⃣1️⃣ Deployment Decisions

Backend → Render  
Frontend → Vercel  
Database → Neon

Reasons:

-   Easy CI/CD
    
-   Free tier available
    
-   HTTPS by default
    
-   Production-ready stack
    

----------

# 1️⃣2️⃣ Known Limitations

1.  Retrieval is keyword-overlap based (not embedding-based)
    
2.  Confidence is heuristic, not probabilistic
    
3.  Does not support multi-document ranking weighting
    
4.  Does not implement document version history
    
5.  Render free tier sleeps
    

These were acceptable tradeoffs for assignment scope.

----------

# 1️⃣3️⃣ Possible Future Improvements

-   Vector embeddings (FAISS / pgvector)
    
-   Versioned document storage
    
-   Audit logs
    
-   Role-based access
    
-   Multi-tenant architecture
    
-   Background processing
    
-   Caching layer
    
-   Semantic similarity instead of token overlap
    

----------

# 1️⃣4️⃣ Database Schema

Tables:

Users  
ReferenceDocuments  
DocumentChunks  
Questionnaires  
Questions  
GenerationSessions  
GeneratedAnswers

Relationships:

User → ReferenceDocuments  
ReferenceDocument → DocumentChunks  
Questionnaire → Questions  
GenerationSession → GeneratedAnswers

----------

# 1️⃣5️⃣ How To Run Locally

Backend:

`cd backend  `

`python -m venv venv  `

`venv\Scripts\activate  `

`pip install -r requirements.txt  `

`uvicorn app.main:app --reload`

Frontend:

`cd frontend  `

`npm install  `

`npm run dev`

----------

# 1️⃣6️⃣ Environment Variables

Backend:

`DATABASE_URL= your database url`

`SECRET_KEY=super secret key`

`FRONTEND_URL=your frontend url`

Frontend:

`NEXT_PUBLIC_API_BASE_URL=your backend url`

----------

# 1️⃣7️⃣ Why This Design Demonstrates Understanding

This system demonstrates:

-   Backend API design
    
-   Structured parsing
    
-   Text normalization
    
-   Retrieval-based grounding
    
-   Confidence modeling
    
-   Controlled generation
    
-   File handling
    
-   Production deployment
    
-   Database migration
    
-   Secure configuration
    
-   Environment-based architecture
    

----------

# Final Statement

This project demonstrates a production-oriented, retrieval-grounded questionnaire automation system that balances:

-   Determinism
    
-   Safety
    
-   Scalability
    
-   Maintainability
    
-   Assignment requirements
    

The system is deployed, tested, and production-ready.