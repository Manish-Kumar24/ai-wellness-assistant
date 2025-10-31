import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
import pickle

# Load dataset
df = pd.read_csv("ml_training/symptom_disease.csv")

X = df["symptoms"]
y = df["disease"]

# Convert text → numeric
vectorizer = CountVectorizer()
X_vec = vectorizer.fit_transform(X)

# Train model
model = DecisionTreeClassifier()
model.fit(X_vec, y)

# ✅ Save both vectorizer & model
with open("ml_training/symptom_model.pkl", "wb") as f:
    pickle.dump((vectorizer, model), f)
