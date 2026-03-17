import streamlit as st
import google.generativeai as genai
import graphviz
import os
from dotenv import load_dotenv
import time
import re
# Load environment variables
load_dotenv()

def render_enhanced_flowchart(steps):
        dot = graphviz.Digraph(format='png', engine='dot')

        # Loop through the steps and assign rectangular shapes and fill colors
        for idx, step in enumerate(steps):
            dot.node(f"step{idx}", step, shape='rectangle', style='filled', fillcolor="#4e5a75", fontcolor="white", width="2")

            # Create edges between nodes if it's not the first node
            if idx > 0:
                dot.edge(f"step{idx-1}", f"step{idx}")

        # Render the flowchart in Streamlit
        st.graphviz_chart(dot)

def main_app():     
    # Configure Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
    genai.configure(api_key=GEMINI_API_KEY)

    # Define generation config
    generation_config = genai.types.GenerationConfig(
        temperature=0.7,
        top_p=0.9,
        max_output_tokens=5000,
    )

    
    def is_career_related_semantically(query):
        classifier_model = genai.GenerativeModel("gemini-2.0-flash")
        classification_prompt = f"""
        You are an expert classifier. Your task is to analyze the user input below and determine whether it is asking for career guidance, planning, job preparation, learning roadmap, or role-specific advice.

        A valid input may include things like:
        - Planning a career in a specific field (e.g., "I want to become a data analyst. Help me plan.")
        - Creating a roadmap or study plan to become something (e.g., "How to become a machine learning engineer?")
        - Job search or resume advice
        - Skills, courses, or certifications for a role
        - Interview preparation, industry expectations, or portfolio suggestions

        An invalid input is anything unrelated to careers, such as:
        - Creative writing, storytelling, history, politics, general facts, entertainment, or casual conversation.

        Now, evaluate the input below:

        "{query}"

        Is this clearly a career-related request? Answer only with 'Yes' or 'No'.
        """

        result = classifier_model.generate_content(classification_prompt)
        return result.text.strip().lower().startswith("yes")


    # Session state
    if "chat" not in st.session_state:
        model = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config)
        st.session_state.chat = model.start_chat(history=[])

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "flowchart": render_enhanced_flowchart(msg["data"]) 
            else:st.markdown(msg["text"], unsafe_allow_html=True)


    # Function to use Gemini to generate job roles dynamically
    def get_job_roles_from_gemini(field):
        prompt = f"Given the field of {field}, suggest a list of relevant job roles in this domain."
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        roles = response.text.strip()

        if not roles:
            roles = "Career roles could not be determined. Please specify the field of interest."

        return roles

    # Function to generate career roadmap using Gemini
    def get_career_steps_from_gemini(career_field):
        prompt = f"Generate a career roadmap for someone wanting to become a {career_field}. List 10 to 15 steps in chronological order. Keep the list clear and concise.Simply generate list nothing else means not any starting text or highlighting text"
        
        # Request Gemini to generate career steps
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        
        steps = response.text.strip().split("\n")
        return steps

    # User input
    prompt = st.chat_input("Ask anything about your career path...")
        
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "text": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_text=""
                if is_career_related_semantically(prompt):
                    # Analyze the query to extract a field (using Gemini's assistance)
                    field_identification_prompt = (
                        f"Based on the user's query, determine the field they are referring to. "
                        f"User query: \"{prompt}\". Provide only the carrer and job field, like 'Machine Learning', 'Data Science',Web development,AI, Cloud Computing, etc."
                    )

                    # field_response = st.session_state.chat.send_message(field_identification_prompt)
                    field_response=genai.GenerativeModel("gemini-2.0-flash").generate_content(field_identification_prompt)
                    field_of_interest = field_response.text.strip()
                    modified_prompt=""
                    steps=[]
                    if field_of_interest:
                        # Get job roles dynamically based on the field of interest
                        job_roles = get_job_roles_from_gemini(field_of_interest)
                        # Append the job roles suggestion to the prompt
                        modified_prompt = (
                        f"{prompt}\n\n"
                        f"**And Relevant Job Roles in {field_of_interest}:**\n{job_roles}\n\n"
                        f"**And suggest some online courses on various plateform such as on udemy and coursera on the topic of {field_of_interest} with examples coureses name"
                        )
                        steps = get_career_steps_from_gemini(field_of_interest)


                    # response = st.session_state.chat.send_message(modified_prompt)
                    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(modified_prompt)
                    full_text = response.text+"\n\nFlow Chart-"

                    placeholder = st.empty()
                    displayed_text = ""

                    # Word-by-word streaming
                    blocks = re.split(r"(?<=\n)\n+", full_text.strip())
                    for block in blocks:
                        block = block.strip()
                        words = block.split(" ")
                        for word in words:
                            displayed_text += word + " "
                            placeholder.markdown(displayed_text + "▌", unsafe_allow_html=True)
                            time.sleep(0.01)
                        displayed_text += "\n\n"
                        placeholder.markdown(displayed_text + "▌", unsafe_allow_html=True)
                        time.sleep(0.1)

                    # Final output
                    placeholder.markdown(displayed_text, unsafe_allow_html=True)

                    # Flowchart
                    if steps:
                        render_enhanced_flowchart(steps)
                    st.session_state.chat_history.append({"role": "assistant", "text": full_text})
                    st.session_state.chat_history.append({ "role": "assistant", "type": "flowchart", "data": steps })
                else:
                    full_text = (
                    "I'm here to assist you with career guidance, job preparation, learning roadmaps, "
                    "and planning for your professional journey. If you have questions about how to enter "
                    "a specific field, what skills to develop, or how to grow in your role — I’d be glad to help!\n\n"
                    "However, this particular request doesn't seem related to career development, so I won’t be able to assist with it. "
                    "Please feel free to ask me anything related to your career path."
                    )
                    st.markdown(full_text)
                    st.session_state.chat_history.append({"role": "assistant", "text": full_text})
        
        
