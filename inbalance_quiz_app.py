import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# ------------------ CONFIG ------------------
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
logo = Image.open("logo.png")
st.image(logo, width=120)

# ------------------ INIT ------------------
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.answers = {}
    st.session_state.waitlist = {}
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ------------------ GOOGLE SHEETS ------------------
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    st.error("⚠️ Google Sheet not connected.")
    sheet = None

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
        dial_code = country.split("(+")[1].split(")")[0]
        full_number = f"+{dial_code}{number}"
        parsed = phonenumbers.parse(full_number)
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

# ------------------ PAGE: INTRO ------------------
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to understand your hormonal health — and how InBalance can help.")

    first = st.text_input("👩‍🦰 First Name")
    last = st.text_input("👩‍🦰 Last Name")
    email = st.text_input("📧 Email")
    countries = get_country_choices()
    country = st.selectbox("🌍 Country", countries)
    phone = st.text_input("📱 Phone (optional, no spaces)")

    if st.button("Start Quiz"):
        if not all([first.strip(), last.strip(), email.strip(), country.strip()]):
            st.warning("Please complete all required fields.")
        elif phone and not validate_phone(country, phone):
            st.warning("Invalid phone number for selected country.")
        else:
            st.session_state.info = {
                "First Name": first,
                "Last Name": last,
                "Email": email,
                "Country": country,
                "Phone": phone
            }
            st.session_state.page = "quiz"

# ------------------ PAGE: QUIZ ------------------
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    unanswered = False
    for key, q in questions.items():
        answer = st.radio(f"**{q['text']}**", q["options"], key=key, index=None)
        st.session_state.answers[key] = answer
        if answer is None:
            unanswered = True

    if st.button("See My Results"):
        if unanswered:
            st.warning("Please answer all questions.")
        else:
            st.session_state.page = "results"

# ------------------ PAGE: RESULTS ------------------
elif st.session_state.page == "results":
    q = list(st.session_state.answers.values())
    # Diagnosis logic
    if "Rarely" in q[0] or "irregular" in q[0]:
        diagnosis = "Cycle Irregularity"
    elif "resistant" in q[1] or "scalp" in q[1]:
        diagnosis = "Potential PCOS"
    elif "Can't lose weight" in q[3]:
        diagnosis = "H-PCO (Hormonal & Metabolic)"
    else:
        diagnosis = "Mild Hormonal Imbalance"

    st.subheader(f"🧬 Diagnosis: {diagnosis}")
    st.markdown("### 🧩 Recommendations based on your answers:")

    recs = []
    if "irregular" in q[0]:
        recs.append("📅 Try using a symptom tracker to identify ovulation trends and disruptions.")
    if "resistant" in q[1] or "scalp" in q[1]:
        recs.append("💇‍♀️ Excess hair and thinning could indicate elevated androgens. Endocrinologist support is key.")
    if "acne" in q[2].lower() or "oily" in q[2].lower():
        recs.append("🧴 Persistent acne can reflect hormone excess. Targeted skincare + hormone review is ideal.")
    if "Struggling" in q[3] or "Can't lose weight" in q[3]:
        recs.append("⚖️ Difficulty with weight may signal insulin resistance. A metabolic plan can help.")
    if "sleepy" in q[4] or "fatigue" in q[4]:
        recs.append("😴 Fatigue after meals might be blood sugar related. Consider glucose-stabilizing strategies.")

    for rec in recs:
        st.info(rec)

    st.warning("⚠️ *Informational only. Always consult a physician before making medical decisions.*")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 📅 Precision cycle & symptom tracking
- 🧬 Phase-specific health recommendations
- 👩‍⚕️ Direct access to gynecologists, endocrinologists, nutritionists & trainers
- 📊 Personalized, data-backed plans
- 🔄 Ongoing guidance as your body evolves
""")
    st.image("qr_code.png", width=140)

    st.session_state.diagnosis = diagnosis
    st.session_state.page = "waitlist"

# ------------------ PAGE: WAITLIST ------------------
elif st.session_state.page == "waitlist":
    st.subheader("💬 Want to join the InBalance waitlist?")
    join = st.radio("Would you like to join?", ["Yes", "No"], index=None)

    tracking = symptoms = goal = notes = ""

    if join == "Yes":
        tracking = st.radio("Do you track your cycle/symptoms?", [
            "Yes, with an app", "Yes, manually", "Not yet", "Other"], index=None)
        symptoms = st.multiselect("Top symptoms you face:", [
            "Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog"])
        goal = st.radio("Main health goal:", [
            "Understand my cycle", "Reduce symptoms", "Get diagnosis", "Personalized plan", "Just curious"], index=None)
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
                st.success("✅ Saved! You’re on our waitlist 🎉")
        except Exception as e:
            st.error(f"❌ Could not save to sheet: {e}")

    if st.button("🔁 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
