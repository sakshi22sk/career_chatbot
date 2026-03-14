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
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

if not GEMINI_API_KEY:
    st.error("Gemini API key not found!")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

generation_config = genai.types.GenerationConfig(
    temperature=0.6,
    top_p=0.9,
    max_output_tokens=800
)
model = genai.GenerativeModel(
    "models/gemini-pro",
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
# Flowchart Renderer
# -------------------------

def render_enhanced_flowchart(steps, title="Career Roadmap"):

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
# Flowchart Trigger
# -------------------------

def should_generate_flowchart(query):

    triggers = [
        "roadmap",
        "step by step",
        "learning path",
        "timeline",
        "workflow"
    ]

    query = query.lower()

    return any(t in query for t in triggers)


# -------------------------
# Detect Field
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
# Generate Roadmap Steps
# -------------------------

def generate_roadmap_steps(field):

    prompt = f"""
Create a step-by-step roadmap for becoming a {field}.

Provide 10 clear steps.
Each step should be short.
"""

    try:

        response = model.generate_content(prompt)

        text = response.text

        steps = []

        for line in text.split("\n"):

            if line.strip():

                clean = re.sub(r'^\d+\.?\s*', '', line).strip()

                steps.append(clean)

        return steps[:10]

    except:

        return [
            "Learn fundamentals",
            "Practice projects",
            "Build portfolio",
            "Apply for jobs"
        ]


# -------------------------
# Main App
# -------------------------

def main_app():

    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history

    for msg in st.session_state.chat_history:

        with st.chat_message(msg["role"]):

            if msg.get("type") == "flowchart":

                render_enhanced_flowchart(msg["data"])

            else:

                st.markdown(msg["text"], unsafe_allow_html=True)

    # Input box

    prompt = st.chat_input("Ask anything about your career...")

    if prompt:

        # Show user message

        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.chat_history.append({
            "role": "user",
            "text": prompt
        })

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    field = detect_field(prompt)

                    final_prompt = f"""
{SYSTEM_PROMPT}

User question:
{prompt}

Career field:
{field}

Provide a helpful answer.
"""

                    response = st.session_state.chat.send_message(final_prompt)

                    text = response.text

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

                    # Flowchart

                    if should_generate_flowchart(prompt):

                        steps = generate_roadmap_steps(field)

                        render_enhanced_flowchart(steps)

                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "type": "flowchart",
                            "data": steps
                        })

                except Exception as e:

                    error = f"Sorry, something went wrong: {e}"

                    st.error(error)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "text": error
                    })
