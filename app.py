import streamlit as st
from groq import Groq
from pylatexenc.latexencode import unicode_to_latex

st.set_page_config(page_title="ATS CV LaTeX Generator", layout="wide")

# -------------------------------
# Sidebar: API Key
# -------------------------------
with st.sidebar:
    st.title("⚙️ Settings")
    groq_api_key = st.text_input("Enter Groq API Key", type="password")

# App title
st.title("📄 ATS LaTeX CV Generator (Streamlit Version)")
st.write("Generate clean, ATS-optimized LaTeX CVs using Groq + LLaMA 3.")

# -------------------------------
# User Inputs
# -------------------------------
job_title = st.text_input("Target Job Title (e.g., Data Scientist)", "")
summary = st.text_area("Professional Summary")
experience = st.text_area("Experience (Bullet Points)")
projects = st.text_area("Projects")
skills = st.text_area("Skills")
education = st.text_area("Education")

generate = st.button("🚀 Generate LaTeX")

# -------------------------------
# Generate LaTeX CV
# -------------------------------
if generate:
    if not groq_api_key:
        st.error("Please enter your Groq API Key in the sidebar.")
        st.stop()

    groq_client = Groq(api_key=groq_api_key)

    prompt = f"""
You are an expert CV generator. Convert the following details into a clean, ATS-optimized LaTeX CV.

Return ONLY valid LaTeX containing:

- Professional Summary
- Experience
- Projects
- Skills
- Education

Here is the data:

Job Title: {job_title}
Summary: {summary}
Experience: {experience}
Projects: {projects}
Skills: {skills}
Education: {education}

Ensure:
- NO fancy colors or templates — keep it simple and ATS-safe.
- No external packages beyond: article, geometry.
- Bullet points must compile.
"""

    with st.spinner("Generating LaTeX using Groq…"):
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        latex_raw = response.choices[0].message.content.strip()

    # Escape unicode for safer LaTeX compilation
    latex_code = unicode_to_latex(latex_raw)

    # -------------------------------
    # Layout: Left (code) | Right (preview)
    # -------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Generated LaTeX Code")
        st.code(latex_code, language="latex")

        # Download button
        st.download_button(
            label="⬇️ Download .tex File",
            data=latex_code,
            file_name="cv.tex",
            mime="text/x-tex"
        )

    with col2:
        st.subheader("👀 Live Preview")
        try:
            st.latex(latex_code)
        except Exception:
            st.warning("Preview could not render due to LaTeX complexity, but the .tex file will still compile.")
