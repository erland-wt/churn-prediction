# Customer Churn Prediction 📊

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-latest-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-stable-F7931E?logo=scikit-learn)](https://scikit-learn.org/)

Sistem end-to-end untuk memprediksi customer churn dengan **REST API (FastAPI)** dan **dashboard interaktif (Streamlit)**. Proyek ini memakai preprocessing pipeline yang terpisah dari model, validasi input yang ketat, dan penyimpanan artefak agar mudah direproduksi.

---

## 🎯 Project Overview

Proyek ini membangun machine learning pipeline lengkap untuk memprediksi apakah pelanggan akan churn (berhenti berlangganan). Alurnya mencakup:

- **Data Exploration**: analisis dataset pelanggan, distribusi target, dan insight awal
- **Preprocessing**: feature engineering, encoding, scaling, dan penyimpanan artefak
- **Model Development**: training beberapa model, evaluasi metrik, tuning hyperparameter, dan threshold optimization
- **Production API**: FastAPI dengan endpoint raw input dan encoded input
- **Interactive UI**: Streamlit dashboard untuk mencoba prediksi dan melihat hasil dengan lebih jelas

**Dataset**: Telco Customer Churn  
**Jumlah data**: 7.043 records setelah cleaning  
**Input raw**: 19 fitur  
**Final features**: 43 fitur setelah encoding dan alignment  
**Task**: binary classification (Churn: Yes/No)

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔮 **Real-time Prediction** | Prediksi dilakukan langsung lewat API |
| 🎨 **Interactive Dashboard** | Form Streamlit untuk input customer dan melihat hasil |
| 🛡️ **Input Validation** | Pydantic schema untuk validasi tipe, enum, dan constraint |
| 🧹 **Feature Engineering** | AvgMonthlyCharges, TenureBucket, dan TotalServices |
| 📊 **Threshold Optimization** | Threshold ditentukan dari Precision-Recall curve |
| 🚀 **Production-Ready** | Logging, error handling, dan loading artefak |
| 🔄 **Dual Preprocessing** | Mendukung raw input dan encoded input |
| 🎓 **Model Comparison** | Beberapa model dibandingkan sebelum dipilih model final |

---

## 🏗️ Tech Stack

**Backend**
- `FastAPI 0.115.0` — REST API framework
- `Uvicorn` — ASGI server
- `Pydantic` — data validation and serialization
- `joblib` — penyimpanan artefak model

**Frontend**
- `Streamlit` — dashboard interaktif
- `requests` — HTTP client untuk memanggil API

**ML/Data**
- `scikit-learn` — preprocessing, training, evaluation, tuning
- `pandas` — data wrangling
- `numpy` — operasi numerik

**Python Version**: gunakan environment Python 3.10+ yang sesuai dengan project dan dependency yang sudah dipasang di venv

---

## 📁 Project Structure

```text
.
├── api/
│   └── main.py
├── app/
│   └── streamlit_app.py
├── dataset/
│   ├── raw/
│   │   └── Telco-Customer-Churn.csv
│   └── processed/
│       ├── X_train.csv
│       ├── X_test.csv
│       ├── y_train.csv
│       └── y_test.csv
├── models/
│   ├── churn_model.joblib
│   └── preprocessor.joblib
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_preprocessing.ipynb
│   └── 03_modeling.ipynb
├── requirements-api.txt
├── requirements-streamlit.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python
- pip

### 1. Install dependencies

```bash
# API environment
.venv-api\Scripts\activate
pip install -r requirements-api.txt

# Streamlit environment
.venv-streamlit\Scripts\activate
pip install -r requirements-streamlit.txt
```

### 2. Jalankan FastAPI

```bash
.venv-api\Scripts\activate
uvicorn api.main:app --reload --port 8000
```

Tautan yang berguna:
- Health check: http://127.0.0.1:8000/
- Metadata: http://127.0.0.1:8000/meta
- Swagger UI: http://127.0.0.1:8000/docs

### 3. Jalankan Streamlit

```bash
.venv-streamlit\Scripts\activate
streamlit run app/streamlit_app.py
```

Dashboard default URL: http://localhost:8501

---

## 📊 Dataset & Preprocessing

### Raw Input Features (19)

```text
gender, SeniorCitizen, Partner, Dependents, tenure, PhoneService,
MultipleLines, InternetService, OnlineSecurity, OnlineBackup,
DeviceProtection, TechSupport, StreamingTV, StreamingMovies,
Contract, PaperlessBilling, PaymentMethod, MonthlyCharges, TotalCharges
```

### Data Cleaning
- Baris dengan `tenure = 0` dibuang
- `TotalCharges` diubah menjadi numeric dengan `errors='coerce'`
- Dataset processed disimpan ulang untuk dipakai di modeling

### Feature Engineering
- `AvgMonthlyCharges = TotalCharges / tenure`
- `TenureBucket` dengan kategori `New`, `Early`, `Established`, `Loyal`
- `TotalServices` dari jumlah layanan aktif bernilai `Yes`

### Encoding & Scaling
- Binary mapping: `Partner`, `Dependents`, `PhoneService`, `PaperlessBilling`
- One-hot encoding untuk kolom kategorikal lainnya
- StandardScaler untuk:
	- `tenure`
	- `MonthlyCharges`
	- `TotalCharges`
	- `AvgMonthlyCharges`
	- `TotalServices`

### Final Feature Count
- Total final features: **43**

---

## 🧠 Model Development

Notebook `03_modeling.ipynb` melakukan:

- Load data processed dari `dataset/processed/`
- Train baseline model
- Bandingkan beberapa model
- Evaluasi dengan metrik klasifikasi
- Tuning hyperparameter menggunakan `RandomizedSearchCV`
- Cari threshold terbaik dari precision-recall curve
- Simpan model final ke `models/churn_model.joblib`

Model yang diuji mencakup:

- `LogisticRegression`
- `RandomForestClassifier`
- model tree-based lain jika dependency tersedia di environment notebook

> Catatan: model final dan threshold diambil dari artefak yang tersimpan di folder `models/`.

---

## 🔗 API Endpoints

### `GET /`
Health check dan status model.

### `GET /meta`
Metadata model, feature names, threshold, dan status preprocessor.

### `POST /predict`
Prediksi menggunakan fitur yang sudah diencode dan diselect sesuai training.

### `POST /predict_raw`
Prediksi menggunakan input raw yang mudah diisi. Endpoint inilah yang dipakai Streamlit.

Contoh payload:

```json
{
	"gender": "Male",
	"SeniorCitizen": 0,
	"Partner": "Yes",
	"Dependents": "No",
	"tenure": 24,
	"PhoneService": "Yes",
	"MultipleLines": "Yes",
	"InternetService": "DSL",
	"OnlineSecurity": "Yes",
	"OnlineBackup": "No",
	"DeviceProtection": "Yes",
	"TechSupport": "No",
	"StreamingTV": "No",
	"StreamingMovies": "No",
	"Contract": "One year",
	"PaperlessBilling": "No",
	"PaymentMethod": "Credit card (automatic)",
	"MonthlyCharges": 65.5,
	"TotalCharges": 1572
}
```

---

## 🎨 Streamlit Dashboard

Dashboard di `app/streamlit_app.py` berisi:

- form input 3 kolom untuk data customer
- tombol prediksi
- tampilan label prediksi
- probability score
- threshold yang dipakai model
- progress bar risiko churn
- bar chart perbandingan skor churn vs no churn
- expander untuk melihat payload dan response lengkap

---

## 🧪 Testing Checklist

Checklist yang disarankan:

- `GET /` mengembalikan status model loaded
- `GET /meta` menampilkan metadata dan threshold
- `POST /predict_raw` dengan input normal berhasil
- `POST /predict_raw` dengan extra field seperti `customerID` tetap aman
- Streamlit berhasil memanggil API dan menampilkan hasil

---

## 📈 Results

Metrik final, threshold, dan feature importance dapat dilihat langsung di notebook `03_modeling.ipynb` serta response `/meta` dan `/predict_raw` pada API.

---

## 📚 Notebooks

| Notebook | Purpose |
|----------|---------|
| `01_eda.ipynb` | Exploratory data analysis |
| `02_preprocessing.ipynb` | Feature engineering, encoding, scaling, dan penyimpanan preprocessor artifact |
| `03_modeling.ipynb` | Model training, tuning, threshold optimization, feature importance, dan penyimpanan model artifact |

---


## 👨‍💻 Author

Portfolio project untuk demonstrasi end-to-end machine learning dengan FastAPI dan Streamlit.

---

## DEMO

ON PROGRESS