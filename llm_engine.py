import os
from dotenv import load_dotenv
from groq import Groq

# TEAM 651 CONFIGURATION

load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.1-8b-instant"

def generate_pharmacist_response(user_query, retrieval_results, user_profile):
    if "gsk_" not in GROQ_API_KEY and "GROQ_API_KEY" not in os.environ:
        return "⚠️ **System Error:** Agent Brain disconnected (No API Key)."

    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        return f"Error initializing Groq client: {e}"

    # 1. Construct Context 
    context_text = ""

    if isinstance(retrieval_results, list):
        # List of points (likely from the Evaluator Agent's safe_drugs list)
        points_to_process = retrieval_results
    elif hasattr(retrieval_results, 'points'):
        # Qdrant QueryResponse object
        points_to_process = retrieval_results.points
    else:
        points_to_process = []

    for doc in points_to_process:
        payload = doc.payload
        context_text += f"""
        ---
        Drug Name: {payload.get('drug_name', 'Unknown')}
        Treats Condition: {payload.get('condition', 'Unknown')}
        Safety Category: {payload.get('pregnancy_category', 'Unknown')}
        Side Effects: {payload.get('side_effects', 'Unknown')}
        ---
        """


    # 2. The "Smart" Prompt with Counter-Factual Logic
    system_prompt = f"""
    You are SafeMeds AI (Team 651), a clinical decision support agent.
    
    USER CONTEXT:
    - Pregnancy Status: { 'YES (High Risk)' if user_profile['pregnancy_risk'] else 'No' }
    - Rx Preference: { 'Prescription Only' if not user_profile['prescription_only_ok'] else 'Any' }
    
    CRITICAL INSTRUCTION: "The Counter-Factual Safety Check"
    If you find a drug that matches the user's condition PERFECTLY but is blocked by Safety Rules (e.g. Accutane for Acne, but user is Pregnant):
    1. DO NOT recommend it.
    2. EXPLICITLY state: "I identified a standard treatment ([Drug Name]), but I have intervened to block it due to [Safety Constraint]."
    3. Suggest a safe alternative if available.
    
    STANDARD RULES:
    1. Match Name or Condition.
    2. Be concise.
    
    OUTPUT FORMAT:
    "**Clinical Decision:** [Approved/Intervention]
     **Recommendation:** [Drug Name or 'None']
     **Reasoning:** [Explain the safety logic]
     **Safety Note:** [Warnings]"
    """

    user_message = f"User Query: {user_query}\n\nAvailable Drug Data:\n{context_text}"

    # 3. Call LLM
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model=LLM_MODEL,
            temperature=0.1, 
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error connecting to Brain: {str(e)}"
    




def analyze_intent(query):
    """
    Classifies user query into: SEARCH_DRUGS, CLARIFY_SYMPTOMS, or EMERGENCY_ALERT.
    """
    if "gsk_" not in GROQ_API_KEY:
        # Fail-safe: If API key is missing, default to search to avoid blocking user
        return "SEARCH_DRUGS"

    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""
You are a strict medical intent classifier.

You MUST return exactly ONE label:

EMERGENCY_ALERT
SEARCH_DRUGS
BLOCK_ADVERSARIAL
CLARIFY_SYMPTOMS

━━━━━━━━━━ ABSOLUTE RULE ━━━━━━━━━━

If the input contains ANY real symptom word — even ONE word — it is SEARCH_DRUGS.
Never treat symptoms as vague.

Symptoms include (but are not limited to):
cough, fever, headache, pain, nausea, vomiting, cold, flu, acne, rash, swelling, infection,
sore throat, dizziness, fatigue, weakness, stomach ache, diarrhea, allergy, itching

━━━━━━━━━━ EMERGENCY RULE ━━━━━━━━━━

Return EMERGENCY_ALERT if input mentions:
• breathing trouble
• chest pain
• unconsciousness
• severe bleeding
• serious allergic reaction
• life-threatening language

Emergency ALWAYS overrides symptom rule.

━━━━━━━━━━ ADVERSARIAL RULE ━━━━━━━━━━

Return BLOCK_ADVERSARIAL ONLY if:
No symptom, no body part, no condition is mentioned at all and the user intent is clearly about seeking drugs or harmful information.

Examples of Adversarial/Drug-Seeking:
"Give me any drug", 
"I want pills", 
"Recommend something strong", 
"I need a high".
Lazy/Vague Requests for Meds: "Just prescribe me something", "Give me medicine" (without symptoms).
Harmful: "How to overdose", "How to make drugs".

━━━━━━━━━━ VAGUE RULE ━━━━━━━━━━

Return CLARIFY_SYMPTOMS ONLY if:
No symptom, no body part, no condition is mentioned at all.

Examples of vague:
"I feel bad"
"I am sick"
"Something is wrong"
"My body feels off"

━━━━━━━━━━ FINAL PRIORITY ━━━━━━━━━━

1. Emergency  
2. Any symptom → SEARCH_DRUGS  
3. Otherwise → CLARIFY_SYMPTOMS  

━━━━━━━━━━ OUTPUT ━━━━━━━━━━

Return ONLY:
EMERGENCY_ALERT
SEARCH_DRUGS
CLARIFY_SYMPTOMS
BLOCK_ADVERSARIAL

User input:
"{query}"
"""

    
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.0 
        )
        return completion.choices[0].message.content.strip()
    except:
        return "SEARCH_DRUGS"
    


def transcribe_audio(audio_file_obj):
    """
    Uses Groq's Whisper model to transcribe voice to text.
    """
    if "gsk_" not in GROQ_API_KEY and "GROQ_API_KEY" not in os.environ:
        return None, "⚠️ API Key missing."

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        transcription = client.audio.transcriptions.create(
            file=(audio_file_obj.name, audio_file_obj.read()),
            model="whisper-large-v3", # Extremely fast
            response_format="json",
            temperature=0.0
        )
        return transcription.text, None
    except Exception as e:
        return None, f"Transcription Error: {str(e)}"
    



    
