import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.metrics import confusion_matrix

DATASET_PATH = "dataset/dataset.csv"

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")
print(f"Total samples: {len(df)}")

print("\nRisk level distribution:")
print(df["risk_level"].value_counts())


X = df["text"]
y = df["risk_level"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )
    ),
    (
        "classifier",
        LogisticRegression(
    max_iter=2000,
    class_weight="balanced"
)
    )
])


print("\nTraining model...")

model.fit(X_train, y_train)

print("Training completed!")


y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print(f"\nAccuracy: {accuracy:.2f}")

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    zero_division=0
))


MODEL_PATH = "model/risk_model.pkl"

joblib.dump(model, MODEL_PATH)

print(f"\nModel saved successfully at: {MODEL_PATH}")
print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    zero_division=0
))

print("\nConfusion Matrix:")
print(confusion_matrix(
    y_test,
    y_pred,
    labels=["LOW", "MODERATE", "HIGH", "CRITICAL"]
))
print("\nMisclassified MODERATE samples:")

for text, actual, predicted in zip(X_test, y_test, y_pred):
    if actual == "MODERATE" and predicted != "MODERATE":
        print(f"\nText: {text}")
        print(f"Actual: {actual}")
        print(f"Predicted: {predicted}")