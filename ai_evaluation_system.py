import streamlit as st
from openai import OpenAI
import csv
import json
import os

# ---------------------------
# Setup OpenAI Client
# ---------------------------
client = OpenAI(api_key="YOUR_API_KEY")

st.title("AI Evaluation System")

# ---------------------------
# Functions
# ---------------------------

def get_response(query):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content


def evaluate_response(query, response):
    eval_prompt = f"""
    Evaluate the AI response based on:
    - Relevance (1-5)
    - Clarity (1-5)
    - Completeness (1-5)

    Query: {query}
    Response: {response}

    Return ONLY JSON like:
    {{
      "relevance": 4,
      "clarity": 5,
      "completeness": 3
    }}
    """

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": eval_prompt}]
    )

    content = result.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {"relevance": 0, "clarity": 0, "completeness": 0}


def save_data(query, response, scores, feedback):
    file_exists = os.path.isfile("data.csv")

    with open("data.csv", "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "query", "response",
                "relevance", "clarity", "completeness",
                "feedback"
            ])

        writer.writerow([
            query,
            response,
            scores["relevance"],
            scores["clarity"],
            scores["completeness"],
            feedback
        ])

# ---------------------------
# UI
# ---------------------------

query = st.text_input("Enter your query:")

if st.button("Generate Response") and query:

    # Step 1: Generate response
    response = get_response(query)

    st.subheader("AI Response")
    st.write(response)

    # Step 2: Evaluate response
    scores = evaluate_response(query, response)

    st.subheader("Evaluation Scores")
    st.write(f"Relevance: {scores['relevance']}")
    st.write(f"Clarity: {scores['clarity']}")
    st.write(f"Completeness: {scores['completeness']}")

    # Step 3: Feedback
    st.subheader("Feedback")

    col1, col2 = st.columns(2)

    feedback = None

    with col1:
        if st.button("👍 Good"):
            feedback = "Good"

    with col2:
        if st.button("👎 Bad"):
            feedback = "Bad"

    # Step 4: Save data
    if feedback:
        save_data(query, response, scores, feedback)
        st.success("Feedback saved!")
