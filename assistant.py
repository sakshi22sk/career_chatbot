import streamlit as st
import google.generativeai as genai
import graphviz
import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# Configure Gemini
# -------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API key not found!")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

generation_config = genai.types.GenerationConfig(
    temperature=0.7,
    top_p=0.9,
    max_output_tokens=5000
)

model = genai.GenerativeModel(
    "gemini-2.0-flash",
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
# FLOWCHART RENDERER
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

def is_career_related_semantically(query):

    classifier_model = genai.GenerativeModel("gemini-2.0-flash")

    classification_prompt = f"""
Determine whether the user query is related to career guidance.

Query:
{query}

Answer only Yes or No.
"""

    result = classifier_model.generate_content(classification_prompt)

    return result.text.lower().startswith("yes")

# -------------------------
# FIELD DETECTOR
# -------------------------

def detect_field(query):

    try:

        prompt = f"""
Identify the career field from this query.

Query: {query}

Return only the field name.
"""

        response = model.generate_content(prompt)

        field = response.text.strip().split("\n")[0]

        if len(field) > 40:
            return "Career"

        return field

    except:
        return "Career"

# -------------------------
# JOB ROLES GENERATOR
# -------------------------

def get_job_roles_from_gemini(field):

    prompt = f"""
List relevant job roles in the field of {field}.
Only return the list.
"""

    response = model.generate_content(prompt)

    return response.text

# -------------------------
# ROADMAP GENERATOR
# -------------------------

def generate_roadmap_steps(field):

    prompt = f"""
Create a step-by-step roadmap for becoming a {field}.

Provide 10 steps.
"""

    response = model.generate_content(prompt)

    steps = []

    for line in response.text.split("\n"):

        if line.strip():

            clean = re.sub(r'^\d+\.?\s*', '', line).strip()

            steps.append(clean)

    return steps[:10]

# -------------------------
# RESUME ANALYZER
# -------------------------

def analyze_resume(resume_text):

    prompt = f"""
You are an expert resume reviewer.

Analyze the following resume.

Provide:

1. Strengths
2. Weaknesses
3. Missing skills
4. ATS optimization tips
5. Suggested improvements

Resume:

{resume_text}
"""

    response = model.generate_content(prompt)

    return response.text

# -------------------------
# MAIN APP
# -------------------------

def main_app():

    st.title("Career Path Oracle")

    # SESSION STATE

    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # -------------------------
    # RESUME ANALYZER UI
    # -------------------------

    st.sidebar.header("Resume Analyzer")

    uploaded_file = st.sidebar.file_uploader(
        "Upload Resume (TXT)", type=["txt"]
    )

    if uploaded_file:

        resume_text = uploaded_file.read().decode("utf-8")

        if st.sidebar.button("Analyze Resume"):

            with st.spinner("Analyzing Resume..."):

                result = analyze_resume(resume_text)

                st.sidebar.markdown(result)

    # -------------------------
    # CHAT HISTORY
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

                if not is_career_related_semantically(prompt):

                    text = """
I'm here to help with career guidance, roadmaps, skills, jobs and professional growth.

Please ask a career related question.
"""

                    st.markdown(text)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "text": text
                    })

                    return

                field = detect_field(prompt)

                job_roles = get_job_roles_from_gemini(field)

                final_prompt = f"""
{SYSTEM_PROMPT}

User question:
{prompt}

Career field:
{field}

Relevant job roles:
{job_roles}

Provide a detailed answer.
"""

                response = st.session_state.chat.send_message(final_prompt)

                text = response.text

                # Streaming Output

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

                if any(x in prompt.lower() for x in ["roadmap","step","path","timeline"]):

                    steps = generate_roadmap_steps(field)

                    render_enhanced_flowchart(steps)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "type": "flowchart",
                        "data": steps
                    })


if __name__ == "__main__":
    main_app()
