import streamlit as st
from PIL import Image
import re
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# ----------------- CONFIG -----------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")
st.image(Image.open("logo.png"), width=140)

# ----------------- SESSION STATE INIT -----------------
defaults = {
    "step": "start",
    "first_name": "",
    "last_name": "",
    "email": "",
    "country_code": "+961",
    "phone_number": "",
    "q_index": 0,
    "answers": [],
    "completed": False,
    "waitlist_opt_in": None,
    "extra_questions_done": False
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
    }
]

# ----------------- GOOGLE SHEETS SETUP -----------------
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# ----------------- STEP: START -----------------
if st.session_state.step == "start":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to help you understand your hormonal health — and how InBalance can help.")

    st.session_state.first_name = st.text_input("👩 First Name", st.session_state.first_name)
    st.session_state.last_name = st.text_input("👩 Last Name", st.session_state.last_name)
    st.session_state.email = st.text_input("📧 Email Address", st.session_state.email)
    country_options = ["🇱🇧 +961", "🇺🇸 +1", "🇬🇧 +44", "🇩🇪 +49", "🇫🇷 +33", "🇸🇦 +966", "🇦🇪 +971", "🇪🇬 +20", "🇮🇳 +91"]
    selection = st.selectbox("🌍 Country Code", country_options, index=0)
    st.session_state.country_code = selection.split(" ")[-1]
    st.session_state.phone_number = st.text_input("📱 Phone Number (no spaces)", st.session_state.phone_number)

    def is_valid_email(email):
        return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email)

    if st.button("Start Quiz"):
        if not st.session_state.first_name.strip() or not st.session_state.last_name.strip():
            st.warning("Please enter your full name.")
        elif not is_valid_email(st.session_state.email):
            st.warning("Enter a valid email address.")
        elif not st.session_state.phone_number.strip().isdigit():
            st.warning("Phone number must be digits only.")
        elif len(st.session_state.phone_number) < 6:
            st.warning("Phone number looks too short.")
        else:
            st.session_state.step = "quiz"
            st.rerun()

# ----------------- STEP: QUIZ -----------------
elif st.session_state.step == "quiz":
    index = st.session_state.q_index
    if index < len(questions):
        q = questions[index]
        st.markdown(f"### {q['q']}")
        selected = st.radio(" ", q["options"], index=None, key=f"q{index}")
        if st.button("Next"):
            if selected is None:
                st.warning("Please select an option.")
            else:
                st.session_state.answers.append(selected)
                st.session_state.q_index += 1
                st.rerun()
    else:
        st.session_state.completed = True
        st.session_state.step = "results"
        st.rerun()

# ----------------- STEP: RESULTS -----------------
elif st.session_state.step == "results":
    st.success("✅ Quiz complete!")

    # Simple scoring logic
    scores = {
        "No, not at all": 1, "No": 1,
        "Yes, manageable with hair removal": 5,
        "Yes, mild but manageable": 4,
        "Stable only with effort": 2,
        "Sometimes after heavy meals": 2,
        "Often irregular (< 25 or > 35 days)": 6,
        "Yes, often despite treatment": 6,
        "Struggling to maintain weight": 5,
        "Yes, often regardless of food": 4,
        "Rarely got period (< 6 times a year)": 8,
        "Yes + scalp thinning or hair loss": 8,
        "Yes, severe and persistent": 8,
        "Can't lose weight despite diet/exercise": 7,
        "Yes, almost daily with alertness issues": 6
    }
    total_score = sum([scores.get(a, 0) for a in st.session_state.answers])

    if total_score < 8:
        diagnosis = "No strong hormonal patterns detected"
        rec = "Your cycle and symptoms seem generally balanced. Keep observing changes month-to-month."
    elif total_score < 16:
        diagnosis = "Ovulatory Imbalance"
        rec = "You may have subtle hormonal fluctuations. These may cause fatigue, breakouts, or missed ovulation."
    elif total_score < 24:
        diagnosis = "HCA-PCO (Possible PCOS)"
        rec = "Several symptoms point to a mild PCOS pattern. Consider confirming this with a clinician."
    else:
        diagnosis = "H-PCO (Androgenic + Metabolic Signs)"
        rec = "You show signs of both hormone and metabolic imbalance. A tailored approach is recommended."

    st.markdown(f"### 🧬 Result: {diagnosis}")
    st.info(rec)

    # Personalized messages
    st.markdown("### 🧬 Personalized Results & Guidance")
    if "Rarely got period" in st.session_state.answers or "Often irregular" in st.session_state.answers:
        st.markdown("🔹 Your cycle seems irregular or infrequent — possibly hormonal imbalance or missed ovulation.")
    if "Yes, severe and persistent" in st.session_state.answers or "Yes, often despite treatment" in st.session_state.answers:
        st.markdown("🔹 Persistent acne or oily skin may reflect hormonal imbalance or inflammation.")
    if "Can't lose weight" in st.session_state.answers or "Yes, almost daily with alertness issues" in st.session_state.answers:
        st.markdown("🔹 Signs of metabolic imbalance (insulin/cortisol resistance) may be present.")

    st.image("qr_code.png", width=160)

    st.session_state.step = "waitlist"

# ----------------- STEP: WAITLIST -----------------
elif st.session_state.step == "waitlist":
    st.markdown("### 💬 Want to join the InBalance app waitlist?")
    waitlist = st.radio("Would you like to join?", ["Yes", "No"], index=None)

    tracking = ""
    symptoms = []
    goal = ""
    notes = ""

    if waitlist == "Yes":
        tracking = st.radio("Do you currently track your cycle or symptoms?", ["Yes, with an app", "Yes, manually", "No, but I want to", "No, and I don’t know where to start", "Other"], index=None)
        symptoms = st.multiselect("What symptoms do you deal with most often?", ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"])
        goal = st.radio("What is your main health goal?", ["Understand my cycle", "Reduce symptoms", "Looking for diagnosis", "Personalized lifestyle plan", "Just curious", "Other"], index=None)
        notes = st.text_area("Anything else you'd like us to know?")

    if st.button("📩 Finish & Save"):
        try:
            if sheet:
                full_phone = st.session_state.country_code + st.session_state.phone_number
                sheet.append_row([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    st.session_state.first_name,
                    st.session_state.last_name,
                    st.session_state.email,
                    full_phone,
                    *st.session_state.answers,
                    diagnosis,
                    rec,
                    waitlist,
                    tracking,
                    ", ".join(symptoms),
                    goal,
                    notes
                ])
                st.success("✅ Your responses were saved successfully!")
            else:
                st.error("❌ Google Sheet not connected.")
        except Exception as e:
            st.error(f"❌ Failed to save: {e}")

# ----------------- RESET -----------------
if st.button("🔄 Restart Quiz"):
    st.session_state.clear()
    st.rerun()
