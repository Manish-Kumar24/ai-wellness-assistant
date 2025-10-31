from app.utils.genai_service import generate_health_response

response = generate_health_response("What is diabetes?")
print("✅ GenAI Response:\n", response)