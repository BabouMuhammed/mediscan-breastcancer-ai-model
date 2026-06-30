# MediScan AI — Breast Cancer Detection

An end-to-end AI application that classifies breast tumor biopsy measurements as **benign** or **malignant**, built for the AI Final Group Project (Option B: Building a Real-World AI Application).

The system uses a PyTorch neural network trained on the Wisconsin Diagnostic Breast Cancer (WDBC) dataset, deployed via a Hugging Face Space, and served to users through a custom web frontend with plain-language, confidence-aware result explanations.

---

## Project Structure

```
mediscan-breastcancer-ai-model/
├── model/
│   ├── train.py              # Training script (PyTorch neural network)
│   └── requirements.txt      # Python dependencies for training
├── backend/
│   ├── app.py                # Flask proxy server (frontend ↔ Hugging Face Space)
│   └── requirements.txt      # Python dependencies for the backend
├── frontend/
│   ├── index.html            # Web app UI
│   ├── style.css             # Styling
│   └── script.js             # Upload, API calls, and result rendering logic
└── README.md
```

---

## How It Works

1. **Model training** (`model/train.py`): trains a fully connected neural network on 30 numeric features per tumor sample (radius, texture, perimeter, area, smoothness, concavity, etc., plus their standard error and worst-case values) extracted from digitized fine needle aspiration (FNA) biopsy images.
2. **Deployment**: the trained model is hosted as a Gradio app on Hugging Face Spaces, exposing a `/predict` API endpoint.
3. **Backend proxy** (`backend/app.py`): a small Flask server that receives CSV uploads from the frontend and forwards them to the Hugging Face Space using `gradio_client`. This avoids browser-side CORS restrictions that occur when calling the Space directly from client-side JavaScript.
4. **Frontend** (`frontend/`): a mobile-first web interface where a user uploads a CSV file of tumor measurements and receives per-sample predictions, each paired with a plain-language explanation and an explicit "this is not a diagnosis" disclaimer. Low-confidence predictions (under 75%) are flagged as inconclusive rather than asserting a label.

---

## Setup Instructions

### 1. Train the model (optional — a pretrained model is already deployed)

```bash
cd model
pip install -r requirements.txt
```

Download the WDBC dataset from [Kaggle](https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data) and place `data.csv` in the `model/` folder, then:

```bash
python train.py
```

This outputs `breast_cancer_model.pth`, along with training curve and confusion matrix plots.

### 2. Run the backend proxy

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend starts on `http://127.0.0.1:5050` and connects to the deployed Hugging Face Space.

### 3. Run the frontend

Open `frontend/index.html` with a local server (e.g., the VS Code "Live Server" extension). Do not open it directly as a `file://` path, since the upload functionality requires a proper HTTP origin.

With the backend running, open the frontend in your browser, upload a CSV file containing 30 tumor measurement columns, and click **Analyze patient data**.

---

## Dataset

**Wisconsin Diagnostic Breast Cancer (WDBC) dataset** — 569 samples, 30 numeric features per sample, binary label (malignant/benign). Source: [UCI Machine Learning Repository / Kaggle](https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data).

---

## Model Architecture

A fully connected feedforward neural network (PyTorch):

```
Input (30 features)
  → Linear(30, 128) → ReLU → Dropout(0.3)
  → Linear(128, 64) → ReLU → Dropout(0.3)
  → Linear(64, 32)  → ReLU
  → Linear(32, 1)   → Sigmoid
```

Trained with binary cross-entropy loss and the Adam optimizer (learning rate 0.0001) for 50 epochs.

---

## Evaluation

The model was evaluated on a held-out test split. See the final report for full metrics, confusion matrix, and discussion of error patterns (including false-negative analysis, which is the most clinically significant error type for a cancer-screening tool).

---

## Limitations and Disclaimer

This tool is an educational prototype and **does not constitute a medical diagnosis**. It is trained on a single, well-known benchmark dataset and has not been clinically validated. The current pipeline accepts numeric biopsy measurements (CSV), not raw medical images; an image-based version (e.g., from mammograms or histology slides) is a potential future extension and a different modeling problem requiring a separate convolutional architecture and dataset.

---

## Team / Authors

(Add your team members' names here.)
