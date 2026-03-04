"""
Career Prediction Module
- Trains ML model on student data
- Predicts suitable career domain
- Uses Logistic Regression and Random Forest
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

class CareerPredictor:
    def __init__(self, dataset_path='datasets/career_prediction_dataset.csv'):
        """
        Initialize Career Predictor with dataset path
        """
        self.dataset_path = dataset_path
        self.model = None
        self.label_encoder = LabelEncoder()
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.scaler = StandardScaler()
        self.feature_names = None
        self.accuracy = None
        
    def load_and_preprocess_data(self):
        """
        Load dataset and preprocess features
        """
        print("📥 Loading dataset...")
        df = pd.read_csv(self.dataset_path)
        
        # Display basic info
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Unique careers: {df['career_label'].nunique()}")
        
        # Handle missing values
        df = df.dropna()
        
        # --- FIXED: Parse skills safely (comma-separated string) ---
        def parse_skills(x):
            if isinstance(x, str):
                # Split by comma and strip whitespace
                skills = [s.strip() for s in x.split(',')]
                return ' '.join(skills)
            return ''
        
        df['skills_text'] = df['skills'].apply(parse_skills)
        # -----------------------------------------------------------
        
        # Combine all text features
        df['combined_text'] = df['skills_text'] + ' ' + df['interest'].fillna('')
        
        # Feature engineering
        X_text = self.vectorizer.fit_transform(df['combined_text']).toarray()
        
        # Numerical features
        numerical_features = ['cgpa', 'projects_count', 'communication_score']
        X_num = df[numerical_features].values
        
        # Categorical features (internship: Yes/No)
        df['internship_binary'] = (df['internship'] == 'Yes').astype(int)
        X_cat = df[['internship_binary']].values
        
        # Combine all features
        X = np.hstack([X_text, X_num, X_cat])
        
        # Target encoding
        y = self.label_encoder.fit_transform(df['career_label'])
        
        # Save feature names for later use
        self.feature_names = {
            'text_features': self.vectorizer.get_feature_names_out().tolist(),
            'numerical_features': numerical_features,
            'categorical_features': ['internship']
        }
        
        print(f"✅ Features prepared: {X.shape[1]} features")
        print(f"✅ Target classes: {len(self.label_encoder.classes_)}")
        
        return X, y, df
    
    def train_models(self, X, y):
        """
        Train both Logistic Regression and Random Forest models
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Initialize models
        models = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        
        results = {}
        best_model = None
        best_score = 0
        
        print("\n" + "="*50)
        print("🤖 Training Models...")
        print("="*50)
        
        for name, model in models.items():
            # Train
            model.fit(X_train_scaled, y_train)
            
            # Predict
            y_pred = model.predict(X_test_scaled)
            
            # Accuracy
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            print(f"\n📊 {name}:")
            print(f"   Test Accuracy: {accuracy:.4f}")
            print(f"   CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
            
            # Track best model
            if accuracy > best_score:
                best_score = accuracy
                best_model = model
                self.model = model
        
        print("\n" + "="*50)
        print(f"🏆 Best Model Selected with accuracy: {best_score:.4f}")
        print("="*50)
        
        self.accuracy = best_score
        return results, best_model
    
    def save_model(self, model_path='ml_models/saved_models/career_predictor.pkl'):
        """
        Save trained model and encoders
        """
        if self.model is None:
            raise ValueError("No trained model found. Train first!")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save everything in a dictionary
        model_artifacts = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'vectorizer': self.vectorizer,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'accuracy': self.accuracy
        }
        
        joblib.dump(model_artifacts, model_path)
        print(f"💾 Model saved to: {model_path}")
        
    def load_model(self, model_path='ml_models/saved_models/career_predictor.pkl'):
        """
        Load trained model and encoders
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        model_artifacts = joblib.load(model_path)
        self.model = model_artifacts['model']
        self.label_encoder = model_artifacts['label_encoder']
        self.vectorizer = model_artifacts['vectorizer']
        self.scaler = model_artifacts['scaler']
        self.feature_names = model_artifacts['feature_names']
        self.accuracy = model_artifacts.get('accuracy', None)
        
        print(f"📂 Model loaded from: {model_path}")
        if self.accuracy:
            print(f"   Model accuracy: {self.accuracy:.4f}")
    
    def predict(self, skills, cgpa, interest, internship, projects_count, communication_score):
        """
        Predict career for a single student
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Prepare input features
        skills_text = ' '.join(skills) if isinstance(skills, list) else skills
        combined_text = skills_text + ' ' + interest
        
        # Transform text
        text_features = self.vectorizer.transform([combined_text]).toarray()
        
        # Numerical features
        num_features = np.array([[cgpa, projects_count, communication_score]])
        
        # Categorical features
        internship_binary = 1 if internship.lower() == 'yes' else 0
        cat_features = np.array([[internship_binary]])
        
        # Combine all features
        X = np.hstack([text_features, num_features, cat_features])
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict
        pred_encoded = self.model.predict(X_scaled)[0]
        pred_proba = self.model.predict_proba(X_scaled)[0]
        
        # Decode
        predicted_career = self.label_encoder.inverse_transform([pred_encoded])[0]
        
        # Get top 3 predictions
        top_3_idx = np.argsort(pred_proba)[-3:][::-1]
        top_3_careers = self.label_encoder.inverse_transform(top_3_idx)
        top_3_proba = pred_proba[top_3_idx]
        
        return {
            'predicted_career': predicted_career,
            'confidence': float(pred_proba[pred_encoded]),
            'top_3_careers': [
                {'career': career, 'probability': float(prob)}
                for career, prob in zip(top_3_careers, top_3_proba)
            ],
            'all_probabilities': {
                career: float(prob) 
                for career, prob in zip(self.label_encoder.classes_, pred_proba)
            }
        }
    
    def train_pipeline(self):
        """
        Complete training pipeline
        """
        print("\n" + "🚀"*10 + " CAREER PREDICTOR TRAINING " + "🚀"*10)
        X, y, df = self.load_and_preprocess_data()
        results, best_model = self.train_models(X, y)
        self.save_model()
        print("\n✅ Training complete!")
        return results

# Example usage
if __name__ == "__main__":
    # Initialize predictor
    predictor = CareerPredictor()
    
    # Train model
    predictor.train_pipeline()
    
    # Test prediction
    test_prediction = predictor.predict(
        skills=['Python', 'Machine Learning', 'SQL'],
        cgpa=8.5,
        interest='AI',
        internship='Yes',
        projects_count=3,
        communication_score=7
    )
    
    print("\n🔮 Test Prediction:")
    print(f"   Predicted Career: {test_prediction['predicted_career']}")
    print(f"   Confidence: {test_prediction['confidence']:.2f}")
    print("\n   Top 3 Careers:")
    for i, career in enumerate(test_prediction['top_3_careers'], 1):
        print(f"   {i}. {career['career']} ({career['probability']:.2f})")