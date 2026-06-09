# LangGraph Workflow Types — Flowcharts

---

## 1️⃣ Sequential Workflow

```
┌─────────────────────────────────────────────────────┐
│              SEQUENTIAL WORKFLOW                    │
│         (Fixed order, one after another)            │
└─────────────────────────────────────────────────────┘

   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌─────┐
   │  Node A  │────▶│  Node B  │────▶│  Node C  │────▶│ END │
   │  Draft   │     │  Review  │     │ Finalise │     └─────┘
   └──────────┘     └──────────┘     └──────────┘

   ● Every node runs in fixed order
   ● No branching, no looping
   ● Output of one becomes input of next
```

---

## 2️⃣ Parallel Workflow

```
┌─────────────────────────────────────────────────────┐
│               PARALLEL WORKFLOW                     │
│       (Multiple nodes run simultaneously)           │
└─────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │  Start Node  │
                    └──────┬───────┘
                           │  fan-out
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     ┌────────────┐ ┌────────────┐ ┌────────────┐
     │  Node A    │ │  Node B    │ │  Node C    │
     │ Evaluate 1 │ │ Evaluate 2 │ │ Evaluate 3 │
     └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
           │              │              │
           └──────────────┼──────────────┘
                          │  merge
                    ┌─────▼──────┐
                    │ Merge Node │
                    └─────┬──────┘
                          ▼
                        ┌─────┐
                        │ END │
                        └─────┘

   ● All 3 nodes run at the SAME TIME
   ● Results merged into one state
   ● Faster than sequential
```

---

## 3️⃣ Conditional Workflow

```
┌─────────────────────────────────────────────────────┐
│             CONDITIONAL WORKFLOW                    │
│     (Routes differently based on state/decision)   │
└─────────────────────────────────────────────────────┘

                 ┌──────────────┐
                 │  Classify    │
                 │    Node      │
                 └──────┬───────┘
                        │
              conditional edge
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   ┌────────────┐ ┌───────────┐ ┌───────────┐
   │ Specialist │ │Specialist │ │Specialist │
   │    A       │ │    B      │ │    C      │
   └─────┬──────┘ └─────┬─────┘ └─────┬─────┘
         │              │             │
         └──────────────┼─────────────┘
                        ▼
                      ┌─────┐
                      │ END │
                      └─────┘

   ● Decision made based on state value
   ● Only ONE path executes per run
   ● Different inputs → different routes
```

---

## 4️⃣ Iterative Workflow

```
┌─────────────────────────────────────────────────────┐
│              ITERATIVE WORKFLOW                     │
│      (Loops back until a condition is met)          │
└─────────────────────────────────────────────────────┘

   ┌──────────┐
   │  START   │
   └────┬─────┘
        ▼
   ┌──────────┐
   │ Generate │◀──────────────────┐
   └────┬─────┘                   │
        ▼                         │
   ┌──────────┐                   │
   │ Evaluate │                   │
   └────┬─────┘                   │
        │                         │
        │ conditional edge        │
        │                         │
   ┌────▼──────────────────┐      │
   │  score >= threshold?  │      │
   └────┬──────────────────┘      │
        │                         │
      NO│                       YES▼── ──▶ ┌─────┐
        │                                  │ END │
        ▼                                  └─────┘
   ┌──────────┐
   │ Improve  │──────────────────▶ (back to Generate/Evaluate)
   └──────────┘

   ● Loop continues until quality threshold met
   ● Max iterations prevent infinite loop
   ● Agent self-corrects
```

---

## ✅ FINAL COMBINED CHART — TripPlanner AI Agent
### (This Project — Uses BOTH Parallel + Iterative)

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRIPPLANNER AI AGENT                         │
│              LangGraph — Parallel + Iterative                   │
└─────────────────────────────────────────────────────────────────┘

         ┌──────────────────────────┐
         │      START               │
         │  (User enters trip       │
         │   preferences)           │
         └────────────┬─────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   collect_preferences  │  Node 1
         │  destination, days,    │  (Sequential)
         │  budget, travel_style  │
         └────────────┬───────────┘
                      │
                      │  fan_out_parallel_research()
                      │  [Send to 3 nodes simultaneously]
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  research_   │ │ research │ │  research_   │  Nodes 2,3,4
│  attractions │ │  _food   │ │  transport   │  ← PARALLEL
│              │ │          │ │              │
│ DuckDuckGo   │ │DuckDuckGo│ │ DuckDuckGo   │
│ Web Search   │ │  Search  │ │   Search     │
│   (Tool ✅)  │ │ (Tool ✅)│ │  (Tool ✅)   │
└──────┬───────┘ └────┬─────┘ └──────┬───────┘
       │              │              │
       └──────────────┼──────────────┘
                      │  (all 3 finish, results merged)
                      ▼
         ┌────────────────────────┐
         │     merge_research     │  Node 5
         │  Combines all 3        │  (Sequential)
         │  research results      │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   generate_itinerary   │  Node 6
         │  Gemini 2.5 Flash LLM  │  (Sequential)
         │  with_structured_      │
         │  output (Pydantic ✅)  │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   review_itinerary     │  Node 7
         │  Scores itinerary 0-10 │  ← ITERATIVE
         │  checks: length,       │     starts here
         │  Day 1, destination    │
         └────────────┬───────────┘
                      │
                      │  route_decision()  ← CONDITIONAL EDGE
                      │
          ┌───────────┴────────────┐
          │                        │
   score >= 6?                score < 6
   approved=True               improvement_count < 1
          │                        │
          ▼                        ▼
       ┌─────┐          ┌────────────────────────┐
       │ END │          │   improve_itinerary     │  Node 8
       └─────┘          │  Gemini re-generates   │  ← ITERATIVE
              ✅        │  better itinerary       │     LOOP
           Approved     └────────────┬────────────┘
                                     │
                                     │ (loops back)
                                     ▼
                        ┌────────────────────────┐
                        │   review_itinerary     │
                        │   (scores again)       │
                        └────────────┬───────────┘
                                     │
                              ┌──────┴──────┐
                              │             │
                         approved       still low
                              │        (max retries)
                              ▼             ▼
                           ┌─────┐       ┌─────┐
                           │ END │       │ END │
                           └─────┘       └─────┘
                        ✅ Improved   ✅ Force approved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LEGEND:
  ──▶  Sequential edge (fixed)
  ══▶  Parallel fan-out (simultaneous)
  ─?▶  Conditional edge (based on state)
  ↩️   Iterative loop (retry)

LANGGRAPH FEATURES USED:
  ✅ TypedDict State     → TripState in state.py
  ✅ 8 Nodes             → all meaningful, not just LLM calls
  ✅ Parallel (Send)     → 3 research nodes simultaneously
  ✅ Conditional Edges   → route_decision() → approved/improve
  ✅ Iterative Loop      → improve → review → loop
  ✅ Tool Use (3 tools)  → DuckDuckGo web search
  ✅ MemorySaver         → thread_id persistence
  ✅ Structured Output   → TripPlan(Pydantic) + with_structured_output
  ✅ Streamlit UI        → app.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
