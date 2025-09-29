import os

# Define the internal structure (relative to ai-wellness-assistant/)
structure = {
    "backend": {
        "app": {
            "main.py": "",
            "api": {
                "routes_symptoms.py": "",
                "routes_cv.py": ""
            },
            "models": {},
            "services": {
                "nlp_service.py": "",
                "ml_service.py": "",
                "cv_service.py": ""
            },
            "db": {},
            "core": {}
        },
        "Dockerfile": "",
        "requirements.txt": ""
    },
    "frontend": {
        "index.html": "",
        "app.js": "",
        "styles.css": ""
    },
    "ml_training": {
        "train_symptom_model.py": "",
        "train_cv_model.py": "",
        "notebooks": {}
    },
    "faiss_index": {
        "build_index.py": "",
        "index.bin": ""
    },
    "docker-compose.yml": "",
    "README.md": ""
}

def create_structure(base_path, structure_dict):
    for name, content in structure_dict.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # Create file (even if empty)
            open(path, 'a').close()  # 'a' creates file if it doesn't exist

# Run from current directory (ai-wellness-assistant/)
create_structure(".", structure)

print("Project structure created successfully inside ai-wellness-assistant!")