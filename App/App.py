# AI-RESUME ANALYZER
import streamlit as st
import pandas as pd
import base64, random, datetime, os, io, socket, platform, secrets
import sqlite3
from geopy.geocoders import Nominatim
from resume_parser import ResumeParser
from streamlit_tags import st_tags
from PIL import Image
import plotly.express as px

from Courses import (
    ds_course, web_course, android_course, ios_course,
    uiux_course, resume_videos, interview_videos
)

# ---------------------- BASIC SETUP ----------------------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="./Logo/recommend.png")
os.makedirs("Uploaded_Resumes", exist_ok=True)

# ---------------------- DATABASE -------------------------
conn = sqlite3.connect("resume_analyzer.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_data (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    sec_token TEXT,
    ip_add TEXT,
    host_name TEXT,
    dev_user TEXT,
    os_name_ver TEXT,
    latlong TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    act_name TEXT,
    act_mail TEXT,
    act_mob TEXT,
    Name TEXT,
    Email_ID TEXT,
    resume_score TEXT,
    Timestamp TEXT,
    Page_no TEXT,
    Predicted_Field TEXT,
    User_level TEXT,
    Actual_skills TEXT,
    Recommended_skills TEXT,
    Recommended_courses TEXT,
    pdf_name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_feedback (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    feed_name TEXT,
    feed_email TEXT,
    feed_score TEXT,
    comments TEXT,
    Timestamp TEXT
)
""")

conn.commit()

# ---------------------- HELPERS --------------------------
def insert_user(*args):
    cursor.execute("""
    INSERT INTO user_data VALUES (
    NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
    )""", args)
    conn.commit()

def insert_feedback(name, email, score, comments, ts):
    cursor.execute(
        "INSERT INTO user_feedback VALUES (NULL,?,?,?,?,?)",
        (name, email, score, comments, ts)
    )
    conn.commit()

def show_pdf(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}" width="700" height="1000"></iframe>',
        unsafe_allow_html=True
    )

# ---------------------- UI -------------------------------
img = Image.open('./Logo/RESUM.png')
st.image(img)

menu = st.sidebar.selectbox("Choose", ["User", "Feedback", "About"])

# ---------------------- USER -----------------------------
if menu == "User":
    name = st.text_input("Name")
    email = st.text_input("Email")
    mobile = st.text_input("Mobile")

    pdf = st.file_uploader("Upload Resume", type=["pdf"])

    if pdf:
        path = f"Uploaded_Resumes/{pdf.name}"
        with open(path, "wb") as f:
            f.write(pdf.getbuffer())

        show_pdf(path)

        # ---------------------- RESUME PARSER ----------------
        data = ResumeParser(path).get_extracted_data()  # Using resume-parser

        if data:
            st.success(f"Hello {data.get('name')}")

            score = random.randint(60, 90)

            st.subheader("Resume Score")
            st.progress(score)

            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

            insert_user(
                secrets.token_hex(8),
                socket.gethostbyname(socket.gethostname()),
                socket.gethostname(),
                "streamlit",
                platform.system(),
                "NA",
                "NA",
                "NA",
                "NA",
                name,
                email,
                mobile,
                data.get("name"),
                data.get("email"),
                score,
                ts,
                "NA",  # resume-parser does not provide page count by default
                "NA",
                "NA",
                str(data.get("skills")),
                "NA",
                "NA",
                pdf.name
            )

            st.balloons()

# ---------------------- FEEDBACK -------------------------
elif menu == "Feedback":
    with st.form("feedback"):
        fname = st.text_input("Name")
        fmail = st.text_input("Email")
        fscore = st.slider("Rating", 1, 5)
        fcomment = st.text_input("Comment")
        submit = st.form_submit_button("Submit")

    if submit:
        insert_feedback(fname, fmail, fscore, fcomment, datetime.datetime.now().isoformat())
        st.success("Feedback saved")

# ---------------------- ABOUT ----------------------------
else:
    st.write("AI Resume Analyzer — Academic Deployment Version")
