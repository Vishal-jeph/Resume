import streamlit as st
import requests
import json
import base64
from pylatexenc.latexencode import unicode_to_latex

st.set_page_config(page_title="AI Resume Generator", layout="wide")

# -------------------------
# GROQ API CALL
# -------------------------
def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }

    response = requests.post(url, json=data, headers=headers)

    try:
        return response.json()["choices"][0]["message"]["content"]
    except:
        st.error("❌ ERROR calling Groq: " + str(response.text))
        return None


# -------------------------
# STRICT LATEX TEMPLATE
# -------------------------
BASE_LATEX_TEMPLATE = r"""
\documentclass{article}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{titlesec}
\usepackage{parskip}

\titleformat{\section}{\large\bfseries}{}{0pt}{}

\begin{document}

\begin{center}
{\LARGE \textbf{Resume}} \\
\vspace{0.2cm}
\end{center}

\section*{Summary}
SUMMARY_PLACEHOLDER

\section*{Education}
EDUCATION_PLACEHOLDER

\section*{Experience}
EXPERIENCE_PLACEHOLDER

\section*{Skills}
SKILLS_PLACEHOLDER

\section*{Projects}
PROJECTS_PLACEHOLDER

\end{document}
"""


# -------------------------
# PDF CONVERSION
# -------------------------
def latex_to_pdf(latex_code):
    import tempfile
    import subprocess

    with tempfile.NamedTemporaryFile(delete=False, suffix=".tex") as temp_tex:
        temp_tex.write(latex_code.encode("utf-8"))
        tex_path = temp_tex.name

    pdf_path = tex_path.replace(".tex", ".pdf")

    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except:
        st.error("❌ LaTeX compilation failed. Please fix the content.")
        return None

    with open(pdf_path, "rb") as f:
        return f.read()


# -------------------------
# MAIN PAGE UI
# -------------------------
st.title("📄 AI LaTeX Resume Generator (Groq + Streamlit)")

left, right = st.columns([1, 1.3])

with left:
    st.header("Enter Resume Details")

    summary = st.text_area("Summary", height=120)
    education = st.text_area("Education", height=120)
    experience = st.text_area("Experience", height=150)
    skills = st.text_area("Skills", height=120)
    projects = st.text_area("Projects", height=120)

    generate_btn = st.button("Generate Resume")

with right:
    st.header("📌 Resume Preview")

    preview_placeholder = st.empty()


# -------------------------
# GENERATE RESUME + PREVIEW
# -------------------------
if generate_btn:

    # --- AI Prompt ---
    prompt = f"""
You are to fill ONLY the placeholders for a LaTeX resume template.

Return valid JSON with keys:
SUMMARY, EDUCATION, EXPERIENCE, SKILLS, PROJECTS.

Rules:
- Do NOT create new LaTeX commands.
- Do NOT wrap output in code blocks.
- Escape characters like %, _, &, $, #.
- Keep formatting simple bullet points.

Input:

Summary: {summary}
Education: {education}
Experience: {experience}
Skills: {skills}
Projects: {projects}

Return JSON ONLY.
"""

    with st.spinner("Generating structured resume content…"):
        ai_output = call_groq(prompt)

    if ai_output is None:
        st.stop()

    # Parse JSON safely
    try:
        fields = json.loads(ai_output)
    except:
        st.error("❌ Groq did NOT return valid JSON. Output shown below:")
        st.code(ai_output)
        st.stop()

    # Fill template
    latex_filled = BASE_LATEX_TEMPLATE
    for key, value in fields.items():
        safe = unicode_to_latex(value)
        latex_filled = latex_filled.replace(f"{key}_PLACEHOLDER", safe)

    # Generate PDF
    with st.spinner("Generating PDF…"):
        pdf_bytes = latex_to_pdf(latex_filled)

    if pdf_bytes is None:
        st.stop()

    # -------------------------
    # SHOW PDF PREVIEW
    # -------------------------
    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    preview_html = f"""
    <embed 
        src="data:application/pdf;base64,{b64_pdf}"
        type="application/pdf"
        width="100%"
        height="600px"
    />
    """

    preview_placeholder.markdown(preview_html, unsafe_allow_html=True)

    # -------------------------
    # Download Button
    # -------------------------
    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_bytes,
        file_name="resume.pdf",
        mime="application/pdf"
    )

    st.success("✨ Resume generated successfully!")
