import streamlit as st
import pandas as pd
import os
from datetime import datetime

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Prior Authorization AI Agent",
    layout="centered",
)

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.title("🏥 Product Overview")
st.sidebar.markdown("""
### Prior Authorization AI Agent
AI-powered decision support tool with human-in-the-loop review.
""")

# -----------------------
# HEADER
# -----------------------
st.markdown("## 🏥 Prior Authorization AI Agent")
st.markdown("AI-powered workflow decision support with human review")

# -----------------------
# THRESHOLDS (NEW)
# -----------------------
st.markdown("### ⚙️ Decision Thresholds")

approve_threshold = st.slider("Auto-Approve Threshold", 50, 100, 85)
review_threshold = st.slider("Review Threshold", 0, approve_threshold, 60)

def route_decision(confidence):
    if confidence >= approve_threshold:
        return "Auto-Approved"
    elif confidence >= review_threshold:
        return "Needs Review"
    else:
        return "Auto-Denied"

# -----------------------
# VALIDATION
# -----------------------
def validate_clinical_notes(documents):
    if not documents or len(documents.strip()) < 20:
        return "invalid", "Clinical notes are too short"

    keywords = ["pain", "injury", "history", "symptoms", "diagnosis", "report"]
    score = sum(1 for word in keywords if word in documents.lower())

    if score >= 2:
        return "valid", "Clinical notes look sufficient"
    elif score == 1:
        return "weak", "Limited clinical detail detected"
    else:
        return "invalid", "Notes lack clinical context"

# -----------------------
# SCENARIO
# -----------------------
sample = st.selectbox(
    "Scenario",
    ["None", "Missing Info", "Complete Case", "Invalid Case"]
)

# -----------------------
# SAMPLE DATA
# -----------------------
if sample == "Missing Info":
    patient_default = "John Doe"
    procedure_default = "MRI"
    diagnosis_default = "Lower back pain"
    insurance_default = "Aetna"
    documents_default = ""

elif sample == "Complete Case":
    patient_default = "Sarah Lee"
    procedure_default = "CT Scan"
    diagnosis_default = "Head injury"
    insurance_default = "Cigna"
    documents_default = "Patient presents with head injury. Symptoms include dizziness and pain."

elif sample == "Invalid Case":
    patient_default = "Mike Ross"
    procedure_default = "Surgery"
    diagnosis_default = ""
    insurance_default = "United Healthcare"
    documents_default = "Hello test text"

else:
    patient_default = ""
    procedure_default = ""
    diagnosis_default = ""
    insurance_default = ""
    documents_default = ""

# -----------------------
# STATE MANAGEMENT
# -----------------------
if "prev_sample" not in st.session_state:
    st.session_state["prev_sample"] = sample
    st.session_state["generated_notes"] = documents_default

if sample != st.session_state["prev_sample"]:
    if sample in ["None", "Missing Info"]:
        st.session_state["generated_notes"] = ""
    else:
        st.session_state["generated_notes"] = documents_default

    st.session_state["prev_sample"] = sample

# -----------------------
# INPUT
# -----------------------
st.subheader("📝 Request Details")

patient = st.text_input("Patient Name", value=patient_default)
procedure = st.text_input("Procedure", value=procedure_default)
diagnosis = st.text_input("Diagnosis", value=diagnosis_default)
insurance = st.text_input("Insurance", value=insurance_default)

uploaded_file = st.file_uploader("Upload Clinical Notes (TXT)", type=["txt"])

if st.button("✨ Generate Sample Clinical Notes"):
    st.session_state["generated_notes"] = (
        "Patient presents with lower back pain for 2 weeks. Symptoms worsening. MRI recommended."
    )

if uploaded_file is not None:
    documents = uploaded_file.read().decode("utf-8")
else:
    documents = st.text_area(
        "Clinical Notes",
        value=st.session_state.get("generated_notes", "")
    )

# -----------------------
# VALIDATION DISPLAY
# -----------------------
validation_status, validation_msg = validate_clinical_notes(documents)

if validation_status == "valid":
    st.success(validation_msg)
elif validation_status == "weak":
    st.warning(validation_msg)
else:
    st.error(validation_msg)

evaluate_clicked = st.button("🚀 Evaluate Request")

# -----------------------
# EVALUATION (UPDATED)
# -----------------------
def evaluate(diagnosis, documents):
    score = 0
    breakdown = {}
    issues = []

    validation_status, _ = validate_clinical_notes(documents)

    if not diagnosis:
        breakdown["Diagnosis"] = -30
        issues.append("missing diagnosis")
    else:
        breakdown["Diagnosis"] = +30
        score += 30

    if validation_status == "invalid":
        breakdown["Clinical Notes"] = -25
        issues.append("invalid clinical notes")
    elif validation_status == "weak":
        breakdown["Clinical Notes"] = -10
        score += 10
    else:
        breakdown["Clinical Notes"] = +25
        score += 25

    confidence = max(0, min(100, score))

    if "missing diagnosis" in issues:
        status = "Denied"
    elif issues:
        status = "Pending Information"
    else:
        status = "Approved"

    return status, confidence, breakdown

# -----------------------
# OUTPUT
# -----------------------
if evaluate_clicked:
    status, confidence, breakdown = evaluate(diagnosis, documents)
    final_status = route_decision(confidence)

    st.markdown(f"### 🧾 Final Decision: **{final_status}**")
    st.write(f"Confidence Score: {confidence}%")

    # 🔥 Confidence Breakdown
    st.markdown("### 📊 Confidence Breakdown")
    for k, v in breakdown.items():
        st.write(f"{k}: {v:+}")

    # -----------------------
    # HUMAN-IN-THE-LOOP
    # -----------------------
    if final_status == "Needs Review":
        human_decision = st.radio("Reviewer Decision:", ["Approve", "Deny"])
        notes = st.text_area("Reviewer Notes")

        if st.button("Submit Review"):
            record = {
                "timestamp": datetime.now(),
                "patient": patient,
                "ai_decision": final_status,
                "confidence": confidence,
                "human_decision": human_decision,
                "notes": notes
            }

            pd.DataFrame([record]).to_csv(
                "reviews.csv",
                mode="a",
                header=not os.path.exists("reviews.csv"),
                index=False
            )

            st.success("Review saved")

    else:
        st.success("Automated decision completed")

# -----------------------
# AUDIT TRAIL (NEW)
# -----------------------
if os.path.exists("reviews.csv"):
    st.markdown("### 📜 Decision Audit Trail")
    df = pd.read_csv("reviews.csv")
    st.dataframe(df.tail(10))

# -----------------------
# FOOTER
# -----------------------
st.markdown("---")
st.caption("⚠️ Prototype for demonstration purposes only.")
