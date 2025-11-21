import streamlit as st
import requests
import base64
from io import BytesIO
from pylatex import Document, NoEscape

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="AI Resume Generator", layout="wide")

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]  # Add this in Streamlit Secrets
MODEL_NAME = "llama3-8b-instant"  # or "mixtral-8x7b"

# ---------------------------
# FUNCTIONS
# ---------------------------

def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()["choices"][0]["message"]["content"]


def generate_latex(summary, education, experience, skills, projects):
    prompt = f"""
You are a world-class CV writer. Convert the following information into a clean,
professional **LaTeX resume** with perfect formatting.

Sections required:
- Summary
- Education
- Experience
- Skills
- Projects

Return ONLY LaTeX code. No explanation.

Summary:
{summary}

Education:
{education}

Experience:
{experience}

Skills:
{skills}

Projects:
{projects}
    """

    latex_code = call_groq(prompt)
    return latex_code


def latex_to_pdf(latex_code):
    # create PDF using pylatex
    doc = Document()
    doc.append(NoEscape(latex_code))
    pdf = doc.generate_pdf(compiler="pdflatex", clean_tex=False)
    return pdf


def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# ---------------------------
# STREAMLIT UI
# ---------------------------

st.title("⚡ AI Resume Generator (Streamlit + Groq)")

left, right = st.columns([0.45, 0.55])

with left:
    st.subheader("✍️ Fill Your Details")

    summary = st.text_area("Summary", height=120)
    education = st.text_area("Education", height=120)
    experience = st.text_area("Experience", height=150)
    skills = st.text_area("Skills", height=120)
    projects = st.text_area("Projects", height=150)

    generate_btn = st.button("🚀 Generate AI Resume")

with right:
    st.subheader("📄 Live CV Preview")

    if generate_btn:
        with st.spinner("Generating AI LaTeX Resume..."):
            latex_code = generate_latex(summary, education, experience, skills, projects)

            # generate pdf
            pdf_bytes = latex_to_pdf(latex_code)

            st.success("Resume Generated Successfully!")

            # show PDF
            display_pdf(pdf_bytes)

            # download
            st.download_button(
                label="⬇ Download Resume (PDF)",
                data=pdf_bytes,
                file_name="resume.pdf",
                mime="application/pdf"
            )

            # show LaTeX code for advanced users
            with st.expander("View LaTeX Code"):
                st.code(latex_code, language="latex")
