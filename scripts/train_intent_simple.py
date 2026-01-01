#!/usr/bin/env python
"""
Quick intent classifier using TF-IDF + Logistic Regression
Fast training (< 1 minute on CPU), good baseline performance

For production, use train_intent_bert.py for higher accuracy
"""

import json
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import numpy as np


def load_data(filepath):
    """Load training data"""
    with open(filepath) as f:
        data = json.load(f)

    texts = [q["text"] for q in data["queries"]]
    labels = [q["intent"] for q in data["queries"]]
    return texts, labels


def train_model(train_texts, train_labels):
    """Train simple TF-IDF + Logistic Regression model"""
    print("Training intent classifier...")

    # Create pipeline
    model = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=5000,
            lowercase=True
        )),
        ('clf', LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        ))
    ])

    # Train
    model.fit(train_texts, train_labels)

    print("✓ Training complete!")
    return model


def evaluate_model(model, test_texts, test_labels):
    """Evaluate model performance"""
    predictions = model.predict(test_texts)
    accuracy = accuracy_score(test_labels, predictions)

    print(f"\n{'='*60}")
    print("Model Evaluation")
    print(f"{'='*60}")
    print(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"\nDetailed Report:")
    print(classification_report(test_labels, predictions))

    return accuracy


def main():
    """Main training function"""
    print("="*60)
    print("Training Simple Intent Classifier")
    print("="*60)

    # Load data
    print("\n1. Loading training data...")
    train_texts, train_labels = load_data("data/raw/intent_train.json")
    print(f"   ✓ Loaded {len(train_texts)} training examples")

    print("\n2. Loading validation data...")
    val_texts, val_labels = load_data("data/raw/intent_val.json")
    print(f"   ✓ Loaded {len(val_texts)} validation examples")

    print("\n3. Loading test data...")
    test_texts, test_labels = load_data("data/raw/intent_test.json")
    print(f"   ✓ Loaded {len(test_texts)} test examples")

    # Train model
    print("\n4. Training model...")
    model = train_model(train_texts, train_labels)

    # Evaluate on validation set
    print("\n5. Evaluating on validation set...")
    val_accuracy = evaluate_model(model, val_texts, val_labels)

    # Evaluate on test set
    print("\n6. Evaluating on test set...")
    test_accuracy = evaluate_model(model, test_texts, test_labels)

    # Save model
    print("\n7. Saving model...")
    model_dir = Path("data/models")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "intent_classifier_simple.pkl"
    joblib.dump(model, model_path)
    print(f"   ✓ Model saved to {model_path}")

    # Save label mapping
    unique_labels = sorted(set(train_labels))
    label_map_path = model_dir / "intent_labels.json"
    with open(label_map_path, 'w') as f:
        json.dump({"labels": unique_labels}, f, indent=2)
    print(f"   ✓ Label mapping saved to {label_map_path}")

    # Test with examples
    print("\n" + "="*60)
    print("Testing with Sample Queries")
    print("="*60)

    test_queries = [
        "I need brake pads for my 2015 Honda Civic",
        "What's my 2018 Toyota Camry worth?",
        "Paint code for my BMW",
        "Decode VIN 1HGBH41JXMN109186",
        "Check engine light P0420",
        "What oil should I use?"
    ]

    for query in test_queries:
        prediction = model.predict([query])[0]
        proba = model.predict_proba([query])[0]
        confidence = max(proba)

        print(f"\nQuery: '{query}'")
        print(f"  → Intent: {prediction}")
        print(f"  → Confidence: {confidence:.3f}")

    print("\n" + "="*60)
    print("✓ Training Complete!")
    print("="*60)
    print(f"\nFinal Metrics:")
    print(f"  Validation Accuracy: {val_accuracy:.4f}")
    print(f"  Test Accuracy: {test_accuracy:.4f}")
    print(f"\nModel saved to: {model_path}")


if __name__ == "__main__":
    main()
