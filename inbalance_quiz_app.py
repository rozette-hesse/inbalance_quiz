import streamlit as st
from PIL import Image
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Streamlit page setup
st.set_page_config(page_title="InBalance Hormonal Quiz", layout="centered")

# Load logo and QR code
logo = Image.open("logo.png")
qr_code = Image.open("qr_code.png")

# Display logo
st.image(logo, width=180)

st.markdown("<h1 style='text-align: center; color: teal;'>How Balanced Are Your Hormones?</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>A 1-minute quiz to help you understand your hormonal health — and how InBalance can help.</p>", unsafe_allow_html=True)


# Google Sheets connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import json
from google.oauth2.service_account import Credentials

credentials_dict = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)

client = gspread.authorize(credentials)
sheet = client.open("InBalance_Quiz_Responses").sheet1



if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

if st.session_state.step == 0:
    name = st.text_input("👤 First Name:")
    email = st.text_input("📧 Email Address:")
    def is_valid_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)
    if st.button("Start Quiz"):
        if not name or not is_valid_email(email):
            st.warning("Please enter a valid name and email to continue.")
        else:
            st.session_state.name = name
            st.session_state.email = email
            st.session_state.step = 1
            st.rerun()




questions = [
    {
        "q": "How regular was your menstrual cycle in the past year?",
        "options": [
            ("Does not apply (e.g., hormonal treatment or pregnancy)", 0),
            ("Regular (25–35 days)", 1),
            ("Often irregular (< 25 or > 35 days)", 6),
            ("Rarely got period (< 6 times a year)", 8),
        ]
    },
    {
        "q": "Do you notice excessive thick black hair on your face, chest, or back?",
        "options": [
            ("No, not at all", 1),
            ("Yes, manageable with hair removal", 5),
            ("Yes, resistant to hair removal", 7),
            ("Yes + scalp thinning or hair loss", 8),
        ]
    },
    {
        "q": "Have you had acne or oily skin this year?",
        "options": [
            ("No", 1),
            ("Yes, but controlled", 4),
            ("Yes, often despite treatment", 6),
            ("Yes, severe and persistent", 8),
        ]
    },
    {
        "q": "Have you experienced weight changes this year?",
        "options": [
            ("No, stable", 1),
            ("Stable with effort", 2),
            ("Struggling without lifestyle change", 5),
            ("Struggling despite healthy lifestyle", 7),
        ]
    },
    {
        "q": "Do you feel very tired or sleepy after meals?",
        "options": [
            ("No", 1),
            ("Sometimes after heavy/sugary meals", 2),
            ("Often, regardless of meal type", 4),
            ("Almost daily — hard to stay alert", 6),
        ]
    }
]

if 1 <= st.session_state.step <= len(questions):
    idx = st.session_state.step - 1
    st.markdown(f"### {questions[idx]['q']}")
    choice = st.radio("", [opt[0] for opt in questions[idx]["options"]])
    if st.button("Next"):
        value = next(score for text, score in questions[idx]["options"] if text == choice)
        st.session_state.answers.append(value)
        st.session_state.step += 1
        st.rerun()


if st.session_state.step > len(questions):
    scores = st.session_state.answers
    total = sum(scores)

    # Clustering
    CA = scores[0] * 4
    HYPRA = scores[1] * 4 + scores[2] * 3
    PCOMIR = scores[3] * 2 + scores[4] * 1

    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        diagnosis = "Phenotype A – Full PCOS Pattern"
        message = "Your symptoms suggest significant cycle irregularity, androgen-related signs like hair or skin changes, and possible insulin resistance."
    elif CA >= 20 and HYPRA >= 20:
        diagnosis = "Phenotype B – Androgenic + Irregular Cycles"
        message = "You may have hormonal imbalances affecting ovulation and male hormone levels. Worth investigating further."
    elif HYPRA >= 20 and PCOMIR >= 10:
        diagnosis = "Phenotype C – Metabolic & Androgenic Signs"
        message = "This pattern may indicate hormonal excess + signs of insulin resistance (acne, fatigue, weight gain)."
    elif CA >= 20 and PCOMIR >= 10:
        diagnosis = "Phenotype D – Ovulatory + Metabolic Issues"
        message = "You may have cycle disruption alongside symptoms of insulin resistance like fatigue or cravings."
    else:
        diagnosis = "Balanced Hormonal Profile"
        message = "No strong hormonal imbalance is showing — but tracking your health is still essential."

    st.success("✅ Quiz Complete!")
    st.markdown(f"<h3 style='color: teal;'>🧬 Result: {diagnosis}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p>{message}</p>", unsafe_allow_html=True)

    st.markdown("### 💡 How InBalance Can Help")
    st.markdown(f"""
    InBalance helps you track symptoms, cycles, cravings, fatigue, and skin/hair changes — and our team of doctors uses that data to guide your care.

    Whether you want a diagnosis, treatment, or a better understanding of your body, we’re here for you. Join our waitlist and be the first to try it.
    """)

    st.image(qr_code, width=180)

    # Save to Google Sheets
    submission = [datetime.now().isoformat(), st.session_state.name, st.session_state.email, diagnosis, *scores]
    sheet.append_row(submission)

    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
