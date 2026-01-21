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
