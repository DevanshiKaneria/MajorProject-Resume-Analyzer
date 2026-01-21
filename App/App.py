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
