import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# ------------------ CONFIG ------------------
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# ------------------ SESSION INIT ------------------
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.answers = {}
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ------------------ GOOGLE SHEETS ------------------
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# ------------------ UTILS ------------------
def get_country_choices():
    countries = []
    for country in pycountry.countries:
        try:
            code = phonenumbers.country_code_for_region(country.alpha_2)
            emoji = chr(127397 + ord(country.alpha_2[0])) + chr(127397 + ord(country.alpha_2[1]))
            countries.append(f"{emoji} {country.name} (+{code})")
        except:
            continue
    return sorted(set(countries))

def validate_phone(country, number):
    try:
        code = country.split("(+")[-1].split(")")[0]
        phone_obj = phonenumbers.parse(f"+{code}{number}")
        return phonenumbers.is_valid_number(phone_obj)
    except:
        return False

# ------------------ QUESTIONS ------------------
questions = {
    "Q1": {
        "text": "How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (e.g., hormonal treatment or pregnancy)",
            "Regular (25–35 days)",
            "Often irregular (< 25 or > 35 days)",
            "Rarely got period (< 6 times a year)"
        ]
    },
    "Q2": {
        "text": "Do you notice excessive thick black hair on your face, chest, or back?",
        "options": [
            "No, not at all",
            "Yes, manageable with hair removal",
            "Yes, resistant to hair removal",
            "Yes + scalp thinning or hair loss"
        ]
    },
    "Q3": {
        "text": "Have you had acne or oily skin this year?",
        "options": [
            "No",
            "Yes, mild but manageable",
            "Yes, often despite treatment",
            "Yes, severe and persistent"
        ]
    },
    "Q4": {
        "text": "Have you experienced weight changes?",
        "options": [
            "No, stable weight",
            "Stable only with effort",
            "Struggling to maintain weight",
            "Can't lose weight despite diet/exercise"
        ]
    },
    "Q5": {
        "text": "Do you feel tired or sleepy after meals?",
        "options": [
            "No, not really",
            "Sometimes after heavy meals",
            "Yes, often regardless of food",
            "Yes, almost daily with alertness issues"
        ]
    }
}

# ------------------ PAGE: INTRO ------------------
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to understand your hormonal health — and how InBalance can help.")

    first = st.text_input("👩‍🦰 First Name")
    last = st.text_input("👩‍🦰 Last Name")
    email = st.text_input("📧 Email")
    country_list = get_country_choices()
    country = st.selectbox("🌍 Country", country_list)
    phone = st.text_input("📱 Phone (optional, no spaces)")

    if st.button("Start Quiz"):
        if not all([first.strip(), last.strip(), email.strip(), country.strip()]):
            st.warning("Please fill in all required fields.")
        elif phone.strip() and not validate_phone(country, phone):
            st.warning("Phone number invalid for selected country.")
        else:
            st.session_state.info = {
                "First Name": first,
                "Last Name": last,
                "Email": email,
                "Country": country,
                "Phone": phone
            }
            st.session_state.page = "quiz"
            st.rerun()

# ------------------ PAGE: QUIZ ------------------
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    for qid, qdata in questions.items():
        st.session_state.answers[qid] = st.radio(f"**{qdata['text']}**", qdata["options"], index=None, key=qid)

    if st.button("Submit Answers"):
        if None in st.session_state.answers.values():
            st.warning("Please answer all questions.")
        else:
            st.session_state.page = "results"
            st.rerun()

# ------------------ PAGE: RESULTS & WAITLIST ------------------
elif st.session_state.page == "results":
    q = st.session_state.answers
    diagnosis = "Mild imbalance or no clear pattern"
    if "irregular" in q["Q1"] or "Rarely" in q["Q1"]:
        diagnosis = "Cycle Irregularity"
    if "resistant" in q["Q2"] or "scalp" in q["Q2"]:
        diagnosis = "Potential PCOS"
    if "Can't" in q["Q4"]:
        diagnosis = "H-PCO (Hormonal and Metabolic)"
    st.session_state.diagnosis = diagnosis

    st.subheader(f"🧬 Diagnosis: {diagnosis}")
    st.markdown("### 🛠️ Personalized Recommendations")
    recs = []
    if "irregular" in q["Q1"]: recs.append("📅 Track ovulation regularly to detect disruptions.")
    if "resistant" in q["Q2"]: recs.append("🧬 Hair pattern may point to high androgens — get hormonal testing.")
    if "acne" in q["Q3"]: recs.append("🧖 Persistent acne may need tailored treatment — consult a skin-hormone expert.")
    if "Can't" in q["Q4"]: recs.append("⚖️ Metabolic patterns may require nutrition & movement planning.")
    if "sleepy" in q["Q5"]: recs.append("🍽️ Feeling tired post-meals? May link to insulin resistance — blood sugar balance matters.")

    for rec in recs:
        st.info(rec)

    st.warning("⚠️ This is informational only. Always consult a physician for medical decisions.")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🗓️ Precision cycle & symptom tracking
- 🔄 Phase-based guidance personalized to you
- 👩‍⚕️ Access to top gynecologists, endocrinologists, nutritionists & trainers
- 📈 Data-informed diagnosis & treatment options
- 🧠 Adjustments based on your biofeedback
""")
    st.image("qr_code.png", width=150)

    # ----------- WAITLIST BELOW RESULTS -----------
    st.markdown("### 💬 Join the InBalance Waitlist")
    join = st.radio("Would you like to join?", ["Yes", "No"], index=None)
    tracking = symptoms = goal = notes = ""

    if join == "Yes":
        tracking = st.radio("Do you track your cycle/symptoms?", ["Yes, with an app", "Yes, manually", "Not yet", "Other"], index=None)
        symptoms = st.multiselect("Top symptoms:", ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog"])
        goal = st.radio("Main health goal:", ["Understand my cycle", "Reduce symptoms", "Get diagnosis", "Personalized plan", "Just curious"], index=None)
        notes = st.text_area("Other notes (optional)")

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
                st.success("✅ All saved. We’ll be in touch soon!")
            else:
                st.error("Google Sheet not connected.")
        except Exception as e:
            st.error(f"❌ Error saving: {e}")

    if st.button("🔁 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
