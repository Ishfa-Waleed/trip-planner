import os
from pathlib import Path

from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Send

from langchain_google_genai import ChatGoogleGenerativeAI

from state import TripState
from schemas import TripPlan
from tools import search_attractions, search_food, search_transport

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# =====================================================
# GEMINI
# =====================================================

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "Missing API key. Create a `.env` file in the project root with:\n"
        "GOOGLE_API_KEY=your-key-here\n"
        "Get a free key at: https://aistudio.google.com/apikey"
    )

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.5
)

structured_llm = llm.with_structured_output(TripPlan)

# =====================================================
# NODE 1 — COLLECT
# =====================================================

def collect_preferences(state: TripState):
    return state

# =====================================================
# PARALLEL RESEARCH — 3 nodes run simultaneously
# =====================================================

def fan_out_parallel_research(state: TripState):
    return [
        Send("research_attractions", state),
        Send("research_food", state),
        Send("research_transport", state),
    ]


def research_attractions(state: TripState):
    result = search_attractions.invoke({"destination": state["destination"]})
    return {"research_parts": [f"[ATTRACTIONS]\n{result}"]}


def research_food(state: TripState):
    result = search_food.invoke({"destination": state["destination"]})
    return {"research_parts": [f"[FOOD & DINING]\n{result}"]}


def research_transport(state: TripState):
    result = search_transport.invoke({"destination": state["destination"]})
    return {"research_parts": [f"[TRANSPORT & LOGISTICS]\n{result}"]}


def merge_research(state: TripState):
    parts = state.get("research_parts", [])
    return {"research": "\n\n".join(parts)}

# =====================================================
# NODE — GENERATE
# =====================================================

def generate_itinerary(state: TripState):

    prompt = f"""
    You are an expert travel planner.

    Destination: {state["destination"]}
    Days: {state["days"]}
    Budget: {state["budget"]} PKR
    Travel Style: {state["travel_style"]}

    Research Info (from parallel web searches):
    {state["research"]}

    Create a detailed day-wise itinerary using this exact format for each day:

    Day 1: [Short title]
    Morning: [activities and places]
    Afternoon: [activities and places]
    Evening: [activities and places]
    Accommodation: [where to stay]

    Day 2: [Short title]
    Morning: ...
    (continue for all {state["days"]} days)

    Use clear section headings (Morning, Afternoon, Evening, etc.) followed by descriptions.
    """

    result = structured_llm.invoke(prompt)

    return {
        "itinerary": result.itinerary
    }

# =====================================================
# NODE — REVIEW (ITERATIVE)
# =====================================================

def review_itinerary(state: TripState):

    itinerary = state["itinerary"]

    score = 0

    if len(itinerary) > 200:
        score += 5

    if "Day 1" in itinerary:
        score += 3

    if state["destination"].lower() in itinerary.lower():
        score += 2

    approved = score >= 6

    return {
        "approved": approved,
        "review_score": score
    }

# =====================================================
# NODE — IMPROVE (ITERATIVE LOOP)
# =====================================================

def improve_itinerary(state: TripState):

    prompt = f"""
    Improve this itinerary:

    - Use clear day headings: Day 1: [title], Day 2: [title], etc.
    - Under each day, use section headings with descriptions:
      Morning: [details]
      Afternoon: [details]
      Evening: [details]
      Accommodation: [details]
    - Improve travel flow and add missing details

    {state["itinerary"]}
    """

    response = llm.invoke(prompt)

    return {
        "itinerary": response.content,
        "improvement_count": state.get("improvement_count", 0) + 1,
    }

# =====================================================
# ROUTING — ITERATIVE
# =====================================================

def route_decision(state: TripState):

    if state.get("approved"):
        return "approved"

    if state.get("review_score", 0) < 6 and state.get("improvement_count", 0) < 1:
        return "improve"

    return "approved"

# =====================================================
# GRAPH — Parallel research + Iterative improve loop
# =====================================================

builder = StateGraph(TripState)

builder.add_node("collect_preferences", collect_preferences)
builder.add_node("research_attractions", research_attractions)
builder.add_node("research_food", research_food)
builder.add_node("research_transport", research_transport)
builder.add_node("merge_research", merge_research)
builder.add_node("generate_itinerary", generate_itinerary)
builder.add_node("review_itinerary", review_itinerary)
builder.add_node("improve_itinerary", improve_itinerary)

builder.set_entry_point("collect_preferences")

# Parallel fan-out: 3 research nodes run at the same time
builder.add_conditional_edges(
    "collect_preferences",
    fan_out_parallel_research,
    ["research_attractions", "research_food", "research_transport"],
)

# Merge parallel results into one research string
builder.add_edge("research_attractions", "merge_research")
builder.add_edge("research_food", "merge_research")
builder.add_edge("research_transport", "merge_research")

builder.add_edge("merge_research", "generate_itinerary")
builder.add_edge("generate_itinerary", "review_itinerary")

builder.add_conditional_edges(
    "review_itinerary",
    route_decision,
    {
        "approved": END,
        "improve": "improve_itinerary",
    },
)

builder.add_edge("improve_itinerary", "review_itinerary")

memory = MemorySaver()

graph = builder.compile(checkpointer=memory)
