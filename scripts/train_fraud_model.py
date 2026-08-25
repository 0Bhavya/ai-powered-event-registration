import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

def train_and_save_model():
    print("Generating synthetic historical registration data...")
    # Generate normal data: average time difference between registrations is e.g. 1000s
    normal_diffs = np.random.normal(loc=1000, scale=300, size=(500, 1))
    
    # Generate anomalous data: very short time differences (bot-like), e.g. 5s
    anomalous_diffs = np.random.normal(loc=5, scale=2, size=(50, 1))
    
    # Combine training data
    X_train = np.vstack([normal_diffs, anomalous_diffs])
    X_train = np.clip(X_train, 1, None) # Time diffs can't be negative
    
    print(f"Training IsolationForest on {len(X_train)} samples...")
    clf = IsolationForest(contamination=0.1, random_state=42)
    clf.fit(X_train)
    
    # Ensure the models directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'models'), exist_ok=True)
    
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'fraud_model.joblib')
    joblib.dump(clf, model_path)
    
    print(f"Model successfully saved to {model_path}")

if __name__ == "__main__":
    train_and_save_model()
