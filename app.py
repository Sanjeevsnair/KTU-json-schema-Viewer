from typing import Dict
from requests import request
import streamlit as st
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_ACCOUNT_FILE = "ktubot-114e855ff83f.json"
GOOGLE_DRIVE_FOLDER_ID="15gnvPIxP4oqFghT1f-3lyciYApL7Qget"
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)

drive_service = build('drive', 'v3', credentials=credentials)
subject_cache: Dict[str, Dict] = {}

def list_drive_folder(folder_id):
    """List all files in a Google Drive folder"""
    try:
        results = drive_service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name, mimeType)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        logger.error(f"Error listing Drive folder: {str(e)}")
        raise Exception("Error accessing Google Drive")
    
def get_file_content(file_id):
    """Get content of a file from Google Drive"""
    request = drive_service.files().get_media(fileId=file_id)
    file_content = request.execute()
    return file_content

def load_subject_data(department: str, semester: str, subject: str) -> Dict:
    cache_key = f"{department}_{semester}_{subject}"
    
    if cache_key in subject_cache:
        return subject_cache[cache_key]
    
    deptfolders = list_drive_folder(GOOGLE_DRIVE_FOLDER_ID)
    dept_folder = next((f for f in deptfolders if f['name'] == department and f['mimeType'] == 'application/vnd.google-apps.folder'), None)
    
    semester_folders = list_drive_folder(dept_folder['id'])
    semester_folder = next((f for f in semester_folders if f['name'] == semester and f['mimeType'] == 'application/vnd.google-apps.folder'), None)
    
    subject_files = list_drive_folder(semester_folder['id'])
    subject_file = next((f for f in subject_files if f['name'] == f"{subject}.json"), None)
    
    file_content = get_file_content(subject_file['id'])
    data = json.loads(file_content.decode('utf-8'))
    subject_cache[cache_key] = data
    return data

def get_departments():
    folders = list_drive_folder(GOOGLE_DRIVE_FOLDER_ID)
    departments = [f['name'] for f in folders if f['mimeType'] == 'application/vnd.google-apps.folder']
    return departments
    
def get_semesters(department : str):
    folders = list_drive_folder(GOOGLE_DRIVE_FOLDER_ID)
    dep_folderids = [f['id'] for f in folders if f['name'] == f'{department}']
    semester_folders = list_drive_folder(dep_folderids[0])
    semesters = [f['name'] for f in semester_folders if f['mimeType'] == 'application/vnd.google-apps.folder']
    return semesters

def get_subjects(department : str, semester : str,):
    folders = list_drive_folder(GOOGLE_DRIVE_FOLDER_ID)
    dep_folderids = [f['id'] for f in folders if f['name'] == f'{department}']
    semester_folders = list_drive_folder(dep_folderids[0])
    semesters = [f['name'] for f in semester_folders if f['mimeType'] == 'application/vnd.google-apps.folder']
    
    sem_folderids = [f['id'] for f in semester_folders if f['name'] == f'{semester}']
    subject_files = list_drive_folder(sem_folderids[0])
    subjects = [f['name'].replace('.json', '') for f in subject_files if f['name'].endswith('.json')]
    return subjects

# Custom CSS for modern styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom Header */
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .custom-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .custom-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Legend/Guide Section */
    .content-guide {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #0284c7;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .guide-title {
        color: #0c4a6e;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .guide-items {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
    }
    
    .guide-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: white;
        border-radius: 10px;
        border-left: 4px solid;
    }
    
    .guide-module {
        border-left-color: #2563eb;
    }
    
    .guide-topic {
        border-left-color: #059669;
    }
    
    .guide-subtopic {
        border-left-color: #dc2626;
    }
    
    .guide-icon {
        width: 35px;
        height: 35px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        color: white;
        font-size: 0.9rem;
    }
    
    .guide-module .guide-icon {
        background: #2563eb;
    }
    
    .guide-topic .guide-icon {
        background: #059669;
        width: 30px;
        height: 30px;
        border-radius: 6px;
        font-size: 0.8rem;
    }
    
    .guide-subtopic .guide-icon {
        background: #dc2626;
        width: 25px;
        height: 25px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    .guide-text {
        flex: 1;
    }
    
    .guide-label {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.25rem;
    }
    
    .guide-description {
        font-size: 0.85rem;
        color: #64748b;
        margin: 0;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 15px;
        padding: 1.5rem;
    }
    
    /* Subject Info Card */
    .subject-info-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border-left: 5px solid #ff6b35;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    
    .subject-info-card h2 {
        color: #2d3748;
        margin: 0 0 0.5rem 0;
        font-weight: 600;
    }
    
    .subject-path {
        color: #4a5568;
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* Consistent Content Cards */
    .content-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Module Style */
    .module-card {
        border-left: 5px solid #2563eb;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .module-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .module-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
    }
    
    .module-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e40af;
        margin: 0;
        display: flex;
        align-items: center;
        flex: 1;
    }
    
    .module-number {
        background: #2563eb;
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-right: 1rem;
        font-size: 0.9rem;
    }
    
    .module-toggle {
        background: none;
        border: none;
        color: #2563eb;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 6px;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 40px;
        height: 40px;
    }
    
    .module-toggle:hover {
        background: rgba(37, 99, 235, 0.1);
        transform: scale(1.1);
    }
    
    .module-content {
        margin-top: 1rem;
        transition: all 0.3s ease;
    }
    
    .module-content.collapsed {
        display: none;
    }
    
    .module-summary {
        margin-top: 0.5rem;
        font-size: 0.9rem;
        color: #64748b;
        font-style: italic;
    }
    
    /* Topic Style */
    .topic-card {
        border-left: 4px solid #059669;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        margin-left: 1rem;
    }
    
    .topic-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #047857;
        margin: 0;
        display: flex;
        align-items: center;
    }
    
    .topic-number {
        background: #059669;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-right: 0.75rem;
        font-size: 0.8rem;
    }
    
    /* Subtopic Style */
    .subtopic-card {
        border-left: 3px solid #dc2626;
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        margin-left: 2rem;
    }
    
    .subtopic-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #b91c1c;
        margin: 0;
        display: flex;
        align-items: center;
    }
    
    .subtopic-number {
        background: #dc2626;
        color: white;
        width: 25px;
        height: 25px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-right: 0.5rem;
        font-size: 0.75rem;
    }
    
    /* Image Gallery Styling */
    .image-gallery {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .image-item {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-align: center;
    }
    
    .image-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 0.75rem;
        padding: 0.4rem 0.8rem;
        background: #f7fafc;
        border-radius: 5px;
        display: inline-block;
    }
    
    @media (max-width: 768px) {
        .image-gallery {
            grid-template-columns: 1fr;
        }
        .guide-items {
            grid-template-columns: 1fr;
        }
    }
    
    @media (max-width: 1024px) and (min-width: 769px) {
        .image-gallery {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    /* Stats Cards */
    .stats-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        flex: 1;
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #4299e1;
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        color: #718096;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Content Text */
    .content-text {
        line-height: 1.6;
        color: #4a5568;
        margin-bottom: 1rem;
    }
    
    /* Progress Indicator */
    .progress-bar {
        height: 4px;
        background: #e2e8f0;
        border-radius: 2px;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4299e1, #38b2ac);
        border-radius: 2px;
        transition: width 0.3s ease;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Page Configuration
st.set_page_config(
    page_title="Modern Learning Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()



# Content Structure Guide - Always show this
st.markdown("""
<div class="content-guide">
    <div class="guide-title">
        🗺️ Content Structure Guide
    </div>
    <div class="guide-items">
        <div class="guide-item guide-module">
            <div class="guide-icon">M1</div>
            <div class="guide-text">
                <div class="guide-label">Modules</div>
                <div class="guide-description"></div>
            </div>
        </div>
        <div class="guide-item guide-topic">
            <div class="guide-icon">1</div>
            <div class="guide-text">
                <div class="guide-label">Topics</div>
                <div class="guide-description"></div>
            </div>
        </div>
        <div class="guide-item guide-subtopic">
            <div class="guide-icon">1</div>
            <div class="guide-text">
                <div class="guide-label">Subtopics</div>
                <div class="guide-description"></div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar with modern styling
with st.sidebar:
    st.markdown("### 📋 Course Selection")
    
    department = st.selectbox(
        "🏫 Department",
        get_departments(),
        help="Select your department"
    )
    
    semester = st.selectbox(
        "📅 Semester", 
        get_semesters(department),
        help="Choose your semester"
    )
    
    subject = st.selectbox(
        "📚 Subject",
        get_subjects(department, semester),
        help="Pick your subject"
    )
    
    # Selection Summary
    st.markdown("---")
    st.markdown("### 📍 Current Selection")
    st.info(f"**{department}** → **{semester}** → **{subject}**")

# Main Content Area
if subject:
    # Load subject data
    with st.spinner("Loading content..."):
        subject_data = load_subject_data(department, semester, subject)
    
    # Subject Info Card
    st.markdown(f"""
    <div class="subject-info-card">
        <h2>📖 {subject}</h2>
        <div class="subject-path">{department} • {semester}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get modules data
    modules = subject_data.get("content", {}).get("modules", [])
    
    # Stats Cards
    total_topics = sum(len(module.get("topics", [])) for module in modules)
    total_subtopics = sum(
        sum(len(topic.get("subtopics", [])) for topic in module.get("topics", []))
        for module in modules
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(modules)}</div>
            <div class="stat-label">Modules</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_topics}</div>
            <div class="stat-label">Topics</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_subtopics}</div>
            <div class="stat-label">Subtopics</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Initialize session state for module collapse
    if 'collapsed_modules' not in st.session_state:
        st.session_state.collapsed_modules = set()
    
    # Display Content in Simple Sequential Structure
    for module in modules:
        module_id = f"module_{module['module_number']}"
        is_collapsed = module_id in st.session_state.collapsed_modules
        
        # Count topics and subtopics for summary
        topic_count = len(module.get("topics", []))
        subtopic_count = sum(len(topic.get("subtopics", [])) for topic in module.get("topics", []))
        
        # MODULE HEADER
        col1, col2 = st.columns([1, 0.1])
        with col1:
            st.markdown(f"""
            <div class="content-card module-card">
                <div class="module-header">
                    <div class="module-title">
                        <div class="module-number">M{module['module_number']}</div>
                        {module['module_title']}
                    </div>
                </div>
                <div class="module-summary">
                    📚 {topic_count} topic{'s' if topic_count != 1 else ''} • 
                    📋 {subtopic_count} subtopic{'s' if subtopic_count != 1 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Toggle button
            if st.button(
                "🔽" if not is_collapsed else "🔼",
                key=f"toggle_{module_id}",
                help="Click to expand/collapse module",
                use_container_width=True
            ):
                if is_collapsed:
                    st.session_state.collapsed_modules.discard(module_id)
                else:
                    st.session_state.collapsed_modules.add(module_id)
                st.rerun()
        
        # MODULE CONTENT - Only show if not collapsed
        if not is_collapsed:
            # TOPICS in this module
            topics = module.get("topics", [])
            for topic_idx, topic in enumerate(topics, 1):
                # TOPIC
                st.markdown(f"""
                <div class="content-card topic-card">
                    <div class="topic-title">
                        <div class="topic-number">{topic_idx}</div>
                        {topic['topic_title']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Topic content
                topic_content = topic["content"].get("text", "")
                if topic_content:
                    st.markdown(f'<div class="content-text" style="margin-left: 1rem; margin-bottom: 1rem;">{topic_content}</div>', unsafe_allow_html=True)
                
                # Topic diagrams - 3 per row
                diagrams = topic["content"].get("diagrams", [])
                if diagrams:
                    # Group diagrams in sets of 3
                    for i in range(0, len(diagrams), 3):
                        diagram_batch = diagrams[i:i+3]
                        cols = st.columns(len(diagram_batch))
                        
                        for col, (idx, url) in zip(cols, enumerate(diagram_batch, i+1)):
                            with col:
                                st.markdown(f"""
                                <div class="image-item">
                                    <div class="image-title">📊 Topic Diagram {idx}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.image(url, use_container_width=True)
                
                # SUBTOPICS for this topic
                subtopics = topic.get("subtopics", [])
                for subtopic_idx, subtopic in enumerate(subtopics, 1):
                    # SUBTOPIC
                    st.markdown(f"""
                    <div class="content-card subtopic-card">
                        <div class="subtopic-title">
                            <div class="subtopic-number">{subtopic_idx}</div>
                            {subtopic['subtopic_title']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Subtopic content
                    subtopic_content = subtopic["content"].get("text", "")
                    if subtopic_content:
                        st.markdown(f'<div class="content-text" style="margin-left: 2rem; margin-bottom: 1rem;">{subtopic_content}</div>', unsafe_allow_html=True)
                    
                    # Subtopic diagrams - 3 per row
                    sub_diagrams = subtopic["content"].get("diagrams", [])
                    if sub_diagrams:
                        # Group diagrams in sets of 3
                        for i in range(0, len(sub_diagrams), 3):
                            diagram_batch = sub_diagrams[i:i+3]
                            cols = st.columns(len(diagram_batch))
                            
                            for col, (idx, url) in zip(cols, enumerate(diagram_batch, i+1)):
                                with col:
                                    st.markdown(f"""
                                    <div class="image-item">
                                        <div class="image-title">📈 Subtopic Diagram {idx}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.image(url, use_container_width=True)

