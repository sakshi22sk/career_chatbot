import streamlit as st
import google.generativeai as genai
import graphviz
import re
import time

# =========================================
# PUT YOUR GEMINI API KEY HERE
# =========================================

GEMINI_API_KEY = "AIzaSyC9cNEuE8TNpOwWRtPp7j8BjKSdnpJb42g"

genai.configure(api_key=GEMINI_API_KEY)

# =========================================
# MODEL CONFIG
# =========================================

generation_config = genai.types.GenerationConfig(
    temperature=0.7,
    top_p=0.9,
    max_output_tokens=2000
)

model = genai.GenerativeModel(
    "models/gemini-1.5-flash-latest",
    generation_config=generation_config
)

# =========================================
# FLOWCHART RENDER
# =========================================

def render_enhanced_flowchart(steps):

    dot = graphviz.Digraph()

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

    for i, step in enumerate(steps):

        clean = re.sub(r'^\d+\.?\s*', '', step)

        dot.node(
            f"step{i}",
            clean,
            shape="rectangle",
            style="filled,rounded",
            fillcolor=colors[i % len(colors)],
            fontcolor="white"
        )

        if i > 0:
            dot.edge(f"step{i-1}", f"step{i}")

    st.graphviz_chart(dot, use_container_width=True)


# =========================================
# GEMINI SAFE CALL
# =========================================

def generate_response(prompt):

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception:

        time.sleep(40)

        response = model.generate_content(prompt)

        return response.text


# =========================================
# RESUME ANALYZER
# =========================================

def analyze_resume(resume_text):

    prompt = f"""
You are a professional resume reviewer.

Analyze the following resume and provide:

1. Strengths
2. Weaknesses
3. Missing Skills
4. ATS Optimization Tips
5. Suggested Improvements

Resume:
{resume_text}
"""

    return generate_response(prompt)


# =========================================
# EXTRACT ROADMAP STEPS
# =========================================

def extract_steps(text):

    steps = []

    for line in text.split("\n"):

        if re.match(r"^\d+\.", line.strip()):

            clean = re.sub(r'^\d+\.\s*', '', line)

            steps.append(clean)

    return steps[:10]


# =========================================
# MAIN APP
# =========================================

def main_app():

    st.title("🚀 Career Path Oracle")

    # SESSION MEMORY

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # =====================================
    # RESUME ANALYZER
    # =====================================

    st.sidebar.header("📄 Resume Analyzer")

    uploaded_file = st.sidebar.file_uploader(
        "Upload Resume (.txt)",
        type=["txt"]
    )

    if uploaded_file:

        resume_text = uploaded_file.read().decode("utf-8")

        if st.sidebar.button("Analyze Resume"):

            with st.spinner("Analyzing Resume..."):

                result = analyze_resume(resume_text)

                st.sidebar.markdown(result)

    # =====================================
    # SHOW CHAT HISTORY
    # =====================================

    for msg in st.session_state.chat_history:

        with st.chat_message(msg["role"]):

            if msg.get("type") == "flowchart":

                render_enhanced_flowchart(msg["data"])

            else:

                st.markdown(msg["text"])

    # =====================================
    # USER INPUT
    # =====================================

    prompt = st.chat_input("Ask about career guidance, roadmap, skills...")

    if prompt:

        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.chat_history.append({
            "role": "user",
            "text": prompt
        })

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                assistant_prompt = f"""
You are an expert career advisor.

User Question:
{prompt}

Provide:

1. Clear career advice
2. Important skills to learn
3. Relevant job roles
4. Recommended courses
5. A roadmap of 8-10 steps

Write roadmap steps like this:

1. Step one
2. Step two
3. Step three
"""

                text = generate_response(assistant_prompt)

                placeholder = st.empty()

                output = ""

                words = text.split(" ")

                for word in words:

                    output += word + " "

                    placeholder.markdown(output + "▌")

                    time.sleep(0.003)

                placeholder.markdown(output)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "text": text
                })

                # =====================================
                # FLOWCHART
                # =====================================

                steps = extract_steps(text)

                if steps:

                    render_enhanced_flowchart(steps)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "type": "flowchart",
                        "data": steps
                    })


if __name__ == "__main__":
    main_app()
