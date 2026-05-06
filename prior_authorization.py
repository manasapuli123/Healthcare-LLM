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
# HEADER
# -----------------------
st.markdown("## 🏥 Prior Authorization AI Agent")
st.markdown("AI-powered workflow decision support with human-in-the-loop")

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
# AI EVALUATION LOGIC
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
# EVIDENCE EXTRACTION
# -----------------------
def extract_sentence(documents, keyword):
    sentences = documents.split(".")
    for sentence in sentences:
        if keyword.lower() in sentence.lower():
            return sentence.strip()
    return None

def highlight_text(text, keyword):
    return text.replace(keyword, f"**{keyword}**")

def get_evidence(diagnosis, documents):
    evidence = {}

    if diagnosis:
        match = extract_sentence(documents, diagnosis)
        if match:
            highlighted = highlight_text(match, diagnosis)
            evidence["diagnosis"] = f"✅ Found: {highlighted}"
        else:
            evidence["diagnosis"] = "⚠️ Diagnosis not clearly supported in notes"

    if not documents or len(documents.strip()) == 0:
        evidence["documents"] = "❌ No clinical notes provided"
    else:
        evidence["documents"] = "✅ Clinical notes provided"

    return evidence

# -----------------------
# SAVE REVIEW DATA
# -----------------------
def save_review(data):
    file_path = "reviews.csv"
    df = pd.DataFrame([data])

    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode="a", header=False, index=False)

# -----------------------
# INPUT FORM
# -----------------------
st.subheader("📝 Request Details")

patient = st.text_input("Patient Name")
procedure = st.text_input("Procedure")
diagnosis = st.text_input("Diagnosis")
insurance = st.text_input("Insurance")

uploaded_file = st.file_uploader("Upload Clinical Notes (TXT)", type=["txt"])

if uploaded_file is not None:
    documents = uploaded_file.read().decode("utf-8")
    st.success(f"Uploaded file: {uploaded_file.name}")
else:
    documents = st.text_area("Or paste clinical notes here")

evaluate_clicked = st.button("🚀 Evaluate Request", use_container_width=True)

# -----------------------
# OUTPUT
# -----------------------
if evaluate_clicked:
    status, explanation, confidence = evaluate(diagnosis, documents)
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
    # EVIDENCE
    # -----------------------
    evidence = get_evidence(diagnosis, documents)

    st.markdown("### 🔍 Supporting Evidence")
    st.write("**Diagnosis Evidence:**")
    st.info(evidence.get("diagnosis", "Not available"))

    st.write("**Documentation Check:**")
    st.info(evidence.get("documents", "Not available"))

    # -----------------------
    # HUMAN-IN-THE-LOOP
    # -----------------------
    if final_status == "Needs Review":
        st.warning("⚠️ This case requires human review")

        human_decision = st.radio("Reviewer Decision:", ["Approve", "Deny"])
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

    else:
        if final_status == "Auto-Approved":
            st.success("✅ Automatically approved")
        else:
            st.error("❌ Automatically denied")

    # -----------------------
    # METRICS
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

Evidence:
{evidence}
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
