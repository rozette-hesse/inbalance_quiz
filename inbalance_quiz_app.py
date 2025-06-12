import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# ── CONFIG ──
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# ── SESSION INIT ──
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.answers = {}
    st.session_state.info = {}
    st.session_state.saved = False

# ── GOOGLE SHEETS ──
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# ── QUESTIONS ──
questions = [
    ("Q1", "How regular was your menstrual cycle in the past year?", [
        "Does not apply (e.g., pregnancy or hormonal treatment)",
        "Regular (25–35 days)",
        "Often irregular (<25 or >35 days)",
        "Rarely got period (<6 times/year)"
    ]),
    ("Q2", "Do you notice thick black hair on your face, chest, or back?", [
        "No",
        "Yes, manageable",
        "Yes, resistant to removal",
        "Yes + scalp thinning/hair loss"
    ]),
    ("Q3", "Did you have acne or oily skin this year?", [
        "No",
        "Yes, mild",
        "Yes, frequent despite treatment",
        "Yes, severe/persistent"
    ]),
    ("Q4", "Have you experienced persistent weight gain or difficulty losing weight?", [
        "No, weight is stable",
        "Stable only with effort",
        "Struggling to maintain",
        "Can't lose with diet/exercise"
    ]),
    ("Q5", "Do you feel tired or drowsy after meals?", [
        "No",
        "Sometimes",
        "Yes, frequently",
        "Yes, daily with low energy"
    ])
]

# ── UTILITIES ──
def get_countries():
    countries = [""]
    for c in pycountry.countries:
        try:
            code = phonenumbers.country_code_for_region(c.alpha_2)
            emoji = chr(127397 + ord(c.alpha_2[0])) + chr(127397 + ord(c.alpha_2[1]))
            countries.append(f"{emoji} {c.name} (+{code})")
        except:
            continue
    return sorted(set(countries))

def valid_phone(country, number):
    if not country or not number:
        return True
    try:
        code = int(country.split("(+")[1].split(")")[0])
        parsed = phonenumbers.parse(f"+{code}{number}")
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

# ── INTRO PAGE ──
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.text_input("First Name", key="fn")
    st.text_input("Last Name", key="ln")
    st.text_input("Email", key="email")
    st.selectbox("Country (optional)", get_countries(), key="country")
    st.text_input("Phone (no spaces, optional)", key="phone")

    if st.button("Start Quiz"):
        if not st.session_state.fn or not st.session_state.ln or not st.session_state.email:
            st.warning("Please enter first name, last name, and email.")
        elif not valid_phone(st.session_state.country, st.session_state.phone):
            st.warning("Invalid phone number for selected country.")
        else:
            st.session_state.info = {
                "First Name": st.session_state.fn,
                "Last Name": st.session_state.ln,
                "Email": st.session_state.email,
                "Country": st.session_state.country,
                "Phone": st.session_state.phone
            }
            st.session_state.page = "quiz"
            st.rerun()

# ── QUIZ ──
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    for qid, qtext, options in questions:
        st.markdown(f"**{qtext}**", unsafe_allow_html=True)
        st.session_state.answers[qid] = st.radio("", options, key=qid, index=None)
        st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("Submit Answers"):
        if any(answer is None for answer in st.session_state.answers.values()):
            st.warning("Please answer all questions.")
        else:
            st.session_state.page = "results"
            st.rerun()

# ── RESULTS ──
elif st.session_state.page == "results":
    a = st.session_state.answers
    st.subheader("🧬 Diagnosis: Based on your responses")

    # Simple logic
    diagnosis = "Mild Hormonal Imbalance"
    st.markdown("### 📌 Personalized Recommendations")


    recs = {
    "Q1": {
        "Does not apply (e.g., pregnancy or hormonal treatment)": "🧭 Hormonal treatments or pregnancy can override natural cycle patterns. Log symptoms instead to find trends.",
        "Regular (25–35 days)": "✅ Your cycle length looks regular! Keep tracking to spot phase-based symptoms.",
        "Often irregular (<25 or >35 days)": "🗓️ Irregular timing could suggest hormonal fluctuations—track your symptoms daily to understand your pattern.",
        "Rarely got period (<6 times/year)": "📉 Infrequent periods may signal PCOS or low estrogen. Consider hormone evaluation."
    },
    "Q2": {
        "No": "✅ No signs of abnormal hair growth. That’s a good indicator of hormone balance.",
        "Yes, manageable": "🔍 Some facial/body hair is common. Keep observing for any changes in amount or texture.",
        "Yes, resistant to removal": "🧬 Hair growth that's hard to manage may reflect high androgens. An expert can help.",
        "Yes + scalp thinning/hair loss": "👩‍⚕️ This pattern may signal androgen excess. A specialist review is useful."
    },
    "Q3": {
        "No": "✅ Clear skin suggests low inflammation and balanced hormones.",
        "Yes, mild": "💡 Occasional breakouts can occur with normal cycle changes. Track when they appear.",
        "Yes, frequent despite treatment": "🧪 Persistent acne can reflect hormonal imbalance. A targeted care plan helps.",
        "Yes, severe/persistent": "📋 Severe acne needs a hormonal + lifestyle approach. Consider expert review."
    },
    "Q4": {
        "No, weight is stable": "✅ Stability in weight is a good metabolic sign. Keep supporting your body with movement & nutrients.",
        "Stable only with effort": "🍽️ Needing extra effort may hint at mild insulin resistance. Support with meal balance.",
        "Struggling to maintain": "⚖️ This might signal metabolic imbalance—nutritionist support can help rebalance.",
        "Can't lose with diet/exercise": "📉 Weight resistance often links to hormones or blood sugar. Explore a metabolic reset plan."
    },
    "Q5": {
        "No": "✅ Great energy after meals! That suggests blood sugar is well-regulated.",
        "Sometimes": "🥱 Post-meal dips can happen—try pairing carbs with protein/fiber.",
        "Yes, frequently": "⚡ Frequent fatigue after eating may mean sugar swings. Track timing & meal content.",
        "Yes, daily with low energy": "🩺 Daily crashes may signal insulin resistance. Support with blood sugar balancing meals + light movement."
    }
}


    has_recommendation = False
    for qid, selected in a.items():
        rec = recs.get(qid, {}).get(selected)
        if rec:
            st.info(rec)
            has_recommendation = True

    if not has_recommendation:
        st.success("🎉 Your answers show no major hormonal concerns. Keep monitoring your cycle and symptoms monthly!")

    st.warning("⚠️ This is informational only. Please consult a physician for any medical advice.")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🧠 Accurate cycle & symptom tracking  
- 🩺 Access to expert care (gynecologists, endocrinologists, nutritionists, fitness pros)  
- 🧬 Personalized care plans based on YOUR profile  
- 🔁 Ongoing tracking and expert adjustment  
- 💬 All in one place, easy and smart
    """)

    st.image("qr_code.png", width=240)

    st.markdown("---")
    st.subheader("📥 Join the InBalance Waitlist")
    join = st.radio("Would you like to join?", ["Yes", "No"], key="join", index=None)

    track = symptoms = goal = notes = ""
    if join == "Yes":
        track = st.radio("How do you track symptoms?", ["App", "Manual", "Not yet", "Other"], key="track")
        symptoms = st.multiselect("Which symptoms affect you most?", ["Irregular cycles", "Acne", "Bloating", "Fatigue", "Mood swings", "Cravings", "Anxiety", "Brain fog", "Sleep issues"], key="symptoms")
        goal = st.radio("Main health goal?", ["Understand my cycle", "Reduce symptoms", "Get a diagnosis", "Personalized plan", "Other"], key="goal")
        notes = st.text_area("Any additional info?", key="notes")

    if st.button("📧 Save & Finish"):
        if sheet:
            row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + list(st.session_state.info.values()) + list(a.values()) + [diagnosis, join or "", track or "", ", ".join(symptoms), goal or "", notes or ""]
            try:
                sheet.append_row(row)
                st.success("✅ Saved! We'll be in touch soon 💌")
            except:
                st.error("❌ Failed to save. Try again.")
        else:
            st.error("Spreadsheet not connected.")
        st.session_state.clear()
        st.rerun()
