import streamlit as st
import pandas as pd
import requests
import json
import re
from io import StringIO
import chromadb
from chromadb.utils import embedding_functions

# Set up Streamlit page
st.set_page_config(page_title="AI Test Case Generator (with RAG)", layout="wide")
st.title("🤖 AI Test Case Generator with RAG")

# Step 1: Feature Input
st.markdown("### 📄 Input Feature Description")
feature_input = st.text_area("Paste the feature description below", height=200)
uploaded_file = st.file_uploader("Or upload a `.txt` file", type=["txt"])
if uploaded_file:
    feature_input = uploaded_file.read().decode("utf-8")

# Step 2: Model Selection
st.markdown("### 🧠 Select AI Model")
model_descriptions = {
    "mistral": "🧪 Mistral: Lightweight and fast open-source model ideal for structured reasoning.",
    "llama2": "🦙 LLaMA 2: Meta's general-purpose model, good for balanced natural language generation.",
    "gemma": "💎 Gemma: Google's open-weight model, strong on logical tasks and alignment.",
    "dolphin-mixtral": "🐬 Dolphin-Mixtral: Creative and structured, good for step-by-step reasoning."
}
model_choice = st.selectbox("Choose a model", list(model_descriptions.keys()), format_func=lambda x: model_descriptions[x])

# Upload CSV to expand example database
st.markdown("### ➕ Add Structured Test Cases to DB")
feature_for_csv = st.text_input("Describe the feature these test cases belong to")

example_csv_structured = st.file_uploader(
    "Upload a CSV with columns: Title, Preconditions, Steps, Expected Result",
    type=["csv"]
)

if feature_for_csv and example_csv_structured:
    try:
        df = pd.read_csv(example_csv_structured)
        required_cols = {"Title", "Preconditions", "Steps", "Expected Result"}
        if not required_cols.issubset(df.columns):
            st.error("❌ CSV must have columns: Title, Preconditions, Steps, Expected Result")
        else:
            # Combine all rows into one test_cases string
            combined_cases = ""
            for _, row in df.iterrows():
                combined_cases += (
                    f"Title: {row['Title']}\n"
                    f"Preconditions: {row['Preconditions']}\n"
                    f"Steps: {row['Steps']}\n"
                    f"Expected Result: {row['Expected Result']}\n\n"
                )

            # Store in ChromaDB
            embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            client = chromadb.Client()
            collection = client.get_or_create_collection(name="test_examples", embedding_function=embedding_fn)

            collection.add(
                documents=[feature_for_csv],
                metadatas=[{"test_cases": combined_cases.strip()}],
                ids=[f"user-{feature_for_csv[:40].replace(' ', '-').lower()}"]
            )

            st.success("✅ Structured test cases added successfully!")

    except Exception as e:
        st.error(f"❌ Error processing CSV: {e}")

# Step 3: Trigger Generation
if st.button("🧠 Generate Test Cases") and feature_input.strip():

    with st.spinner("🔎 Retrieving similar features from knowledge base..."):
        # Set up ChromaDB + embedding model
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        client = chromadb.Client()
        collection = client.get_or_create_collection(name="test_examples", embedding_function=embedding_fn)

        # Perform similarity search
        try:
            results = collection.query(query_texts=[feature_input], n_results=3)
            retrieved_examples = "\n\n".join(
                f"Feature: {results['documents'][0][i]}\nTest Cases: {results['metadatas'][0][i]['test_cases']}"
                for i in range(len(results['documents'][0]))
            )
        except Exception:
            retrieved_examples = ""  # fallback if retrieval fails

    # Step 4: Build the prompt with RAG content
    prompt = f"""
You are a skilled and exhaustive test analyst.

Here are similar feature descriptions and their test cases:
{retrieved_examples}

Now generate a comprehensive, detailed list of test cases for the new feature below. Include:
- Positive and negative scenarios
- Edge cases and boundary conditions
- Validation and exception handling
- Role-based behavior if applicable

Output only a valid JSON array with dictionaries like:
[
  {{
    "Title": "...",
    "Preconditions": "...",
    "Steps": "Step 1: ...\\nStep 2: ...",
    "Expected Result": "..."
  }}
]

Feature:
{feature_input}
"""

    try:
        with st.spinner("⏳ Generating test cases..."):
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model_choice, "prompt": prompt, "stream": False}
            )
            stdout = response.json().get("response", "")

        try:
            json_str_match = re.search(r'\[\s*{.*?}\s*\]', stdout, re.DOTALL)
            json_str = json_str_match.group(0) if json_str_match else stdout.strip()
            test_cases = json.loads(json_str)
        except json.JSONDecodeError as e:
            st.error(f"⚠️ JSON Decode Error: {str(e)}")
            st.text_area("🔧 Raw Model Output", stdout, height=300)
            test_cases = []

        if test_cases:
            df = pd.DataFrame(test_cases)
            st.success("✅ Test Cases Generated")
            st.dataframe(df, use_container_width=True)

            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_buffer.getvalue(),
                file_name="test_cases.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ The model responded but did not return any valid test cases.")

        with st.expander("📜 Raw model response"):
            st.text_area("Raw Output", stdout, height=300)

    except Exception as e:
        st.error(f"❌ Error during generation: {str(e)}")

else:
    st.info("Paste a feature description or upload a `.txt` file to begin.")

