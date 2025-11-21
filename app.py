import streamlit as st
import requests
import json
from pylatex import Document, Section, Command
from pylatex.utils import NoEscape

# -----------------------
# GROQ API CALL FUNCTION
# -----------------------
def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a LaTeX resume generator. Output ONLY LaTeX code."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(url, json=data, headers=headers)

    # ------------ ERROR HANDLING -------------
    try:
        res_json = response.json()
    except:
        return "ERROR: Groq returned non-JSON response."

    if "error" in res_json:
        return f"ERROR FROM GROQ: {res_json['error']['message']}"

    if "choices" not in res_json:
        return "ERROR: Groq did not return 'choices'."

    return res_json["choices"][0]["message"]["content"]


# ---------------------------
# Generate LaTeX using AI
# ---------------------------
def generate_latex(summary, education, experience, skills, projects):
    prompt = f"""
Create a clean LaTeX resume. Include the following sections:

SUMMARY:
{summary}

EDUCATION:
{education}

EXPERIENCE:
{experience}

SKILLS:
{skills}

PROJECTS:
{projects}

Use modern professional LaTeX formatting.
OUTPUT ONLY LATEX CODE. NO EXPLANATION.
"""

    latex_code = call_groq(prompt)
    return latex_code


# ---------------------------
# Convert LaTeX → PDF
# ---------------------------
def latex_to_pdf(latex_code):
    try:
        doc = Document()
        doc.append(NoEscape(latex_code))
        return doc.dumps().encode("utf-8")
    except Exception as e:
        return None


# ---------------------------
# STREAMLIT UI
# ---------------------------
st.title("AI Resume Generator (LaTeX + Groq + Streamlit)")

st.write("Fill the fields below and generate a clean, AI-powered resume.")

summary = st.text_area("Summary")
education = st.text_area("Education")
experience = st.text_area("Experience")
skills = st.text_area("Skills")
projects = st.text_area("Projects")

generate_btn = st.button("Generate Resume")


if generate_btn:
    with st.spinner("Generating AI LaTeX Resume..."):
        latex_code = generate_latex(summary, education, experience, skills, projects)

        st.subheader("Generated LaTeX Code")
        st.code(latex_code, language="latex")

        pdf_bytes = latex_to_pdf(latex_code)

        if pdf_bytes:
            st.download_button(
                "Download Resume PDF",
                pdf_bytes,
                file_name="resume.pdf",
                mime="application/pdf"
            )
        else:
            st.error("PDF generation failed. Check LaTeX formatting.")
