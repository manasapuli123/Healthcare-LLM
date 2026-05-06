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
# ROUTING LOGIC (NEW)
# -----------------------
def route_decision(confidence):
    if confidence >= 85:
        return "Auto-Approved"
    elif confidence >= 60:
        return "Needs Review"
    else:
        return "Auto-Denied"

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
    documents_default = "Clinical notes, imaging report"

elif sample == "Invalid Case":
    patient_default = "Mike Ross"
    procedure_default = "Surgery"
    diagnosis_default = ""
    insurance_default = "United Healthcare"
    documents_default = "Clinical notes"

else:
    patient_default = ""
    procedure_default = ""
    diagnosis_default = ""
    insurance_default = ""
    documents_default = ""

# -----------------------
# INPUT
# -----------------------
st.subheader("📝 Request Details")

patient = st.text_input("Patient Name", value=patient_default)
procedure = st.text_input("Procedure", value=procedure_default)
diagnosis = st.text_input("Diagnosis", value=diagnosis_default)
insurance = st.text_input("Insurance", value=insurance_default)

uploaded_file = st.file_uploader("Upload Clinical Notes (TXT)", type=["txt"])

if uploaded_file is not None:
    documents = uploaded_file.read().decode("utf-8")
    st.success(f"Uploaded file: {uploaded_file.name}")
else:
    documents = st.text_area("Or paste clinical notes here", value=documents_default)

evaluate_clicked = st.button("🚀 Evaluate Request", use_container_width=True)

# -----------------------
# CORE AI LOGIC
# -----------------------
def evaluate(diagnosis, documents):
    issues = []

    if not diagnosis:
        issues.append("missing diagnosis")

    if not documents or len(documents.strip()) < 1:
        issues.append("missing clinical notes")

    if "missing diagnosis" in issues:
        status = "Denied"
        confidence = 40
    elif issues:
        status = "Pending Information"
        confidence = 65
    else:
        status = "Approved"
        confidence = 90

    # Explainability (IMPROVED)
    explanation = []
    if "missing diagnosis" in issues:
        explanation.append("❌ Missing valid diagnosis")
    else:
        explanation.append("✅ Diagnosis provided")

    if "missing clinical notes" in issues:
        explanation.append("❌ Missing clinical documentation")
    else:
        explanation.append("✅ Supporting documentation present")

    return status, explanation, confidence

# -----------------------
# SAVE REVIEW DATA (NEW)
# -----------------------
def save_review(data):
    file_path = "reviews.csv"
    df = pd.DataFrame([data])

    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode="a", header=False, index=False)

# -----------------------
# OUTPUT
# -----------------------
if evaluate_clicked:
    status, explanation, confidence = evaluate(diagnosis, documents)

    # 🔥 NEW ROUTED DECISION
    final_status = route_decision(confidence)

    st.markdown(f"### 🧾 Final Decision: **{final_status}**")
    st.write(f"Confidence Score: {confidence}%")

    # -----------------------
    # EXPLANATION
    # -----------------------
    st.markdown("### 🧠 AI Reasoning")
    for item in explanation:
        st.write(item)

    # -----------------------
    # HUMAN-IN-THE-LOOP UI (NEW)
    # -----------------------
    if final_status == "Needs Review":
        st.warning("⚠️ This case requires human review")

        human_decision = st.radio(
            "Reviewer Decision:",
            ["Approve", "Deny"]
        )

        reviewer_notes = st.text_area("Reviewer Notes")

        if st.button("Submit Review"):
            st.success(f"Final Decision: {human_decision}")

            review_data = {
                "patient": patient,
                "ai_decision": final_status,
                "confidence": confidence,
                "human_decision": human_decision,
                "notes": reviewer_notes
            }

            save_review(review_data)

    # -----------------------
    # AUTO DECISIONS
    # -----------------------
    else:
        if final_status == "Auto-Approved":
            st.success("✅ Automatically approved based on high confidence")
        else:
            st.error("❌ Automatically denied due to insufficient data")

    # -----------------------
    # METRICS (NEW)
    # -----------------------
    if os.path.exists("reviews.csv"):
        df = pd.read_csv("reviews.csv")

        st.markdown("### 📊 Review Metrics")
        st.write("Total Reviews:", len(df))

        if "human_decision" in df.columns:
            override_rate = (df["ai_decision"] != df["human_decision"]).mean()
            st.write(f"Override Rate: {round(override_rate * 100, 2)}%")

    # -----------------------
    # REPORT
    # -----------------------
    report = f"""
Patient Name: {patient}
Procedure: {procedure}
Diagnosis: {diagnosis}
Insurance: {insurance}

AI Decision: {final_status}
Confidence: {confidence}%

Explanation:
{', '.join(explanation)}
"""

    st.download_button(
        label="📄 Download Report",
        data=report,
        file_name="prior_authorization_report.txt",
        mime="text/plain"
    )

# -----------------------
# FOOTER
# -----------------------
st.markdown("---")
st.caption("⚠️ Prototype for demonstration purposes only. Not for clinical use.")
