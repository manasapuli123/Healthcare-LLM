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

/* App background */
.main {
    background-color: #f8fafc;
}

/* Card styling */
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
    margin-bottom: 10px;
}

/* Inputs */
input, textarea {
    background-color: #f9fafb !important;
}

/* Dropdown fix */
div[data-baseweb="select"] {
    background-color: #f9fafb !important;
    border-radius: 8px;
}
div[data-baseweb="select"] > div {
    background-color: #f9fafb !important;
}
div[data-baseweb="select"] span {
    background-color: #f9fafb !important;
}

/* 🔥 Remove empty blocks */
div[data-testid="stVerticalBlock"] > div:empty {
    display: none !important;
}

/* 🔥 Reduce spacing */
div[data-testid="stVerticalBlock"] {
    gap: 0.5rem;
}

/* ✅ Optional fix (ADD HERE) */
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
**Prior Authorization AI Agent**

Simulates real-world authorization workflows.

**What it does**
- Evaluates requests  
- Flags missing documentation  
- Assigns status  
- Suggests next steps  
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
# 🔥 Fix: absorb Streamlit's extra block
with st.container():
    st.markdown(
        "<div style='margin-top:-20px'></div>",
        unsafe_allow_html=True
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
st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("📝 Request Details")

patient = st.text_input("Patient Name", value=patient_default)
procedure = st.text_input("Procedure", value=procedure_default)
diagnosis = st.text_input("Diagnosis", value=diagnosis_default)
insurance = st.text_input("Insurance", value=insurance_default)
documents = st.text_area("Documents Provided", value=documents_default)

evaluate_clicked = st.button("🚀 Evaluate Request", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# LOGIC
# -----------------------
def evaluate(diagnosis, documents):
    if not diagnosis:
        return "Denied", "Missing diagnosis", 40
    if "clinical notes" not in documents.lower():
        return "Pending Information", "Missing clinical notes", 65
    return "Approved", "All required information present", 90

# -----------------------
# OUTPUT CARD
# -----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("📊 Decision Outcome")

if evaluate_clicked:
    status, reason, confidence = evaluate(diagnosis, documents)

    if status == "Approved":
        st.success(f"✅ {status}")
    elif status == "Denied":
        st.error(f"❌ {status}")
    else:
        st.warning(f"⚠️ {status}")

    st.markdown("### Explanation")
    st.write(reason)

    st.caption("Model confidence based on completeness of provided data")
    st.markdown("### Confidence Score")
    st.progress(confidence / 100)
    st.write(f"{confidence}% confidence")

else:
    st.info("Run evaluation to see results")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# FOOTER
# -----------------------
st.markdown("---")
st.caption("⚠️ Prototype for demonstration purposes only. Not for clinical use.")
