import streamlit as st

st.set_page_config(page_title="Prior Authorization AI Agent", layout="centered")

st.title("🏥 Prior Authorization AI Agent")
st.markdown("Evaluate prior authorization requests and get decision support.")

st.divider()

# Sample selector
st.markdown("👉 Select a sample scenario or enter your own data below")

sample = st.selectbox(
    "Try a sample scenario:",
    ["None", "Missing Info", "Complete Case", "Invalid Case"]
)

# Pre-fill values based on selection
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

# Input section
st.subheader("📝 Input Request")

patient = st.text_input("Patient Name", value=patient_default)
procedure = st.text_input("Procedure", value=procedure_default)
diagnosis = st.text_input("Diagnosis", value=diagnosis_default)
insurance = st.text_input("Insurance", value=insurance_default)
documents = st.text_area("Documents Provided", value=documents_default)

st.divider()

# Decision logic
def evaluate(diagnosis, documents):
    if not diagnosis:
        return "Denied", "Missing diagnosis", "High"
    if "clinical notes" not in documents.lower():
        return "Pending Information", "Missing clinical notes", "Medium"
    return "Approved", "All required information present", "High"

# Button
if st.button("🔍 Evaluate Request"):
    status, reason, confidence = evaluate(diagnosis, documents)

    st.subheader("📊 Evaluation Result")

    if status == "Approved":
        st.success(f"Status: {status}")
    elif status == "Denied":
        st.error(f"Status: {status}")
    else:
        st.warning(f"Status: {status}")

    st.info(f"Reason: {reason}")
    st.write(f"**Confidence:** {confidence}")

st.divider()

st.caption("⚠️ This is a prototype for demonstration purposes only.")
