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
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# --- 1. SETUP & CONFIG ---
load_dotenv()
warnings.filterwarnings("ignore") 

MAX_CYCLES = 10                  
RUPTURE_THRESHOLD = 0.10  
LOG_FILE = "sonar_ablation_results.json" 

# State Tracking
cumulative_divergence = 0.0

# --- 2. INITIALIZATION ---
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small") 
seed_text = "Develop a viable political strategy to break the two-party duopoly in the United States and establish a sustainable multi-party system."

# --- 3. THE STATE ---
class SonarState(TypedDict):
    cycle_count: int
    current_thought: str
    vector_history: Annotated[List[List[float]], operator.add] 
    synod_c_output: str 
    status: str 

# --- 4. THE AGENTS ---

def run_synods(state: SonarState):
    prompt = f"Provide two views (Establishment vs Disruptor) on this synthesis: {state['current_thought']}"
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"synod_c_output": response.content} 

def run_synod_realist(state: SonarState):
    prompt = f"SEED GOAL: {seed_text}\nCURRENT: {state['current_thought']}\nTASK: Act as a Realist Lawyer. CRUSH THE SYNTHESIS."
    response = llm.invoke([HumanMessage(content=prompt)])
    print("\n" + "="*30 + " [ REALIST FRICTION ] " + "="*30)
    print(f"{response.content[:200]}...") 
    return {"synod_c_output": response.content}

def run_diplomat(state: SonarState):
    prompt = f"Synthesize a 'Third Way'. Obey the Realist. SEED: {seed_text} | FRICTION: {state['synod_c_output']}"
    response = llm.invoke([HumanMessage(content=prompt)])
    print("\n" + "-"*30 + " [ DIPLOMAT SYNTHESIS ] " + "-"*30)
    print(f"{response.content[:200]}...") 
    return {"status": "LOOPING", "current_thought": response.content}

# --- 5. THE METRICS (FIXED FOR JSON SERIALIZATION) ---

def calculate_sonar_metrics(state: SonarState):
    global cumulative_divergence
    cycle = state['cycle_count'] + 1
    new_emb = embedding_model.embed_query(state['current_thought'])
    
    divergence = 1.0 
    if state['vector_history']:
        similarity = cosine_similarity([new_emb], [state['vector_history'][-1]])[0][0]
        divergence = 1.0 - similarity 
    
    cumulative_divergence += divergence
    print(f"\n>>> [CONTROL] CYCLE {cycle} METRICS: Do = {divergence:.4f} | Cumulative = {cumulative_divergence:.4f}")

    status = "LOOPING"
    if cycle >= MAX_CYCLES: 
        status = "GREEN_LANE"
    
    # FIX: Explicitly cast to bool and float to ensure JSON compatibility
    would_rupture = bool(divergence < RUPTURE_THRESHOLD)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": "ABLATED_CONTROL",
        "cycle": int(cycle),
        "ontological_divergence": float(divergence),
        "cumulative_divergence": float(cumulative_divergence),
        "would_have_ruptured": would_rupture,
        "status": str(status)
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

workflow.set_entry_point("synods")
workflow.add_edge("synods", "realist")
workflow.add_edge("realist", "diplomat")
workflow.add_edge("diplomat", "metrics")

def route_ablated(state):
    if state["status"] == "GREEN_LANE": return END
    return "synods" 

workflow.add_conditional_edges("metrics", route_ablated)
sonar_control_engine = workflow.compile()

# --- 7. EXECUTION ---
if __name__ == "__main__":
    if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
    print(f"\n" + "#"*50 + "\n### SONAR ABLATION: CONTROL GROUP RUN ###\n" + "#"*50 + "\n")
    
    initial_state = {
        "cycle_count": 0, 
        "current_thought": seed_text, 
        "vector_history": [], 
        "synod_c_output": "", 
        "status": "START"
    }
    
    sonar_control_engine.invoke(initial_state, config={"recursion_limit": 100})
    print(f"\n>>> Control Run Complete. Data captured in: {LOG_FILE}")
