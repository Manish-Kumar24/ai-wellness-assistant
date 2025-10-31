from llama_cpp import Llama
import os

# Load model once at startup
MODEL_PATH = "models/llama-2-7b-chat.Q4_K_M.gguf"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"GenAI model not found at {MODEL_PATH}")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,        # Context window
    n_threads=4,       # CPU threads
    n_gpu_layers=0,    # 0 = CPU only
    verbose=False
)

def generate_health_response(user_message: str, patient_context: str = "") -> str:
    """
    Generate a health-focused response using Llama-2.
    """
    # Build prompt with health-specific instructions
    prompt = f"""<s>[INST] <<SYS>>
You are a helpful, respectful, and honest AI Health Assistant. 
Always provide safe, general health information. Never diagnose. 
Always advise consulting a real doctor for medical concerns.
<</SYS>>

User message: {user_message}
{f"Patient context: {patient_context}" if patient_context else ""}

Provide a concise, empathetic response. [/INST]"""

    output = llm(
        prompt,
        max_tokens=256,
        stop=["</s>", "[/INST]"],
        echo=False
    )
    
    response = output["choices"][0]["text"].strip()
    return response if response else "I'm here to help with general health information. Please consult a doctor for medical advice."