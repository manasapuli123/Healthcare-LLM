import streamlit as st

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Prior Authorization AI Agent",
    layout="centered",
)

# -----------------------
# STYLES
# -----------------------
st.markdown("""
<style>

/* -----------------------
   APP BACKGROUND
----------------------- */

/* 🌊 FULL APP BACKGROUND */
[data-testid="stAppViewContainer"] {
    background-color: #eef6ff;
}

/* -----------------------
   HEADER SPACING
----------------------- */
.block-container {
    padding-top: 2rem !important;
}

/* -----------------------
   CARD STYLE
----------------------- */
.card {
    background-color: white;
    padding: 24px;
    border-radius: 14px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 16px;
    border: 1px solid #f1f5f9;
}

/* -----------------------
   INPUT FIELDS
----------------------- */
input, textarea {
    background-color: #f9fafb !important;
}

/* -----------------------
   DROPDOWN (FIXED + COMPACT)
----------------------- */

/* actual dropdown element (controls height) */
div[data-baseweb="select"] > div {
    background-color: #f9fafb !important;
    border-radius: 8px;
    min-height: 34px !important;
    padding-top: 2px !important;
    padding-bottom: 2px !important;
}

/* remove white strip inside */
div[data-baseweb="select"] span {
    background-color: #f9fafb !important;
}

/* reduce spacing below dropdown */
div[data-testid="stSelectbox"] {
    margin-bottom: 4px !important;
}

/* -----------------------
   LAYOUT SPACING
----------------------- */

/* remove empty blocks */
div[data-testid="stVerticalBlock"] > div:empty {
    display: none !important;
}

/* tighten vertical spacing */
div[data-testid="stVerticalBlock"] {
    gap: 0.3rem;
}

/* remove gap after cards */
.card + div {
    margin-top: 0 !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.title("🏥 Product Overview")

st.sidebar.markdown("""
### Prior Authorization AI Agent

An AI-powered decision support tool that simulates real-world healthcare authorization workflows.

---

### 🚀 What this product does
- Evaluates prior authorization requests  
- Analyzes clinical inputs and documentation  
- Generates approval decisions (Approved / Pending / Denied)  
- Provides clear explanations and recommended actions  

---

### 🧠 Key Capabilities
- Multi-factor decision logic (diagnosis + documentation)  
- Confidence scoring for each decision  
- Clinical reasoning-style explanations  
- File-based input support (clinical notes upload)  

---

### 📄 Output
- Structured decision summary  
- Actionable next steps  
- Downloadable report for audit/documentation  

---

### 💡 Why this matters
Prior authorization is a critical bottleneck in healthcare.  
This tool demonstrates how AI can streamline decision-making, improve transparency, and reduce manual review effort.

---

### ⚠️ Note
This is a prototype for demonstration purposes only.
""")

# -----------------------
# HEADER
# -----------------------
st.markdown("## 🏥 Prior Authorization AI Agent")
st.markdown("AI-powered workflow decision support for healthcare authorization")

# -----------------------
# SAMPLE SELECTOR
# -----------------------
st.markdown("### 🎯 Try a Sample Scenario")

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
# INPUT CARD
# -----------------------
with st.container():

    st.subheader("📝 Request Details")

    patient = st.text_input("Patient Name", value=patient_default)
    procedure = st.text_input("Procedure", value=procedure_default)
    diagnosis = st.text_input("Diagnosis", value=diagnosis_default)
    insurance = st.text_input("Insurance", value=insurance_default)

    uploaded_file = st.file_uploader(
        "Upload Clinical Notes (TXT)",
        type=["txt"]
    )

    if uploaded_file is not None:
        documents = uploaded_file.read().decode("utf-8")
        st.success(f"Uploaded file: {uploaded_file.name}")
    else:
        documents = st.text_area(
            "Or paste clinical notes here",
            value=documents_default
        )

    evaluate_clicked = st.button("🚀 Evaluate Request", use_container_width=True)
    
# -----------------------
# LOGIC
# -----------------------
def evaluate(diagnosis, documents):
    issues = []
    
    if not diagnosis:
        issues.append("missing diagnosis")

    if not documents or len(documents.strip()) < 20:
        issues.append("missing clinical notes")

    # Decision logic
    if "missing diagnosis" in issues:
        status = "Denied"
        confidence = 40
    elif issues:
        status = "Pending Information"
        confidence = 65
    else:
        status = "Approved"
        confidence = 90

    # Build explanation dynamically
    if not issues:
        explanation = (
            "The request meets medical necessity criteria based on the provided diagnosis "
            "and supporting clinical documentation. All required information is complete."
        )
    else:
        explanation = "The request requires additional review due to the following issues: "

        if "missing diagnosis" in issues:
            explanation += "a valid diagnosis is not provided. "

        if "missing clinical notes" in issues:
            explanation += "supporting clinical documentation is missing. "

        explanation += "Please provide the required information to proceed."

    return status, explanation, confidence

# -----------------------
# OUTPUT CARD
# -----------------------
if evaluate_clicked:
    status, reason, confidence = evaluate(diagnosis, documents)

    # Status
    if status == "Approved":
        st.success(f"✅ {status}")
    elif status == "Denied":
        st.error(f"❌ {status}")
    else:
        st.warning(f"⚠️ {status}")

    # Explanation
    st.markdown("### 🧠 AI Explanation")
    st.write(reason)

    # Recommended action
    st.markdown("### 📌 Recommended Action")
    if status == "Denied":
        st.error("Update and resubmit with required diagnosis information.")
    elif status == "Pending Information":
        st.warning("Upload missing clinical notes to proceed with review.")
    else:
        st.success("No further action required. Request approved.")

    # Confidence
    st.markdown("### Confidence Score")
    st.progress(confidence / 100)
    st.write(f"{confidence}% confidence")

    # 🔥 REPORT
    report = f"""
Prior Authorization Report
--------------------------

Patient Name: {patient}
Procedure: {procedure}
Diagnosis: {diagnosis}
Insurance: {insurance}

Decision: {status}
Confidence: {confidence}%

Explanation:
{reason}

Recommended Action:
{"Update and resubmit with required diagnosis information." if status == "Denied" else
 "Upload missing clinical notes to proceed with review." if status == "Pending Information" else
 "No further action required. Request approved."}
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
