import streamlit as st
from PIL import Image
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime



# Streamlit page setup
st.set_page_config(page_title="InBalance Hormonal Quiz", layout="centered")


# --------- Initialize session state keys ----------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "completed" not in st.session_state:
    st.session_state.completed = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "email" not in st.session_state:
    st.session_state.email = ""


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



# ---------------------- QUIZ FLOW ----------------------
if st.session_state.q_index < len(questions):
    question = questions[st.session_state.q_index]

    st.markdown(f"<h4 style='font-size: 22px; font-weight: bold;'>{question['q']}</h4>", unsafe_allow_html=True)

    option = st.radio(" ", [opt[0] for opt in question["options"]], key=f"radio_{st.session_state.q_index}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Back", key=f"back_{st.session_state.q_index}"):
            if st.session_state.q_index > 0:
                st.session_state.q_index -= 1
                if st.session_state.answers:
                    st.session_state.answers.pop()
                st.rerun()

    with col2:
        if st.button("➡️ Next", key=f"next_{st.session_state.q_index}"):
            if option:  # make sure something is selected
                selected_score = [opt[1] for opt in question["options"] if opt[0] == option][0]
                if len(st.session_state.answers) <= st.session_state.q_index:
                    st.session_state.answers.append(selected_score)
                else:
                    st.session_state.answers[st.session_state.q_index] = selected_score

                st.session_state.q_index += 1
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

# Waitlist CTA
st.markdown("## 💬 Want to join the InBalance app waitlist?")
join = st.radio("Would you like to join?", ["Yes", "No"])

if join == "Yes":
    st.markdown("### 📋 Tell us more")

    track = st.radio("Do you currently track your cycle or symptoms?", [
        "Yes, with an app",
        "Yes, manually",
        "No, but I want to",
        "No, and I don’t know where to start",
        "Other"
    ])

    symptoms = st.multiselect("What symptoms do you deal with most often?", [
        "Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne",
        "Anxiety", "Sleep issues", "Brain fog", "Other"
    ])

    goal = st.radio("What is your main health goal right now?", [
        "I want to understand my cycle better",
        "I want to reduce symptoms like fatigue, acne, or cravings",
        "Looking for diagnosis or answers",
        "I want a personalized lifestyle plan",
        "Just curious",
        "Other"
    ])

    notes = st.text_area("Anything you'd like us to know?")

    # Save these values or append them to the sheet
    st.success("🎉 You're on the waitlist! We'll be in touch.")


    # Save to Google Sheets
    submission = [datetime.now().isoformat(), st.session_state.name, st.session_state.email, diagnosis, *scores]
    sheet.append_row(submission)

    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
