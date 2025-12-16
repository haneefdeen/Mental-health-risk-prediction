# MindScope AI (EMPATH) – Multimodal Mental Health Analysis

MindScope AI is a CPU‑friendly, multimodal mental health analysis app.  
It combines **text (DistilBERT)**, **image (ResNet)**, and **behavioural signals** to estimate stress/risk and provide AI‑driven wellness tips.

The stack is:
- **Backend**: Flask (`mindscope_flask/app.py`)
- **Frontend**: Single‑page Bootstrap UI (`templates/index.html` + `assets/`)
- **Models**: PyTorch + Hugging Face (under `backend/model/`)

---

## 1. Installation

From the project root:

```bash
python -m venv venv
venv\Scripts\activate          # On Windows

pip install -r requirements.txt
pip install flask flask-bcrypt flask-cors flask-sqlalchemy flask-migrate
```

> Make sure you are always inside the virtual environment (`(venv)` shows in the prompt) when running commands below.

---

## 2. Train Models (one‑time, optional but recommended)

This uses your included datasets (Reddit/Dreaddit, DAIC‑WOZ, FER, etc.) and saves weights under `models/`:

```bash
cd backend
python train_models.py --model all
cd ..
```

To evaluate the text stress model and write metrics for the admin dashboard:

```bash
cd backend
python evaluate_models.py
cd ..
```

This will create `models/metrics.json` with accuracy/precision/recall/F1.

---

## 3. Run the Backend (Flask API + UI)

From the project root:

```bash
cd D:\capstone_project        # adjust if needed
venv\Scripts\activate

set PYTHONPATH=%CD%
python -m mindscope_flask.app
```

The app will be available at:

```text
http://localhost:5000
```

> Webcam (`getUserMedia`) **only works** when accessed over `http://localhost` or `https`.  
> It will not work if you double‑click `index.html` and open it as `file://...`.

---

## 4. Run Everything with a Single Script (Windows)

From the project root, you can use:

```bash
run_all.bat
```

This will:
- Activate the virtual environment (if present).
- Start `python -m mindscope_flask.app`.
- Open `http://localhost:5000` in your default browser.

---

## 5. Frontend Usage

Open in your browser:

```text
http://localhost:5000
```

Features:
- **User mode**: text, image, fusion, and webcam analysis; timeline; behavioural fingerprint; PDF report; ZIP export; delete‑my‑data.
- **Admin mode**: everything in user mode plus:
  - User list
  - Global analytics (class counts, emotion & stress distribution, high‑stress alerts)
  - Support messages
  - Model metrics card (accuracy/F1 from `backend/evaluate_models.py`)

You can log in with the default accounts:
- Admin: `admin / admin123`
- Demo user: `user1 / user123`

Dark/light theme:
- Use the theme toggle in the navbar.
- Preference is stored in `localStorage` and persisted across reloads.

Webcam:
- Click **Start Webcam** and allow camera access when prompted.
- Click **Capture & Analyze** to send a frame to the backend.
- If webcam is unavailable or blocked, you can always **upload an image** instead.

---

## 6. API Overview (Flask)

Main endpoints (JSON):

- `POST /api/analyze/text` – text‑only analysis
- `POST /api/analyze/image` – image‑only analysis
- `POST /api/analyze/fusion` – combined text+image+behavioural analysis
- `POST /api/analyze/webcam` – webcam image analysis (same as `/api/analyze/image`)
- `POST /api/predict` – unified prediction endpoint; body:

  ```json
  {
    "mode": "text" | "image" | "fusion" | "webcam",
    "text": "...optional...",
    "image_base64": "...optional..."
  }
  ```

  Returns:

  ```json
  {
    "risk_label": "Low" | "Medium" | "High",
    "risk_score": 0.0,
    "extras": { "...record fields..." }
  }
  ```

- `POST /api/explain/text` – word‑level importance / highlight data
- `POST /api/explain/image` – Grad‑CAM‑style heatmap overlay (base64)
- `GET /api/user/timeline` – per‑user stress timeline
- `GET /api/user/behavioral` – behavioural fingerprint (emoji, sessions, etc.)
- `DELETE /api/user/data` – clear all of the current user’s stored analyses
- `POST /api/reports/pdf` – generate latest PDF report
- `POST /api/reports/export` – export all user data as a ZIP
- `GET /api/admin/users` – admin user list
- `GET /api/admin/analytics` – admin analytics (counts, distributions, alerts)
- `POST /api/admin/support` – send a support message to a user
- `GET /api/admin/metrics` – return model metrics from `models/metrics.json`
- `GET /api/system/status` – simple health/status

All `/api/...` routes (except health) expect a valid JWT in the `Authorization: Bearer <token>` header obtained from:

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`

---

## 7. Folder Structure (simplified)

```text
.
├── assets/
│   ├── css/
│   │   └── style.css            # main Bootstrap-based styling + dark/light theme
│   └── js/
│       └── app_enhanced.js      # frontend logic (auth, analysis, admin, explainability)
├── backend/
│   ├── model/
│   │   ├── text_analyzer.py     # DistilBERT text analysis
│   │   ├── image_analyzer.py    # ResNet image analysis
│   │   ├── behavioral_analyzer.py
│   │   ├── fusion_model.py
│   │   └── explainability.py    # text + image explanation helpers
│   ├── datasets/                # dataset manager and metadata
│   ├── train_models.py          # trains text + image models on your datasets
│   └── evaluate_models.py       # evaluates text model and writes models/metrics.json
├── mindscope_flask/
│   └── app.py                   # Flask app factory + routes
├── templates/
│   └── index.html               # main single-page UI served at /
├── models/                      # saved model weights + metrics.json
├── run_all.bat                  # start backend + open browser (Windows)
├── requirements.txt             # Python dependencies
└── README.md                    # this file
```

---

## 8. Troubleshooting

- **Webcam not working**  
  - Ensure you are using `http://localhost:5000` (not `file://...`).  
  - Check browser permissions (camera allowed for `localhost`).  
  - On unsupported browsers/devices, use image upload instead.

- **Backend import errors (`No module named backend`)**  
  - Ensure `PYTHONPATH` is set to the project root before running Flask:
    ```bash
    set PYTHONPATH=%CD%
    python -m mindscope_flask.app
    ```

- **Metrics not showing in admin panel**  
  - Run:
    ```bash
    cd backend
    python evaluate_models.py
    cd ..
    ```
  - Reload the admin dashboard.

- **Predictions feel random**  
  - Make sure you have trained models via `backend/train_models.py --model all`.  
  - Without trained weights, the analyzers fall back to generic pretrained behaviour.

---

## 9. Accuracy Information

The provided training and evaluation scripts aim for **reasonable, data‑driven performance** on your datasets (text stress detection and facial emotion recognition) and typically achieve around the **70%+ accuracy/F1** range on held‑out text data, depending on hardware and random seed.

Use `backend/evaluate_models.py` to generate fresh metrics on your machine; the admin “Model Performance” card simply reads and displays those values from `models/metrics.json`.
