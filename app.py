import streamlit as st
from groq import Groq
from jinja2 import Template
import subprocess
import uuid

st.title("AI Resume Generator (Groq + LaTeX + Streamlit)")

# Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# User inputs
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone")
linkedin = st.text_input("LinkedIn URL")

summary_raw = st.text_area("Summary (raw text)")
experience_raw = st.text_area("Experience (raw text)")
education_raw = st.text_area("Education (raw text)")
projects_raw = st.text_area("Projects (raw text)")
skills_raw = st.text_area("Skills (raw text)")

# AI function
def format_with_ai(section_text):
    if not section_text.strip():
        return ""

    prompt = f"""
    You are a CV LaTeX formatter.
    Convert the following raw text into clean LaTeX:

    {section_text}

    Output only LaTeX code. No explanation.
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content

# Generate PDF
if st.button("Generate CV"):
    with st.spinner("Generating LaTeX using Groq..."):
        summary = format_with_ai(summary_raw)
        experience = format_with_ai(experience_raw)
        education = format_with_ai(education_raw)
        projects = format_with_ai(projects_raw)
        skills = format_with_ai(skills_raw)

    with open("template.tex") as f:
        template = Template(f.read())

    full_tex = template.render(
        NAME=name,
        EMAIL=email,
        PHONE=phone,
        LINKEDIN=linkedin,
        SUMMARY=summary,
        EXPERIENCE=experience,
        EDUCATION=education,
        PROJECTS=projects,
        SKILLS=skills,
    )

    # Save temp tex file
    tex_filename = f"cv_{uuid.uuid4()}.tex"
    with open(tex_filename, "w") as f:
        f.write(full_tex)

    # Compile LaTeX → PDF using Tectonic
    subprocess.run(["tectonic", tex_filename])

    pdf_filename = tex_filename.replace(".tex", ".pdf")

    # Provide download option
    with open(pdf_filename, "rb") as f:
        st.download_button(
            "Download CV PDF",
            f,
            file_name="Resume.pdf",
            mime="application/pdf",
        )

    st.success("CV generated successfully!")
