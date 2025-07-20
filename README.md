# 📦 Order Metrics API

A FastAPI-based project to process CSV files from a remote URL, clean and analyze the data, and return useful metrics like blank rows, malformed entries, duplicates, and more.

---

## 🚀 Overview

This API is designed to:
- Download large CSV files from a provided public URL
- Clean the data (normalize column names, remove duplicates, handle malformed rows, etc.)
- Return detailed processing statistics
- Optionally, store and retrieve metrics based on file ID

Swagger UI is automatically available for easy testing.

---

## 🧱 Project Structure

```
order-metrics-api/
├── app/
│   ├── routes/            # API route definitions
│   ├── services/          # Business logic (CSV processing)
│   └── main.py            # FastAPI entry point
├── data/                  # Stores downloaded CSV files
├── tests/                 # Unit tests for processing logic
├── requirements.txt       # Python dependencies
└── README.md              # You are here!
```
---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/order-metrics-api.git
cd order-metrics-api
```

---
### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---
### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI application

```bash
uvicorn app.main:app --reload

```

Then open your browser and visit:

http://127.0.0.1:8000/docs

This will load Swagger UI for testing the endpoints.
