import streamlit as st
import google.generativeai as genai
import PyPDF2
import docx
import numpy as np
import os
import time
import re
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
genai.configure(api_key=GEMINI_API_KEY)

# Define generation config
generation_config = genai.types.GenerationConfig(
    temperature=0.7,
    top_p=0.9,
    max_output_tokens=5000,
)

# Enhanced keyword database for skill extraction
SKILL_KEYWORDS = {
    'programming_languages': [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'C', 'PHP', 'Ruby', 'Go', 'Rust',
        'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'Bash', 'PowerShell', 'VBA',
        'HTML', 'CSS', 'SQL', 'NoSQL', 'GraphQL', 'Dart', 'Objective-C', 'Assembly', 'COBOL', 'Fortran'
    ],
    'frameworks_libraries': [
        'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js', 'Django', 'Flask', 'FastAPI', 'Spring',
        'Spring Boot', 'Laravel', 'CodeIgniter', 'Ruby on Rails', 'ASP.NET', '.NET Core', 'jQuery',
        'Bootstrap', 'Tailwind CSS', 'Material-UI', 'Ant Design', 'Semantic UI', 'Foundation',
        'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn',
        'OpenCV', 'NLTK', 'spaCy', 'Hugging Face', 'LangChain', 'Streamlit', 'Gradio', 'Plotly'
    ],
    'databases': [
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server', 'MariaDB',
        'Cassandra', 'Neo4j', 'DynamoDB', 'Firebase', 'Supabase', 'CouchDB', 'InfluxDB', 'TimescaleDB'
    ],
    'cloud_devops': [
        'AWS', 'Azure', 'Google Cloud', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI',
        'GitHub Actions', 'CircleCI', 'Travis CI', 'Terraform', 'Ansible', 'Chef', 'Puppet',
        'Nagios', 'Prometheus', 'Grafana', 'ELK Stack', 'Splunk', 'New Relic', 'Datadog'
    ],
    'data_analytics': [
        'Tableau', 'Power BI', 'Looker', 'Google Analytics', 'Adobe Analytics', 'Mixpanel',
        'Segment', 'Apache Spark', 'Apache Kafka', 'Airflow', 'Databricks', 'Snowflake',
        'BigQuery', 'Redshift', 'Data Warehousing', 'ETL', 'Data Mining', 'Statistical Analysis'
    ],
    'mobile_development': [
        'Android', 'iOS', 'React Native', 'Flutter', 'Xamarin', 'Ionic', 'Cordova', 'PhoneGap',
        'Swift UI', 'Jetpack Compose', 'Android Studio', 'Xcode'
    ],
    'design_tools': [
        'Figma', 'Adobe XD', 'Sketch', 'InVision', 'Photoshop', 'Illustrator', 'After Effects',
        'Premiere Pro', 'Canva', 'Framer', 'Principle', 'Zeplin', 'Abstract'
    ],
    'project_management': [
        'Agile', 'Scrum', 'Kanban', 'JIRA', 'Trello', 'Asana', 'Monday.com', 'Notion',
        'Confluence', 'Slack', 'Microsoft Teams', 'Zoom', 'Project Management'
    ],
    'soft_skills': [
        'Leadership', 'Communication', 'Problem Solving', 'Critical Thinking', 'Teamwork',
        'Collaboration', 'Time Management', 'Adaptability', 'Creativity', 'Innovation',
        'Analytical Skills', 'Attention to Detail', 'Customer Service', 'Public Speaking',
        'Negotiation', 'Conflict Resolution', 'Mentoring', 'Coaching', 'Strategic Planning'
    ],
    'methodologies': [
        'Machine Learning', 'Deep Learning', 'Natural Language Processing', 'Computer Vision',
        'Data Science', 'Artificial Intelligence', 'Blockchain', 'Cybersecurity', 'DevOps',
        'Full Stack Development', 'Frontend Development', 'Backend Development', 'UI/UX Design',
        'Product Management', 'Digital Marketing', 'SEO', 'SEM', 'Content Marketing'
    ]
}

def extract_skills_keyword_matching(resume_text):
    """Extract skills using keyword matching"""
    text_lower = resume_text.lower()
    found_skills = set()
    
    for category, skills in SKILL_KEYWORDS.items():
        for skill in skills:
            # Check for exact matches and variations
            skill_lower = skill.lower()
            if (skill_lower in text_lower or 
                skill_lower.replace('.', '') in text_lower or
                skill_lower.replace(' ', '') in text_lower):
                found_skills.add(skill)
    
    return list(found_skills)

def extract_skills_semantic(resume_text):
    """Extract skills using semantic analysis with Gemini"""
    
    # Check for minimum viable content
    if len(resume_text.strip()) < 50:
        return []
    
    prompt = f"""
    You are an expert skill extraction system. Analyze the resume text below and extract ALL professional skills.

    IMPORTANT RULES:
    1. NEVER say "impossible", "cannot extract", or refuse to extract skills
    2. If the text is short, infer skills from any job titles, education, or context mentioned
    3. Look for implied skills from company names, project descriptions, or responsibilities
    4. Always return a comma-separated list of skills, even if you need to make reasonable inferences
    5. Focus on what a person with this background would likely know

    Extract these types of skills:
    - Technical skills (programming, tools, software)
    - Professional skills (project management, communication)
    - Domain knowledge (industry-specific expertise)
    - Soft skills (leadership, problem-solving)

    Resume Text:
    \"\"\" 
    {resume_text}
    \"\"\" 

    Return ONLY a comma-separated list of skills. No explanations or refusals.
    """

    try:
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        raw_output = response.text.strip()

        # Handle refusal responses
        refusal_indicators = ["impossible", "cannot", "no skills", "purely speculative", "limited text"]
        if any(indicator in raw_output.lower() for indicator in refusal_indicators):
            return []
       
        # Extract skills from response
        # Try to find comma-separated skills
        if ',' in raw_output:
            lines = raw_output.split('\n')
            for line in lines:
                if ',' in line and len(line.split(',')) >= 3:
                    skills = [skill.strip() for skill in line.split(",") if skill.strip()]
                    # Filter out non-skill words
                    valid_skills = []
                    for skill in skills:
                        if len(skill) > 2 and not skill.lower().startswith(('the ', 'and ', 'or ', 'but ')):
                            valid_skills.append(skill)
                    return valid_skills
        
        return []
    except Exception as e:
        print("Error during Gemini semantic skill extraction:", e)
        return []

def extract_skills_hybrid(resume_text):
    """Combine both keyword matching and semantic analysis"""
    
    # Validate input
    if not resume_text or len(resume_text.strip()) < 10:
        return fallback_extract_skills("general professional")
    
    # Get skills from both methods
    keyword_skills = extract_skills_keyword_matching(resume_text)
    semantic_skills = extract_skills_semantic(resume_text)
    
    # Combine and deduplicate
    all_skills = list(set(keyword_skills + semantic_skills))
    
    # If we still don't have enough skills, use enhanced fallback
    if len(all_skills) < 5:
        # Try to infer from any context in the text
        text_lower = resume_text.lower()
        context_skills = []
        
        # Check for common patterns
        if any(word in text_lower for word in ['student', 'graduate', 'university', 'college']):
            context_skills.extend(['Research', 'Analysis', 'Communication', 'Time Management', 'Problem Solving'])
        
        if any(word in text_lower for word in ['work', 'job', 'experience', 'position']):
            context_skills.extend(['Professional Communication', 'Teamwork', 'Adaptability', 'Customer Service'])
            
        if any(word in text_lower for word in ['project', 'team', 'lead', 'manage']):
            context_skills.extend(['Project Management', 'Leadership', 'Collaboration', 'Planning'])
            
        # Add context skills and general professional skills
        fallback_skills = fallback_extract_skills(resume_text)
        all_skills = list(set(all_skills + context_skills + fallback_skills))
    
    # Ensure we always return some skills
    if len(all_skills) < 3:
        all_skills.extend(['Communication', 'Problem Solving', 'Time Management', 'Adaptability', 'Critical Thinking'])
    
    return sorted(list(set(all_skills)))

def extract_skills(resume_text):
    """Main skill extraction function using hybrid approach"""
    return extract_skills_hybrid(resume_text)

def fallback_extract_skills(text):
    """Enhanced fallback skill extraction with better intelligence"""
    text_lower = text.lower()
    found_skills = []
    
    # If the text is extremely short or meaningless, provide general professional skills
    if len(text.strip()) < 10 or text.strip() in ["1\n2", "1 2", "12", "1", "2"]:
        return [
            'Communication', 'Problem Solving', 'Time Management', 'Teamwork', 
            'Adaptability', 'Critical Thinking', 'Organization', 'Leadership Potential',
            'Customer Service', 'Microsoft Office', 'Email Management', 'Data Entry'
        ]
    
    # Job title-based skill inference
    job_title_skills = {
        'developer': ['Programming', 'Software Development', 'Debugging', 'Version Control', 'Problem Solving'],
        'engineer': ['Engineering', 'Problem Solving', 'Technical Analysis', 'System Design', 'Mathematics'],
        'analyst': ['Data Analysis', 'Excel', 'SQL', 'Critical Thinking', 'Reporting', 'Statistics'],
        'manager': ['Leadership', 'Project Management', 'Team Management', 'Communication', 'Planning'],
        'designer': ['Design', 'Creativity', 'Adobe Creative Suite', 'UI/UX', 'Visual Design', 'Typography'],
        'marketing': ['Digital Marketing', 'Communication', 'Analytics', 'Content Creation', 'Social Media'],
        'sales': ['Sales', 'Communication', 'Negotiation', 'Customer Relations', 'CRM', 'Prospecting'],
        'teacher': ['Education', 'Communication', 'Curriculum Development', 'Public Speaking', 'Mentoring'],
        'nurse': ['Healthcare', 'Patient Care', 'Medical Knowledge', 'Communication', 'Emergency Response'],
        'accountant': ['Accounting', 'Financial Analysis', 'Excel', 'Tax Preparation', 'Bookkeeping'],
        'consultant': ['Consulting', 'Analysis', 'Communication', 'Problem Solving', 'Business Strategy']
    }
    
    # Check for job title-based skills
    for title, skills in job_title_skills.items():
        if title in text_lower:
            found_skills.extend(skills)
    
    # Education-based skills
    education_skills = {
        'university': ['Research', 'Writing', 'Analysis', 'Time Management', 'Academic Research'],
        'college': ['Study Skills', 'Research', 'Writing', 'Presentation', 'Group Work'],
        'mba': ['Business Strategy', 'Leadership', 'Finance', 'Marketing', 'Operations'],
        'engineering': ['Mathematics', 'Problem Solving', 'Technical Analysis', 'Design', 'Programming'],
        'computer science': ['Programming', 'Algorithms', 'Data Structures', 'Software Development'],
        'business': ['Business Analysis', 'Communication', 'Finance', 'Marketing', 'Strategy']
    }
    
    for education, skills in education_skills.items():
        if education in text_lower:
            found_skills.extend(skills)
    
    # Company-based skill inference
    company_skills = {
        'google': ['Technology', 'Innovation', 'Data Analysis', 'Cloud Computing', 'Digital Marketing'],
        'microsoft': ['Software Development', 'Cloud Computing', 'Office Suite', 'Technology'],
        'amazon': ['E-commerce', 'Cloud Computing', 'Logistics', 'Customer Service', 'Analytics'],
        'apple': ['Design', 'Innovation', 'Technology', 'User Experience', 'Product Development'],
        'facebook': ['Social Media', 'Digital Marketing', 'Analytics', 'Technology', 'Communication'],
        'tesla': ['Innovation', 'Engineering', 'Sustainability', 'Manufacturing', 'Technology']
    }
    
    for company, skills in company_skills.items():
        if company in text_lower:
            found_skills.extend(skills)
    
    # Common technical keywords with variations
    tech_keywords_map = {
        'python': 'Python Programming',
        'java': 'Java Programming', 
        'javascript': 'JavaScript',
        'sql': 'SQL Database Management',
        'excel': 'Microsoft Excel',
        'powerpoint': 'Microsoft PowerPoint',
        'word': 'Microsoft Word',
        'photoshop': 'Adobe Photoshop',
        'illustrator': 'Adobe Illustrator',
        'html': 'HTML',
        'css': 'CSS',
        'react': 'React.js',
        'node': 'Node.js',
        'aws': 'Amazon Web Services',
        'azure': 'Microsoft Azure',
        'docker': 'Docker',
        'git': 'Git Version Control',
        'linux': 'Linux',
        'windows': 'Windows Operating System',
        'machine learning': 'Machine Learning',
        'ai': 'Artificial Intelligence',
        'data science': 'Data Science',
        'analytics': 'Data Analytics'
    }
    
    for keyword, skill_name in tech_keywords_map.items():
        if keyword in text_lower:
            found_skills.append(skill_name)
    
    # If still no skills found, add universal professional skills
    if not found_skills:
        found_skills = [
            'Communication', 'Teamwork', 'Problem Solving', 'Time Management',
            'Adaptability', 'Attention to Detail', 'Customer Service', 'Organization'
        ]
    
    return list(set(found_skills))  # Remove duplicates

# Function to read PDF file
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# Function to read DOCX file
def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Enhanced career path generation
def get_career_paths(skills):
    """Generate comprehensive career paths based on skills"""
    
    if not skills:
        skills = ['Communication', 'Problem Solving', 'Time Management']
    
    prompt = f"""
    Based on these skills: {', '.join(skills)}

    Provide a comprehensive career analysis with:

    ## 🎯 PRIMARY CAREER PATHS
    List 3-4 main career directions that match these skills.

    ## 💰 HIGH-PAYING ROLES  
    For each path, suggest specific job titles with salary ranges.

    ## 🚀 EMERGING OPPORTUNITIES
    Identify trending roles in growing fields.

    ## 📈 SKILL DEVELOPMENT
    Recommend additional skills to learn for advancement.

    ## 🏢 INDUSTRY RECOMMENDATIONS
    Which industries would value these skills most.

    ## ✅ IMMEDIATE NEXT STEPS
    3-5 actionable steps to take right now.

    Keep it practical, specific, and actionable. Focus on real opportunities this person can pursue.
    """
    
    try:
        response = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config).generate_content(prompt)
        return response.text
    except Exception as e:
        return f"""
        ## 🎯 Based on your skills: {', '.join(skills)}

        **Primary Career Paths:**
        • Business Analysis & Operations
        • Project Management & Coordination  
        • Customer Relations & Support
        • Administrative & Executive Assistance

        **High-Paying Roles:**
        • Senior Business Analyst ($60k-$90k)
        • Project Manager ($70k-$100k)
        • Operations Manager ($65k-$95k)
        • Executive Assistant ($45k-$70k)

        **Next Steps:**
        1. Update your resume highlighting these transferable skills
        2. Consider certification in Project Management (PMP) or Business Analysis
        3. Build a LinkedIn profile showcasing your experience
        4. Network with professionals in your target industries
        5. Apply for roles that match your skill set

        These skills are valuable across many industries - focus on roles that leverage your strengths!
        """

# Streamlit UI for file upload
def resume_analyzer():
    st.markdown("# 📄 Resume Analyzer for Career Pathways")
    
    # Add some guidance
    st.markdown("""
    **Upload your resume and get:**
    - ✅ Comprehensive skill extraction (keyword + AI analysis)
    - 🎯 Personalized career path recommendations  
    - 💰 High-paying job role suggestions
    - 📈 Industry insights and growth opportunities
    """)
    
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or DOCX)", 
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX. Maximum file size: 200MB"
    )
    
    if uploaded_file:
        with st.chat_message("assistant"):
            with st.spinner("🔍 Analyzing your resume with hybrid AI + keyword matching..."):
                try:
                    # Extract text based on file type
                    if uploaded_file.type == "application/pdf":
                        resume_text = read_pdf(uploaded_file)
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        resume_text = read_docx(uploaded_file)
                    else:
                        st.error("Unsupported file format. Please upload a PDF or DOCX file.")
                        return

                    if not resume_text.strip():
                        st.error("❌ Could not extract text from the uploaded file.")
                        st.info("This might be an image-based PDF or encrypted file. Try converting it to text format first.")
                        return

                    # Show extracted text for transparency
                    with st.expander("🔍 View Extracted Text (for debugging)", expanded=False):
                        st.text_area("Raw extracted text:", resume_text[:500], height=100, disabled=True)

                    # Check for very short or meaningless content
                    if len(resume_text.strip()) < 50 or resume_text.strip() in ["1\n2", "1 2", "12"]:
                        st.warning("⚠️ The extracted text appears to be incomplete or corrupted.")
                        
                        # Provide specific guidance
                        st.markdown("""
                        **What's happening:** Your PDF was uploaded successfully, but it only contains: `{}`
                        
                        **Possible causes:**
                        - The PDF might be image-based (scanned document)
                        - The PDF might have copy protection
                        - The content might be in tables or special formatting
                        - The file might be corrupted
                        
                        **Solutions:**
                        1. **Try OCR**: If it's a scanned PDF, use an OCR tool first
                        2. **Copy-paste**: Manually copy your resume text and use the Bot Assistant
                        3. **Convert format**: Try saving as a different PDF or Word document
                        4. **Use Bot Assistant**: Just tell me about your skills and experience directly
                        """.format(resume_text.strip()[:50]))
                        
                        # Offer alternative
                        st.info("💡 **Quick Alternative**: Use the Bot Assistant to describe your background and get career advice!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🤖 Switch to Bot Assistant", use_container_width=True, type="primary"):
                                st.session_state.selected_option = "Bot Assistant"
                                st.rerun()
                        with col2:
                            if st.button("🔄 Try Different File", use_container_width=True):
                                st.rerun()
                        return

                    # Extract skills using hybrid approach
                    skills = extract_skills(resume_text)
                    
                    if skills and len(skills) > 2:
                        # Display extracted skills in a nice format
                        st.success(f"✅ Found {len(skills)} skills in your resume!")
                        
                        # Group skills by category for better display
                        skill_categories = {
                            'Technical Skills': [],
                            'Soft Skills': [],
                            'Other Skills': []
                        }
                        
                        for skill in skills:
                            skill_lower = skill.lower()
                            if any(soft_skill.lower() in skill_lower for soft_skill in SKILL_KEYWORDS['soft_skills']):
                                skill_categories['Soft Skills'].append(skill)
                            elif (any(tech_skill.lower() in skill_lower for tech_skill in 
                                    SKILL_KEYWORDS['programming_languages'] + 
                                    SKILL_KEYWORDS['frameworks_libraries'] + 
                                    SKILL_KEYWORDS['databases'] + 
                                    SKILL_KEYWORDS['cloud_devops'])):
                                skill_categories['Technical Skills'].append(skill)
                            else:
                                skill_categories['Other Skills'].append(skill)
                        
                        # Display categorized skills
                        cols = st.columns(3)
                        for i, (category, category_skills) in enumerate(skill_categories.items()):
                            if category_skills:
                                with cols[i]:
                                    st.markdown(f"**{category}:**")
                                    st.markdown("• " + "\n• ".join(category_skills))
                        
                        st.markdown("---")
                        
                        # Generate career paths
                        with st.spinner("🚀 Generating personalized career recommendations..."):
                            career_paths = get_career_paths(skills)
                            
                            # Stream the response
                            placeholder = st.empty()
                            displayed_text = ""
                            
                            # Word-by-word streaming with better formatting
                            sections = re.split(r"(?<=\n)\n+", career_paths.strip())
                            for section in sections:
                                section = section.strip()
                                if section:
                                    words = section.split(" ")
                                    for word in words:
                                        displayed_text += word + " "
                                        placeholder.markdown(displayed_text + "▌", unsafe_allow_html=True)
                                        time.sleep(0.01)
                                    displayed_text += "\n\n"
                                    placeholder.markdown(displayed_text + "▌", unsafe_allow_html=True)
                                    time.sleep(0.05)
                            
                            # Final output without cursor
                            placeholder.markdown(displayed_text, unsafe_allow_html=True)
                    
                    else:
                        st.info("🤔 I wasn't able to extract specific skills from this resume format.")
                        st.markdown("""
                        **This is normal and can happen when:**
                        - The resume uses unique formatting
                        - Skills are embedded in paragraphs rather than listed
                        - The document uses tables or complex layouts
                        - The content is very brief or general
                        
                        **Let's try a different approach! I can still help you:**
                        """)
                        
                        # Offer manual skill input
                        st.markdown("### 🎯 Tell me about yourself:")
                        manual_input = st.text_area(
                            "Describe your skills, experience, or career interests:",
                            placeholder="e.g., I'm a marketing professional with 3 years experience in social media, content creation, and campaign management. I know Adobe Creative Suite and Google Analytics...",
                            height=100
                        )
                        
                        if manual_input and len(manual_input.strip()) > 20:
                            with st.spinner("🔍 Analyzing your background..."):
                                # Use the manual input as resume text
                                manual_skills = extract_skills(manual_input)
                                
                                if manual_skills:
                                    st.success(f"✅ Great! I identified these skills from your description:")
                                    st.markdown("• " + "\n• ".join(manual_skills))
                                    
                                    st.markdown("---")
                                    
                                    # Generate career paths based on manual input
                                    career_analysis = get_career_paths(manual_skills)
                                    
                                    # Stream the response
                                    placeholder = st.empty()
                                    displayed_text = ""
                                    
                                    sections = re.split(r"(?<=\n)\n+", career_analysis.strip())
                                    for section in sections:
                                        section = section.strip()
                                        if section:
                                            words = section.split(" ")
                                            for word in words:
                                                displayed_text += word + " "
                                                placeholder.markdown(displayed_text + "▌", unsafe_allow_html=True)
                                                time.sleep(0.01)
                                            displayed_text += "\n\n"
                                            placeholder.markdown(displayed_text + "▌", unsafe_allow_html=True)
                                            time.sleep(0.05)
                                    
                                    placeholder.markdown(displayed_text, unsafe_allow_html=True)
                        elif st.button("🤖 Switch to Bot Assistant Instead", type="primary"):
                            st.session_state.selected_option = "Bot Assistant"
                            st.rerun()
                        
                        
                except Exception as e:
                    st.error(f"An error occurred while processing your resume: {str(e)}")
                    st.markdown("Please try uploading a different file or contact support if the issue persists.")
    
    else:
        # Show example when no file is uploaded
        st.info("👆 Upload your resume above to get started!")
        
        with st.expander("💡 What skills will be extracted?"):
            st.markdown("""
            Our hybrid extraction system looks for:
            
            **Technical Skills:**
            - Programming languages (Python, Java, JavaScript, etc.)
            - Frameworks & Libraries (React, Django, TensorFlow, etc.) 
            - Databases (MySQL, MongoDB, PostgreSQL, etc.)
            - Cloud platforms (AWS, Azure, Google Cloud, etc.)
            - Tools & Technologies (Docker, Git, Jenkins, etc.)
            
            **Soft Skills:**
            - Leadership, Communication, Problem-solving
            - Project Management, Teamwork, etc.
            
            **Domain Knowledge:**
            - Industry-specific skills and methodologies
            - Certifications and specializations
            """)