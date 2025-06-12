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
    st.session_state.recommendations = []

# ── SHEETS SETUP ──
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

# ── DIAGNOSIS ──
def determine_diagnosis(score):
    if score < 25:
        return "No strong hormonal patterns detected"
    elif score < 35:
        return "Possible Ovulatory Imbalance"
    elif score < 45:
        return "Possible Metabolic-Hormonal Imbalance"
    elif score < 55:
        return "H-PCO (Androgenic PCOS)"
    else:
        return "HCA-PCO (Classic PCOS)"

# ── RECOMMENDATIONS MAP ──
recs_map = {
    "Q1": {
        "Does not apply (e.g., pregnancy or hormonal treatment)": "Hormonal treatments or pregnancy can override your cycle — track symptoms instead.",
        "Regular (25–35 days)": "Your cycle is regular — keep tracking phase-based changes.",
        "Often irregular (<25 or >35 days)": "Irregular cycles may suggest hormone shifts — daily tracking can help.",
        "Rarely got period (<6 times/year)": "Infrequent periods might indicate PCOS or low estrogen — consult a provider."
    },
    "Q2": {
        "No": "No excess hair growth noted — a good hormone sign.",
        "Yes, manageable": "Track for any progression in hair growth patterns.",
        "Yes, resistant to removal": "Persistent growth may point to androgen issues — consider labs.",
        "Yes + scalp thinning/hair loss": "Androgen imbalance could be at play — consult a specialist."
    },
    "Q3": {
        "No": "Clear skin suggests low inflammation and balance.",
        "Yes, mild": "Mild acne may track with cycle shifts — log symptoms.",
        "Yes, frequent despite treatment": "Persistent acne often points to hormonal causes — a care plan may help.",
        "Yes, severe/persistent": "Consider a combined approach with hormonal and lifestyle adjustments."
    },
    "Q4": {
        "No, weight is stable": "Stable weight suggests good metabolism — maintain your habits.",
        "Stable only with effort": "Might indicate mild insulin resistance — meal timing can help.",
        "Struggling to maintain": "May reflect metabolic dysregulation — get nutritional support.",
        "Can't lose with diet/exercise": "Could be hormonal or blood sugar related — test and tailor your plan."
    },
    "Q5": {
        "No": "Steady energy after meals — a great sign.",
        "Sometimes": "Minor fatigue post-meals is common — stabilize meals.",
        "Yes, frequently": "Frequent fatigue may suggest sugar swings — log meals and energy.",
        "Yes, daily with low energy": "May signal insulin resistance — aim for balanced meals and movement."
    }
}

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
        p = phonenumbers.parse(f"+{code}{number}")
        return phonenumbers.is_valid_number(p)
    except:
        return False

# ── INTRO ──
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.text_input("First Name", key="fn")
    st.text_input("Last Name", key="ln")
    st.text_input("Email", key="email")
    st.selectbox("Country (optional)", get_countries(), key="country")
    st.text_input("Phone (optional)", key="phone")

    if st.button("Start Quiz"):
        if not st.session_state.fn or not st.session_state.ln or not st.session_state.email:
            st.warning("Please complete name and email.")
        elif not valid_phone(st.session_state.country, st.session_state.phone):
            st.warning("Invalid phone number.")
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
    st.header("📝 Hormonal Health Quiz")
    score = 0
    weights = [4, 3, 2.5, 2, 1]
    st.session_state.recommendations.clear()

    for idx, (qid, qtext, opts) in enumerate(questions):
        st.markdown(f"<b>{qtext}</b>", unsafe_allow_html=True)
        choice = st.radio("", opts, key=qid, index=None, label_visibility="collapsed")
        if choice:
            score += opts.index(choice) * weights[idx]
            st.session_state.answers[qid] = choice
            st.session_state.recommendations.append(recs_map[qid][choice])
        st.markdown("<hr style='margin: 6px 0;'>", unsafe_allow_html=True)

    if st.button("Submit Answers"):
        if any(v is None for v in st.session_state.answers.values()):
            st.warning("Please answer all questions.")
        else:
            st.session_state.total_score = score
            st.session_state.page = "results"
            st.rerun()

# ── RESULTS ──
elif st.session_state.page == "results":
    diagnosis = determine_diagnosis(st.session_state.total_score)
    st.subheader(f"🧬 Diagnosis: {diagnosis}")
    st.markdown("### 📌 Personalized Recommendations")

    for rec in st.session_state.recommendations:
        st.info(rec)

    st.warning("⚠️ This is for informational purposes only. Consult a doctor for medical advice.")
    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🧠 Smart cycle & symptom tracking  
- 🩺 Access to gynecologists, endocrinologists, nutritionists  
- 🧬 Personalized care plans  
- 🔁 Ongoing support  
- 📱 One easy platform
""")
    st.image("qr_code.png", width=240)

    st.markdown("---")
    st.subheader("📥 Join the InBalance Waitlist")
    join = st.radio("Would you like to join?", ["Yes", "No"], key="join_choice", index=None)

    track = symptoms = goal = notes = ""
    if join == "Yes":
        track = st.radio("How do you track symptoms?", ["App", "Manual", "Not yet", "Other"], key="track", index=None)
        symptoms = st.multiselect("Which symptoms affect you most?", [
            "Irregular cycles", "Acne", "Bloating", "Fatigue", "Mood swings",
            "Cravings", "Anxiety", "Brain fog", "Sleep issues"
        ], key="symptoms")
        goal = st.radio("Main health goal?", ["Understand my cycle", "Reduce symptoms", "Get a diagnosis", "Personalized plan", "Other"], key="goal", index=None)
        notes = st.text_area("Any additional info?", key="notes")

    if st.button("📧 Save & Finish"):
        if sheet:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                st.session_state.info.get("First Name", ""),
                st.session_state.info.get("Last Name", ""),
                st.session_state.info.get("Email", ""),
                st.session_state.info.get("Country", ""),
                st.session_state.info.get("Phone", ""),
            ] + [st.session_state.answers.get(q[0], "") for q in questions] + [
                diagnosis,
                join or "",
                track or "",
                ", ".join(symptoms),
                goal or "",
                notes or "",
                " | ".join(st.session_state.recommendations)
            ]
            try:
                sheet.append_row(row)
                st.success("✅ Saved! We’ll be in touch soon 💌")
            except:
                st.error("❌ Save failed. Please try again.")
        else:
            st.error("Google Sheet not connected.")
        st.session_state.clear()
        st.rerun()
