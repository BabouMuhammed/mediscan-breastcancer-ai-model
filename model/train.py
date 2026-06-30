"""
train.py — Trains the MediScan AI breast cancer classifier on the
Wisconsin Diagnostic Breast Cancer (WDBC) dataset.

Originally developed as a Kaggle notebook; converted to a standalone
script for reproducibility per the project's deliverable requirements.

Dataset: https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data
(also available via sklearn.datasets.load_breast_cancer for convenience)

Usage:
    python train.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset


# ---------------------------------------------------------------------
# 1. Load and clean data
# ---------------------------------------------------------------------
# Update this path to wherever you've placed the WDBC CSV locally,
# or download it from the Kaggle link above.
DATA_PATH = "data.csv"

df = pd.read_csv(DATA_PATH)
print(df.shape)

df = df.drop(['id', 'Unnamed: 32'], axis=1)
df['diagnosis'] = df['diagnosis'].map({'M': 1, 'B': 0})
print(df['diagnosis'].value_counts())

X = df.drop('diagnosis', axis=1).values
y = df['diagnosis'].values


# ---------------------------------------------------------------------
# 2. Train/test split and feature scaling
# ---------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

X_train_t = torch.tensor(X_train, dtype=torch.float32)
X_test_t = torch.tensor(X_test, dtype=torch.float32)
y_train_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
y_test_t = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

train_dataset = TensorDataset(X_train_t, y_train_t)
test_dataset = TensorDataset(X_test_t, y_test_t)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32)
print("Tensors ready!")


# ---------------------------------------------------------------------
# 3. Model definition
# ---------------------------------------------------------------------
class BreastCancerModel(nn.Module):
    def __init__(self, input_dim):
        super(BreastCancerModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)


input_dim = X_train_t.shape[1]
model = BreastCancerModel(input_dim)
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)
print(model)


# ---------------------------------------------------------------------
# 4. Training loop
# ---------------------------------------------------------------------
EPOCHS = 50
train_losses, val_losses = [], []
train_accs, val_accs = [], []

for epoch in range(EPOCHS):
    # Training
    model.train()
    total_loss, correct, total = 0, 0, 0
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        preds = (outputs > 0.5).float()
        correct += (preds == y_batch).sum().item()
        total += y_batch.size(0)
    train_losses.append(total_loss / len(train_loader))
    train_accs.append(correct / total)

    # Validation
    model.eval()
    val_loss, val_correct, val_total = 0, 0, 0
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            val_loss += loss.item()
            preds = (outputs > 0.5).float()
            val_correct += (preds == y_batch).sum().item()
            val_total += y_batch.size(0)
    val_losses.append(val_loss / len(test_loader))
    val_accs.append(val_correct / val_total)

    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/{EPOCHS} | Train Acc: {train_accs[-1]:.4f} | Val Acc: {val_accs[-1]:.4f}")


# ---------------------------------------------------------------------
# 5. Training curves
# ---------------------------------------------------------------------
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(train_accs, label='Train Accuracy')
plt.plot(val_accs, label='Val Accuracy')
plt.legend()
plt.title('Accuracy')
plt.subplot(1, 2, 2)
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Val Loss')
plt.legend()
plt.title('Loss')
plt.savefig('training_curves.png')
plt.show()


# ---------------------------------------------------------------------
# 6. Final evaluation
# ---------------------------------------------------------------------
model.eval()
all_preds, all_labels = [], []
with torch.no_grad():
    for X_batch, y_batch in test_loader:
        outputs = model(X_batch)
        preds = (outputs > 0.5).float()
        all_preds.extend(preds.numpy())
        all_labels.extend(y_batch.numpy())

print(classification_report(all_labels, all_preds, target_names=['Benign', 'Malignant']))

cm = confusion_matrix(all_labels, all_preds)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Benign', 'Malignant'],
            yticklabels=['Benign', 'Malignant'])
plt.title('Confusion Matrix')
plt.savefig('confusion_matrix.png')
plt.show()


# ---------------------------------------------------------------------
# 7. Save model
# ---------------------------------------------------------------------
torch.save(model.state_dict(), 'breast_cancer_model.pth')
print("Model saved!")
