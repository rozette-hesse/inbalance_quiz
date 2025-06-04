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
    "first_name": "", "last_name": "", "email": "",
    "country_code": "+961", "phone_number": "",
    "answers": [], "completed": False, "diagnosis": "",
    "waitlist_opt_in": None, "extra_questions_done": False
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

# ----------------- GOOGLE SHEETS -----------------
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# ----------------- STEP: START -----------------
if st.session_state.step == "start":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to understand your hormonal health — and how InBalance can help.")

    st.session_state.first_name = st.text_input("👩 First Name", st.session_state.first_name)
    st.session_state.last_name = st.text_input("👩 Last Name", st.session_state.last_name)
    st.session_state.email = st.text_input("📧 Email Address", st.session_state.email)

    countries = {
        "🇱🇧 Lebanon": "+961", "🇺🇸 USA": "+1", "🇬🇧 UK": "+44", "🇩🇪 Germany": "+49",
        "🇫🇷 France": "+33", "🇦🇪 UAE": "+971", "🇸🇦 Saudi": "+966", "🇪🇬 Egypt": "+20", "🇮🇳 India": "+91"
    }
    selected = st.selectbox("🌍 Country", list(countries.keys()))
    st.session_state.country_code = countries[selected]
    st.session_state.phone_number = st.text_input("📱 Phone Number (without spaces)", st.session_state.phone_number)

    def is_valid_email(email): return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email)

    if st.button("Start Quiz"):
        if not st.session_state.first_name or not st.session_state.last_name:
            st.warning("Please enter your full name.")
        elif not is_valid_email(st.session_state.email):
            st.warning("Enter a valid email address.")
        elif not st.session_state.phone_number.isdigit() or len(st.session_state.phone_number) < 6:
            st.warning("Enter a valid phone number.")
        else:
            st.session_state.step = "quiz"
            st.rerun()

# ----------------- STEP: QUIZ -----------------
elif st.session_state.step == "quiz":
    st.header("📝 Answer All Questions")

    answers = []
    for i, q in enumerate(questions):
        response = st.radio(f"{i+1}. {q['q']}", q["options"], index=None, key=f"q{i}")
        answers.append(response)

    if st.button("Submit Answers"):
        if None in answers:
            st.warning("Please answer all questions before continuing.")
        else:
            st.session_state.answers = answers
            st.session_state.step = "results"
            st.rerun()

# ----------------- STEP: RESULTS -----------------
elif st.session_state.step == "results":
    st.success("✅ Quiz complete!")

    q1, q2, q3, q4, q5 = st.session_state.answers

    # ----------------- DIAGNOSIS -----------------
    score_map = {
        0: {"Regular": 1, "No": 1},
        1: 2, 2: 4, 3: 6, 4: 8
    }
    score = sum([i for i in range(1, 6) if st.session_state.answers[i-1]])
    if "Rarely" in q1 or "Often irregular" in q1:
        diagnosis = "H-PCO (Hormonal and Metabolic)"
        rec = "- Your cycle seems irregular or infrequent — could indicate hormonal imbalance or missed ovulation.\n- You may also be experiencing insulin resistance or inflammation, especially if weight and fatigue are issues."
    elif "Yes + scalp thinning" in q2:
        diagnosis = "Androgen Dominance"
        rec = "- Excess hair and scalp thinning suggest androgen excess, often tied to PCOS or adrenal patterns."
    elif "Yes, severe and persistent" in q3:
        diagnosis = "Inflammatory Hormonal Imbalance"
        rec = "- Chronic skin issues point to inflammation driven by hormone imbalance, often related to cortisol or insulin."
    elif "Can't lose weight" in q4:
        diagnosis = "Metabolic Imbalance"
        rec = "- Difficulty losing weight despite efforts may signal insulin resistance or thyroid-related issues."
    else:
        diagnosis = "Ovulatory Imbalance"
        rec = "- Subtle symptoms suggest irregular ovulation or mild estrogen-progesterone imbalance."

    st.markdown(f"### 🧬 Diagnosis: **{diagnosis}**")
    st.markdown("#### 🔍 Personalized Insights")
    st.markdown(rec)

    st.image("qr_code.png", width=180)

    # ----------------- WAITLIST -----------------
    st.markdown("### 💬 Want to join the InBalance waitlist?")
    st.session_state.waitlist_opt_in = st.radio("Would you like to join?", ["Yes", "No"], index=None)

    tracking = goal = notes = ""
    symptoms = []

    if st.session_state.waitlist_opt_in == "Yes":
        tracking = st.radio("Do you track your cycle/symptoms?", ["Yes, with an app", "Yes, manually", "No, but I want to", "Other"], index=None)
        symptoms = st.multiselect("Symptoms you face:", ["Irregular cycles", "Low energy", "Mood swings", "Acne", "Cravings", "Bloating", "Brain fog"])
        goal = st.radio("Your main health goal?", ["Understand my cycle", "Reduce symptoms", "Looking for diagnosis", "Lifestyle plan", "Other"], index=None)
        notes = st.text_area("Anything else you'd like to share?")

    if st.button("📩 Finish & Save"):
        try:
            if sheet:
                sheet.append_row([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    st.session_state.first_name,
                    st.session_state.last_name,
                    st.session_state.email,
                    st.session_state.country_code + st.session_state.phone_number,
                    *st.session_state.answers,
                    diagnosis,
                    rec,
                    st.session_state.waitlist_opt_in,
                    tracking,
                    ", ".join(symptoms),
                    goal,
                    notes
                ])
                st.success("✅ Your answers were saved successfully!")
            else:
                st.error("Google Sheets is not connected.")
        except Exception as e:
            st.error(f"Could not save to Google Sheets: {e}")

# ----------------- RESTART -----------------
if st.button("🔄 Restart Quiz"):
    st.session_state.clear()
    st.rerun()
