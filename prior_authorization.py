import streamlit as st

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Prior Authorization AI Agent",
    layout="wide",
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
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
}

/* Input styling */
input, textarea {
    background-color: #f9fafb !important;
}

/* 🔥 FIX: Remove white bar in dropdown */
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

</style>
""", unsafe_allow_html=True)

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.title("🏥 Product Overview")

st.sidebar.markdown("""
**Prior Authorization AI Agent**

This tool simulates real-world healthcare authorization workflows.

### What it does:
- Evaluates prior authorization requests  
- Identifies missing documentation  
- Assigns workflow status  
- Recommends next steps  
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

st.markdown("---")

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
    procedure
