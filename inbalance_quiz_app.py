# --- Imports ---
import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# --- Config ---
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
logo = Image.open("logo.png")
st.image(logo, width=120)

# --- Session Init ---
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.answers = {}
    st.session_state.waitlist = {}
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Google Sheets Setup ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# --- Questions ---
questions = {
    "Q1": "How regular was your menstrual cycle in the past year?",
    "Q2": "Do you notice excessive thick black hair on your face, chest, or back?",
    "Q3": "Have you had acne or oily skin this year?",
    "Q4": "Have you experienced weight changes?",
    "Q5": "Do you feel tired or sleepy after meals?",
}
options = {
    "Q1": [
        "Does not apply (e.g., hormonal treatment or pregnancy)",
        "Regular (25–35 days)",
        "Often irregular (< 25 or > 35 days)",
        "Rarely got period (< 6 times a year)"
    ],
    "Q2": [
        "No, not at all",
        "Yes, manageable with hair removal",
        "Yes, resistant to hair removal",
        "Yes + scalp thinning or hair loss"
    ],
    "Q3": [
        "No",
        "Yes, mild but manageable",
        "Yes, often despite treatment",
        "Yes, severe and persistent"
    ],
    "Q4": [
        "No, stable weight",
        "Stable only with effort",
        "Struggling to maintain weight",
        "Can't lose weight despite diet/exercise"
    ],
    "Q5": [
        "No, not really",
        "Sometimes after heavy meals",
        "Yes, often regardless of food",
        "Yes, almost daily with alertness issues"
    ]
}

# --- Utils ---
def get_country_choices():
    countries = []
    for c in pycountry.countries:
        try:
            code = phonenumbers.country_code_for_region(c.alpha_2)
            emoji = chr(127397 + ord(c.alpha_2[0])) + chr(127397 + ord(c.alpha_2[1]))
            countries.append(f"{emoji} {c.name} (+{code})")
        except:
            continue
    return sorted(set(countries))

def validate_phone(country_str, number):
    try:
        code = country_str.split("(+")[1].split(")")[0]
        phone_obj = phonenumbers.parse(f"+{code}{number}")
        return phonenumbers.is_valid_number(phone_obj)
    except:
        return False

# --- Intro Page ---
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to understand your hormonal health — and how InBalance can help.")

    first_name = st.text_input("👩‍🦰 First Name")
    last_name = st.text_input("👩‍🦰 Last Name")
    email = st.text_input("📧 Email")
    countries = get_country_choices()
    country = st.selectbox("🌍 Country", countries)
    phone = st.text_input("📱 Phone (optional)")

    if st.button("Start Quiz"):
        if not all([first_name.strip(), last_name.strip(), email.strip(), country]):
            st.warning("Please complete all required fields.")
        elif phone.strip() and not validate_phone(country, phone):
            st.warning("Invalid phone number for selected country.")
        else:
            st.session_state.info = {
                "First Name": first_name,
                "Last Name": last_name,
                "Email": email,
                "Country": country,
                "Phone": phone
            }
            st.session_state.page = "quiz"
            st.rerun()

# --- Quiz Page ---
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    for key, text in questions.items():
        st.session_state.answers[key] = st.radio(f"**{text}**", options[key], key=key, index=None)

    if st.button("Submit Answers"):
        if None in st.session_state.answers.values():
            st.warning("Please answer all questions.")
        else:
            st.session_state.page = "results"
            st.rerun()

# --- Results Page ---
elif st.session_state.page == "results":
    st.header("🍭 Diagnosis")

    q = st.session_state.answers
    diagnosis = "Mild imbalance or no clear pattern"
    if "irregular" in q["Q1"] or "Rarely" in q["Q1"]:
        diagnosis = "Cycle Irregularity"
    if "resistant" in q["Q2"] or "scalp" in q["Q2"]:
        diagnosis = "Potential PCOS"
    if "Can't lose" in q["Q4"]:
        diagnosis = "H-PCO (Hormonal and Metabolic)"

    st.session_state.diagnosis = diagnosis
    st.subheader(f"🧬 Diagnosis: {diagnosis}")

    # Recommendations
    st.markdown("### 🛠️ Personalized Recommendations")
    recs = []
    if "irregular" in q["Q1"]: recs.append("🩸 Track ovulation consistently to identify hormonal fluctuations.")
    if "resistant" in q["Q2"]: recs.append("🧬 High androgens? Consider tests and specialist support.")
    if "acne" in q["Q3"]: recs.append("🧖 Persistent acne could reflect internal hormone issues.")
    if "Can't" in q["Q4"]: recs.append("⚖️ Weight resistance suggests metabolic factors like insulin resistance.")
    if "sleepy" in q["Q5"]: recs.append("🍽️ Tired after meals? You may need a sugar-balancing plan.")

    for rec in recs:
        st.info(rec)

    st.warning("⚠️ Informational only. Always consult a physician.")

    # InBalance help section
    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 📅 Track cycles and symptoms across phases  
- 📊 Phase-based recommendations  
- 👩‍⚕️ Access to experts: gynecologists, endocrinologists, nutritionists & trainers  
- 🧠 Data-driven personalized plans  
- 🔁 Ongoing support through your journey  
""")
    st.image("qr_code.png", width=140)

    # Waitlist
    st.session_state.page = "waitlist"
    st.rerun()

# --- Waitlist Page ---
elif st.session_state.page == "waitlist":
    st.subheader("💬 Want to join the InBalance waitlist?")
    join = st.radio("Would you like to join?", ["Yes", "No"], index=None)

    tracking = symptoms = goal = notes = ""
    if join == "Yes":
        tracking = st.radio("Do you track your cycle/symptoms?", ["Yes, with an app", "Yes, manually", "Not yet", "Other"], index=None)
        symptoms = st.multiselect("Top symptoms:", ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog"])
        goal = st.radio("Main health goal:", ["Understand my cycle", "Reduce symptoms", "Get diagnosis", "Personalized plan", "Just curious"], index=None)
        notes = st.text_area("Other notes")

    if st.button("📩 Finish & Save"):
        try:
            if sheet:
                row = [
                    st.session_state.timestamp,
                    *st.session_state.info.values(),
                    *st.session_state.answers.values(),
                    st.session_state.diagnosis,
                    join,
                    tracking,
                    ", ".join(symptoms),
                    goal,
                    notes
                ]
                sheet.append_row(row)
                st.success("✅ Saved! You're on the list.")
            else:
                st.error("Google Sheet not connected.")
        except Exception as e:
            st.error(f"Error saving: {e}")

    if st.button("🔁 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
