import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# --------------- CONFIG ----------------
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
logo = Image.open("logo.png")
st.image(logo, width=120)

# --------------- SESSION INIT ---------------
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.answers = {}
    st.session_state.waitlist = {}
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.diagnosis = ""

# --------------- GOOGLE SHEETS ---------------
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except Exception:
    st.warning("⚠️ Google Sheet not connected. Responses will not be saved.")
    sheet = None

# --------------- QUESTIONS ----------------
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

# ------------- UTILS -------------
def get_country_choices():
    countries = []
    for country in pycountry.countries:
        try:
            code = phonenumbers.country_code_for_region(country.alpha_2)
            emoji = chr(127397 + ord(country.alpha_2[0])) + chr(127397 + ord(country.alpha_2[1]))
            countries.append(f"{emoji} {country.name} (+{code})")
        except:
            continue
    return sorted(countries)

def validate_phone(country, number):
    try:
        code = country.split("(+")[-1].split(")")[0]
        parsed = phonenumbers.parse(f"+{code}{number}")
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

# ------------- INTRO PAGE -------------
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to understand your hormonal health — and how InBalance can help.")

    fn = st.text_input("👩 First Name")
    ln = st.text_input("👩 Last Name")
    email = st.text_input("📧 Email")
    country = st.selectbox("🌍 Country (optional)", [""] + get_country_choices())
    phone = st.text_input("📱 Phone (optional, no spaces)")

    if st.button("Start Quiz"):
        if not all([fn.strip(), ln.strip(), email.strip()]):
            st.warning("Please complete first name, last name and email.")
        elif phone.strip() and country and not validate_phone(country, phone):
            st.warning("Phone number is not valid for the selected country.")
        else:
            st.session_state.info = {
                "First Name": fn.strip(),
                "Last Name": ln.strip(),
                "Email": email.strip(),
                "Country": country,
                "Phone": phone.strip()
            }
            st.session_state.page = "quiz"
            st.rerun()

# ------------- QUIZ PAGE -------------
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    unanswered = False

    for idx, (qid, q) in enumerate(questions.items(), start=1):
        text = f"{idx}. {q['text']}"
        opts = q["options"]
        answer = st.radio(text, opts, key=f"q{idx}", index=None)
        if answer:
            st.session_state.answers[qid] = answer
        else:
            unanswered = True

    if st.button("See My Results"):
        if unanswered:
            st.warning("Please answer all questions before continuing.")
        else:
            st.session_state.page = "results"
            st.rerun()

# ------------- RESULTS PAGE -------------
elif st.session_state.page == "results":
    q = list(st.session_state.answers.values())
    diagnosis = "Mild Hormonal Imbalance"
    if "Rarely" in q[0] or "irregular" in q[0]:
        diagnosis = "Cycle Irregularity"
    if "resistant" in q[1] or "scalp" in q[1]:
        diagnosis = "Potential PCOS"
    if "Can't lose" in q[3]:
        diagnosis = "H-PCO (Hormonal and Metabolic)"

    st.subheader(f"🍭 Diagnosis: {diagnosis}")
    st.markdown("### ❎ Recommendations based on your answers:")
    recs = []

    if "irregular" in q[0]:
        recs.append("🗓️ Try using a symptom tracker to identify ovulation trends and disruptions.")
    if "resistant" in q[1] or "scalp" in q[1]:
        recs.append("🧬 Excess hair and thinning could indicate elevated androgens. Endocrinologist support is key.")
    if "despite" in q[2] or "persistent" in q[2]:
        recs.append("💊 Persistent acne often signals a hormonal imbalance. Consider expert skin & hormonal care.")
    if "Struggling" in q[3] or "Can't" in q[3]:
        recs.append("🏋️ Difficulty managing weight? Metabolic optimization can help regulate insulin and hormones.")
    if "sleepy" in q[4] or "daily" in q[4]:
        recs.append("🍽️ Fatigue after meals may be tied to glucose drops. A sugar-balancing approach helps.")

    for r in recs:
        st.info(r)

    st.warning("⚠️ *Informational only. Always consult a physician before making medical decisions.*")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🧠 Precision cycle & symptom tracking  
- 🧪 Phase-specific health recommendations  
- 👩‍⚕️ Access to gynecologists, endocrinologists, nutritionists & trainers  
- 📊 Personalized, data-backed plans  
- 🔁 Ongoing guidance as your body evolves
""")
    st.image("qr_code.png", width=140)

    st.session_state.diagnosis = diagnosis
    st.session_state.page = "waitlist"
    st.rerun()

# ------------- WAITLIST PAGE -------------
elif st.session_state.page == "waitlist":
    st.subheader("📥 Join the InBalance Waitlist")

    join = st.radio("Would you like to join?", ["Yes", "No"], index=None)
    tracking = symptoms = goal = notes = ""

    if join == "Yes":
        tracking = st.radio("Do you track your cycle/symptoms?", ["Yes, with an app", "Yes, manually", "Not yet", "Other"], index=None)
        symptoms = st.multiselect("Top symptoms you face:", ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog"])
        goal = st.radio("Main health goal:", ["Understand my cycle", "Reduce symptoms", "Get diagnosis", "Personalized plan", "Just curious"], index=None)
        notes = st.text_area("Other notes you'd like to share:")

    if st.button("📩 Save & Finish"):
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
                st.success("✅ Saved! We’ll be in touch 💌")
        except Exception as e:
            st.error(f"❌ Could not save to sheet: {e}")

    if st.button("🔁 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
