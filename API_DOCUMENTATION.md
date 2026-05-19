# API Documentation

Dokumentasi ini menjelaskan layanan FastAPI yang dipakai untuk prediksi customer churn. API ini menyediakan dua jalur prediksi:

- `/predict` untuk input yang sudah diencode
- `/predict_raw` untuk input raw yang lebih mudah dipakai manusia dan Streamlit

---

## Overview

**Base URL**

```text
http://127.0.0.1:8000
```

**Implementation file**

- [api/main.py](api/main.py)

**Perilaku penting**

- Model artefak dibaca dari `models/churn_model.joblib`
- Preprocessor artefak dibaca dari `models/preprocessor.joblib`
- `RawCustomer` memakai `extra = "ignore"`, jadi field tambahan seperti `customerID` akan diabaikan
- Validasi input dilakukan oleh Pydantic sebelum masuk ke logika prediksi

---

## Available Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/` | Health check dan status model |
| `GET` | `/meta` | Metadata model dan preprocessor |
| `POST` | `/predict` | Prediksi dari fitur encoded |
| `POST` | `/predict_raw` | Prediksi dari input raw |

---

## `GET /`

Health check untuk memastikan API aktif dan model berhasil diload.

### Response

```json
{
	"status": "ok",
	"model_loaded": true,
	"model_error": null
}
```

### Catatan

- `model_loaded: false` berarti artefak model tidak berhasil diload
- `model_error` akan berisi pesan error jika proses loading gagal

---

## `GET /meta`

Mengembalikan metadata model, threshold, dan status preprocessor.

### Response

```json
{
	"feature_names": [
		"SeniorCitizen",
		"Partner",
		"Dependents",
		"tenure",
		"PhoneService",
		"PaperlessBilling",
		"MonthlyCharges",
		"TotalCharges",
		"AvgMonthlyCharges",
		"TotalServices",
		"gender_Male",
		"MultipleLines_No phone service",
		"MultipleLines_Yes",
		"InternetService_Fiber optic",
		"InternetService_No",
		"OnlineSecurity_No internet service",
		"OnlineSecurity_Yes",
		"OnlineBackup_No internet service",
		"OnlineBackup_Yes",
		"DeviceProtection_No internet service",
		"DeviceProtection_Yes",
		"TechSupport_No internet service",
		"TechSupport_Yes",
		"StreamingTV_No internet service",
		"StreamingTV_Yes",
		"StreamingMovies_No internet service",
		"StreamingMovies_Yes",
		"Contract_One year",
		"Contract_Two year",
		"PaymentMethod_Credit card (automatic)",
		"PaymentMethod_Electronic check",
		"PaymentMethod_Mailed check",
		"TenureBucket_Established",
		"TenureBucket_Loyal",
		"TenureBucket_New"
	],
	"threshold": 0.5,
	"preprocessor_loaded": true
}
```

### Catatan

- `feature_names` diambil dari model artefak atau dari `preprocessor.joblib`
- `threshold` berasal dari artefak model
- `preprocessor_loaded` menunjukkan apakah `models/preprocessor.joblib` tersedia

---

## `POST /predict`

Prediksi menggunakan fitur yang sudah diencode. Endpoint ini cocok kalau preprocessing dilakukan di luar API.

### Request Model

Model ini sesuai class `Customer` di [api/main.py](api/main.py).

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `SeniorCitizen` | int | 0 atau 1 |
| `Partner` | int | 0 atau 1 |
| `Dependents` | int | 0 atau 1 |
| `tenure` | float | Nilai tenure yang sudah diproses |
| `PhoneService` | int | 0 atau 1 |
| `PaperlessBilling` | int | 0 atau 1 |
| `MonthlyCharges` | float | Nilai encoded/scaled sesuai pipeline |
| `TotalCharges` | float | Nilai encoded/scaled sesuai pipeline |
| `AvgMonthlyCharges` | float | Feature engineering hasil pipeline |
| `TotalServices` | float | Feature engineering hasil pipeline |
| `gender_Male` | int | 0 atau 1 |
| `MultipleLines_No phone service` | int | 0 atau 1 |
| `MultipleLines_Yes` | int | 0 atau 1 |
| `InternetService_Fiber optic` | int | 0 atau 1 |
| `InternetService_No` | int | 0 atau 1 |
| `OnlineSecurity_No internet service` | int | 0 atau 1 |
| `OnlineSecurity_Yes` | int | 0 atau 1 |
| `OnlineBackup_No internet service` | int | 0 atau 1 |
| `OnlineBackup_Yes` | int | 0 atau 1 |
| `DeviceProtection_No internet service` | int | 0 atau 1 |
| `DeviceProtection_Yes` | int | 0 atau 1 |
| `TechSupport_No internet service` | int | 0 atau 1 |
| `TechSupport_Yes` | int | 0 atau 1 |
| `StreamingTV_No internet service` | int | 0 atau 1 |
| `StreamingTV_Yes` | int | 0 atau 1 |
| `StreamingMovies_No internet service` | int | 0 atau 1 |
| `StreamingMovies_Yes` | int | 0 atau 1 |
| `Contract_One year` | int | 0 atau 1 |
| `Contract_Two year` | int | 0 atau 1 |
| `PaymentMethod_Credit card (automatic)` | int | 0 atau 1 |
| `PaymentMethod_Electronic check` | int | 0 atau 1 |
| `PaymentMethod_Mailed check` | int | 0 atau 1 |
| `TenureBucket_Established` | int | 0 atau 1 |
| `TenureBucket_Loyal` | int | 0 atau 1 |
| `TenureBucket_New` | int | 0 atau 1 |

### Example Request

```json
{
	"SeniorCitizen": 0,
	"Partner": 1,
	"Dependents": 0,
	"tenure": 1.3218,
	"PhoneService": 1,
	"PaperlessBilling": 0,
	"MonthlyCharges": 0.9787,
	"TotalCharges": 1.6598,
	"AvgMonthlyCharges": 0.9431,
	"TotalServices": 1.1081,
	"gender_Male": 1,
	"MultipleLines_No phone service": 0,
	"MultipleLines_Yes": 1,
	"InternetService_Fiber optic": 1,
	"InternetService_No": 0,
	"OnlineSecurity_No internet service": 0,
	"OnlineSecurity_Yes": 1,
	"OnlineBackup_No internet service": 0,
	"OnlineBackup_Yes": 1,
	"DeviceProtection_No internet service": 0,
	"DeviceProtection_Yes": 1,
	"TechSupport_No internet service": 0,
	"TechSupport_Yes": 1,
	"StreamingTV_No internet service": 0,
	"StreamingTV_Yes": 0,
	"StreamingMovies_No internet service": 0,
	"StreamingMovies_Yes": 0,
	"Contract_One year": 0,
	"Contract_Two year": 0,
	"PaymentMethod_Credit card (automatic)": 0,
	"PaymentMethod_Electronic check": 1,
	"PaymentMethod_Mailed check": 0,
	"TenureBucket_Established": 0,
	"TenureBucket_Loyal": 0,
	"TenureBucket_New": 1
}
```

### Response

```json
{
	"prediction": 0,
	"probability": 0.16672415351266023,
	"threshold": 0.4960121793609208
}
```

### Perilaku

- Jika `probability >= threshold`, hasil akan menjadi `prediction = 1`
- Jika model tidak memiliki `predict_proba`, API akan fallback ke `predict`
- Jika ada fitur yang hilang dari encoded input, response akan 400 untuk bagian validasi atau logika model

---

## `POST /predict_raw`

Endpoint ini adalah jalur yang direkomendasikan untuk aplikasi yang dipakai langsung oleh user, termasuk Streamlit. API akan melakukan preprocessing di dalam backend.

### Request Model

Model yang dipakai adalah `RawCustomer` di [api/main.py](api/main.py).

### Raw Fields

| Field | Type | Allowed Values |
|-------|------|----------------|
| `gender` | string | `Female`, `Male` |
| `SeniorCitizen` | int | `0`, `1` |
| `Partner` | string | `Yes`, `No` |
| `Dependents` | string | `Yes`, `No` |
| `tenure` | float | `>= 0` |
| `PhoneService` | string | `Yes`, `No` |
| `MultipleLines` | string | `No`, `Yes`, `No phone service` |
| `InternetService` | string | `DSL`, `Fiber optic`, `No` |
| `OnlineSecurity` | string | `No`, `Yes`, `No internet service` |
| `OnlineBackup` | string | `No`, `Yes`, `No internet service` |
| `DeviceProtection` | string | `No`, `Yes`, `No internet service` |
| `TechSupport` | string | `No`, `Yes`, `No internet service` |
| `StreamingTV` | string | `No`, `Yes`, `No internet service` |
| `StreamingMovies` | string | `No`, `Yes`, `No internet service` |
| `Contract` | string | `Month-to-month`, `One year`, `Two year` |
| `PaperlessBilling` | string | `Yes`, `No` |
| `PaymentMethod` | string | `Electronic check`, `Mailed check`, `Bank transfer (automatic)`, `Credit card (automatic)` |
| `MonthlyCharges` | float | `>= 0` |
| `TotalCharges` | float | `>= 0` |

### Perilaku penting

- `extra = "ignore"` pada `RawCustomer`
- Extra field seperti `customerID` di Swagger atau request client akan diabaikan
- Validation error tetap bisa muncul jika nilai enum atau type tidak sesuai

### Example Request

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

### Example Response

```json
{
	"prediction": 0,
	"probability": 0.16672415351266023,
	"threshold": 0.4960121793609208
}
```

### Langkah preprocessing di backend

1. Build DataFrame dari raw payload
2. Feature engineering:
	 - `AvgMonthlyCharges = TotalCharges / tenure`
	 - `TenureBucket`
	 - `TotalServices`
3. Mapping binary fields:
	 - `Partner`, `Dependents`, `PhoneService`, `PaperlessBilling`
4. One-hot encoding categorical fields
5. Align kolom ke `expected_columns` dari artifact preprocessing
6. Scaling numeric columns dengan `StandardScaler`
7. Predict dengan model artifact

---

## Status Codes

| Status | Meaning |
|--------|---------|
| `200` | Request berhasil dan hasil prediksi dikembalikan |
| `400` | Input valid secara format, tetapi ada masalah logika atau fitur yang hilang |
| `422` | Validation error dari Pydantic |
| `500` | Model/preprocessor error atau runtime exception |

---

## Error Examples

### 1. Validation Error

```json
{
	"detail": [
		{
			"loc": ["body", "gender"],
			"msg": "unexpected value; permitted: 'Female', 'Male'",
			"type": "value_error.const"
		}
	]
}
```

### 2. Model Not Loaded

```json
{
	"detail": "Model not loaded"
}
```

### 3. Preprocessor Not Loaded

```json
{
	"detail": "Preprocessor artifact not loaded (models/preprocessor.joblib)"
}
```

---

## Usage Examples

### Python `requests`

```python
import requests

payload = {
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

response = requests.post("http://127.0.0.1:8000/predict_raw", json=payload)
print(response.json())
```

### cURL

```bash
curl -X POST http://127.0.0.1:8000/predict_raw \
	-H "Content-Type: application/json" \
	-d '{
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
	}'
```

---

## Swagger UI

Interactive API docs tersedia di:

```text
http://127.0.0.1:8000/docs
```

Gunakan Swagger untuk:

- mencoba `GET /meta`
- mengisi payload `POST /predict_raw`
- menguji `POST /predict`

---

## Implementation Notes

- Model artefak disimpan sebagai dictionary dengan key `model`, `threshold`, dan `feature_names`
- Preprocessor artefak disimpan sebagai dictionary dengan key `expected_columns`, `scale_cols`, dan `scaler`
- `predict_raw` dipakai oleh Streamlit agar user tidak perlu mengisi fitur encoded
- `predict` berguna untuk integrasi sistem lain yang sudah punya preprocessing sendiri

---

## Related Files

- [api/main.py](api/main.py)
- [app/streamlit_app.py](app/streamlit_app.py)
- [README.md](README.md)

