import streamlit as st
import google.generativeai as genai
import graphviz
import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# CONFIGURE GEMINI
# -------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API key not found!")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

generation_config = genai.types.GenerationConfig(
    temperature=0.7,
    top_p=0.9,
    max_output_tokens=2000
)

MODEL_NAME = "gemini-1.5-flash"

model = genai.GenerativeModel(
    MODEL_NAME,
    generation_config=generation_config
)

SYSTEM_PROMPT = """
You are Career Path Oracle, an expert AI career advisor.

Your job is to:
- Help users plan their career
- Suggest skills to learn
- Recommend courses and certifications
- Explain salary ranges
- Suggest companies and job roles
- Create step-by-step career roadmaps

Always give practical and clear advice.
"""

# -------------------------
# SAFE GEMINI CALL (RETRY)
# -------------------------

def safe_generate(prompt):

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception:

        time.sleep(50)

        response = model.generate_content(prompt)
        return response.text


# -------------------------
# FLOWCHART
# -------------------------

def render_enhanced_flowchart(steps):

    dot = graphviz.Digraph(format="png")
    dot.attr(rankdir="TB")

    colors = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#96CEB4",
        "#FECA57",
        "#FF9FF3",
        "#54A0FF"
    ]

    processed = []

    for step in steps:

        clean = step.strip()
        clean = re.sub(r'^\d+\.?\s*', '', clean)
        clean = re.sub(r'^[\-\*•]\s*', '', clean)

        if clean:
            processed.append(clean)

    for i, step in enumerate(processed):

        dot.node(
            f"step{i}",
            step,
            shape="rectangle",
            style="filled,rounded",
            fillcolor=colors[i % len(colors)],
            fontcolor="white"
        )

    for i in range(len(processed) - 1):
        dot.edge(f"step{i}", f"step{i+1}")

    st.graphviz_chart(dot, use_container_width=True)


# -------------------------
# CAREER CLASSIFIER
# -------------------------

def is_career_related(query):

    prompt = f"""
Determine if the query is related to career guidance.

Query:
{query}

Answer Yes or No only.
"""

    result = safe_generate(prompt)

    return result.lower().startswith("yes")


# -------------------------
# FIELD DETECTOR
# -------------------------

def detect_field(query):

    prompt = f"""
Identify the career field from this query.

Query:
{query}

Return only the field name.
"""

    result = safe_generate(prompt)

    field = result.split("\n")[0]

    if len(field) > 40:
        return "Career"

    return field


# -------------------------
# JOB ROLES
# -------------------------

def get_job_roles(field):

    prompt = f"""
List relevant job roles in the field of {field}.
Return only a list.
"""

    return safe_generate(prompt)


# -------------------------
# ROADMAP
# -------------------------

def generate_roadmap(field):

    prompt = f"""
Create a step-by-step roadmap for becoming a {field}.

Provide 10 short steps.
"""

    text = safe_generate(prompt)

    steps = []

    for line in text.split("\n"):

        if line.strip():

            clean = re.sub(r'^\d+\.?\s*', '', line).strip()

            steps.append(clean)

    return steps[:10]


# -------------------------
# RESUME ANALYZER
# -------------------------

def analyze_resume(resume):

    prompt = f"""
You are a professional resume reviewer.

Analyze the resume below.

Provide:
1. Strengths
2. Weaknesses
3. Missing Skills
4. ATS Optimization Tips
5. Suggested Improvements

Resume:
{resume}
"""

    return safe_generate(prompt)


# -------------------------
# MAIN APP
# -------------------------

def main_app():

    st.title("Career Path Oracle")

    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # -------------------------
    # RESUME ANALYZER SIDEBAR
    # -------------------------

    st.sidebar.header("Resume Analyzer")

    uploaded_file = st.sidebar.file_uploader(
        "Upload Resume (TXT)", type=["txt"]
    )

    if uploaded_file:

        resume_text = uploaded_file.read().decode("utf-8")

        if st.sidebar.button("Analyze Resume"):

            with st.spinner("Analyzing resume..."):

                result = analyze_resume(resume_text)

                st.sidebar.markdown(result)

    # -------------------------
    # DISPLAY CHAT HISTORY
    # -------------------------

    for msg in st.session_state.chat_history:

        with st.chat_message(msg["role"]):

            if msg.get("type") == "flowchart":
                render_enhanced_flowchart(msg["data"])

            else:
                st.markdown(msg["text"], unsafe_allow_html=True)

    # -------------------------
    # USER INPUT
    # -------------------------

    prompt = st.chat_input("Ask anything about your career path...")

    if prompt:

        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.chat_history.append({
            "role": "user",
            "text": prompt
        })

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                if not is_career_related(prompt):

                    text = """
I'm here to assist with career guidance, job preparation,
learning roadmaps, and professional growth.

Please ask a career related question.
"""

                    st.markdown(text)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "text": text
                    })

                    return

                field = detect_field(prompt)

                job_roles = get_job_roles(field)

                final_prompt = f"""
{SYSTEM_PROMPT}

User Question:
{prompt}

Career Field:
{field}

Relevant Job Roles:
{job_roles}

Provide a detailed answer with practical guidance.
"""

                text = safe_generate(final_prompt)

                placeholder = st.empty()

                output = ""

                words = text.split(" ")

                for word in words:

                    output += word + " "

                    placeholder.markdown(output + "▌")

                    time.sleep(0.005)

                placeholder.markdown(output)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "text": text
                })

                # FLOWCHART

                if any(x in prompt.lower() for x in ["roadmap","steps","path","timeline"]):

                    steps = generate_roadmap(field)

                    render_enhanced_flowchart(steps)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "type": "flowchart",
                        "data": steps
                    })


if __name__ == "__main__":
    main_app()
