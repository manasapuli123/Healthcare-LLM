import streamlit as st
import pandas as pd
import os

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Prior Authorization AI Agent",
    layout="centered",
)
st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background-color: #E6F2FF;
    }

    /* Text input fields */
    input, textarea {
        background-color: white !important;
    }

    /* Streamlit specific input containers */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: white !important;
    }

    /* File uploader */
    .stFileUploader {
        background-color: white !important;
        border-radius: 8px;
        padding: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
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
# ROUTING LOGIC
# -----------------------
def route_decision(confidence):
    if confidence >= 85:
        return "Auto-Approved"
    elif confidence >= 60:
        return "Needs Review"
    else:
        return "Auto-Denied"

# -----------------------
# CLINICAL NOTE VALIDATION
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
# SAMPLE SELECTOR
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
# 🔥 UPDATED SCENARIO LOGIC (FIXED)
# -----------------------
if "prev_sample" not in st.session_state:
    st.session_state["prev_sample"] = sample
    st.session_state["generated_notes"] = documents_default

if sample != st.session_state["prev_sample"]:

    if sample in ["None", "Missing Info"]:
        st.session_state["generated_notes"] = ""

    elif sample in ["Complete Case", "Invalid Case"]:
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

# SAMPLE GENERATOR
if st.button("✨ Generate Sample Clinical Notes"):
    st.session_state["generated_notes"] = (
        "Patient presents with lower back pain for 2 weeks. "
        "Symptoms worsening. MRI recommended to evaluate underlying cause."
    )

if uploaded_file is not None:
    documents = uploaded_file.read().decode("utf-8")
    st.success(f"Uploaded file: {uploaded_file.name}")
else:
    documents = st.text_area(
        "Or paste clinical notes here",
        value=st.session_state.get("generated_notes", ""),
        placeholder="Example: Patient presents with lower back pain for 2 weeks..."
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

evaluate_clicked = st.button("🚀 Evaluate Request", use_container_width=True)

# -----------------------
# CORE AI LOGIC
# -----------------------
def evaluate(diagnosis, documents):
    issues = []

    validation_status, _ = validate_clinical_notes(documents)

    if not diagnosis:
        issues.append("missing diagnosis")

    if validation_status == "invalid":
        issues.append("invalid clinical notes")

    if "missing diagnosis" in issues:
        status = "Denied"
        confidence = 40
    elif issues:
        status = "Pending Information"
        confidence = 65
    else:
        status = "Approved"
        confidence = 90

    explanation = []
    if "missing diagnosis" in issues:
        explanation.append("❌ Missing valid diagnosis")
    else:
        explanation.append("✅ Diagnosis provided")

    if "invalid clinical notes" in issues:
        explanation.append("❌ Clinical notes lack sufficient medical context")
    else:
        explanation.append("✅ Supporting documentation present")

    return status, explanation, confidence

# -----------------------
# OUTPUT
# -----------------------
if evaluate_clicked:
    status, explanation, confidence = evaluate(diagnosis, documents)
    final_status = route_decision(confidence)

    st.markdown(f"### 🧾 Final Decision: **{final_status}**")
    st.write(f"Confidence Score: {confidence}%")

    st.markdown("### 🧠 AI Reasoning")
    for item in explanation:
        st.write(item)

    if final_status == "Needs Review":
        st.warning("⚠️ Requires human review")

        human_decision = st.radio("Reviewer Decision:", ["Approve", "Deny"])
        reviewer_notes = st.text_area("Reviewer Notes")

        if st.button("Submit Review"):
            st.success(f"Final Decision: {human_decision}")

            pd.DataFrame([{
                "patient": patient,
                "ai_decision": final_status,
                "confidence": confidence,
                "human_decision": human_decision,
                "notes": reviewer_notes
            }]).to_csv(
                "reviews.csv",
                mode="a",
                header=not os.path.exists("reviews.csv"),
                index=False
            )

    else:
        st.success("Automated decision completed")

# -----------------------
# FOOTER
# -----------------------
st.markdown("---")
st.caption("⚠️ Prototype for demonstration purposes only. Not for clinical use.")
