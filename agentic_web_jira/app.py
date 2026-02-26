import streamlit as st
import config
from jira_agent import JiraAgent
from scraper import ScraperAgent
from llm_processor import LLMProcessor
import pandas as pd
import json
from logger import setup_logging, get_logger

# Initialize Logging
setup_logging()
logger = get_logger("JiraApp")

# Page Configuration
st.set_page_config(
    page_title="Agentic Jira Story Creator",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #0052cc;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0065ff;
        border-color: #0065ff;
    }
    /* Section Headers */
    h1, h2, h3 {
        color: #0052cc !important;
    }
    .css-1kyx75w {
        background-color: #172b4d;
        color: white;
    }
    .story-card {
        background-color: #ffffff;
        color: #172b4d !important;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dfe1e6;
        border-left: 5px solid #0052cc;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .story-card h3, .story-card p, .story-card strong, .story-card li {
        color: #172b4d !important;
    }
    .success-text {
        color: #36b37e !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialization
if 'connected' not in st.session_state:
    st.session_state.connected = False
    st.session_state.stories = []
    st.session_state.projects = []
    st.session_state.issue_types = []
    st.session_state.selected_project = ""
    st.session_state.selected_issue_type = "Story"

@st.cache_resource
def get_jira_agent(url, email, token):
    # Update config for the agent
    config.JIRA_URL = url
    config.JIRA_EMAIL = email
    config.JIRA_API_TOKEN = token
    agent = JiraAgent(email=email)
    if agent.connect(email):
        return agent
    return None

# Sidebar - Configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    with st.expander("Jira Settings", expanded=not st.session_state.connected):
        ui_jira_url = st.text_input("Jira URL", value=config.JIRA_URL)
        ui_jira_email = st.text_input("Jira Email", value=config.JIRA_EMAIL)
        ui_jira_token = st.text_input("Jira API Token", value=config.JIRA_API_TOKEN, type="password")
        
        if st.button("Connect to Jira"):
            jira_agent = get_jira_agent(ui_jira_url, ui_jira_email, ui_jira_token)
            if jira_agent:
                st.session_state.connected = True
                st.session_state.projects = jira_agent.get_projects()
                st.success("Connected successfully!")
            else:
                st.error("Connection failed. Check your credentials.")

    # Get agent from cache if connected
    jira_agent = None
    if st.session_state.connected:
        jira_agent = get_jira_agent(ui_jira_url, ui_jira_email, ui_jira_token)

    with st.expander("LLM Settings", expanded=True):
        st.info("Using local Ollama LLM")
        base_url = st.text_input("Ollama Base URL", value=config.OLLAMA_BASE_URL)
        model = st.text_input("Model", value=config.OLLAMA_MODEL)

    st.divider()
    st.info("This agent scrapes meeting notes and uses AI to generate Jira stories.")

# Main UI
st.title("🎫 Agentic Jira Story Creator")

# Step 1: Content Retrieval
st.header("1. Retrieve Content")
col1, col2 = st.columns([1, 1])

with col1:
    source_option = st.radio("Select Source", ["URL Scraping", "Manual Input"])

content = ""
if source_option == "URL Scraping":
    target_url = st.text_input("Enter URL (Confluence or Web)", value=config.CONFLUENCE_PAGE_URL)
    if st.button("Scrape Content"):
        with st.spinner("Scraping..."):
            scraper = ScraperAgent()
            # Pass credentials in case it's Confluence
            email_val = ui_jira_email if st.session_state.connected else config.JIRA_EMAIL
            token_val = ui_jira_token if st.session_state.connected else config.JIRA_API_TOKEN
            content = scraper.scrape_url(target_url, username=email_val, token=token_val)
            if content:
                st.session_state.raw_content = content
                st.success(f"Retrieved {len(content)} characters.")
            else:
                st.error("Failed to retrieve content.")
else:
    content = st.text_area("Paste Meeting Notes", height=200, placeholder="Enter notes here...")
    if st.button("Use Manual Notes"):
        st.session_state.raw_content = content
        st.success("Content saved.")

if 'raw_content' in st.session_state and st.session_state.raw_content:
    with st.expander("View Raw Content"):
        st.write(st.session_state.raw_content)

    # Step 2: LLM Processing
    st.header("2. Generate Stories")
    if st.button("✨ Generate Jira Stories"):
        with st.spinner("LLM is analyzing content..."):
            # Update config for the processor
            config.OLLAMA_BASE_URL = base_url
            config.OLLAMA_MODEL = model
            
            processor = LLMProcessor(model_name=model)
            stories = processor.generate_stories(st.session_state.raw_content)
            if stories:
                st.session_state.stories = stories
                st.success(f"Generated {len(stories)} stories!")
            else:
                st.error("No stories were generated. Please check LLM settings or content.")

# Step 3: Review and Create
if st.session_state.stories:
    st.header("3. Review & Create")
    
    # Project & Issue Type Selection
    if st.session_state.connected and jira_agent:
        c1, c2 = st.columns(2)
        with c1:
            project_options = [f"{k} - {n}" for k, n in st.session_state.projects]
            selected_proj_str = st.selectbox("Select Project", project_options)
            current_project_key = selected_proj_str.split(" - ")[0]
            if current_project_key != st.session_state.selected_project:
                st.session_state.selected_project = current_project_key
                st.session_state.issue_types = [] # Reset issue types for new project
        
        with c2:
            if not st.session_state.issue_types:
                with st.spinner("Fetching issue types..."):
                    st.session_state.issue_types = jira_agent.get_issue_types(st.session_state.selected_project)
            
            st.session_state.selected_issue_type = st.selectbox(
                "Select Issue Type", 
                st.session_state.issue_types if st.session_state.issue_types else ["Story"],
                index=0
            )

    # List Stories
    for i, story in enumerate(st.session_state.stories):
        with st.container():
            st.markdown(f"""
            <div class="story-card">
                <h3>Story {i+1}: {story.get('summary')}</h3>
                <p><strong>Description:</strong> {story.get('description')}</p>
                <p><strong>Acceptance Criteria:</strong></p>
                <ul>
                    {"".join([f"<li>{ac}</li>" for ac in story.get('acceptance_criteria', [])])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns([1, 4])
            with col_a:
                if not st.session_state.connected:
                    st.warning("Connect to Jira first")
                elif st.button(f"Create Story {i+1}", key=f"btn_{i}"):
                    desc = story.get('description') + "\n\n*Acceptance Criteria:*\n" + "\n".join(f"- {ac}" for ac in story.get('acceptance_criteria', []))
                    with st.spinner("Creating..."):
                        issue_key = jira_agent.create_story(
                            st.session_state.selected_project, 
                            story.get('summary'), 
                            desc, 
                            issue_type=st.session_state.selected_issue_type
                        )
                        if issue_key:
                            st.markdown(f'<p class="success-text">✅ Created: <a href="{ui_jira_url}/browse/{issue_key}" target="_blank">{issue_key}</a></p>', unsafe_allow_html=True)
                        else:
                            st.error("Failed to create issue.")

st.divider()
st.caption("Powered by LangChain & Streamlit")
