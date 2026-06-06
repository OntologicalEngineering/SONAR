import os
import operator
import json
import numpy as np
import warnings
from datetime import datetime
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings 
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# --- 1. SETUP & CONFIGURATION ---
load_dotenv()
warnings.filterwarnings("ignore") 

# Protocol Parameters
MAX_CYCLES = 6                    # <--- CHANGED TO 6 FOR EFFICIENCY
RUPTURE_THRESHOLD = 0.10          # The Stasis Threshold (tau)
LOG_FILE = "sonar_journal_data.json"

# Global Tracker (Will be reset automatically on Cycle 1)
cumulative_divergence = 0.0

# --- 2. INITIALIZATION ---
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small") 
seed_text = "Develop a viable political strategy to break the two-party duopoly in the United States and establish a sustainable multi-party system."

try:
    search = TavilySearchResults(k=2) 
except:
    search = None

# --- 3. STATE DEFINITION ---
class SonarState(TypedDict):
    cycle_count: int
    current_thought: str
    vector_history: Annotated[List[List[float]], operator.add] 
    synod_c_output: str 
    status: str 
    mode: str # 'FULL' = With Rupture, 'ABLATED' = Control Group

# --- 4. THE AGENTS ---

def run_synods(state: SonarState):
    """Generates the dialectic tension."""
    prompt = f"Provide two views (Establishment vs Disruptor) on this synthesis: {state['current_thought']}"
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"synod_c_output": response.content} 

def run_synod_realist(state: SonarState):
    """The Friction Agent: Adversarial critique."""
    prompt = f"SEED GOAL: {seed_text}\nCURRENT: {state['current_thought']}\nTASK: Act as a Realist Lawyer. CRUSH THE SYNTHESIS."
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # CONSOLE: Truncated for readability
    print("\n" + "="*30 + " [ REALIST FRICTION ] " + "="*30)
    print(f"{response.content[:200]}...") 
    
    # STATE: Full content is preserved
    return {"synod_c_output": response.content}

def run_diplomat(state: SonarState):
    """The Synthesis Agent: Resolution."""
    prompt = f"Synthesize a 'Third Way'. Obey the Realist. SEED: {seed_text} | FRICTION: {state['synod_c_output']}"
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # CONSOLE: Truncated for readability
    print("\n" + "-"*30 + " [ DIPLOMAT SYNTHESIS ] " + "-"*30)
    print(f"{response.content[:200]}...") 
    
    return {"status": "LOOPING", "current_thought": response.content}

def run_rupture(state: SonarState):
    """The Entropy Injection Node (Only active in FULL mode)."""
    query = f"Unique institutional failures of: {state['current_thought'][:100]}"
    friction_data = "External search offline."
    
    if search:
        try:
            print(f"\n[!] RUPTURE AGENT ENGAGED: Pinging Tavily (Cycle {state['cycle_count']})...")
            friction_data = search.run(query) 
            print(f">>> [TAVILY DATA]: {str(friction_data)[:200]}...")
        except:
            pass

    prompt = f"""
    [CRITICAL RUPTURE] Stasis reached. SEED: {seed_text}
    NEW EXTERNAL FRICTION: {friction_data}
    MANDATE: Pivot immediately. Abandon previous logic.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    
    print("\n" + "!"*30 + " [ RUPTURE PIVOT ] " + "!"*30)
    return {"current_thought": response.content, "status": "LOOPING"}

# --- 5. METRICS & CONTROL LOGIC ---

def calculate_sonar_metrics(state: SonarState):
    global cumulative_divergence
    cycle = state['cycle_count'] + 1
    new_emb = embedding_model.embed_query(state['current_thought'])
    
    # --- BUG FIX: AUTO-RESET ON CYCLE 1 ---
    # This prevents the "Infinite Accumulator" error in batch runs.
    if cycle == 1:
        cumulative_divergence = 0.0

    divergence = 1.0 
    if state['vector_history']:
        similarity = cosine_similarity([new_emb], [state['vector_history'][-1]])[0][0]
        divergence = 1.0 - similarity 
    
    cumulative_divergence += divergence
    
    # Detect Status
    status = "LOOPING"
    if cycle >= MAX_CYCLES: 
        status = "GREEN_LANE"
    elif divergence < RUPTURE_THRESHOLD:
        # If mode is 'ABLATED', we IGNORE the low divergence (Control Group)
        if state.get("mode") == "ABLATED":
            status = "LOOPING" 
        else:
            status = "RUPTURE_TRIGGERED"

    print(f"\n>>> CYCLE {cycle} METRICS: Do = {divergence:.4f} | Cumulative = {cumulative_divergence:.4f}")

    # JOURNAL LOGGING
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": state.get("mode", "FULL"),
        "cycle": cycle,
        "ontological_divergence": float(divergence),
        "cumulative_divergence": float(cumulative_divergence),
        "status": status,
        "full_thought": state['current_thought'] 
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {"cycle_count": cycle, "vector_history": [new_emb], "status": status}

# --- 6. THE GRAPH ---
workflow = StateGraph(SonarState)
workflow.add_node("synods", run_synods)
workflow.add_node("realist", run_synod_realist)
workflow.add_node("diplomat", run_diplomat)
workflow.add_node("metrics", calculate_sonar_metrics)
workflow.add_node("rupture", run_rupture)

workflow.set_entry_point("synods")
workflow.add_edge("synods", "realist")
workflow.add_edge("realist", "diplomat")
workflow.add_edge("diplomat", "metrics")

def route_sonar(state):
    if state["status"] == "GREEN_LANE": return END
    if state["status"] == "RUPTURE_TRIGGERED": return "rupture"
    return "synods"

workflow.add_conditional_edges("metrics", route_sonar)
workflow.add_edge("rupture", "synods")
sonar_engine = workflow.compile()

# --- 7. EXECUTION (If run directly) ---
if __name__ == "__main__":
    if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
    
    print(f"\n" + "#"*50 + "\n### SONAR ENGINE: DIRECT EXECUTION (N=1) ###\n" + "#"*50 + "\n")
    
    initial_state = {
        "cycle_count": 0, 
        "current_thought": seed_text, 
        "vector_history": [], 
        "synod_c_output": "", 
        "status": "START",
        "mode": "FULL" 
    }
    
    sonar_engine.invoke(initial_state, config={"recursion_limit": 100})
    print(f"\n>>> Run Complete. Full Data Logged in: {LOG_FILE}")
