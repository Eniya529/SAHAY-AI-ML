import joblib

MODEL_PATH = "model/risk_model.pkl"

# Load trained model
model = joblib.load(MODEL_PATH)

print("SAHAY Risk Prediction System")
print("--------------------------------")

while True:
    message = input("\nEnter victim message (or type 'exit'): ")

    if message.lower() == "exit":
        print("Exiting...")
        break

    if not message.strip():
        print("Please enter a message.")
        continue

    # Predict risk
    prediction = model.predict([message])[0]

    # Get confidence
    probabilities = model.predict_proba([message])[0]
    confidence = max(probabilities)

    print(f"\nRisk Level : {prediction}")
    print(f"Confidence : {confidence:.2f}")