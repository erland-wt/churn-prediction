import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/predict_raw"

st.set_page_config(
    page_title="Customer Churn Predictor",
    page_icon="📉",
    layout="wide"
)

st.title("Customer Churn Prediction Dashboard")
st.caption("Input customer data, lalu lihat prediksi churn dan probability score.")

# ----------------------------
# Helpers
# ----------------------------
def yes_no_option(label, default="No"):
    return st.radio(label, ["No", "Yes"], horizontal=True, index=1 if default == "Yes" else 0)

def build_payload(form_values):
    # Payload raw yang sesuai dengan /predict_raw
    return {
        "gender": form_values["gender"],
        "SeniorCitizen": form_values["SeniorCitizen"],
        "Partner": form_values["Partner"],
        "Dependents": form_values["Dependents"],
        "tenure": form_values["tenure"],
        "PhoneService": form_values["PhoneService"],
        "MultipleLines": form_values["MultipleLines"],
        "InternetService": form_values["InternetService"],
        "OnlineSecurity": form_values["OnlineSecurity"],
        "OnlineBackup": form_values["OnlineBackup"],
        "DeviceProtection": form_values["DeviceProtection"],
        "TechSupport": form_values["TechSupport"],
        "StreamingTV": form_values["StreamingTV"],
        "StreamingMovies": form_values["StreamingMovies"],
        "Contract": form_values["Contract"],
        "PaperlessBilling": form_values["PaperlessBilling"],
        "PaymentMethod": form_values["PaymentMethod"],
        "MonthlyCharges": form_values["MonthlyCharges"],
        "TotalCharges": form_values["TotalCharges"],
    }

def call_api(payload):
    response = requests.post(API_URL, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

def churn_label(prediction):
    return "Churn" if int(prediction) == 1 else "No Churn"

def risk_badge(probability):
    if probability is None:
        return "Unknown"
    if probability >= 0.75:
        return "High Risk"
    if probability >= 0.50:
        return "Medium Risk"
    return "Low Risk"


# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.header("Model Info")
st.sidebar.write("API endpoint:", API_URL)

st.sidebar.divider()
show_example = st.sidebar.checkbox("Gunakan contoh input", value=False)

if show_example:
    st.sidebar.success("Contoh input aktif. Kamu bisa ubah nilainya di form.")


# ----------------------------
# Form layout
# ----------------------------
with st.form("churn_form"):
    st.subheader("Customer Profile")

    col1, col2, col3 = st.columns(3)

    with col1:
        gender = st.selectbox("Gender", ["Female", "Male"])
        SeniorCitizen = st.selectbox("Senior Citizen", [0, 1], index=0)
        Partner = yes_no_option("Partner", default="Yes")
        Dependents = yes_no_option("Dependents", default="No")
        tenure = st.number_input("Tenure (months)", min_value=0.0, value=12.0, step=1.0)

    with col2:
        PhoneService = yes_no_option("Phone Service", default="Yes")
        MultipleLines = st.selectbox(
            "Multiple Lines",
            ["No", "Yes", "No phone service"],
            index=0
        )
        InternetService = st.selectbox(
            "Internet Service",
            ["DSL", "Fiber optic", "No"],
            index=1
        )
        OnlineSecurity = st.selectbox(
            "Online Security",
            ["No", "Yes", "No internet service"],
            index=0
        )

    with col3:
        OnlineBackup = st.selectbox(
            "Online Backup",
            ["No", "Yes", "No internet service"],
            index=1
        )
        DeviceProtection = st.selectbox(
            "Device Protection",
            ["No", "Yes", "No internet service"],
            index=0
        )
        TechSupport = st.selectbox(
            "Tech Support",
            ["No", "Yes", "No internet service"],
            index=0
        )
        StreamingTV = st.selectbox(
            "Streaming TV",
            ["No", "Yes", "No internet service"],
            index=1
        )

    st.divider()

    col4, col5, col6 = st.columns(3)

    with col4:
        StreamingMovies = st.selectbox(
            "Streaming Movies",
            ["No", "Yes", "No internet service"],
            index=0
        )
        Contract = st.selectbox(
            "Contract",
            ["Month-to-month", "One year", "Two year"],
            index=0
        )
        PaperlessBilling = yes_no_option("Paperless Billing", default="Yes")

    with col5:
        PaymentMethod = st.selectbox(
            "Payment Method",
            [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
            ],
            index=0
        )
        MonthlyCharges = st.number_input("Monthly Charges", min_value=0.0, value=70.0, step=0.1)
        TotalCharges = st.number_input("Total Charges", min_value=0.0, value=800.0, step=0.1)

    with col6:
        st.info(
            "Tips:\n"
            "- Jika `tenure` kecil dan `Contract` month-to-month, risiko churn biasanya lebih tinggi.\n"
            "- `TotalCharges` sebaiknya konsisten dengan `tenure` dan `MonthlyCharges`."
        )

    submitted = st.form_submit_button("Predict Churn")


# ----------------------------
# Prediction
# ----------------------------
if submitted:
    form_values = {
        "gender": gender,
        "SeniorCitizen": SeniorCitizen,
        "Partner": Partner,
        "Dependents": Dependents,
        "tenure": tenure,
        "PhoneService": PhoneService,
        "MultipleLines": MultipleLines,
        "InternetService": InternetService,
        "OnlineSecurity": OnlineSecurity,
        "OnlineBackup": OnlineBackup,
        "DeviceProtection": DeviceProtection,
        "TechSupport": TechSupport,
        "StreamingTV": StreamingTV,
        "StreamingMovies": StreamingMovies,
        "Contract": Contract,
        "PaperlessBilling": PaperlessBilling,
        "PaymentMethod": PaymentMethod,
        "MonthlyCharges": MonthlyCharges,
        "TotalCharges": TotalCharges,
    }

    payload = build_payload(form_values)

    with st.spinner("Mengirim data ke API..."):
        try:
            result = call_api(payload)

            prediction = result.get("prediction")
            probability = result.get("probability")
            threshold = result.get("threshold")

            st.success("Prediksi selesai")

            result_col1, result_col2, result_col3 = st.columns(3)
            with result_col1:
                st.metric("Prediction", churn_label(prediction))
            with result_col2:
                if probability is not None:
                    st.metric("Churn Probability", f"{probability:.4f}")
                else:
                    st.metric("Churn Probability", "-")
            with result_col3:
                st.metric("Threshold", f"{threshold:.4f}" if threshold is not None else "-")

            if probability is not None:
                st.progress(min(max(probability, 0.0), 1.0))
                st.write(f"Risk level: **{risk_badge(probability)}**")

                score_df = pd.DataFrame(
                    {
                        "Class": ["No Churn", "Churn"],
                        "Score": [1 - probability, probability]
                    }
                )
                st.bar_chart(score_df.set_index("Class"))

            with st.expander("Lihat payload yang dikirim ke API"):
                st.json(payload)

            with st.expander("Lihat response lengkap"):
                st.json(result)

        except requests.exceptions.RequestException as e:
            st.error("Gagal menghubungi API.")
            st.exception(e)
        except Exception as e:
            st.error("Terjadi error saat prediksi.")
            st.exception(e)