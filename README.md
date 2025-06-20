# 🤖 AI Test Case Generator

Automatically generate structured test cases from plain English feature or requirement descriptions using open-source Large Language Models (LLMs) like Mistral or LLaMA2 via Ollama.

---

## 🚀 Features

* 🧾 Paste or upload a `.txt` feature/requirement description
* 🧠 Generate test cases using local LLMs (Ollama)
* 📄 Test cases include:

  * Title
  * Preconditions
  * Steps 
  * Expected Result
* 📥 Download test cases as CSV
* 🔄 View raw model output for debugging
* 🧩 Works fully offline using open-source models

---

## 📦 Tech Stack

* [Streamlit](https://streamlit.io/) – Simple Python-based GUI
* [Ollama](https://ollama.com/) – Local model runner
* [Pandas](https://pandas.pydata.org/) – CSV formatting
* [Mistral, LLaMA2, Gemma](https://ollama.com/library) – LLMs used

---

## 🧠 Ollama Installation & Setup

### Step 1: Install Ollama

#### macOS/Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

> Ollama provides a local REST API on `http://localhost:11434`

### Step 2: Pull a Model

```bash
ollama pull mistral
```

You can also try:

```bash
ollama pull llama2
ollama pull gemma
```

---

## ⚙️ Running the App Locally

### Requirements

* Python 3.10+
* Ollama installed (see above)

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run test_case_generator.py
```

The app will open in your browser (usually at `http://localhost:8501`).

---

## 🧪 CI/CD

This project uses GitHub Actions for:

* ✅ Linting with `flake8`
* 📦 Dependency verification

See `.github/workflows/python-ci.yml` for workflow configuration.

---

## 🔮 Future Enhancements

* Test tagging (e.g., regression, priority, security)
* Export to Jira
* Integration with Google Sheets or REST APIs
* Severity/Priority fields in test cases
* Fine-tuned model training with custom test data

---

## 🙌 Acknowledgements

Built with ❤️ using open-source tools and local AI models.

