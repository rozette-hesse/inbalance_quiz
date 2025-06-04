from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from PIL import Image
import re
import gspread
from google.oauth2.service_account import Credentials

# ----------------- CONFIGURATION -----------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# Load branding
logo = Image.open("logo.png")
st.image(logo, width=120)

# ----------------- SESSION STATE INIT -----------------
defaults = {
    "q_index": 0,
    "answers": [],
    "completed": False,
    "name": "",
    "email": "",
    "phone": "",
    "waitlist_opt_in": None,
    "extra_questions_done": False
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ----------------- GOOGLE SHEETS -----------------
try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
    client = gspread.authorize(credentials)
    sheet = client.open("InBalance_Quiz_Responses").sheet1
except Exception:
    sheet = None

# ----------------- START SCREEN -----------------
if st.session_state.q_index == 0 and not st.session_state.completed:
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to help you understand your hormonal health — and how InBalance can help.")

    st.session_state.name = st.text_input("👤 First Name:", st.session_state.name)
    st.session_state.email = st.text_input("📧 Email Address:", st.session_state.email)
    st.session_state.phone = st.text_input("📱 Phone Number (optional):", st.session_state.phone)

    def is_valid_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    if st.button("Start Quiz"):
        if not st.session_state.name.strip():
            st.warning("Please enter your name to continue.")
        elif not is_valid_email(st.session_state.email):
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.q_index = 1
            st.rerun()
    st.stop()

# ----------------- QUIZ QUESTIONS -----------------
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
            ("Yes, mild but manageable", 4),
            ("Yes, often despite treatment", 6),
            ("Yes, severe and persistent", 8),
        ]
    },
    {
        "q": "Have you experienced weight changes?",
        "options": [
            ("No, stable weight", 1),
            ("Stable only with effort", 2),
            ("Struggling to maintain weight", 5),
            ("Can't lose weight despite diet/exercise", 7),
        ]
    },
    {
        "q": "Do you feel tired or sleepy after meals?",
        "options": [
            ("No, not really", 1),
            ("Sometimes after heavy meals", 2),
            ("Yes, often regardless of food", 4),
            ("Yes, almost daily with alertness issues", 6),
        ]
    },
]

# ----------------- QUIZ FLOW -----------------
index = st.session_state.q_index
if 1 <= index <= len(questions):
    q = questions[index - 1]
    st.markdown(f"### {q['q']}")
    options = [opt[0] for opt in q["options"]]
    selected_option = st.radio(" ", options, key=f"q{index}")

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
            if selected_option:
                score = next(score for text, score in q["options"] if text == selected_option)
                st.session_state.answers.append(score)
                st.session_state.q_index += 1
                if st.session_state.q_index > len(questions):
                    st.session_state.completed = True
                st.rerun()
            else:
                st.warning("Please select an option to continue.")

# ----------------- DIAGNOSIS -----------------
if st.session_state.completed:
    total = sum(st.session_state.answers)
    st.session_state.total_score = total

    if total < 8:
        diagnosis = "No strong hormonal patterns detected"
        rec = "Your cycle and symptoms seem generally balanced. Keep observing changes month-to-month."
    elif total < 16:
        diagnosis = "Ovulatory Imbalance"
        rec = "You may have subtle hormonal fluctuations. These may cause fatigue, breakouts, or missed ovulation."
    elif total < 24:
        diagnosis = "HCA-PCO (Possible PCOS)"
        rec = "Several symptoms point to a mild PCOS pattern. Consider confirming this with a clinician."
    else:
        diagnosis = "H-PCO (Androgenic + Metabolic Signs)"
        rec = "You show signs of both hormone and metabolic imbalance. A tailored approach is recommended."

    st.session_state.diagnosis = diagnosis

    st.success("✅ Quiz complete!")
    st.markdown(f"### 🧬 Result: {diagnosis}")
    st.write(rec)

    st.markdown("#### 💡 How InBalance Can Help")
    st.info("InBalance helps you track symptoms, cycles, fatigue, skin changes, and more — and our experts use that data to guide your care.")

    qr = Image.open("qr_code.png")
    st.image(qr, width=180)

    st.markdown("### 💬 Want to join the InBalance app waitlist?")
    st.session_state.waitlist_opt_in = st.radio("Would you like to join?", ["Yes", "No"])

    if not st.session_state.extra_questions_done:
        if st.session_state.waitlist_opt_in == "Yes":
            tracking = st.radio("Do you currently track your cycle or symptoms?", [
                "Yes, with an app", "Yes, manually", "No, but I want to", "No, and I don’t know where to start", "Other"])
            symptoms = st.multiselect("What symptoms do you deal with most often?", [
                "Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"])
            goal = st.radio("What is your main health goal?", [
                "Understand my cycle", "Reduce symptoms", "Looking for diagnosis", "Personalized lifestyle plan", "Just curious", "Other"])
            notes = st.text_area("Anything else you'd like us to know?")
        else:
            tracking = "Declined waitlist"
            symptoms = []
            goal = ""
            notes = ""

        if st.button("📩 Finish & Save"):
            try:
                if sheet:
                    sheet.append_row([
                        st.session_state.name,
                        st.session_state.email,
                        st.session_state.phone,
                        *st.session_state.answers,
                        st.session_state.get("diagnosis", ""),
                        st.session_state.get("total_score", ""),
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
