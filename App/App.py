import streamlit as st
import pandas as pd
import base64
import random
import time
import datetime
import sqlite3
import os
import io
import re
import hashlib
import plotly.express as px
import plotly.graph_objects as go
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter

# --- CONFIG & STYLING ---
st.set_page_config(page_title="Aura AI | Next-Gen Recruitment", page_icon='✨', layout="wide")

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Base Theme */
        .main { background: linear-gradient(135deg, #f8f9fc 0%, #e2e8f0 100%); }
        
        /* Glassmorphism Cards */
        .stMarkdown div[data-testid="stVerticalBlock"] > div.creative-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 20px 40px rgba(0,0,0,0.05);
            margin-bottom: 25px;
        }
        /* Step Headers */
        .step-header {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 20px;
            margin-top: 10px;
            padding-left: 10px;
            border-left: 5px solid #6366f1;
        }
        /* Hero Headers */
        .hero-section {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #f8fafc;
            padding: 60px 40px;
            border-radius: 30px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 15px 30px rgba(15, 23, 42, 0.2);
        }
        .hero-section h1 { color: #f1f5f9 !important; font-size: 3.5rem !important; font-weight: 800; letter-spacing: -1px; }
        .hero-section p { font-size: 1.2rem; color: #94a3b8; }
        
        /* Custom Buttons */
        .stButton>button {
            width: 100%;
            border-radius: 14px;
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
            background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
        }
        
        /* Metrics Styling */
        [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 700 !important; color: #1e293b !important; }
        
        /* Tech Badges */
        .tech-badge {
            background: #e2e8f0;
            color: #475569;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-right: 5px;
            display: inline-block;
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('aura_cv.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Name TEXT, Email TEXT, Mobile TEXT, Degree TEXT,
                        Job_Choice TEXT, Score INTEGER, Level TEXT, Timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                        Name TEXT, Email TEXT, Rating INTEGER, Comments TEXT, Date TEXT)''')
    conn.commit()
    conn.close()
# --- HELPER FUNCTIONS ---
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    file.seek(0)
    for page in PDFPage.get_pages(file, caching=True, check_extractable=True):
        page_interpreter.process_page(page)
    text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text

# --- APP LOGIC ---
def run():
    init_db()
    apply_custom_theme()
    
    # --- HARDCODED ADMIN CREDENTIALS ---
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "aura_password_2025" # Change this to your preferred master password
    
    with st.sidebar:
        st.markdown("<h1 style='text-align: center; color: #4f46e5;'>✨ AURA AI</h1>", unsafe_allow_html=True)
        st.divider()
        choice = st.radio("Navigation", ["🌈 User Portal", "💬 Feedback Hub", "📖 About Project", "🔐 Admin Nexus"], label_visibility="collapsed")
        st.divider()
        st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #64748b;'>Empowering Careers with Intelligence<br>© 2025 Aura Intelligence</p>", unsafe_allow_html=True)

    if choice == "🌈 User Portal":
        st.markdown("<div class='hero-section'><h1>Unlock Your Potential 🚀</h1><p>Upload your resume and let our AI curate your professional roadmap</p></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='step-header'>Step 1: Personal Blueprint</div>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='creative-card'>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            u_name = c1.text_input("Full Name", placeholder="John Doe")
            u_mail = c2.text_input("Email Address", placeholder="john@example.com")
            u_mob = c1.text_input("Contact Number", placeholder="+91 0000000000")
            u_deg = c2.text_input("Highest Degree", placeholder="B.Tech Computer Science")
            
            tech_roles = [
                "Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer",
                "Data Scientist", "Data Analyst", "Machine Learning Engineer", "AI Researcher",
                "DevOps Engineer", "Cloud Architect (AWS/Azure)", "Cybersecurity Analyst",
                "UI/UX Designer", "Product Manager", "Mobile App Developer (iOS/Android)",
                "Blockchain Developer", "Embedded Systems Engineer", "Quality Assurance (QA) Engineer",
                "Database Administrator", "Network Engineer", "Game Developer", "Salesforce Developer"
            ]
            u_job = st.selectbox("🎯 Target Technology Role", tech_roles)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='step-header'>Step 2: Experience Validation</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type=["pdf"])

        if uploaded_file and u_name and u_mail:
            with st.spinner("🧬 Processing Neural Patterns..."):
                resume_text = pdf_reader(uploaded_file).lower()
                score = 0
                tips = []
if u_mail.lower() in resume_text: score += 10
                else: tips.append("❌ Your email in the form doesn't match the resume header.")

                sections = {'education': 15, 'experience': 20, 'skills': 15, 'projects': 15, 'certifications': 10}
                for section, points in sections.items():
                    if section in resume_text: score += points
                    else: tips.append(f"🚩 Missing section: {section.capitalize()}. Adding this boosts visibility.")

                role_keywords = {
                    "Data Scientist": ["python", "pandas", "machine learning", "statistics", "sql"],
                    "Web Developer": ["javascript", "react", "html", "css", "node"],
                    "Frontend Developer": ["javascript", "react", "html", "css", "vue", "angular", "tailwind"],
                    "Backend Developer": ["python", "node", "express", "sql", "nosql", "api", "django"],
                    "DevOps Engineer": ["docker", "kubernetes", "aws", "jenkins", "terraform"]
                }
                
                match_count = 0
                current_keywords = role_keywords.get(u_job, ["api", "git", "database", "problem solving", "optimization"]) 
                detected_skills = []
                for k in current_keywords:
                    if k in resume_text: 
                        match_count += 1
                        detected_skills.append(k)
                
                score += (match_count * 3) 
                if match_count < 3:
                    tips.append(f"💡 Technical Gap: Add more keywords like {', '.join(current_keywords[:3])}.")

                role_questions = {
                    "Software Engineer": [
                        "Explain the difference between Stack and Queue data structures.",
                        "How do you handle error management in your typical coding workflow?",
                        "What is your approach to optimizing code for better performance?"
                    ],
                    "Data Scientist": [
                        "What is the difference between Overfitting and Underfitting?",
                        "How do you handle missing values in a large dataset?",
                        "Explain the concept of P-value in statistical hypothesis testing."
                    ],
                    "Web Developer": [
                        "What are the benefits of using React Hooks over Class Components?",
                        "Explain the Box Model in CSS and how it impacts layout design.",
                        "How does asynchronous programming work in JavaScript?"
                    ]
                }
                interview_q = role_questions.get(u_job, [
                    "What is your greatest technical accomplishment to date?",
                    "How do you stay updated with the latest trends in your industry?",
                    "Describe a time you had to troubleshoot a complex problem."
                ])

                role_video_map = {
                    "Software Engineer": "https://www.youtube.com/watch?v=avdDEZCcluo",
                    "Frontend Developer": "https://www.youtube.com/watch?v=DbRXv5TXMEE",
                    "Backend Developer": "https://www.youtube.com/watch?v=OeEHJgzqS1k",
                    "Full Stack Developer": "https://www.youtube.com/watch?v=GxmfcnU3feo",
                    "Data Scientist": "https://www.youtube.com/watch?v=9R3X0JoCLyU",
                    "Data Analyst": "https://www.youtube.com/watch?v=8411fEhNKNc",
                    "Machine Learning Engineer": "https://www.youtube.com/watch?v=quTX3fevt3s",
                    "AI Researcher": "https://www.youtube.com/watch?v=LVrQcTfm4pc",
                    "DevOps Engineer": "https://www.youtube.com/watch?v=RRBF2YWXFtY",
                    "UI/UX Designer": "https://www.youtube.com/watch?v=Q324oRLYhlM",
                    "Product Manager": "https://www.youtube.com/watch?v=Jk2g9Drr1rI",
                    "Cybersecurity Analyst": "https://www.youtube.com/watch?v=20W7BML1JRI",
                    "Cloud Architect (AWS/Azure)": "https://www.youtube.com/watch?v=N4sJj-SxX00",
                    "Mobile App Developer (iOS/Android)": "https://www.youtube.com/watch?v=s4rdFWNoL40",
                    "Blockchain Developer": "https://www.youtube.com/watch?v=uULy2rc6YDc",
                    "Quality Assurance (QA) Engineer": "https://www.youtube.com/watch?v=Hjt0SCeGrBY",
                    "Game Developer": "https://www.youtube.com/watch?v=MjHalxr_tDw"
                }
                yt_link = role_video_map.get(u_job, "https://www.youtube.com/watch?v=YS4e4q9oBaU")

                experience_keywords = ['years', 'senior', 'manager', 'lead', 'specialist']
                if 'intern' in resume_text or 'student' in resume_text:
                    level = "Internship / Entry Level"
                    course_rec = "Foundational Certification in " + u_job
                elif any(x in resume_text for x in experience_keywords) and score > 70:
                    level = "Advanced / Professional"
                    course_rec = "Advanced System Architecture & Leadership"
                else:
                    level = "Fresher / Junior Associate"
                    course_rec = "Intermediate Specialization in " + u_job

                st.balloons()
                st.markdown("<div class='creative-card'>", unsafe_allow_html=True)
                st.header(f"📊 Assessment for {u_name}")
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Resume Score", f"{min(score, 100)}%")
                    st.subheader(f"Level: {level}")
                    st.write(f"**Target Role:** {u_job}")
                
                with col2:
                    st.markdown("### 🛠️ 10 Professional Improvement Tips")
                    base_tips =[
                        "Use action verbs like 'Developed', 'Managed', 'Optimized'.",
                        "Quantify achievements (e.g., 'Reduced latency by 20%').",
                        "Ensure consistent font sizing for headers.",
                        "Save resume as 'Firstname_Lastname_Role.pdf'.",
                        "Limit resume to 1-2 pages maximum.",
                        "Include your GitHub or Portfolio link.",
                        "Check for any spelling or grammatical errors.",
                        "Use a clean, ATS-friendly single-column layout.",
                        "Tailor your summary to mention the target role directly.",
                        "Avoid using progress bars for skill levels; use text."
                    ]
                    final_tips = (tips + base_tips)[:10]
                    for t in final_tips:
                        st.write(t)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='creative-card'>", unsafe_allow_html=True)
                st.subheader("🕸️ Skill Gap Visualization")
                categories = ['Core Skills', 'Education', 'Projects', 'Experience', 'Keywords']
                core_val = (match_count / len(current_keywords)) * 100 if current_keywords else 0
                edu_val = 100 if 'education' in resume_text else 0
                proj_val = 100 if 'projects' in resume_text else 0
                exp_val = 100 if 'experience' in resume_text else 0
                key_val = 80 if score > 50 else 40
                
