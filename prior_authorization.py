import streamlit as st

st.set_page_config(
    page_title="Prior Authorization AI Agent",
    layout="wide",
)

# -----------------------
# Custom Styling (STARTUP LOOK)
# -----------------------
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .title {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
    }
    .subtitle {
        color: #6b7280;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------
# HEADER
# -----------------------
st.markdown('<div class="title">🏥 Prior Authorization AI Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered workflow decision support for healthcare authorization</div>', unsafe_allow_html=True)

# -----------------------
# SIDEBAR (STARTUP FEEL)
# -----------------------
st.sidebar.title("⚙️ Demo Controls")

sample = st.sidebar.selectbox(
    "Load Sample Scenario",
    ["None", "Missing Info", "Complete Case", "Invalid Case"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Use sample scenarios to quickly test the system.")

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
# LAYOUT (2 COLUMNS)
# -----------------------
col1, col2 = st.columns([1, 1])

# -----------------------
# INPUT CARD
# -----------------------
with col1:
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
# DECISION LOGIC
# -----------------------
def evaluate(diagnosis, documents):
    if not diagnosis:
        return "Denied", "Missing diagnosis", "High"
    if "clinical notes" not in documents.lower():
        return "Pending Information", "Missing clinical notes", "Medium"
    return "Approved", "All required information present", "High"

# -----------------------
# OUTPUT CARD
# -----------------------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📊 Decision Outcome")

    if evaluate_clicked:
        status, reason, confidence = evaluate(diagnosis, documents)

        # Status Badge
        if status == "Approved":
            st.success(f"✅ {status}")
        elif status == "Denied":
            st.error(f"❌ {status}")
        else:
            st.warning(f"⚠️ {status}")

        st.markdown("### Explanation")
        st.write(reason)

        st.markdown("### Confidence")
        st.write(confidence)

    else:
        st.info("Run evaluation to see results")

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# FOOTER
# -----------------------
st.markdown("---")
st.caption("⚠️ Prototype for demonstration purposes only. Not for clinical use.")
