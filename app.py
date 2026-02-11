import streamlit as st
import time
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, FieldCondition, MatchValue
from llm_engine import generate_pharmacist_response,transcribe_audio,analyze_intent

# --- 1. SETUP & ANONYMITY (Team 651) ---
st.set_page_config(
    page_title="Team 651 - SafeMeds", 
    page_icon="💊",
    layout="wide"
)

# Initialize Backend
@st.cache_resource
def get_qdrant_client():
    return QdrantClient(path="qdrant_db")

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

try:
    client = get_qdrant_client()
    model = get_embedding_model()
except Exception as e:
    st.error(f"System Error: {e}")
    st.stop()

COLLECTION_NAME = "drugs_knowledge_base"

# --- 2. SESSION STATE (MEMORY) ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"pregnancy_risk": False, "prescription_only_ok": True}

# --- 3. SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.header("🧠 Patient Context Memory")
    st.info("Constraints persist across the entire session.")
    
    # Critical Safety Toggle
    is_pregnant = st.toggle("⚠️ Patient is Pregnant", value=st.session_state.user_profile["pregnancy_risk"])
    if is_pregnant != st.session_state.user_profile["pregnancy_risk"]:
        st.session_state.user_profile["pregnancy_risk"] = is_pregnant
        st.rerun()

    # Rx Preference
    rx_mode = st.radio("Access Level", ["All (Rx + OTC)", "OTC Only"])
    st.session_state.user_profile["prescription_only_ok"] = (rx_mode == "All (Rx + OTC)")

    st.divider()
    
    # Status Indicators
    if st.session_state.user_profile["pregnancy_risk"]:
        st.error("🛡️ PREGNANCY PROTOCOL: ACTIVE\nBlocking FDA Category D/X")
    else:
        st.success("✅ Standard Protocol Active")
    
    st.divider()
    dev_mode = st.checkbox("🛠️ Developer Mode (Show Agent Internals)")

# --- 4. AGENT DEFINITIONS (The Orchestration Layer) ---

def agent_planner(query):
    """
    Role: Triage Nurse. Analyzes intent and delegates to tools.
    """
    with st.chat_message("planner", avatar="🧠"):
        st.write(f"**Planner Agent:** Analyzing clinical query: *'{query}'*")
        
        # Call the Intent Brain
        intent = analyze_intent(query)
        time.sleep(0.3) 
        
        if "EMERGENCY" in intent:
            st.error("🚨 **CRITICAL ALERT:** Emergency Intent Detected.")
            st.markdown("""
            **Planner Decision:** BYPASS RETRIEVAL.
            *Action:* Advise immediate medical attention. 
            
            **Please call Emergency Services (911/112) immediately.**
            Do not rely on AI for life-threatening situations.
            """)
            return False 
            
        elif "BLOCK_ADVERSARIAL" in intent:
            st.error("⛔ **Planner Alert:** Security Intervention.")
            st.markdown("""
             **Planner Decision:** REQUEST BLOCKED.
             *Reasoning:* The request appears to be 'Drug Seeking Behavior' or lacks clinical specificity.
             *Action:* Refusal to dispense without specific symptoms.
             """)
            return False
            
        elif "CLARIFY" in intent:
            st.warning("⚠️ **Planner Alert:** Vague Symptoms.")
            st.markdown(f"""
            **Planner Decision:** HALT RETRIEVAL.
            *Reasoning:* Input '{query}' is too insufficient for a safe recommendation.
            
            **Action:** Please describe your specific symptoms (e.g., "I have a throbbing headache" or "Sharp stomach pain").
            """)
            return False 
        
        else:
            # The Standard Path
            st.caption("Step 1: Intent Recognition -> Valid Clinical Query")
            st.caption("Step 2: Tool Selection -> 'Qdrant Vector Store'")
            st.write("**Decision:** Delegate to Retriever Agent.")
            return True 
        
def agent_retriever(query, filters):
    """
    Role: Pharmacist. Uses the Qdrant Tool to fetch data.
    """
    with st.chat_message("retriever", avatar="🔎"):
        st.write("**Retriever Agent:** Activating 'Vector Search' Tool...")
        
        
        query_vector = model.encode(query).tolist()
        
        
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=filters,
            limit=4
        )
        
        if results:
            st.success(f"**Tool Output:** Retrieved {len(results.points)} context chunks.")
            if dev_mode:
                with st.expander("🔧 Inspect Vector Payloads"):
                    for hit in results.points:
                        st.json(hit.payload)
                        st.caption(f"Score: {hit.score}")
            else:
                with st.expander("📄 View Retrieved Context"):
                    for hit in results.points:
                        st.markdown(f"- **{hit.payload['drug_name']}** (Cat: {hit.payload['pregnancy_category']})")
        else:
            st.error("**Tool Output:** No vectors found satisfying safety constraints.")
            
    return results

def agent_evaluator(user_profile, results):
    """
    Role: Safety Officer. Critiques the result before showing it.
    """
    with st.chat_message("evaluator", avatar="🛡️"):
        st.write("**Evaluator Agent:** Validating retrieved context against Patient Memory...")
        time.sleep(0.3)
        
        # 1. Check Pregnancy Constraint
        if user_profile["pregnancy_risk"]:
            st.warning("⚠️ Critical Constraint: Patient is Pregnant.")
            
            # Active Decision: Filter the results manually to show "Reasoning"
            safe_drugs = []
            for hit in results.points:
                cat = hit.payload.get('pregnancy_category', 'N')
                # Strict B or N only
                if cat in ['B', 'N', 'A']:
                    safe_drugs.append(hit)
                else:
                    if dev_mode: st.error(f"Blocking {hit.payload['drug_name']} (Category {cat})")
            
            if not safe_drugs:
                st.error("❌ Evaluation: All candidates rejected due to Teratogenic Risk.")
                return None
            else:
                st.success(f"✅ Evaluation: {len(safe_drugs)} candidates approved for Synthesis.")
                return safe_drugs
        
        # 2. Standard Case
        else:
            st.info("✅ Evaluation: Standard safety checks passed.")
            return results

# --- 5. MAIN INTERFACE ---
st.title("SafeMeds AI")
st.caption("Multi-Agent Clinical Decision Support System | Team ID: 651")


# --- MULTIMODAL INPUT (Voice + Text) ---
col_mic, col_text = st.columns([1, 4])

with col_mic:
    st.write("🎙️ **Voice Input**")
    audio_val = st.audio_input("Record", label_visibility="collapsed")


default_query = ""
if audio_val:
    with st.spinner("Transcribing voice..."):
        text, error = transcribe_audio(audio_val)
        if text:
            default_query = text
            st.success("Voice Captured!")
        else:
            st.error(error)


with col_text:
    st.write("📝 **Clinical Query**")
    query = st.text_input(
        "Enter symptoms:", 
        value=default_query, 
        placeholder="e.g., 'I have a migraine and I am pregnant'", 
        label_visibility="collapsed"
    )

if st.button("Initialize Multi-Agent Workflow", type="primary") and query:
    st.divider()
    
    # --- PHASE 1: PLAN ---
    if agent_planner(query):
        
        
        filter_conditions = []
        if st.session_state.user_profile["pregnancy_risk"]:
            filter_conditions.append(FieldCondition(key="pregnancy_category", match=MatchValue(value="B")))
        if not st.session_state.user_profile["prescription_only_ok"]:
             filter_conditions.append(FieldCondition(key="rx_otc", match=MatchValue(value="Rx/OTC")))
        search_filter = Filter(must=filter_conditions) if filter_conditions else None

        # --- PHASE 2: RETRIEVE ---
        raw_results = agent_retriever(query, search_filter)
        
        # --- PHASE 3: EVALUATE ---
        if raw_results:
            validated_results = agent_evaluator(st.session_state.user_profile, raw_results)
            
            # --- PHASE 4: SYNTHESIZE (LLM) ---
            if validated_results:
                st.divider()
                st.subheader("💡 Final Agent Response")
                with st.spinner("Synthesizing clinical advice..."):
                    response = generate_pharmacist_response(query, validated_results, st.session_state.user_profile)
                    st.markdown(response)
            else:
                 st.error("🛑 AGENT INTERVENTION: Response blocked by Evaluator for Patient Safety.")