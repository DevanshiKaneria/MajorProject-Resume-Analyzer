import streamlit as st
import pandas as pd
import base64, random, datetime, os, io
import sqlite3
from PIL import Image
import plotly.express as px
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
import re

# --- COURSES DATA ---
ds_course = [['Machine Learning Crash Course by Google [Free]', 'https://developers.google.com/machine-learning/crash-course'], ['Machine Learning A-Z by Udemy','https://www.udemy.com/course/machinelearning/']]
web_course = [['Django Crash course [Free]','https://youtu.be/e1IyzVyrLSU'], ['React Crash Course [Free]','https://youtu.be/Dorf8i6lCuk']]
android_course = [['Android Development for Beginners [Free]','https://youtu.be/fis26HvvDII']]
ios_course = [['Become an iOS Developer','https://www.udacity.com/course/ios-developer-nanodegree--nd003']]
uiux_course = [['Google UX Design Professional Certificate','https://www.coursera.org/professional-certificates/google-ux-design']]
resume_videos = ['https://youtu.be/Tt08KmFfIYQ','https://youtu.be/y8YH0Qbu5h4']
interview_videos = ['https://youtu.be/HG68Ymazo18','https://youtu.be/BOvAAoxM4vg']

# --- DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect("resume_analyzer.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_data (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT, Email_ID TEXT, Mobile TEXT,
        Score INTEGER, Timestamp TEXT, Predicted_Field TEXT, Skills TEXT
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_feedback (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        feed_name TEXT, feed_email TEXT, feed_score TEXT, comments TEXT, Timestamp TEXT
    )""")
    conn.commit()

# --- HELPER FUNCTIONS ---
def extract_skills(text):
    skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Deep Learning', 'SQL', 'Tableau', 'React', 'Django', 'JavaScript', 'HTML', 'CSS', 'Java', 'C++', 'AWS', 'Docker']
    found_skills = [skill for skill in skills_list if skill.lower() in text.lower()]
    return found_skills

def predict_field(skills):
    if any(s in ['Python', 'Machine Learning', 'SQL', 'Data Analysis'] for s in skills):
        return "Data Science", ds_course
    elif any(s in ['React', 'Django', 'HTML', 'CSS', 'JavaScript'] for s in skills):
        return "Web Development", web_course
    return "Software Engineering", []

def extract_education(text):
    # Simple regex to find mentions of common degrees
    education_keywords = ['B.Tech', 'B.E', 'M.Tech', 'MBA', 'BSc', 'MSc', 'Bachelor', 'Master']
    found_edu = [edu for edu in education_keywords if edu.lower() in text.lower()]
    return found_edu

# --- MAIN APP ---
def main():
    st.set_page_config(page_title="AI Resume Analyzer", page_icon="📝")
    init_db()
    
    st.title("AI Resume Analyzer")
    
    menu = st.sidebar.selectbox("Choose", ["User", "Feedback", "About"])

    if menu == "User":
        st.info("Upload your resume and get an AI-driven analysis of your profile.")
        name = st.text_input("Full Name")
        email = st.text_input("Email ID")
        mobile = st.text_input("Mobile Number")
        pdf_file = st.file_uploader("Upload Resume", type=["pdf"])

        if pdf_file is not None:
            # Extract text
            with st.spinner('Analyzing Resume...'):
                text = extract_text(pdf_file)
                reader = PdfReader(pdf_file)
                pages = len(reader.pages)
                
                # Logic for Skills & Field
                skills = extract_skills(text)
                field, recommended_courses = predict_field(skills)
                education = extract_education(text)
                
                # Scoring Logic
                score = 20 # Base score for uploading
                if len(skills) > 5: score += 30
                if len(education) > 0: score += 20
                if pages >= 1: score += 10
                score += random.randint(5, 15) # Random variability
                score = min(score, 100)

                st.success(f"Analysis Complete for {name if name else 'User'}!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Profile Insights")
                    st.write(f"**Predicted Field:** {field}")
                    st.write(f"**Education Detected:** {', '.join(education) if education else 'Not specified'}")
                    st.write(f"**Resume Pages:** {pages}")
                
                with col2:
                    st.subheader("Resume Score")
                    st.metric(label="Overall Match", value=f"{score}%")
                    st.progress(score / 100)

                st.subheader("Extracted Skills")
                st.write(f"{', '.join(skills) if skills else 'No matching technical skills detected.'}")
                
                # Recommendations
                if recommended_courses:
                    st.subheader("Recommended Courses to Improve Your Score")
                    for c_name, c_link in recommended_courses:
                        st.markdown(f"✅ [{c_name}]({c_link})")

                # Save to DB
                conn = get_db_connection()
                cursor = conn.cursor()
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO user_data (Name, Email_ID, Mobile, Score, Timestamp, Predicted_Field, Skills) VALUES (?,?,?,?,?,?,?)",
                               (name, email, mobile, score, ts, field, str(skills)))
                conn.commit()
                st.balloons()

    elif menu == "Feedback":
        st.subheader("We value your feedback")
        with st.form("feedback_form"):
            f_name = st.text_input("Name")
            f_email = st.text_input("Email")
            f_score = st.slider("How satisfied are you with the analysis?", 1, 5)
            f_comment = st.text_area("What can we improve?")
            if st.form_submit_button("Submit Feedback"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user_feedback (feed_name, feed_email, feed_score, comments, Timestamp) VALUES (?,?,?,?,?)",
                               (f_name, f_email, f_score, f_comment, datetime.datetime.now().isoformat()))
                conn.commit()
                st.success("Thank you for your feedback!")

    else:
        st.subheader("About AI Resume Analyzer")
        st.write("This tool uses Natural Language Processing (NLP) and PDF parsing to analyze professional resumes.")
        st.write("- **Skills Extraction:** Detects core technical competencies.")
        st.write("- **Field Prediction:** Categorizes your profile into Data Science, Web Dev, etc.")
        st.write("- **Score:** Evaluates the completeness of your resume.")

if __name__ == "__main__":
    main()
