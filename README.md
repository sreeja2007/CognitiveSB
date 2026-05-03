# ShadowByte

> Most study tools let you read passively. ShadowByte forces active recall — upload your material and get a Socratic tutor, structured notes, auto-generated quizzes, spaced repetition flashcards, and an interactive knowledge graph, all powered by a RAG pipeline that actually understands your content.

![ShadowByte Demo](assets/demo.gif)

---

## Screenshots

| Dashboard | Study Chat |
|---|---|
| ![Dashboard](assets/dashboard.png) | ![Chat](assets/chat.png) |

| MCQ Quiz | Short Answer |
|---|---|
| ![Quiz](assets/quiz.png) | ![Short Answer](assets/short_answer.png) |

| Flashcards | Mind Map |
|---|---|
| ![Flashcards](assets/flashcards.png) | ![Mind Map](assets/mindmap.png) |

---

## What it does

Upload a PDF, DOCX, TXT, or YouTube URL. ShadowByte ingests it through a RAG pipeline and gives you:

- **4 chat modes** — Socratic (guides with questions), Feynman (you explain it to the AI), Simple (explain like I'm 12), Exam Prep (high-yield definitions and likely questions)
- **Structured notes** — key topics extracted with difficulty ratings, click any topic to go deeper
- **MCQ quiz** — auto-generated multiple choice with hints and difficulty tags
- **Short answer practice** — LLM-graded answers with specific feedback
- **Flashcards** — spaced repetition with SM-2 algorithm, tracks mastery across cards
- **Interactive mind map** — click any node to ask the AI about that specific concept

---

## Tech Stack

**Backend**
- Python, Flask, Flask-CORS
- LangChain, LangGraph
- Groq (LLM inference)
- HuggingFace sentence-transformers (embeddings)
- FAISS (vector store)
- YouTube Transcript API

**Frontend**
- React 19, TypeScript, Vite
- Tailwind CSS, Framer Motion
- React Force Graph 2D (mind map)
- React Router, Lucide Icons, Sonner

---

## Architecture

```
Upload (PDF / DOCX / TXT / YouTube URL)
        ↓
  Loader Manager
        ↓
  Chunker → Embedder → FAISS Vector Store
        ↓
  Session Store (in-memory)
        ↓
  ┌─────────────────────────────────────┐
  │         LangGraph RAG Pipeline      │
  │  Retrieve → Rerank → Stream (Groq)  │
  └─────────────────────────────────────┘
        ↓
  Mode Prompts: Socratic / Feynman / Simple / Exam
        ↓
  SSE Streaming → React Frontend
```

```
.
├── app.py                  # Flask entry point
├── agents/
│   ├── prompts.py          # All mode prompt templates
│   └── rag_workflow.py     # LangGraph RAG pipeline
├── loaders/                # PDF, DOCX, TXT, YouTube loaders
├── processing/             # Chunker, embedder, graph extractor
├── retrieval/              # FAISS vector store wrapper
├── routes/                 # Flask API blueprints
├── llm/                    # Groq LLM wrapper
├── utils/                  # JSON helpers
├── frontend/               # Vite + React app
│   └── src/
│       ├── pages/          # Dashboard, StudyChat
│       ├── components/ui/  # Chat, flashcards, quiz, notes, graph
│       ├── hooks/          # useChat (SSE streaming)
│       ├── lib/            # API client, utils
│       └── styles/         # Design tokens (flat dark)
├── uploads/                # Runtime — gitignored
└── vector_store/           # Runtime FAISS index — gitignored
```

---

## API

All routes under `/api`:

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/upload` | Upload file or YouTube URL |
| `GET` | `/api/chat` | Stream chat via SSE |
| `GET` | `/api/sessions` | List sessions |
| `DELETE` | `/api/sessions/<id>` | Delete session |
| `GET` | `/api/notes/<id>` | Get notes |
| `POST` | `/api/notes/generate/<id>` | Generate notes |
| `GET` | `/api/flashcards/<id>` | Get flashcards |
| `POST` | `/api/flashcards/generate/<id>` | Generate flashcards |
| `POST` | `/api/flashcards/rate` | Rate flashcard mastery |
| `GET` | `/api/quiz/<id>` | Get quiz |
| `POST` | `/api/quiz/generate/<id>` | Generate quiz |
| `POST` | `/api/quiz/grade` | LLM-grade short answer |
| `GET` | `/api/graph/<id>` | Get knowledge graph |
| `POST` | `/api/graph/generate/<id>` | Generate knowledge graph |
| `GET` | `/api/fact/<id>` | Get a study fact |

---

## Setup

**1. Clone and set up backend**

```bash
git clone https://github.com/Sudhanshukumar0007/CognitiveSB.git
cd CognitiveSB

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

**2. Configure environment**

```bash
copy .env.sample .env         # Windows
cp .env.sample .env           # Mac/Linux
```

Edit `.env` and set:

```env
GROQ_API_KEY="your_groq_api_key"
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

**3. Set up frontend**

```bash
cd frontend
npm install
```

**4. Run**

```bash
# Terminal 1 — backend
python app.py

# Terminal 2 — frontend
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## Known Limitations

- Sessions are in-memory — lost on Flask restart
- FAISS retrieval is not strictly isolated per session
- `vector_store/` and `uploads/` are gitignored and created at runtime

---

## Built by

[Sudhanshu Kumar](https://github.com/Sudhanshukumar0007) — 2nd year CS student building AI systems.
Part of the larger **Aira** project — a modular AI OS connecting multiple specialized agents.
