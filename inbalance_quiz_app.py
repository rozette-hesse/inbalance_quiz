from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from PIL import Image
import re
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# -------------- CONFIG --------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# -------------- SESSION INIT --------------
defaults = {
    "q_index": 0, "answers": [], "completed": False,
    "first_name": "", "last_name": "", "email": "",
    "country_code": "+961", "phone_number": "",
    "waitlist_opt_in": None, "extra_questions_done": False
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------- GOOGLE SHEETS --------------
try:
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    credentials_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
    sheet = gspread.authorize(credentials).open("InBalance_Quiz_Responses").sheet1
except Exception:
    sheet = None

# -------------- QUESTIONS --------------
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

# -------------- START PAGE --------------
if st.session_state.q_index == 0 and not st.session_state.completed:
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to help you understand your hormonal health — and how InBalance can help.")

    st.session_state.first_name = st.text_input("👩 First Name:", st.session_state.first_name)
    st.session_state.last_name = st.text_input("👩 Last Name:", st.session_state.last_name)
    st.session_state.email = st.text_input("📧 Email Address:", st.session_state.email)

    country_options = ["+961", "+1", "+44", "+49", "+33", "+971", "+966", "+20", "+91"]
    st.session_state.country_code = st.selectbox("🌍 Country Code", country_options, index=country_options.index(st.session_state.country_code))
    st.session_state.phone_number = st.text_input("📱 Phone Number (no spaces):", st.session_state.phone_number)

    def is_valid_email(email):
        return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email)

    if st.button("Start Quiz"):
        if not st.session_state.first_name.strip() or not st.session_state.last_name.strip():
            st.warning("Please enter both first and last name.")
        elif not is_valid_email(st.session_state.email):
            st.warning("Please enter a valid email address.")
        elif not st.session_state.phone_number.strip().isdigit():
            st.warning("Phone number must be digits only.")
        else:
            st.session_state.q_index = 1
            st.rerun()
    st.stop()

# -------------- QUIZ LOGIC --------------
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

# -------------- RESULTS + INSIGHTS --------------
# -------------- RESULTS + DIAGNOSIS + INSIGHTS --------------
if st.session_state.completed:
    st.success("✅ Quiz complete!")

    st.markdown("## 🧬 Your Diagnosis")
    answers = st.session_state.answers
    diagnosis = ""
    summary = ""

    # Count patterns
    patterns = {
        "irregular_cycle": "irregular" in answers[0].lower() or "rarely" in answers[0].lower(),
        "androgen": "hair loss" in answers[1].lower() or "resistant" in answers[1].lower(),
        "acne": "persistent" in answers[2].lower() or "despite" in answers[2].lower(),
        "weight": "can't lose" in answers[3].lower() or "struggling" in answers[3].lower(),
        "fatigue": "tired" in answers[4].lower() or "daily" in answers[4].lower()
    }

    # Diagnosis logic
    total_flags = sum(patterns.values())
    if total_flags <= 1:
        diagnosis = "No strong hormonal patterns detected"
        summary = "Your cycle and symptoms seem generally balanced. Keep observing changes month-to-month."
    elif total_flags == 2:
        diagnosis = "Ovulatory Imbalance"
        summary = "You may have subtle hormonal fluctuations. These may cause fatigue, breakouts, or missed ovulation."
    elif total_flags == 3 or total_flags == 4:
        diagnosis = "HCA-PCO (Possible PCOS)"
        summary = "Several symptoms point to a mild PCOS pattern. Consider confirming this with a clinician."
    else:
        diagnosis = "H-PCO (Androgenic + Metabolic Signs)"
        summary = "You show signs of both hormone and metabolic imbalance. A tailored approach is recommended."

    st.markdown(f"### 🔍 **{diagnosis}**")
    st.write(summary)

    # Personalized insights
    st.markdown("### 🧬 Personalized Results & Guidance")
    insights = []

    if patterns["irregular_cycle"]:
        insights.append("Your cycle seems irregular or infrequent. This could indicate hormonal disruptions or lack of ovulation.")
    if patterns["androgen"]:
        insights.append("You may be experiencing elevated androgens, often linked to PCOS or other imbalances.")
    if patterns["acne"]:
        insights.append("Chronic acne may point to underlying hormone or inflammation issues.")
    if patterns["weight"]:
        insights.append("You might be facing metabolic challenges — especially related to insulin or cortisol.")
    if patterns["fatigue"]:
        insights.append("Post-meal fatigue is often connected to insulin resistance or blood sugar dysregulation.")

    for insight in insights:
        st.write(f"🔹 {insight}")

    # Show QR Code after insights
    st.markdown("#### 💡 How InBalance Can Help")
    st.info("InBalance helps you track symptoms, cycles, fatigue, skin changes, and more — and our experts use that data to guide your care.")
    st.image("qr_code.png", width=180)

# -------------- RESTART --------------
if st.button("🔄 Restart Quiz"):
    st.session_state.clear()
    st.rerun()
