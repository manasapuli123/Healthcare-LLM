import streamlit as st

st.title("🏥 Prior Authorization AI Agent")
st.markdown("Evaluate prior authorization requests and get decision support.")

# Inputs
st.subheader("Input Request")
patient = st.text_input("Patient Name")
procedure = st.text_input("Procedure")
diagnosis = st.text_input("Diagnosis")
insurance = st.text_input("Insurance")
documents = st.text_area("Documents Provided")

# Logic
def evaluate(diagnosis, documents):
    if not diagnosis:
        return "Denied", "Missing diagnosis"
    if "clinical notes" not in documents.lower():
        return "Pending Information", "Missing clinical notes"
    return "Approved", "All required info present"

# Button
if st.button("Evaluate Request"):
    status, reason = evaluate(diagnosis, documents)

    st.subheader("Evaluation Result")
    st.write("Status:", status)
    st.write("Reason:", reason)

st.caption("⚠️ Prototype for demonstration purposes only.")