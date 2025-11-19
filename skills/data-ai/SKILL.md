---
name: data-science-ai
description: Build machine learning models, data pipelines, and AI applications using Python, TensorFlow, PyTorch, and modern ML frameworks. Use when working with data, machine learning, deep learning, NLP, or AI systems.
---

# Data Science & AI Skill

## Quick Start

### Python Data Analysis
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load and explore data
df = pd.read_csv('data.csv')
print(df.head())
print(df.info())
print(df.describe())

# Data cleaning
df = df.dropna()
df['age'] = df['age'].astype(int)
df['name'] = df['name'].str.lower()

# Visualization
plt.figure(figsize=(10, 6))
plt.hist(df['age'], bins=30)
plt.xlabel('Age')
plt.ylabel('Frequency')
plt.show()
```

### Scikit-learn Classification
```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(confusion_matrix(y_test, y_pred))
```

### Deep Learning with PyTorch
```python
import torch
import torch.nn as nn

class SimpleNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = x.flatten(1)
        x = self.relu(self.fc1(x))
        return self.fc2(x)

model = SimpleNN()
optimizer = torch.optim.Adam(model.parameters())
loss_fn = nn.CrossEntropyLoss()

# Training loop
for epoch in range(10):
    for batch_X, batch_y in dataloader:
        optimizer.zero_grad()
        predictions = model(batch_X)
        loss = loss_fn(predictions, batch_y)
        loss.backward()
        optimizer.step()
```

### TensorFlow Keras Model
```python
import tensorflow as tf
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(784,)),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(10, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.1)
```

## Machine Learning Workflow

### Feature Engineering
```python
# Scaling
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

# Encoding categorical variables
from sklearn.preprocessing import LabelEncoder

encoder = LabelEncoder()
df['category'] = encoder.fit_transform(df['category'])

# Feature selection
from sklearn.feature_selection import SelectKBest, f_classif

selector = SelectKBest(f_classif, k=10)
X_selected = selector.fit_transform(X, y)
```

### Model Evaluation Metrics
```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, roc_curve
)

# Classification metrics
print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
print(f"Precision: {precision_score(y_true, y_pred):.4f}")
print(f"Recall: {recall_score(y_true, y_pred):.4f}")
print(f"F1 Score: {f1_score(y_true, y_pred):.4f}")

# ROC-AUC for binary classification
print(f"ROC-AUC: {roc_auc_score(y_true, y_pred_proba):.4f}")

# Regression metrics
from sklearn.metrics import mean_squared_error, r2_score
print(f"RMSE: {np.sqrt(mean_squared_error(y_true, y_pred)):.4f}")
print(f"R² Score: {r2_score(y_true, y_pred):.4f}")
```

## NLP with Transformers

### Hugging Face Transformers
```python
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Sentiment analysis
classifier = pipeline('sentiment-analysis')
result = classifier('This movie is amazing!')

# Named Entity Recognition
ner = pipeline('ner')
entities = ner('Elon Musk works at Tesla')

# Custom model
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModelForSequenceClassification.from_pretrained('bert-base-uncased')

tokens = tokenizer('Hello world', return_tensors='pt')
outputs = model(**tokens)
logits = outputs.logits
```

### LLM Prompt Engineering
```python
from langchain import OpenAI, PromptTemplate, LLMChain

llm = OpenAI(temperature=0.7)

prompt = PromptTemplate(
    input_variables=['topic'],
    template='Write a blog post about {topic}'
)

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(topic='Machine Learning')

# Few-shot learning
few_shot_prompt = """
Examples:
Question: What is 2+2?
Answer: 4

Question: What is capital of France?
Answer: Paris

Question: {question}
Answer:
"""
```

## Data Pipeline with Apache Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract_data():
    # Extract from source
    pass

def transform_data():
    # Transform and clean
    pass

def load_data():
    # Load to warehouse
    pass

with DAG('data_pipeline', start_date=datetime(2024, 1, 1)) as dag:
    extract = PythonOperator(task_id='extract', python_callable=extract_data)
    transform = PythonOperator(task_id='transform', python_callable=transform_data)
    load = PythonOperator(task_id='load', python_callable=load_data)

    extract >> transform >> load
```

## MLOps Best Practices

### Model Versioning with MLflow
```python
import mlflow
import mlflow.sklearn

# Log parameters
mlflow.log_param('n_estimators', 100)
mlflow.log_param('max_depth', 10)

# Log metrics
mlflow.log_metric('accuracy', 0.95)
mlflow.log_metric('f1_score', 0.93)

# Log model
mlflow.sklearn.log_model(model, 'model')

# Predictions
with mlflow.start_run():
    model = train_model()
    mlflow.sklearn.log_model(model, 'model')
```

### Model Serving with FastAPI
```python
from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()
model = joblib.load('model.pkl')

@app.post('/predict')
def predict(features: list[float]):
    X = np.array(features).reshape(1, -1)
    prediction = model.predict(X)
    return {'prediction': float(prediction[0])}
```

## Common Algorithms & Models

| Algorithm | Use Case | Pros | Cons |
|-----------|----------|------|------|
| **Linear Regression** | Continuous prediction | Interpretable, fast | Limited complexity |
| **Logistic Regression** | Binary classification | Simple, efficient | Linear decisions only |
| **Random Forest** | General ML | Robust, feature importance | Less interpretable |
| **XGBoost** | Kaggle/competitions | High accuracy | Hyperparameter tuning |
| **Neural Networks** | Complex patterns | Very flexible | Requires data & compute |
| **SVM** | Binary/multiclass | Good generalization | Slow on large datasets |

## Resources
- [Scikit-learn Documentation](https://scikit-learn.org)
- [TensorFlow & Keras](https://www.tensorflow.org)
- [PyTorch Tutorials](https://pytorch.org/tutorials)
- [Hugging Face Documentation](https://huggingface.co/docs)
- [Fast.ai Courses](https://course.fast.ai)
