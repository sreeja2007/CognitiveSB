# ShadowByte — Frontend & Prompt Improvement Specification

> **For Codex:** This document describes targeted improvements to the existing ShadowByte codebase. Every change is additive or a drop-in replacement. Do not restructure the project, rename files, or change the API surface. Work within the existing Flask + Vite/React/Tailwind/TypeScript stack.

---

## 1. Prompt Improvements — `agents/prompts.py`

### 1.1 Add a shared formatting constant

Add this constant at the top of `agents/prompts.py`, before any other prompt definitions. Append it to every system prompt using string concatenation.

```python
CHAT_FORMAT_RULES = """

FORMAT RULES — always follow these without exception:
- Keep responses concise. Maximum 3-4 short paragraphs OR 5-6 bullet points per response. Never both.
- Do NOT use bold markdown headers like "How does X work?" or "What is Y?". Use plain flowing prose instead.
- Use markdown sparingly: **bold** only for key terms (max 2-3 per response), `backticks` for technical terms and code identifiers, bullet lists only when listing 3 or more distinct items.
- Answer the specific question asked, then stop. Do not volunteer adjacent information unprompted.
- If giving an analogy, give exactly one good one. Not two or three.
- Never write a summary paragraph at the end of a response.
- End naturally — a brief follow-up hook like "Want me to go deeper on any part?" is good. A numbered summary of what you just said is not.
- When the user asks for code, wrap it in a fenced markdown code block with the correct language identifier.
"""
```

### 1.2 Update each system prompt

Replace the existing four system prompt strings with these. The content intent is preserved; only length constraints and formatting discipline are added.

```python
SOCRATIC_SYSTEM = """You are a Socratic tutor. You never give direct answers.
Guide the student with probing questions that lead them to discover answers themselves.
Use the provided context to inform your questions. Ask exactly one question at a time.
If the student is stuck, give a small hint framed as another question.
Never answer more than one sub-topic per response.""" + CHAT_FORMAT_RULES

FEYNMAN_SYSTEM = """You are a curious student who knows nothing about this topic.
The user must explain the concept to you. Ask clarifying questions frequently.
Say "I don't understand" when something is unclear. Ask "but why?" to go deeper.
Push back gently when an explanation is vague.
Keep each response to one or two short reactions — do not write long paragraphs of confusion.""" + CHAT_FORMAT_RULES

SIMPLE_SYSTEM = """Explain everything as if the user is 12 years old.
Use simple words, one real-world analogy, and relatable examples.
Avoid all jargon. If you must use a technical term, immediately explain it in plain language.
Keep it short — maximum 3 paragraphs. Stop when the concept is clear.""" + CHAT_FORMAT_RULES

EXAM_PREP_SYSTEM = """You are an exam preparation specialist.
For each question: give the core definition in one sentence, flag one common exam trap if relevant, and give one memory hook.
Be direct. Use a short bullet list only when comparing multiple items side by side.
Never write more than 150 words per response unless the student explicitly asks to go deeper.
Reference the study material directly when relevant.""" + CHAT_FORMAT_RULES
```

### 1.3 Update `NOTES_PROMPT`

The existing prompt returns generic notes. This version adds importance ranking and enforces a tighter card format.

```python
NOTES_PROMPT = """Analyze the provided context and extract 5 to 7 key concepts as structured sticky notes.
Each note must be self-contained and useful for revision.
Prioritize concepts most likely to appear in an exam. Order cards by importance descending.
Return ONLY valid JSON, no other text:
{
  "points": [
    {
      "bullet": "Short concept name, 3 to 5 words maximum",
      "explanation": "2 to 3 sentence explanation in plain English, no jargon",
      "example": "One concrete real-world example",
      "importance": "high or medium or low"
    }
  ]
}"""
```

### 1.4 Update `QUIZ_MCQ_PROMPT`

Add a difficulty field and improve explanation quality instruction.

```python
QUIZ_MCQ_PROMPT = """Based on the provided context, generate exactly 5 multiple choice questions.
Vary difficulty: 2 easy, 2 medium, 1 hard.
Each explanation must state WHY the correct answer is right AND why each wrong option is wrong.
Return ONLY valid JSON, no other text:
{
  "mcq": [
    {
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "answer": 0,
      "difficulty": "easy or medium or hard",
      "explanation": "string explaining correct answer and why distractors are wrong"
    }
  ]
}"""
```

### 1.5 Update `FLASHCARD_GENERATION_PROMPT`

Add a difficulty field and a hint field.

```python
FLASHCARD_GENERATION_PROMPT = """Based on the provided context, generate exactly 10 flashcards.
Cover a mix of definitions, comparisons, and application questions.
Return ONLY valid JSON, no other text:
{
  "cards": [
    {
      "front": "question or term",
      "back": "answer or definition",
      "explanation": "brief explanation of why this answer is correct",
      "hint": "one-word or one-phrase hint that does not give away the answer"
    }
  ]
}"""
```

### 1.6 Update `GRADING_PROMPT`

No structural change — just make the feedback more actionable.

```python
GRADING_PROMPT = """Grade this student answer on a scale of 0 to 10.
Be fair but specific. Feedback must tell the student exactly what to study next.
Question: {question}
Sample correct answer: {sample_answer}
Student answer: {user_answer}
Return ONLY valid JSON:
{{
  "score": 8,
  "feedback": "Specific, actionable feedback in 1-2 sentences",
  "correct_concepts": ["list of concepts the student got right"],
  "missed_concepts": ["list of concepts the student missed or got wrong"],
  "study_tip": "One specific thing the student should review next"
}}"""
```

---

## 2. Frontend Improvements — `frontend/src`

All changes below are isolated. No file is deleted. No component is renamed. Each section states exactly which file to edit and what to change.

---

### 2.1 Chat message rendering — markdown styling

**File:** wherever the chat message list is rendered (likely `frontend/src/components/Chat.tsx` or similar).

**Problem:** `react-markdown` is installed but renders with browser-default styles, producing unstyled black text, oversized bold headings, and no visual separation between turns.

**Fix:** Pass a `components` prop to `ReactMarkdown` with dark-theme styles. This is a drop-in addition — do not remove any existing props, only add `components`.

```tsx
import ReactMarkdown from 'react-markdown';

const markdownComponents = {
  p: ({ children }: any) => (
    <p style={{
      marginBottom: '10px',
      lineHeight: '1.75',
      color: 'rgba(255,255,255,0.85)',
      fontSize: '14px',
    }}>
      {children}
    </p>
  ),
  strong: ({ children }: any) => (
    <strong style={{ color: '#a9a3f0', fontWeight: 500 }}>
      {children}
    </strong>
  ),
  em: ({ children }: any) => (
    <em style={{ color: 'rgba(255,255,255,0.6)', fontStyle: 'italic' }}>
      {children}
    </em>
  ),
  code: ({ inline, children }: any) =>
    inline ? (
      <code style={{
        background: 'rgba(127,119,221,0.15)',
        color: '#c4b5fd',
        padding: '2px 6px',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '13px',
      }}>
        {children}
      </code>
    ) : (
      <pre style={{
        background: '#11101d',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: '8px',
        padding: '14px 16px',
        overflowX: 'auto',
        margin: '10px 0',
      }}>
        <code style={{ fontFamily: 'monospace', fontSize: '13px', color: '#cdd6f4', lineHeight: '1.7' }}>
          {children}
        </code>
      </pre>
    ),
  ul: ({ children }: any) => (
    <ul style={{
      paddingLeft: '20px',
      marginBottom: '10px',
      color: 'rgba(255,255,255,0.8)',
    }}>
      {children}
    </ul>
  ),
  ol: ({ children }: any) => (
    <ol style={{
      paddingLeft: '20px',
      marginBottom: '10px',
      color: 'rgba(255,255,255,0.8)',
    }}>
      {children}
    </ol>
  ),
  li: ({ children }: any) => (
    <li style={{ marginBottom: '6px', lineHeight: '1.6' }}>
      {children}
    </li>
  ),
  h1: ({ children }: any) => (
    <p style={{ fontSize: '15px', fontWeight: 500, color: '#a9a3f0', marginBottom: '8px' }}>
      {children}
    </p>
  ),
  h2: ({ children }: any) => (
    <p style={{ fontSize: '14px', fontWeight: 500, color: '#a9a3f0', marginBottom: '6px' }}>
      {children}
    </p>
  ),
  h3: ({ children }: any) => (
    <p style={{ fontSize: '14px', fontWeight: 500, color: 'rgba(255,255,255,0.7)', marginBottom: '6px' }}>
      {children}
    </p>
  ),
  blockquote: ({ children }: any) => (
    <blockquote style={{
      borderLeft: '3px solid rgba(127,119,221,0.4)',
      paddingLeft: '12px',
      margin: '10px 0',
      color: 'rgba(255,255,255,0.55)',
      fontStyle: 'italic',
    }}>
      {children}
    </blockquote>
  ),
};

// Usage — replace existing <ReactMarkdown> call with:
<ReactMarkdown components={markdownComponents}>
  {message.content}
</ReactMarkdown>
```

---

### 2.2 Chat message layout — avatars and spacing

**File:** chat message list component.

**Problem:** Messages render as a plain vertical list with no visual distinction between AI and user turns. The screenshot shows text pasted directly into the chat area with no avatars, no bubbles, and no turn separation.

**Fix:** Wrap each message in a flex row. This is a Tailwind addition — use existing Tailwind classes already in the project.

```tsx
// AI message row
<div className="flex items-start gap-3 mb-6">
  <div className="w-7 h-7 rounded-full bg-purple-900/40 border border-purple-500/25 flex items-center justify-center flex-shrink-0 mt-0.5">
    <span className="text-purple-300 text-xs font-medium">AI</span>
  </div>
  <div className="flex-1 min-w-0">
    <ReactMarkdown components={markdownComponents}>
      {message.content}
    </ReactMarkdown>
  </div>
</div>

// User message row
<div className="flex items-start gap-3 mb-6 flex-row-reverse">
  <div className="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0 mt-0.5">
    <span className="text-white/60 text-xs font-medium">U</span>
  </div>
  <div className="max-w-[78%] bg-purple-500/15 border border-purple-500/25 rounded-2xl rounded-tr-sm px-4 py-2.5">
    <p className="text-white/90 text-sm leading-relaxed">{message.content}</p>
  </div>
</div>
```

---

### 2.3 Chat scroll area — padding and overflow

**File:** chat container element.

**Problem:** The chat area has tight or zero padding causing text to sit flush against the edges.

**Fix:** Add padding to the scroll container. Add padding-bottom so the last message is never hidden behind the input bar.

```tsx
// Wrap the message list in:
<div className="flex-1 overflow-y-auto px-5 pt-6 pb-28 flex flex-col">
  {messages.map(...)}
</div>
```

---

### 2.4 Notes cards — add importance badge

**File:** Notes component (likely `frontend/src/components/Notes.tsx` or similar).

**Problem:** Notes cards show no visual priority signal. All cards look identical.

**Fix:** Read the `importance` field returned from the updated `NOTES_PROMPT` and render a badge. This is additive — it only applies when the field exists.

```tsx
const importanceStyles: Record<string, string> = {
  high:   'bg-red-500/15 text-red-300 border border-red-500/25',
  medium: 'bg-amber-500/15 text-amber-300 border border-amber-500/25',
  low:    'bg-white/5 text-white/40 border border-white/10',
};

// Inside the note card JSX, after the title:
{note.importance && (
  <span className={`text-xs px-2 py-0.5 rounded-full ${importanceStyles[note.importance] ?? importanceStyles.low}`}>
    {note.importance}
  </span>
)}
```

---

### 2.5 Quiz — show difficulty badge on MCQ cards

**File:** Quiz component.

**Problem:** All quiz questions look identical regardless of difficulty. Students have no way to gauge challenge level.

**Fix:** Render the `difficulty` field returned from the updated `QUIZ_MCQ_PROMPT`.

```tsx
const difficultyStyles: Record<string, string> = {
  easy:   'bg-green-500/15 text-green-300',
  medium: 'bg-amber-500/15 text-amber-300',
  hard:   'bg-red-500/15 text-red-300',
};

// In the question card header:
{question.difficulty && (
  <span className={`text-xs px-2 py-0.5 rounded-full ${difficultyStyles[question.difficulty] ?? ''}`}>
    {question.difficulty}
  </span>
)}
```

---

### 2.6 Flashcard — show hint button

**File:** Flashcard component.

**Problem:** Flashcards flip directly from question to full answer with no middle ground.

**Fix:** Add a "Show hint" toggle that reveals the `hint` field before the full answer is shown. Uses local state only — no API changes needed.

```tsx
const [hintVisible, setHintVisible] = React.useState(false);

// Reset hint when card changes:
React.useEffect(() => { setHintVisible(false); }, [currentCardIndex]);

// In the card front face, before the flip button:
{!flipped && card.hint && (
  <button
    onClick={() => setHintVisible(v => !v)}
    className="text-xs text-purple-400/70 hover:text-purple-300 transition-colors mt-3"
  >
    {hintVisible ? 'Hide hint' : 'Show hint'}
  </button>
)}
{hintVisible && !flipped && (
  <p className="text-sm text-white/50 italic mt-1">{card.hint}</p>
)}
```

---

### 2.7 Grading — show study tip

**File:** Quiz short-answer grading result component.

**Problem:** Grading result shows score and feedback but does not surface the `study_tip` field.

**Fix:** Render the tip when it exists. Additive — no existing UI is removed.

```tsx
{result.study_tip && (
  <div className="mt-3 p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
    <p className="text-xs text-purple-300/80 font-medium mb-1">Study tip</p>
    <p className="text-sm text-white/70">{result.study_tip}</p>
  </div>
)}
```

---

### 2.8 Mode tab active state — minor visual fix

**File:** mode tab bar component.

**Problem:** From the screenshot, the active mode tab (e.g. "Simple") uses a solid purple fill that is visually heavy compared to the rest of the dark UI.

**Fix:** Replace solid fill with a tinted border-highlight style that matches the rest of the app's treatment of active states.

```tsx
// Replace active tab className with:
const tabClass = (active: boolean) =>
  active
    ? 'px-4 py-1.5 rounded-full text-sm text-purple-300 bg-purple-500/15 border border-purple-500/35 cursor-pointer'
    : 'px-4 py-1.5 rounded-full text-sm text-white/40 border border-transparent hover:text-white/60 cursor-pointer transition-colors';
```

---

## 3. Backend — minor additions to `routes/`

These are small additive changes that improve the data returned to the frontend without breaking existing consumers.

### 3.1 Return session file name in session list

**File:** `routes/sessions.py` or wherever `GET /api/sessions` is handled.

**Problem:** The sidebar shows session IDs or truncated filenames. It is unclear what material each session covers.

**Fix:** Ensure the session metadata stored in `routes/store.py` includes `original_filename` when a file is uploaded, and that `GET /api/sessions` returns it. If it already does, no change needed.

```python
# In routes/upload.py, when storing session metadata, ensure:
store[session_id] = {
    "session_id": session_id,
    "filename": original_filename,   # already present — verify this key name
    "created_at": datetime.utcnow().isoformat(),
    "text": full_text,
}
```

### 3.2 Propagate `study_tip` from grading response

**File:** `routes/quiz.py` — the `POST /api/quiz/grade` route.

**Problem:** The updated `GRADING_PROMPT` now returns a `study_tip` field. Make sure the route passes the full parsed JSON back to the client without stripping unknown keys.

**Fix:** Verify the grading route returns the full dict from `llm/generator.py` without filtering. If it currently does `return jsonify({"score": result["score"], "feedback": result["feedback"]})`, change it to:

```python
return jsonify(result)  # return the full parsed dict
```

---

## 4. Compatibility checklist

Before submitting changes, verify:

- [ ] `agents/prompts.py` — all four system prompts still end with `+ CHAT_FORMAT_RULES`. No prompt is missing the append.
- [ ] `FLASHCARD_GENERATION_PROMPT` — `hint` field added. Flashcard component handles `card.hint` being `undefined` gracefully (it will be on old cached data).
- [ ] `QUIZ_MCQ_PROMPT` — `difficulty` field added. Quiz component handles `question.difficulty` being `undefined` gracefully.
- [ ] `NOTES_PROMPT` — `importance` field added. Notes component handles `note.importance` being `undefined` gracefully (falls back to `low` style).
- [ ] `GRADING_PROMPT` — `study_tip` field added. Grading UI handles `result.study_tip` being `undefined` (renders nothing).
- [ ] `ReactMarkdown` `components` prop — does not conflict with any existing `className` on the markdown wrapper div.
- [ ] Chat avatar rows — `flex-row-reverse` on user messages. Confirm no existing CSS sets `direction: rtl` or conflicting flex on the parent.
- [ ] Mode tab class change — confirm the tab onClick handler and state management are untouched. Only the className string changes.
- [ ] No API routes are renamed. No Python files are moved. No `store.py` data shape changes — only additions.

---

## 5. What is intentionally not changed

- The RAG workflow in `agents/rag_workflow.py` — no changes.
- The FAISS retrieval path in `retrieval/vector_store.py` — no changes.
- The streaming SSE implementation in `GET /api/chat` — no changes.
- The YouTube loader or file loaders — no changes.
- The knowledge graph generation and `react-force-graph-2d` component — no changes.
- The Flask CORS config — no changes.
- `frontend/src/lib/api.ts` — no changes.
- The overall page layout (sidebar, right panel, tab navigation) — no changes.
