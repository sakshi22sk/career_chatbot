import streamlit as st
import google.generativeai as genai
import graphviz
import os
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

import re
import graphviz
import streamlit as st

def render_enhanced_flowchart(steps, title="Career Roadmap"):
    dot = graphviz.Digraph(format="png", engine="dot")

    # Overall diagram settings
    dot.attr(rankdir="TB", size="7,7", dpi="72")  # TB = top to bottom

    processed_steps = []
    for step in steps:
        if step.strip():
            clean_step = step.strip()
            clean_step = re.sub(r'^\d+\.?\s*', '', clean_step)   # remove numbers
            clean_step = re.sub(r'^[\-\*•]\s*', '', clean_step)  # remove bullets
            processed_steps.append(clean_step)

    # Color palette
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']

    # Create nodes with colors
    for i, step in enumerate(processed_steps):
        color = colors[i % len(colors)]
        dot.node(
            f"step{i}",
            step,
            shape="rectangle",
            style="filled,rounded",
            fillcolor=color,
            fontcolor="white",
            fontsize="10",
            width="2",
            height="0.6"
        )

    # Create arrows between steps
    for i in range(len(processed_steps) - 1):
        dot.edge(f"step{i}", f"step{i+1}", color="#333333", penwidth="1.5")

    # ✅ Render only once (this prevents duplicate grey chart)
    try:
        st.graphviz_chart(dot, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render flowchart: {e}")
        st.markdown("### 📋 Step-by-Step Roadmap:")
        for i, step in enumerate(processed_steps, 1):
            st.markdown(f"**Step {i}:** {step}")

""""
def render_enhanced_flowchart(steps, title="Career Roadmap"):
    dot = graphviz.Digraph(format="png", engine="dot")

    # Force overall size
    dot.attr(size="5,5")
    dot.attr(dpi="72")




    # Process steps and create nodes
    processed_steps = []
    for i, step in enumerate(steps):
        if step.strip():
            # Clean step text
            clean_step = step.strip()
            # Remove numbering if present
            clean_step = re.sub(r'^\d+\.?\s*', '', clean_step)
            # Remove bullet points
            clean_step = re.sub(r'^[\-\*•]\s*', '', clean_step)
            # Better length management - shorter for better fit
            if len(clean_step) > 50:
                # Break long text into multiple lines
                words = clean_step.split()
                lines = []
                current_line = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 <= 25:  # Shorter lines
                        current_line.append(word)
                        current_length += len(word) + 1
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                clean_step = '\\n'.join(lines[:2])  # Max 2 lines for better fit
                
            processed_steps.append(clean_step)

    # Create nodes with better colors and sizing
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
    
    for i, step in enumerate(processed_steps):
        color = colors[i % len(colors)]
        dot.node(f"step{i}", step, 
                fillcolor=color, 
                fontcolor="white", 
                fontsize='9')  # Smaller font for better fit

    # Connect title to first step
    if processed_steps:
        dot.edge('title', 'step0', style='invis')

    # Create edges between nodes
    for i in range(len(processed_steps) - 1):
        dot.edge(f"step{i}", f"step{i+1}", color='#666666', penwidth='2')

    # Render with container width - this is key for responsive sizing
    try:
        st.graphviz_chart(dot, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render flowchart: {e}")
        # Fallback to text-based steps
        st.markdown("### 📋 Step-by-Step Roadmap:")
        for i, step in enumerate(processed_steps, 1):
            st.markdown(f"**Step {i}:** {step}")

"""

def should_generate_flowchart(query):
    """Determine if the query requires a flowchart/diagram"""
    flowchart_indicators = [
        'roadmap', 'steps', 'process', 'workflow', 'path', 'journey', 'plan',
        'timeline', 'progression', 'sequence', 'stages', 'phases', 'diagram',
        'flowchart', 'chart', 'visual', 'step by step', 'how to become',
        'learning path', 'career progression', 'development path'
    ]
    
    query_lower = query.lower()
    return any(indicator in query_lower for indicator in flowchart_indicators)

def get_response_format(query):
    """Determine the appropriate response format based on query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['salary', 'pay', 'earning', 'income', 'compensation']):
        return 'salary_focus'
    elif any(word in query_lower for word in ['course', 'learn', 'study', 'education', 'training']):
        return 'learning_focus'
    elif any(word in query_lower for word in ['company', 'companies', 'employer', 'organization']):
        return 'company_focus'
    elif any(word in query_lower for word in ['skill', 'skills', 'requirement', 'qualifications']):
        return 'skills_focus'
    elif any(word in query_lower for word in ['interview', 'preparation', 'tips', 'advice']):
        return 'interview_focus'
    elif any(word in query_lower for word in ['roadmap', 'path', 'steps', 'plan', 'journey']):
        return 'roadmap_focus'
    else:
        return 'general'

def create_dynamic_prompt(query, response_format, field_of_interest=None):
    """Create dynamic prompts based on query type and format needed"""
    
    base_context = f"User query: '{query}'"
    if field_of_interest:
        base_context += f"\nIdentified field: {field_of_interest}"
    
    format_prompts = {
        'salary_focus': f"""
        {base_context}
        
        Focus heavily on salary and compensation information. Provide:
        1. Detailed salary ranges for different experience levels
        2. Factors that affect compensation
        3. Geographic variations in pay
        4. Benefits and perks typically offered
        5. Salary progression over time
        6. High-paying specializations within the field
        
        Include specific numbers and ranges wherever possible.
        """,
        
        'learning_focus': f"""
        {base_context}
        
        Focus on educational resources and learning paths. Provide:
        1. Specific course recommendations with platforms (Coursera, Udemy, edX)
        2. Free vs paid learning options
        3. Books and reading materials
        4. Hands-on projects and portfolios
        5. Certifications worth pursuing
        6. Time estimates for learning paths
        7. Prerequisites and learning sequence
        
        Include actual course names and instructor recommendations where relevant.
        """,
        
        'company_focus': f"""
        {base_context}
        
        Focus on company and employment information. Provide:
        1. Top companies hiring in this field
        2. Startup vs enterprise opportunities
        3. Remote work possibilities
        4. Company culture considerations
        5. Growth opportunities at different company types
        6. Industry leaders and emerging companies
        
        Include specific company names and what makes them attractive employers.
        """,
        
        'skills_focus': f"""
        {base_context}
        
        Focus on detailed skill requirements. Provide:
        1. Essential technical skills with proficiency levels
        2. Soft skills and their importance
        3. Tools and technologies to master
        4. Skill progression from beginner to expert
        5. Most in-demand skills currently
        6. Future skills that will be important
        7. How to demonstrate these skills
        
        Be very specific about skill requirements and how to develop them.
        """,
        
        'interview_focus': f"""
        {base_context}
        
        Focus on interview and job preparation. Provide:
        1. Common interview questions and how to answer them
        2. Technical assessment preparation
        3. Portfolio and project showcase tips
        4. Resume optimization for this field
        5. Networking strategies
        6. Interview formats (technical, behavioral, case studies)
        7. Salary negotiation tips
        
        Include specific examples and actionable advice.
        """,
        
        'roadmap_focus': f"""
        {base_context}
        
        Create a comprehensive roadmap with:
        1. Clear timeline and milestones
        2. Sequential learning steps
        3. Practical projects at each stage
        4. Skill validation methods
        5. Career transition strategies
        6. Resource allocation and time management
        7. Alternative paths and specializations
        
        Structure as a step-by-step journey with specific actions and timeframes.
        """,
        
        'general': f"""
        {base_context}
        
        Provide a well-rounded response covering:
        1. Overview of the field/role
        2. Key opportunities and trends
        3. Getting started advice
        4. Resources and next steps
        5. Common challenges and how to overcome them
        
        Tailor the response to be most helpful for this specific question.
        """
    }
    
    return format_prompts.get(response_format, format_prompts['general'])

def main_app():     
    # Configure Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
    genai.configure(api_key=GEMINI_API_KEY)

    # Define generation config
    generation_config = genai.types.GenerationConfig(
        temperature=0.7,
        top_p=0.9,
        max_output_tokens=6000,
    )

    def is_career_related_semantically(query):
        classifier_model = genai.GenerativeModel("gemini-2.0-flash")
        classification_prompt = f"""
        You are an expert classifier. Analyze the user input and determine if it's asking for career guidance, job advice, professional development, or work-related help.

        VALID career-related inputs include:
        - Career planning and transitions
        - Job search and application advice
        - Skill development and learning paths
        - Interview preparation
        - Salary and compensation questions
        - Professional development
        - Industry insights and trends
        - Educational and certification guidance
        - Workplace challenges and solutions
        - Entrepreneurship and business advice
        - Portfolio and project guidance
        - Networking and professional relationships

        INVALID inputs are completely unrelated topics like:
        - Creative writing, stories, entertainment
        - General facts, history, science (unless career-related)
        - Personal relationships (unless workplace-related)
        - Health, fitness, cooking (unless career-related)
        - Travel, hobbies, sports (unless career-related)

        Query: "{query}"

        Is this clearly career/professional development related? Answer only 'Yes' or 'No'.
        """

        try:
            result = classifier_model.generate_content(classification_prompt)
            return result.text.strip().lower().startswith("yes")
        except:
            # If classification fails, be generous and assume it might be career-related
            career_keywords = ['job', 'career', 'work', 'skill', 'resume', 'interview', 'salary', 'company', 'professional', 'development', 'learn', 'study', 'certification']
            return any(keyword in query.lower() for keyword in career_keywords)

    # Session state
    if "chat" not in st.session_state:
        model = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config)
        st.session_state.chat = model.start_chat(history=[])

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "flowchart": 
                render_enhanced_flowchart(msg["data"], msg.get("title", "Career Roadmap"))
            else:
                st.markdown(msg["text"], unsafe_allow_html=True)

    # Function to generate job roles dynamically
    def get_job_roles_from_gemini(field):
        prompt = f"""
        For the field of {field}, provide:
        1. Entry-level positions (0-2 years experience)
        2. Mid-level roles (3-5 years experience)  
        3. Senior positions (6+ years experience)
        4. Leadership roles
        5. Specialized/niche roles
        6. Emerging roles in this field
        
        Include brief descriptions of key responsibilities for each role.
        """
        
        try:
            response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Various roles are available in {field} including entry-level to senior positions. Please specify what level you're interested in for more detailed information."

    # Function to generate career roadmap steps
    def get_career_steps_from_gemini(career_field, query):
        # Determine if user wants a detailed timeline
        timeline_indicators = ['year', 'month', 'timeline', 'when', 'how long', 'duration']
        wants_timeline = any(indicator in query.lower() for indicator in timeline_indicators)
        
        if wants_timeline:
            prompt = f"""
            Create a detailed timeline roadmap for becoming a {career_field}. 
            Provide 12-15 specific steps with approximate timeframes.
            Format each step as: "Month X-Y: Specific action or milestone"
            Focus on practical, actionable steps with realistic time estimates.
            """
        else:
            prompt = f"""
            Create a comprehensive step-by-step roadmap for becoming a {career_field}.
            Provide 10-12 clear, actionable steps in logical sequence.
            Each step should be specific and measurable.
            Focus on the most important milestones and activities.
            """
        
        try:
            response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
            steps_text = response.text.strip()
            
            # Parse steps from the response
            steps = []
            for line in steps_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                    # Clean up the step
                    clean_step = re.sub(r'^\d+\.?\s*', '', line)
                    clean_step = re.sub(r'^[\-\*•]\s*', '', clean_step)
                    if clean_step:
                        steps.append(clean_step)
            
            return steps if steps else ["Start learning fundamentals", "Build projects", "Apply for positions"]
            
        except Exception as e:
            return ["Learn the basics", "Practice with projects", "Build a portfolio", "Apply for jobs"]

    # User input
    prompt = st.chat_input("Ask anything about your career path...")
        
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "text": prompt})

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                if is_career_related_semantically(prompt):
                    try:
                        # Determine response format needed
                        response_format = get_response_format(prompt)
                        
                        # Check if flowchart is needed
                        needs_flowchart = should_generate_flowchart(prompt)
                        
                        # Extract field of interest
                        field_identification_prompt = f"""
                        Analyze this career-related query and identify the main field/domain being discussed.
                        Query: "{prompt}"
                        
                        Provide only the field name (e.g., "Data Science", "Web Development", "Product Management", "Digital Marketing").
                        If no specific field is mentioned, respond with "General Career Guidance".
                        """

                        field_response = genai.GenerativeModel("gemini-2.0-flash").generate_content(field_identification_prompt)
                        field_of_interest = field_response.text.strip()
                        
                        # Create dynamic prompt based on query type
                        dynamic_prompt = create_dynamic_prompt(prompt, response_format, field_of_interest)
                        
                        # Add job roles and courses if relevant
                        enhanced_prompt = dynamic_prompt
                        if response_format in ['general', 'learning_focus', 'company_focus'] and field_of_interest != "General Career Guidance":
                            job_roles = get_job_roles_from_gemini(field_of_interest)
                            enhanced_prompt += f"\n\n**Relevant Job Roles in {field_of_interest}:**\n{job_roles}"
                            
                            if response_format == 'learning_focus':
                                enhanced_prompt += f"\n\n**Please also suggest specific online courses and learning resources for {field_of_interest} with course names and platforms.**"

                        # Generate main response
                        response = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config).generate_content(enhanced_prompt)
                        full_text = response.text

                        # Add flowchart indicator if needed
                        if needs_flowchart:
                            full_text += "\n\n📊 **Visual Roadmap Below** ⬇️"

                        # Stream the response with enhanced formatting
                        placeholder = st.empty()
                        displayed_text = ""

                        # Enhanced streaming with better pacing
                        paragraphs = full_text.split('\n\n')
                        for para in paragraphs:
                            para = para.strip()
                            if para:
                                words = para.split(' ')
                                for word in words:
                                    displayed_text += word + " "
                                    placeholder.markdown(displayed_text + "▌", unsafe_allow_html=True)
                                    time.sleep(0.008)  # Slightly faster
                                displayed_text += "\n\n"
                                placeholder.markdown(displayed_text + "▌", unsafe_allow_html=True)
                                time.sleep(0.1)

                        # Final output without cursor
                        placeholder.markdown(displayed_text, unsafe_allow_html=True)

                        # Generate and display flowchart if needed
                        if needs_flowchart and field_of_interest != "General Career Guidance":
                            with st.spinner("📊 Creating visual roadmap..."):
                                steps = get_career_steps_from_gemini(field_of_interest, prompt)
                                if steps:
                                    flowchart_title = f"{field_of_interest} Career Roadmap"
                                    render_enhanced_flowchart(steps, flowchart_title)
                                    
                                    # Store in chat history
                                    st.session_state.chat_history.append({"role": "assistant", "text": full_text})
                                    st.session_state.chat_history.append({
                                        "role": "assistant", 
                                        "type": "flowchart", 
                                        "data": steps,
                                        "title": flowchart_title
                                    })
                                else:
                                    st.session_state.chat_history.append({"role": "assistant", "text": full_text})
                        else:
                            st.session_state.chat_history.append({"role": "assistant", "text": full_text})
                            
                    except Exception as e:
                        error_message = "I encountered an issue generating your career guidance. Let me try a different approach - could you rephrase your question or be more specific about what you'd like to know?"
                        st.markdown(error_message)
                        st.session_state.chat_history.append({"role": "assistant", "text": error_message})
                
                else:
                    # Enhanced non-career response
                    non_career_response = """
                    🎯 **I'm your specialized Career Path Oracle!** 
                    
                    I'm designed to help you with:
                    
                    **Career Planning & Development**
                    - Career transitions and path planning
                    - Skill development roadmaps
                    - Industry insights and trends
                    - Job Search & Applications
                    - Resume optimization tips
                    - Interview preparation strategies
                    - Salary negotiation guidance
                    - Professional Growth
                    - Learning resources and courses
                    - Certification recommendations  
                    - Portfolio and project guidance
                    
                    -- 🚀 Try asking me: --
                    - "How do I transition from marketing to data science?"
                    - "Create a 6-month roadmap for becoming a full-stack developer"
                    - "What skills do I need for a Product Manager role?"
                    - "Best companies for remote software engineering jobs"
                    
                    What career goal can I help you achieve today?
                    """
                    st.markdown(non_career_response)
                    st.session_state.chat_history.append({"role": "assistant", "text": non_career_response})