import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
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

st.info("Tip: Click **Load Sample Clinical Notes** to quickly test the AI assistant.")

# ---------------------------
# STYLING
# ---------------------------
st.markdown("""
<style>

/* ---------- BASE UI ---------- */

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

/* Buttons */

.stButton>button {
    background-color:#3aafa9;
    color:white;
    border-radius:8px;
    border:none;
    padding:10px 16px;
    font-weight:500;
}

.stButton>button:hover {
    background-color:#2f8f89;
}

/* Chat bubbles */

.user-msg {
    background:#DCF8C6;
    padding:12px;
    border-radius:12px;
    margin:8px;
    text-align:right;
    color:black;
    max-width:70%;
    margin-left:auto;
}

.bot-msg {
    background:#F1F0F0;
    padding:12px;
    border-radius:12px;
    margin:8px;
    color:black;
    max-width:70%;
}

/* ---------- LIGHT MODE ---------- */

@media (prefers-color-scheme: light) {

body, p, span, div, label {
    color:#1a1a1a;
}

textarea {
    color:#1a1a1a;
}

[data-testid="stFileUploader"] span {
    color:#1a1a1a;
}

[data-testid="stChatInput"] textarea {
    color:#1a1a1a;
}

}

/* ---------- DARK MODE ---------- */

@media (prefers-color-scheme: dark) {

/* Global text */

body, p, span, div, label {
    color: white !important;
}

/* Text area */

textarea {
    color: white !important;
}

/* Chat input */

[data-testid="stChatInput"] textarea {
    color: white !important;
}

/* Drag & Drop uploader */

[data-testid="stFileUploaderDropzone"] {
    color: white !important;
}

[data-testid="stFileUploaderDropzone"] span {
    color: white !important;
}

[data-testid="stFileUploaderDropzone"] div {
    color: white !important;
}

/* Browse files button */

[data-testid="stFileUploader"] button {
    color: white !important;
    border-color: white !important;
}

/* Upload helper text */

[data-testid="stFileUploader"] small {
    color: white !important;
}

/* Upload icon */

[data-testid="stFileUploader"] svg {
    color: white !important;
}

/* Top Streamlit toolbar (>>, Share, Deploy icons) */

header, header * {
    color: white !important;
}

/* Chat placeholder */

[data-testid="stChatInput"] input::placeholder {
    color: white !important;
}

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

# ---------------------------
# SAMPLE CLINICAL NOTES
# ---------------------------

sample_notes = """
Patient Name: John Smith
Age: 58
Chief Complaint: Chest pain and shortness of breath

Medical History:
Hypertension
Type 2 Diabetes
Hyperlipidemia

Medications:
Metformin 500 mg twice daily
Lisinopril 10 mg daily
Atorvastatin 20 mg daily

Lab Results:
LDL Cholesterol: 145 mg/dL
HbA1c: 7.9%

Physician Notes:
Patient reports intermittent chest discomfort during mild exertion.
Recommend ECG and cardiology follow-up.
"""

if "clinical_notes" not in st.session_state:
    st.session_state.clinical_notes = ""

if st.button("Load Sample Clinical Notes"):
    st.session_state.clinical_notes = sample_notes

# ---------------------------
# CLINICAL NOTES INPUT
# ---------------------------

uploaded_file = st.file_uploader("Upload Medical Report (PDF)", type="pdf")

if uploaded_file:

    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    st.session_state.clinical_notes = text

clinical_notes = st.text_area(
    "Paste Clinical Notes",
    value=st.session_state.clinical_notes,
    height=200
)

st.session_state.clinical_notes = clinical_notes

# ---------------------------
# GENERATE SUMMARY
# ---------------------------

if st.button("Generate Clinical Summary"):

    if clinical_notes == "":
        st.warning("Please upload or paste clinical notes first.")

    else:

        prompt = f"""
You are a clinical AI assistant.

Summarize the following clinical notes into:

• Patient Summary
• Diagnosis
• Medications
• Lab Results
• Follow-up Recommendations

Clinical Notes:
{clinical_notes}
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        summary = response.choices[0].message.content

        st.subheader("Generated Clinical Summary")
        st.write(summary)

# ---------------------------
# CHAT MEMORY
# ---------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ---------------------------
# DISPLAY CHAT
# ---------------------------

for i, msg in enumerate(st.session_state.messages):

    if msg["role"] == "user":

        col1, col2 = st.columns([8,1])

        with col1:
            st.markdown(
                f'<div class="user-msg">🧑 {msg["content"]}</div>',
                unsafe_allow_html=True
            )

        with col2:
            if st.button("✏️", key=f"edit_{i}"):
                st.session_state.edit_index = i

    else:

        st.markdown(
            f'<div class="bot-msg">👩‍⚕️ {msg["content"]}</div>',
            unsafe_allow_html=True
        )

# ---------------------------
# EDIT QUESTION
# ---------------------------

if st.session_state.edit_index is not None:

    edit_text = st.text_input(
        "Edit your question",
        value=st.session_state.messages[st.session_state.edit_index]["content"]
    )

    if st.button("Resubmit Question"):

        edited_question = edit_text

        st.session_state.messages[st.session_state.edit_index]["content"] = edited_question

        if len(st.session_state.messages) > st.session_state.edit_index + 1:
            st.session_state.messages.pop(st.session_state.edit_index + 1)

        with st.spinner("Assistant is typing..."):

            query_embedding = model.encode([edited_question])

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
{st.session_state.clinical_notes}

Medical Knowledge:
{knowledge_context}

Question:
{edited_question}

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

        st.session_state.edit_index = None
        st.rerun()

# ---------------------------
# CHAT INPUT
# ---------------------------

if not st.session_state.messages:
    st.info("Ask a question about the patient using the chat below.")

user_input = st.chat_input("Ask the Clinical AI Assistant...")

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