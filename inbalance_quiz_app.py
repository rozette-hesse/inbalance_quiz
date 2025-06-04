from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from PIL import Image
import re
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ----------------- CONFIG -----------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")
logo = Image.open("logo.png")
st.image(logo, width=120)

# ----------------- SESSION STATE INIT -----------------
defaults = {
    "q_index": 0,
    "answers": [],
    "completed": False,
    "first_name": "",
    "last_name": "",
    "email": "",
    "phone": "",
    "waitlist_opt_in": None,
    "extra_questions_done": False
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ----------------- GOOGLE SHEETS -----------------
try:
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    credentials_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
    client = gspread.authorize(credentials)
    sheet = client.open("InBalance_Quiz_Responses").sheet1
except Exception:
    sheet = None

# ----------------- QUESTIONS -----------------
questions = [
    {
        "q": "How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (e.g., hormonal treatment or pregnancy)",
            "Regular (25–35 days)",
            "Often irregular (< 25 or > 35 days)",
            "Rarely got period (< 6 times a year)"
        ]
    },
    {
        "q": "Do you notice excessive thick black hair on your face, chest, or back?",
        "options": [
            "No, not at all",
            "Yes, manageable with hair removal",
            "Yes, resistant to hair removal",
            "Yes + scalp thinning or hair loss"
        ]
    },
    {
        "q": "Have you had acne or oily skin this year?",
        "options": [
            "No",
            "Yes, mild but manageable",
            "Yes, often despite treatment",
            "Yes, severe and persistent"
        ]
    },
    {
        "q": "Have you experienced weight changes?",
        "options": [
            "No, stable weight",
            "Stable only with effort",
            "Struggling to maintain weight",
            "Can't lose weight despite diet/exercise"
        ]
    },
    {
        "q": "Do you feel tired or sleepy after meals?",
        "options": [
            "No, not really",
            "Sometimes after heavy meals",
            "Yes, often regardless of food",
            "Yes, almost daily with alertness issues"
        ]
    },
]

# ----------------- START SCREEN -----------------
if st.session_state.q_index == 0 and not st.session_state.completed:
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to help you understand your hormonal health — and how InBalance can help.")

    st.session_state.first_name = st.text_input("👤 First Name:", st.session_state.first_name)
    st.session_state.last_name = st.text_input("👤 Last Name:", st.session_state.last_name)
    st.session_state.email = st.text_input("📧 Email Address:", st.session_state.email)
    st.session_state.phone = st.text_input("📱 Phone Number (include country code):", st.session_state.phone, placeholder="+961...")

    def is_valid_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    if st.button("Start Quiz"):
        if not st.session_state.first_name.strip() or not st.session_state.last_name.strip():
            st.warning("Please enter both first and last name.")
        elif not is_valid_email(st.session_state.email):
            st.warning("Please enter a valid email address.")
        elif not st.session_state.phone.strip().startswith("+"):
            st.warning("Please enter a valid phone number with country code (e.g. +961...).")
        else:
            st.session_state.q_index = 1
            st.rerun()
    st.stop()

# ----------------- QUIZ FLOW -----------------
index = st.session_state.q_index
if 1 <= index <= len(questions):
    q = questions[index - 1]
    st.markdown(f"### {q['q']}")
    selected_option = st.radio(" ", q["options"], key=f"q{index}", index=None)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            if index > 1:
                st.session_state.q_index -= 1
                if st.session_state.answers:
                    st.session_state.answers.pop()
                st.rerun()

    with col2:
        if st.button("➡️ Next"):
            if selected_option is None:
                st.warning("Please select an option to continue.")
            else:
                st.session_state.answers.append(selected_option)
                st.session_state.q_index += 1
                if st.session_state.q_index > len(questions):
                    st.session_state.completed = True
                st.rerun()

# ----------------- RESULT + WAITLIST -----------------
if st.session_state.completed:
    st.success("✅ Quiz complete!")

    st.markdown("#### 💡 How InBalance Can Help")
    st.info("InBalance helps you track symptoms, cycles, fatigue, skin changes, and more — and our experts use that data to guide your care.")

    st.image("qr_code.png", width=180)
    st.markdown("### 💬 Want to join the InBalance app waitlist?")
    waitlist = st.radio("Would you like to join?", ["Yes", "No"], index=None)

    tracking, symptoms, goal, notes = "", [], "", ""
    if waitlist == "Yes":
        tracking = st.radio("Do you currently track your cycle or symptoms?", ["Yes, with an app", "Yes, manually", "No, but I want to", "No, and I don’t know where to start", "Other"], index=None)
        symptoms = st.multiselect("What symptoms do you deal with most often?", ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"])
        goal = st.radio("What is your main health goal?", ["Understand my cycle", "Reduce symptoms", "Looking for diagnosis", "Personalized lifestyle plan", "Just curious", "Other"], index=None)
        notes = st.text_area("Anything else you'd like us to know?")

    if st.button("📩 Finish & Save"):
        try:
            if sheet:
                sheet.append_row([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    st.session_state.first_name,
                    st.session_state.last_name,
                    st.session_state.email,
                    st.session_state.phone,
                    *st.session_state.answers,
                    waitlist,
                    tracking,
                    ", ".join(symptoms),
                    goal,
                    notes
                ])
                st.success("✅ Your responses were saved successfully!")
                st.session_state.extra_questions_done = True
            else:
                st.error("❌ Google Sheet not connected properly.")
        except Exception as e:
            st.error(f"❌ Could not save to Google Sheets: {e}")

# ----------------- RESTART OPTION -----------------
if st.button("🔄 Restart Quiz"):
    st.session_state.clear()
    st.rerun()
