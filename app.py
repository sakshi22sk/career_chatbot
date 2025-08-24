import streamlit as st
from streamlit_option_menu import option_menu
from resume import resume_analyzer
from assistant import main_app
import os

# Set page config
st.set_page_config(
    page_title="Career Path Oracle 🧙‍♂️",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'intro_shown' not in st.session_state:
    st.session_state.intro_shown = False

def show_intro():
    """Enhanced introduction page with better styling and information"""
    st.markdown("""
    <style>
    @media (max-width: 300px) {//768
        .intro-container { padding: 1rem; }
        .feature-icon { font-size: 2rem; }
        .intro-title { font-size: 2rem; }
        .intro-subtitle { font-size: 1.25rem; }
        .team-member { margin-bottom: 1rem; }
    }
    .intro-container {
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        color: white;
        text-align: center;
    }
    .feature-card {
        background: linear-gradient(135deg, #ff6ec4 0%, #a066e0 50%, #4d9fef 100%);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
    }
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
        display: inline-block;
    }
    .feature-icon:hover {
        transform: scale(1.2) rotate(10deg);
    }
    .team-card {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    .step-card {
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 15px;
        padding: 1.2rem;
        margin: 0.5rem;
        color: white;
        text-align: center;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main header
    st.markdown("""
    <div class="intro-container">
        <div style="margin-bottom: 2rem;">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                🧙‍♂️ Career Path Oracle
            </h1>
            <h2 style="font-size: 1.8rem; margin-bottom: 1rem; opacity: 0.9;">
                Your AI-Powered Career Companion
            </h2>
            <p style="font-size: 1.2rem; opacity: 0.8; max-width: 600px; margin: 0 auto;">
                Get personalized career guidance with hybrid AI analysis, comprehensive skill extraction, 
                and dynamic response formatting tailored to your unique needs.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")

    # Enhanced features section
    st.markdown("## ✨ What Makes Me Special")
    
    feature_cols = st.columns(3)
    features = [
        {
            "icon": "🔍", 
            "title": "Hybrid Resume Analysis", 
            "desc": "Advanced keyword matching + semantic AI analysis extracts skills you didn't even know you listed",
            "highlight": "99% skill detection accuracy"
        },
        {
            "icon": "🎯", 
            "title": "Dynamic Response Formatting", 
            "desc": "Intelligent responses that adapt format based on your question type - salary, learning, companies, etc.",
            "highlight": "7 specialized response types"
        },
        {
            "icon": "📊", 
            "title": "Smart Visual Roadmaps", 
            "desc": "Automatically generates flowcharts when you need step-by-step guidance or career progression maps",
            "highlight": "Auto-generated diagrams"
        }
    ]
    
    for idx, feature in enumerate(features):
        with feature_cols[idx]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{feature["icon"]}</div>
                <h3 style="margin-bottom: 1rem; color: #fff;">{feature["title"]}</h3>
                <p style="opacity: 0.9; margin-bottom: 1rem;">{feature["desc"]}</p>
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 10px; font-weight: bold;">
                    {feature["highlight"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")
    
    # Capabilities section
    st.markdown("## 🚀 My Capabilities")
    
    cap_cols = st.columns(2)
    with cap_cols[0]:
        st.markdown("""
        ### 📝 Resume Analysis
        - **Hybrid Extraction**: Keyword + AI semantic analysis
        - **Skill Categorization**: Technical, soft, and domain skills
        - **Smart Inference**: Detects implied skills from job titles
        - **Comprehensive Database**: 200+ skill categories
        """)
        
        st.markdown("""
        ### 🎯 Personalized Guidance  
        - **Career Path Mapping**: Multiple progression routes
        - **Salary Intelligence**: Current market rates & trends
        - **Industry Insights**: Company culture & opportunities
        - **Learning Roadmaps**: Courses, books, certifications
        """)
    
    with cap_cols[1]:
        st.markdown("""
        ### 🤖 Intelligent Responses
        - **Context-Aware**: Understands your specific needs
        - **Format Adaptation**: Salary, learning, interview focus
        - **Visual Generation**: Auto-creates flowcharts & diagrams
        - **Real-time Streaming**: Engaging response delivery
        """)
        
        st.markdown("""
        ### 💡 Advanced Features
        - **Multi-format Support**: PDF, DOCX resume upload
        - **Fallback Systems**: Never leaves you without answers
        - **Career Transition**: Specialized change management
        - **Future-ready**: Emerging role identification
        """)

    st.write("---")
    
    # How it works - Enhanced
    st.markdown("## 🛠️ How It Works")
    steps = [
        {"num": "1️⃣", "title": "Upload & Analyze", "desc": "Resume analysis or skill description"},
        {"num": "2️⃣", "title": "AI Processing", "desc": "Hybrid extraction + semantic understanding"},
        {"num": "3️⃣", "title": "Smart Responses", "desc": "Dynamic formatting based on your needs"},
        {"num": "4️⃣", "title": "Visual Guidance", "desc": "Auto-generated roadmaps when needed"}
    ]
    
    step_cols = st.columns(4)
    for idx, step in enumerate(steps):
        with step_cols[idx]:
            st.markdown(f"""
            <div class="step-card">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{step["num"]}</div>
                <h4 style="margin-bottom: 0.5rem;">{step["title"]}</h4>
                <p style="font-size: 0.9rem; opacity: 0.9;">{step["desc"]}</p>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")
    
    # Team section - Enhanced
    st.markdown("## 👥 Our Team")
    team_cols = st.columns(3)
    team = [
        {"name": "Pavan", "id": "12305446", "role": "ML Engineer", "focus": "AI & Analytics"},
        {"name": "Sakshi", "id": "12306499", "role": "Data Scientist", "focus": "Career Intelligence"},
        {"name": "Kausar", "id": "12316343", "role": "ML Engineer", "focus": "NLP & Automation"}
    ]
    
    for idx, member in enumerate(team):
        with team_cols[idx]:
            st.markdown(f"""
            <div class="team-card">
                <h3 style="margin-bottom: 0.5rem;">{member["name"]}</h3>
                <p style="opacity: 0.9; margin-bottom: 0.3rem;">{member["role"]}</p>
                <p style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.5rem;">{member["focus"]}</p>
                <code style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.6rem; border-radius: 5px;">
                    ID: {member["id"]}
                </code>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")
    
    # Example queries
    st.markdown("## 💭 Try These Example Queries")
    
    example_cols = st.columns(2)
    with example_cols[0]:
        st.markdown("""
        **🎯 For Specific Guidance:**
        - "Create a 6-month roadmap for becoming a data scientist"
        - "What salary can I expect as a Python developer in 2025?"
        - "Best companies for remote product management roles"
        - "How do I transition from marketing to UX design?"
        """)
    
    with example_cols[1]:
        st.markdown("""
        **📚 For Learning & Development:**
        - "What skills do I need for cloud architecture?"
        - "Best Coursera courses for machine learning engineering"
        - "How to prepare for Google software engineer interviews"
        - "Essential certifications for cybersecurity careers"
        """)

    # Call to action
    st.write("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Your Career Journey", use_container_width=True, type="primary"):
            st.session_state.intro_shown = True
            st.rerun()

def main_page():
    """Main application page with enhanced sidebar and navigation"""
    
    # Custom CSS for better styling and visibility
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .sidebar-section {
        background: linear-gradient(135deg, #ff6ec4, #a066e0, #4d9fef);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .sidebar-section h3 {
        color: ##FFFFFF;
        margin-bottom: 12px;
        font-size: 16px;
        font-weight: 700;
    }
    .sidebar-section p {
        color: ##FFFFFF;
        margin: 8px 0;
        font-size: 14px;
        line-height: 1.4;
    }
    .sidebar-section ul {
        color: #FFFFFF;
        font-size: 14px;
        line-height: 1.4;
    }
    .sidebar-section ul li {
        margin: 5px 0;
    }
    /* Fix for graphviz charts */
    .stGraphvizChart > div {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    .stGraphvizChart svg {
        max-width: 100% !important;
        height: auto !important;
    }
    /* Better contrast for all text */
    .stMarkdown {
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem;">🧙‍♂️ Career Path Oracle</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Your AI-powered career companion with hybrid analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state for menu selection
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = "Bot Assistant"

    # Enhanced sidebar
    with st.sidebar:
        # Navigation menu with better visibility
        selected = option_menu(
            menu_title="🚀 Navigation",
            options=["Bot Assistant", "Resume Analyzer"],
            icons=["robot", "file-earmark-text"],
            menu_icon="cast",
            default_index=["Bot Assistant", "Resume Analyzer"].index(st.session_state.selected_option),
            orientation="vertical",
            key="selected_option",
            styles={
                "container": {"padding": "0!important", "background": "linear-gradient(135deg, #00c853, #00bcd4)", "border-radius": "10px"},
                "icon": {"color": "#667eea", "font-size": "20px"}, 
                "nav-link": {
                    "font-size": "18px", 
                    "text-align": "left", 
                    "margin": "5px", 
                    "padding": "12px",
                    "--hover-color": "#e8f0fe",
                    "border-radius": "8px",
                    "color": "#2c3e50",
                    "font-weight": "600"
                },
                "nav-link-selected": {
                "background": "linear-gradient(135deg, #ff6ec4, #a066e0, #4d9fef)",
                "color": "white",
                "font-weight": "700",
                "border": "2px solid #5a67d8"
                },
            }
        )
        
        st.write("---")
        
        # About section
        st.markdown("""
        <div class="sidebar-section">
            <h3>🤖 About Me</h3>
            <p>I'm your Career Path Oracle with advanced capabilities:</p>
            <ul>
                <li><strong>Hybrid AI Analysis</strong>: Keyword + semantic skill extraction</li>
                <li><strong>Dynamic Responses</strong>: Tailored to your question type</li>
                <li><strong>Smart Visuals</strong>: Auto-generated career roadmaps</li>
                <li><strong>Real-time Intelligence</strong>: Current market insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Example questions
        st.markdown("""
        <div class="sidebar-section">
            <h3>💡 Example Questions</h3>
            <p><strong>For Career Planning:</strong></p>
            <ul>
                <li>"Plan my transition to AI engineering"</li>
                <li>"Create roadmap for product management"</li>
                <li>"Best path from marketing to data science"</li>
            </ul>
            <p><strong>For Specific Info:</strong></p>
            <ul>
                <li>"Data scientist salary in 2025"</li>
                <li>"Top remote-friendly tech companies"</li>
                <li>"Essential AWS certifications"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Features highlight
        st.markdown("""
        <div class="sidebar-section">
            <h3>✨ New Features</h3>
            <ul>
                <li>🔍 <strong>Advanced Skill Detection</strong>: Finds skills you didn't know you had</li>
                <li>🎯 <strong>Smart Formatting</strong>: Responses adapt to your needs</li>
                <li>📊 <strong>Auto Flowcharts</strong>: Visual roadmaps when needed</li>
                <li>⚡ <strong>Faster Processing</strong>: Enhanced AI performance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Team info with better formatting
       
        # Team info with proper formatting
        st.markdown("""
        <div class="sidebar-section">
            <h3>👥 Development Team</h3>
                <ul>
                <li><strong>Sakshi</strong>, <i>ML Engineer, AI & Analytics<i></li>
                <li><strong>Pavan</strong>,<i> Data analyst</i></li>
                <li><strong>Kausar</strong>, <i> Ml engineer, </i></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


    # Show content based on selection
    if st.session_state.selected_option == "Bot Assistant":
        main_app()
    elif st.session_state.selected_option == "Resume Analyzer":
        resume_analyzer()

# Main app entry point
def main():
    """Main application entry point"""
    try:
        # Check if required environment variables are set
        if not os.getenv("GEMINI_API_KEY"):
            st.error("⚠️ GEMINI_API_KEY not found in environment variables!")
            st.info("Please set your Gemini API key in the .env file or environment variables.")
            st.stop()
            
        # Show intro or main page based on session state
        if not st.session_state.intro_shown:
            show_intro()
        else:
            main_page()
            
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()