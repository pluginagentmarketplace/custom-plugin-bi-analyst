# Data Science & AI Guide

> BI Analyst Plugin - Data-AI Skill Reference
> Version: 1.0.0

## Overview

Comprehensive guide covering machine learning pipelines, deep learning, MLOps, and AI application development with production-ready patterns.

## Table of Contents

1. [ML Pipeline Architecture](#ml-pipeline-architecture)
2. [Feature Engineering](#feature-engineering)
3. [Model Training Best Practices](#model-training-best-practices)
4. [Deep Learning Patterns](#deep-learning-patterns)
5. [MLOps & Production ML](#mlops--production-ml)
6. [LLM & AI Agents](#llm--ai-agents)

---

## ML Pipeline Architecture

### Standard ML Pipeline Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Data     │───▶│  Feature    │───▶│   Model     │
│   Ingestion │    │ Engineering │    │  Training   │
└─────────────┘    └─────────────┘    └─────────────┘
                                            │
┌─────────────┐    ┌─────────────┐    ┌─────▼───────┐
│ Deployment  │◀───│   Model     │◀───│ Evaluation  │
│  & Serving  │    │  Registry   │    │ & Validation│
└─────────────┘    └─────────────┘    └─────────────┘
```

### Scikit-learn Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

# Define column types
numeric_features = ['age', 'income', 'balance']
categorical_features = ['category', 'region']

# Numeric transformer
numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

# Categorical transformer
categorical_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

# Combined preprocessor
preprocessor = ColumnTransformer([
    ('num', numeric_transformer, numeric_features),
    ('cat', categorical_transformer, categorical_features)
])

# Complete pipeline
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Train and evaluate
pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)
```

---

## Feature Engineering

### Feature Types and Transformations

| Feature Type | Transformations | When to Use |
|--------------|-----------------|-------------|
| Numeric | StandardScaler, MinMaxScaler, Log | Continuous values |
| Categorical | OneHotEncoder, LabelEncoder | Discrete categories |
| DateTime | Extract year, month, day, hour | Time-based data |
| Text | TF-IDF, Word2Vec, Embeddings | Natural language |
| Geospatial | Haversine distance, clustering | Location data |

### Advanced Feature Engineering

```python
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class AdvancedFeatureTransformer(BaseEstimator, TransformerMixin):
    """Custom feature engineering transformer."""

    def __init__(self, date_columns=None, text_columns=None):
        self.date_columns = date_columns or []
        self.text_columns = text_columns or []

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        # DateTime features
        for col in self.date_columns:
            if col in X.columns:
                X[f'{col}_year'] = pd.to_datetime(X[col]).dt.year
                X[f'{col}_month'] = pd.to_datetime(X[col]).dt.month
                X[f'{col}_day'] = pd.to_datetime(X[col]).dt.day
                X[f'{col}_dayofweek'] = pd.to_datetime(X[col]).dt.dayofweek
                X[f'{col}_is_weekend'] = X[f'{col}_dayofweek'].isin([5, 6]).astype(int)
                X = X.drop(col, axis=1)

        # Interaction features
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            X['feature_ratio'] = X[numeric_cols[0]] / (X[numeric_cols[1]] + 1e-10)

        return X


# Feature selection with mutual information
from sklearn.feature_selection import mutual_info_classif, SelectKBest

selector = SelectKBest(mutual_info_classif, k=20)
X_selected = selector.fit_transform(X, y)

# Get selected feature names
selected_mask = selector.get_support()
selected_features = X.columns[selected_mask].tolist()
```

---

## Model Training Best Practices

### Hyperparameter Tuning with Optuna

```python
import optuna
from sklearn.model_selection import cross_val_score
from xgboost import XGBClassifier


def objective(trial):
    """Optuna objective function for XGBoost."""
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
    }

    model = XGBClassifier(**params, random_state=42, use_label_encoder=False)
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')

    return scores.mean()


# Run optimization
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100, show_progress_bar=True)

# Get best parameters
best_params = study.best_params
print(f"Best F1 Score: {study.best_value:.4f}")
```

### Cross-Validation Strategies

```python
from sklearn.model_selection import (
    StratifiedKFold,
    TimeSeriesSplit,
    GroupKFold
)

# Stratified K-Fold (for imbalanced classification)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Time Series Split (for temporal data)
tss = TimeSeriesSplit(n_splits=5)

# Group K-Fold (for grouped data)
gkf = GroupKFold(n_splits=5)

# Custom evaluation
from sklearn.model_selection import cross_validate

cv_results = cross_validate(
    model, X, y,
    cv=skf,
    scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc'],
    return_train_score=True
)

print(f"Test F1: {cv_results['test_f1'].mean():.4f} (+/- {cv_results['test_f1'].std():.4f})")
```

---

## Deep Learning Patterns

### PyTorch Training Loop

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm


class Trainer:
    """PyTorch model trainer with best practices."""

    def __init__(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        criterion: nn.Module,
        device: str = 'cuda'
    ):
        self.model = model.to(device)
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self.history = {'train_loss': [], 'val_loss': [], 'val_acc': []}

    def train_epoch(self, dataloader: DataLoader) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0

        for batch in tqdm(dataloader, desc='Training'):
            inputs = batch['input'].to(self.device)
            targets = batch['target'].to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

            self.optimizer.step()
            total_loss += loss.item()

        return total_loss / len(dataloader)

    @torch.no_grad()
    def evaluate(self, dataloader: DataLoader) -> tuple[float, float]:
        """Evaluate model."""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0

        for batch in dataloader:
            inputs = batch['input'].to(self.device)
            targets = batch['target'].to(self.device)

            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            total_loss += loss.item()

            _, predicted = outputs.max(1)
            correct += predicted.eq(targets).sum().item()
            total += targets.size(0)

        return total_loss / len(dataloader), correct / total

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int,
        early_stopping_patience: int = 10
    ):
        """Full training loop with early stopping."""
        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss, val_acc = self.evaluate(val_loader)

            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)

            print(f"Epoch {epoch+1}: Train Loss={train_loss:.4f}, "
                  f"Val Loss={val_loss:.4f}, Val Acc={val_acc:.4f}")

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                torch.save(self.model.state_dict(), 'best_model.pt')
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    print(f"Early stopping at epoch {epoch+1}")
                    break

        # Load best model
        self.model.load_state_dict(torch.load('best_model.pt'))
```

---

## MLOps & Production ML

### MLflow Experiment Tracking

```python
import mlflow
import mlflow.sklearn
from sklearn.metrics import accuracy_score, f1_score


def train_with_mlflow(model, X_train, y_train, X_test, y_test, params):
    """Train model with MLflow tracking."""

    mlflow.set_experiment("churn_prediction")

    with mlflow.start_run():
        # Log parameters
        mlflow.log_params(params)

        # Train model
        model.fit(X_train, y_train)

        # Predictions
        y_pred = model.predict(X_test)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        # Log metrics
        mlflow.log_metrics({
            "accuracy": accuracy,
            "f1_score": f1
        })

        # Log model
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name="ChurnPredictor"
        )

        # Log artifacts
        mlflow.log_artifact("feature_importance.png")

        print(f"Run ID: {mlflow.active_run().info.run_id}")
        print(f"Accuracy: {accuracy:.4f}, F1: {f1:.4f}")

        return model
```

### Model Serving with FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="ML Model API")

# Load model at startup
model = None

@app.on_event("startup")
async def load_model():
    global model
    model = joblib.load("model.joblib")


class PredictionRequest(BaseModel):
    features: list[float]


class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    model_version: str = "1.0.0"


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make prediction."""
    try:
        features = np.array(request.features).reshape(1, -1)
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0].max()

        return PredictionResponse(
            prediction=int(prediction),
            probability=float(probability)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}
```

---

## LLM & AI Agents

### RAG (Retrieval-Augmented Generation)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI


def create_rag_chain(documents: list[str], persist_directory: str = "./chroma_db"):
    """Create RAG chain for document Q&A."""

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    splits = text_splitter.split_documents(documents)

    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        splits,
        embeddings,
        persist_directory=persist_directory
    )

    # Create retrieval chain
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain


# Usage
chain = create_rag_chain(documents)
result = chain({"query": "What is the main topic of the document?"})
print(result["result"])
```

### Prompt Engineering Best Practices

```python
from string import Template

# Structured prompt template
ANALYSIS_PROMPT = Template("""
You are an expert data analyst. Analyze the following data and provide insights.

## Context
$context

## Data Summary
$data_summary

## Analysis Request
$request

## Output Format
Provide your analysis in the following structure:
1. Key Findings (3-5 bullet points)
2. Statistical Insights
3. Recommendations
4. Potential Issues or Limitations

Be specific and cite data where possible.
""")

def create_analysis_prompt(context: str, data_summary: str, request: str) -> str:
    """Create structured analysis prompt."""
    return ANALYSIS_PROMPT.substitute(
        context=context,
        data_summary=data_summary,
        request=request
    )
```

---

## Resources

- [Scikit-learn Documentation](https://scikit-learn.org)
- [PyTorch Tutorials](https://pytorch.org/tutorials)
- [MLflow Documentation](https://mlflow.org/docs)
- [LangChain Documentation](https://python.langchain.com)
- [Optuna Documentation](https://optuna.readthedocs.io)
- [Papers With Code](https://paperswithcode.com)

---

*Last Updated: 2025-01-01*
*BI Analyst Plugin - Data-AI Skill*
