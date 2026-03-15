import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="Clinical AI Assistant",
    page_icon="🩺",
    layout="centered"
)

# ---------------------------
# DEMO INSTRUCTION
# ---------------------------

st.info("Tip: Click **Load Sample Clinical Notes** to quickly test the AI assistant.")

# ---------------------------
# STYLING
# ---------------------------

st.markdown("""
<style>

.stApp {
    background-color:#eaf7f4;
}

.header {
    background-color:#3aafa9;
    padding:15px;
    border-radius:10px;
    color:white;
    font-weight:bold;
}

.chat-container {
    height:450px;
    overflow-y:auto;
    padding:15px;
    background:white;
    border-radius:10px;
}

.user-msg {
    background:#dcf8c6;
    padding:10px;
    border-radius:10px;
    margin:6px;
    text-align:right;
}

.bot-msg {
    background:#f1f0f0;
    padding:10px;
    border-radius:10px;
    margin:6px;
}

textarea {
    border:2px solid black !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# LOAD API KEY
# ---------------------------

load_dotenv()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------------
# LOAD EMBEDDING MODEL
# ---------------------------

@st.cache_resource(show_spinner=False)
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ---------------------------
# LOAD MEDICAL KNOWLEDGE
# ---------------------------

@st.cache_resource(show_spinner=False)
def load_knowledge():

    with open("medical_knowledge.txt","r") as f:
        knowledge = f.read()

    chunks = knowledge.split("\n\n")

    embeddings = model.encode(chunks)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings).astype("float32"))

    return chunks, index

chunks, index = load_knowledge()

# ---------------------------
# SIDEBAR
# ---------------------------

st.sidebar.title("🩺 Clinical AI Assistant")

st.sidebar.write("""
Upload patient notes and chat with the assistant.

Powered by:
• FAISS RAG
• OpenAI LLM
""")

# ---------------------------
# HEADER
# ---------------------------

st.markdown(
"""
<div class="header">
👩‍⚕️ Medical AI Assistant
</div>
""",
unsafe_allow_html=True
)

sample_notes = """
Patient Name: John Doe
Age: 56
Chief Complaint: Chest pain and shortness of breath

Medical History:
Hypertension, Type 2 Diabetes

Medications:
Metformin 500mg
Lisinopril 10mg

Recent Labs:
Blood Pressure: 150/95
HbA1c: 7.8
LDL Cholesterol: 140

Physician Notes:
Patient reports intermittent chest discomfort for the past 2 days.
Recommend cardiac evaluation and ECG.
"""

if st.button("Load Sample Clinical Notes"):
    clinical_notes = sample_notes

# ---------------------------
# CLINICAL NOTES
# ---------------------------

clinical_notes = st.text_area(
    "Paste Clinical Notes",
    height=200
)

uploaded_file = st.file_uploader("Upload Medical Report (PDF)", type="pdf")

if uploaded_file:

    reader = PdfReader(uploaded_file)

    for page in reader.pages:
        text = page.extract_text()
        if text:
            clinical_notes += text

notes_input = st.text_area("Or paste clinical notes")

if notes_input:
    clinical_notes = notes_input

# ---------------------------
# CHAT MEMORY
# ---------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# DISPLAY CHAT
# ---------------------------

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:

    if msg["role"] == "user":

        st.markdown(
            f'<div class="user-msg">🧑 {msg["content"]}</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f'<div class="bot-msg">👩‍⚕️ {msg["content"]}</div>',
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# CHAT INPUT
# ---------------------------

user_input = st.chat_input("Ask a question about the patient")

if user_input:

    st.session_state.messages.append(
        {"role":"user","content":user_input}
    )

    if clinical_notes == "":
        reply = "Please upload or paste clinical notes first."

    else:

        with st.spinner("Assistant is typing..."):

            query_embedding = model.encode([user_input])

            distances, indices = index.search(
                np.array(query_embedding).astype("float32"), k=2
            )

            retrieved_chunks = [
                chunks[i] for i in indices[0]
            ]

            knowledge_context = "\n".join(retrieved_chunks)

            prompt = f"""
You are a clinical AI assistant.

Patient Notes:
{clinical_notes}

Medical Knowledge:
{knowledge_context}

Question:
{user_input}

Provide a helpful medical answer.
"""

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role":"user","content":prompt}]
            )

            reply = response.choices[0].message.content

    st.session_state.messages.append(
        {"role":"assistant","content":reply}
    )

    st.rerun()

# ---------------------------
# FOOTER
# ---------------------------

st.caption(
"⚠️ AI responses are informational and should be clinically verified."
)