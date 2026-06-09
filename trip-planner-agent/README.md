# AI Trip Planner Agent

A LangGraph-powered travel planning agent that researches destinations, generates day-wise itineraries, reviews quality, and iteratively improves low-scoring plans.

Built for the **QAU LangGraph Group Project Assignment**.

---

## Problem

Planning a trip takes time — researching attractions, matching activities to budget, and organizing a day-by-day schedule. This agent automates that workflow: you enter your destination, days, budget, and travel style, and it returns a structured itinerary backed by live web research.

---

## Workflow Types: **Parallel + Iterative**

The graph combines two course workflow patterns:

### Parallel (research phase)
Three web-search nodes run **simultaneously**, then results are merged:

```
collect_preferences ──┬── research_attractions ──┐
                      ├── research_food ───────────┼── merge_research
                      └── research_transport ──────┘
```

### Iterative (quality phase)
Generate → review → improve loop until the plan passes:

```
merge_research → generate_itinerary → review_itinerary
                                              ↓
                                    approved? ──yes──→ END
                                              ↓ no
                                    improve_itinerary ──→ (loop back)
```

1. **Collect** user preferences (destination, days, budget, style)
2. **Parallel research** — attractions, food, and transport searched at the same time
3. **Merge** all research into one summary
4. **Generate** a structured itinerary using Gemini
5. **Review** the itinerary and score it
6. If score is too low → **Improve** and loop back to review
7. If approved → finish

---

## LangGraph Features Used

| Feature | Implementation |
|---------|----------------|
| State management (TypedDict) | `state.py` — `TripState` |
| Meaningful nodes (8) | collect, 3× parallel research, merge, generate, review, improve |
| Parallel workflow | `Send` fan-out → 3 nodes run simultaneously → merge |
| Conditional edges | `route_decision()` routes to END or improve |
| Iterative loop | improve → review until approved |
| Tool use | 3 DuckDuckGo search tools (`tools.py`) |
| Memory / Persistence | `MemorySaver` with `thread_id` |
| Structured output | Pydantic `TripPlan` + `with_structured_output()` |
| Streamlit interface | `app.py` |

---

## Project Structure

```
trip-planner-agent/
├── app.py              # Streamlit UI
├── agent.py            # LangGraph agent & graph definition
├── tools.py            # Web search tool
├── schemas.py          # Pydantic models
├── state.py            # TypedDict state
├── agent.ipynb         # Jupyter notebook (graph viz + demo)
├── requirements.txt
├── flowchart/          # Agent flowchart diagram
├── slides/             # Presentation slides
└── assets/             # Graph visualization images
```

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd trip-planner-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key

Copy the example env file and add your Google Gemini API key:

```bash
copy .env.example .env        # Windows
cp .env.example .env          # macOS / Linux
```

Edit `.env`:

```
GOOGLE_API_KEY=your-actual-key-here
```

Get a free key at: https://aistudio.google.com/apikey

> **Never commit your real `.env` file.** It is listed in `.gitignore`.

---

## How to Run

### Streamlit App (main demo)

```bash
streamlit run app.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`), fill in the form, and click **Generate Trip Plan**.

### Jupyter Notebook

```bash
jupyter notebook agent.ipynb
```

Run all cells. The notebook includes a `draw_mermaid_png()` graph visualization.

---

## Demo Tips

Use two different inputs during presentation to show branching/looping:

| Input | Expected behaviour |
|-------|--------------------|
| **Skardu, 5 days, Luxury** | High review score → approved on first pass |
| **Murree, 1 day, Budget** | May trigger improve loop if score < 6 |

Check the **Review Score** and **Approved** fields in the Streamlit output.

---

## Tech Stack

- **LangGraph** — agent graph & state machine
- **LangChain + Google Gemini** — LLM (`gemini-2.5-flash`)
- **DuckDuckGo Search** — destination research tool
- **Pydantic** — structured itinerary output
- **Streamlit** — web interface

---

## Group Members

<!-- Add your names here -->
- Member 1
- Member 2
- Member 3
