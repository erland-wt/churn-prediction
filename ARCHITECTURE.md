# System Architecture

Dokumen ini menjelaskan arsitektur project customer churn prediction dari sisi komponen, alur data, dan peran masing-masing file. Tujuannya supaya struktur project mudah dipahami, baik saat dibaca sendiri maupun ketika dipresentasikan di portfolio.

---

## Komponen Utama

### 1. Data Layer

**Raw dataset**
- File: `dataset/raw/Telco-Customer-Churn.csv`
- Sumber data untuk seluruh proses EDA, preprocessing, dan modeling

**Processed dataset**
- File: `dataset/processed/X_train.csv`
- File: `dataset/processed/X_test.csv`
- File: `dataset/processed/y_train.csv`
- File: `dataset/processed/y_test.csv`
- Digunakan ulang oleh notebook modeling agar pipeline tetap konsisten

### 2. Notebook Layer

**`notebooks/01_eda.ipynb`**
- Melihat distribusi target
- Mengecek fitur kategorikal dan numerik
- Membuat visualisasi awal dan insight data

**`notebooks/02_preprocessing.ipynb`**
- Cleaning data
- Feature engineering
- Binary mapping
- One-hot encoding
- Scaling dengan StandardScaler
- Penyimpanan `preprocessor.joblib`

**`notebooks/03_modeling.ipynb`**
- Load data processed
- Bandingkan beberapa model
- Hyperparameter tuning dengan RandomizedSearchCV
- Threshold optimization
- Feature importance analysis
- Penyimpanan `churn_model.joblib`

### 3. API Layer

**File**: `api/main.py`

Tugasnya:
- Memuat artefak model dan preprocessor
- Menyediakan endpoint health check, metadata, dan prediksi
- Memvalidasi input dengan Pydantic
- Melakukan preprocessing input raw sebelum inferensi
- Mengembalikan response JSON yang konsisten

### 4. UI Layer

**File**: `app/streamlit_app.py`

Tugasnya:
- Menyediakan form input customer
- Mengirim payload ke endpoint `/predict_raw`
- Menampilkan hasil prediksi, probability, threshold, dan risk level
- Menampilkan payload dan response agar proses mudah ditelusuri

### 5. Artifact Layer

**Model artefak**
- File: `models/churn_model.joblib`
- Berisi model final, threshold, dan feature names

**Preprocessor artefak**
- File: `models/preprocessor.joblib`
- Berisi `expected_columns`, `scale_cols`, dan fitted `scaler`

---

## Alur Data

### A. Raw Prediction Flow (`/predict_raw`)

1. User mengisi form di Streamlit atau Swagger
2. Request dikirim ke FastAPI sebagai JSON
3. Pydantic memvalidasi schema `RawCustomer`
4. Backend membuat DataFrame dari payload
5. Backend melakukan feature engineering:
   - `AvgMonthlyCharges`
   - `TenureBucket`
   - `TotalServices`
6. Backend melakukan binary mapping untuk field tertentu
7. Backend melakukan one-hot encoding untuk kolom kategorikal
8. Backend menyesuaikan kolom ke `expected_columns`
9. Backend melakukan scaling untuk kolom numerik tertentu
10. Model memprediksi probability
11. Threshold dipakai untuk menentukan class final
12. Response JSON dikirim kembali ke client

### B. Encoded Prediction Flow (`/predict`)

1. Client mengirim fitur yang sudah encoded
2. Pydantic memvalidasi `Customer`
3. Backend membentuk DataFrame dari payload
4. Data diteruskan langsung ke model
5. Model mengembalikan probability atau class prediction

---

## Desain Preprocessing

Preprocessing dipisah dari model agar transformasi data tetap konsisten antara training dan inference.

### Feature Engineering

- `AvgMonthlyCharges = TotalCharges / tenure`
- `TenureBucket`
  - `New` untuk tenure <= 12
  - `Early` untuk tenure <= 24
  - `Established` untuk tenure <= 48
  - `Loyal` untuk tenure > 48
- `TotalServices` = jumlah layanan aktif bernilai `Yes`

### Encoding

**Binary mapping**
- `Partner`
- `Dependents`
- `PhoneService`
- `PaperlessBilling`

**One-hot encoding**
- `gender`
- `MultipleLines`
- `InternetService`
- `OnlineSecurity`
- `OnlineBackup`
- `DeviceProtection`
- `TechSupport`
- `StreamingTV`
- `StreamingMovies`
- `Contract`
- `PaymentMethod`
- `TenureBucket`

### Scaling

Kolom numerik yang disimpan dalam `scale_cols`:

- `tenure`
- `MonthlyCharges`
- `TotalCharges`
- `AvgMonthlyCharges`
- `TotalServices`

Scaler yang digunakan adalah `StandardScaler` dan disimpan ke `preprocessor.joblib`.

---

## Strategi Validasi API

### `Customer`

Dipakai untuk endpoint `/predict`.

Karakteristik:
- Berisi fitur encoded
- Field harus lengkap sesuai training columns
- Cocok untuk integrasi dengan pipeline yang sudah melakukan preprocessing sendiri

### `RawCustomer`

Dipakai untuk endpoint `/predict_raw`.

Karakteristik:
- Berisi input raw yang mudah dipahami user
- Menggunakan `Literal` untuk nilai kategori
- Menggunakan `Field(..., ge=0, le=1)` atau `Field(..., ge=0)` untuk constraint numerik
- Menggunakan `extra = "ignore"` agar field tambahan seperti `customerID` tidak memicu error

---

## Flow Artefak

### `models/churn_model.joblib`

Disimpan sebagai dictionary dengan isi utama:

```python
{
    "model": final_model_fitted,
    "threshold": final_threshold,
    "feature_names": X_train.columns.tolist()
}
```

### `models/preprocessor.joblib`

Disimpan sebagai dictionary dengan isi utama:

```python
{
    "expected_columns": X_train.columns.tolist(),
    "scale_cols": scale_cols,
    "scaler": scaler
}
```

Artefak ini dipakai saat inference supaya transformasi input tetap sama dengan proses training.

---

## Topologi Deployment

### Current Local Setup

- `.venv-api` untuk FastAPI
- `.venv-streamlit` untuk Streamlit
- Dua environment dipisah agar dependency tidak saling konflik

### Kenapa pakai dua virtual environment

- FastAPI dan Streamlit punya dependency yang berbeda
- Pemisahan environment mengurangi risiko konflik package
- Workflow jadi lebih aman untuk development dan demo portfolio

---

## Tanggung Jawab File

| File | Responsibility |
|------|----------------|
| `notebooks/01_eda.ipynb` | Exploratory data analysis |
| `notebooks/02_preprocessing.ipynb` | Cleaning, feature engineering, preprocessing artifact |
| `notebooks/03_modeling.ipynb` | Training, tuning, evaluation, model artifact |
| `api/main.py` | FastAPI service dan inference logic |
| `app/streamlit_app.py` | Dashboard UI dan API client |
| `models/churn_model.joblib` | Final model artifact |
| `models/preprocessor.joblib` | Preprocessing artifact |

---

## Prinsip Arsitektur

- **Separation of concerns**: preprocessing, API, dan UI dipisah
- **Reproducibility**: artefak preprocessing dan model disimpan
- **Validation-first design**: Pydantic menolak input yang salah lebih awal
- **User-friendly interface**: Streamlit memakai raw endpoint agar mudah dipakai
- **Traceability**: response menampilkan payload dan hasil prediksi untuk debugging

---

## Dokumentasi Terkait

- [README.md](README.md)
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- [api/main.py](api/main.py)
- [app/streamlit_app.py](app/streamlit_app.py)
