from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

print("🔄 Loading TinyLlama model from Hugging Face...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)
print("✅ TinyLlama loaded successfully!")

def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=128)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
