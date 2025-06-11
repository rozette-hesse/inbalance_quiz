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

# --------------- GOOGLE SHEETS ---------------
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except Exception:
    st.error("❌ Google Sheets not connected.")
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
            flag = chr(127397 + ord(country.alpha_2[0])) + chr(127397 + ord(country.alpha_2[1]))
            countries.append(f"{flag} {country.name} (+{code})")
        except:
            continue
    return sorted(set(countries))

def validate_phone(country, number):
    try:
        code = country.split("(+")[1].split(")")[0]
        phone_obj = phonenumbers.parse(f"+{code}{number}")
        return phonenumbers.is_valid_number(phone_obj)
    except:
        return False

# ------------- PAGE: INTRO -------------
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to understand your hormonal health — and how InBalance can help.")

    fname = st.text_input("👩 First Name")
    lname = st.text_input("👩 Last Name")
    email = st.text_input("📧 Email")
    country = st.selectbox("🌍 Country", get_country_choices())
    phone = st.text_input("📱 Phone (without spaces)")

    if st.button("Start Quiz"):
        if not all([fname.strip(), lname.strip(), email.strip(), country]):
            st.warning("Please complete name, email, and country.")
        elif phone.strip() and not validate_phone(country, phone):
            st.warning("Invalid phone number format.")
        else:
            st.session_state.info = {
                "First Name": fname, "Last Name": lname, "Email": email,
                "Country": country, "Phone": phone
            }
            st.session_state.page = "quiz"
            st.rerun()

# ------------- PAGE: QUIZ -------------
elif st.session_state.page == "quiz":
    st.header("📝 Quiz: Answer All Questions")
    all_answered = True
    for key, q in questions.items():
        answer = st.radio(f"**{q['text']}**", q["options"], index=None, key=key)
        st.session_state.answers[key] = answer
        if answer is None:
            all_answered = False

    if st.button("➡️ Submit Answers"):
        if not all_answered:
            st.warning("Please answer all questions.")
        else:
            st.session_state.page = "results"
            st.rerun()

# ------------- PAGE: RESULTS -------------
elif st.session_state.page == "results":
    st.header("🧬 Your Hormonal Pattern")
    answers = st.session_state.answers
    q_values = list(answers.values())

    # Diagnosis
    if "Rarely" in q_values[0] or "irregular" in q_values[0]:
        diagnosis = "Hormonal Cycle Imbalance"
    elif "scalp" in q_values[1]:
        diagnosis = "Androgen-Driven PCOS"
    elif "Can't lose weight" in q_values[3]:
        diagnosis = "Metabolic-Inflammatory Pattern"
    else:
        diagnosis = "No Strong Pattern Detected"

    st.subheader(f"✅ Diagnosis: {diagnosis}")

    # Recommendations
    st.markdown("### 🛠️ Personalized Recommendations:")
    rec_map = {
        "Regular (25–35 days)": "Track cycles monthly to maintain awareness of ovulation timing.",
        "Rarely got period (< 6 times a year)": "This may suggest PCOS or hypothalamic amenorrhea. Seek a hormonal panel.",
        "Yes + scalp thinning or hair loss": "May signal androgen excess. An endocrinologist can assist.",
        "Yes, severe and persistent": "Consider both hormone and gut assessments. Nutrition therapy may help.",
        "Can't lose weight despite diet/exercise": "This suggests metabolic resistance. Tailored lifestyle plans matter.",
        "Yes, almost daily with alertness issues": "Could reflect insulin imbalance. Consider glucose monitoring."
    }

    for ans in q_values:
        if ans in rec_map:
            st.info(rec_map[ans])

    st.warning("⚠️ This result is informational and not a diagnosis. Please consult a licensed physician.")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 📊 Advanced symptom & cycle tracking tools  
- 👩‍⚕️ Access to gynecologists, endocrinologists, and certified trainers  
- 🔁 Adjustments and expert care over time  
- 🧬 Personalized recommendations in-app based on data  
""")
    st.image("qr_code.png", width=140)

    st.session_state.page = "waitlist"
    st.rerun()

# ------------- PAGE: WAITLIST -------------
elif st.session_state.page == "waitlist":
    st.header("📬 Join the InBalance Waitlist")

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
                    diagnosis,
                    join,
                    tracking,
                    ", ".join(symptoms),
                    goal,
                    notes
                ]
                sheet.append_row(row)
                st.success("✅ Saved! We'll be in touch 💌")
        except Exception as e:
            st.error(f"❌ Could not save to sheet: {e}")

    if st.button("🔁 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
