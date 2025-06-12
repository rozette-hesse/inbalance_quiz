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

# ── GOOGLE SHEETS SETUP ──
try:
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# ── QUESTIONS & WEIGHTS ──
questions = [
    ("Q1","How regular was your menstrual cycle in the past year?",[
        "Does not apply (e.g., pregnancy or hormonal treatment)",
        "Regular (25–35 days)",
        "Often irregular (<25 or >35 days)",
        "Rarely got period (<6 times/year)"
    ]),
    ("Q2","Do you notice thick black hair on your face, chest, or back?",[
        "No",
        "Yes, manageable",
        "Yes, resistant to removal",
        "Yes + scalp thinning/hair loss"
    ]),
    ("Q3","Did you have acne or oily skin this year?",[
        "No",
        "Yes, mild",
        "Yes, frequent despite treatment",
        "Yes, severe/persistent"
    ]),
    ("Q4","Have you experienced persistent weight gain or difficulty losing weight?",[
        "No, weight is stable",
        "Stable only with effort",
        "Struggling to maintain",
        "Can't lose with diet/exercise"
    ]),
    ("Q5","Do you feel tired or drowsy after meals?",[
        "No",
        "Sometimes",
        "Yes, frequently",
        "Yes, daily with low energy"
    ]),
]
weights = [4,3,2.5,2,1]

# ── DIAGNOSIS & RECOMMENDATIONS ──
def determine_diagnosis(total):
    if total < 25:
        return "No strong hormonal patterns detected"
    if total < 35:
        return "Possible Ovulatory Imbalance"
    if total < 45:
        return "Possible Metabolic‑Hormonal Imbalance"
    if total < 55:
        return "H‑PCO (Androgenic PCOS)"
    return "HCA‑PCO (Classic PCOS)"

recs_map = {
    "Q1": {
        questions[0][2][0]: "Track symptoms—hormonal treatments/pregnancy can mask cycle data.",
        questions[0][2][1]: "Great—your cycle is regular. Keep tracking phases.",
        questions[0][2][2]: "Irregular cycles suggest ovulatory issues—daily logging helps.",
        questions[0][2][3]: "Infrequent periods may signal low estrogen or PCOS—hormone testing is advised."
    },
    "Q2": {
        questions[1][2][0]: "No excess hair is positive—supports healthy androgen balance.",
        questions[1][2][1]: "Mild hair growth is normal—monitor for changes.",
        questions[1][2][2]: "Resistant hair may indicate high androgens—consider endocrine consult.",
        questions[1][2][3]: "Body hair with thinning may signal hormone imbalance—seek specialist advice."
    },
    "Q3": {
        questions[2][2][0]: "Clear skin is a great sign of balanced hormones.",
        questions[2][2][1]: "Mild acne is common—track when it occurs.",
        questions[2][2][2]: "Persistent acne can reflect hormonal imbalance—consider a care plan.",
        questions[2][2][3]: "Severe acne often needs medical support—talk to a clinician."
    },
    "Q4": {
        questions[3][2][0]: "Stable weight is excellent—keep up healthy habits.",
        questions[3][2][1]: "Effortful balance may indicate mild insulin resistance—support meal planning.",
        questions[3][2][2]: "Difficulty maintaining weight may signal metabolic shifts—nutritional support helps.",
        questions[3][2][3]: "Resistance to weight loss often relates to hormones—consider a metabolic reset plan."
    },
    "Q5": {
        questions[4][2][0]: "No post‑meal fatigue suggests good blood sugar regulation.",
        questions[4][2][1]: "Occasional dips are normal—try protein/fiber pairing.",
        questions[4][2][2]: "Frequent tiredness may signal sugar imbalance—track meals and timing.",
        questions[4][2][3]: "Daily low energy may reflect insulin issues—balanced meals and movement help."
    }
}

# ── UTILITIES ──
def get_countries():
    choices = [""]
    for c in pycountry.countries:
        code = phonenumbers.country_code_for_region(c.alpha_2)
        if not code: continue
        emoji = chr(127397+ord(c.alpha_2[0]))+chr(127397+ord(c.alpha_2[1]))
        choices.append(f"{emoji} {c.name} (+{code})")
    return sorted(choices)

def valid_phone(country, num):
    if not country or not num:
        return True
    try:
        code = int(country.split("(+")[1].split(")")[0])
        return phonenumbers.is_valid_number(phonenumbers.parse(f"+{code}{num}"))
    except:
        return False

# ── PAGE: INTRO ──
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.text_input("First Name", key="fn")
    st.text_input("Last Name", key="ln")
    st.text_input("Email", key="email")
    st.selectbox("Country (optional)", get_countries(), key="country")
    st.text_input("Phone (optional, no spaces)", key="phone")
    if st.button("Start Quiz"):
        if not (st.session_state.fn and st.session_state.ln and st.session_state.email):
            st.warning("Please fill first name, last name, and email.")
        elif not valid_phone(st.session_state.country, st.session_state.phone):
            st.warning("Invalid phone for selected country.")
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

# ── PAGE: QUIZ ──
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    for i,(qid,text,opts) in enumerate(questions):
        st.markdown(f"**{text}**")
        st.session_state.answers[qid] = st.radio("", opts, key=qid, index=None)
        st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Submit Answers"):
        if any(v is None for v in st.session_state.answers.values()):
            st.warning("Please answer every question.")
        else:
            st.session_state.page = "results"
            st.rerun()

# ── PAGE: RESULTS & WAITLIST ──
elif st.session_state.page == "results":
    # Score
    total = sum(weights[i] * questions[i][2].index(st.session_state.answers[questions[i][0]])
                for i in range(len(questions)))
    diagnosis = determine_diagnosis(total)
    st.subheader(f"🧬 Diagnosis: {diagnosis}")
    st.markdown("### 📌 Personalized Recommendations")
    for qid, sel in st.session_state.answers.items():
        st.info(recs_map[qid][sel])
    st.warning("⚠️ Informational only. Consult your physician for medical advice.")
    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🧠 Smart cycle & symptom tracking  
- 🩺 Access to medical experts (gyne, endo, nutrition, fitness)  
- 🧬 Personalized lifestyle & clinical plans  
- 🔁 Ongoing monitoring & adjustments  
- 💬 All in one platform
""")
    st.image("qr_code.png", width=240)
    st.markdown("---")
    st.subheader("📥 Join the InBalance Waitlist")
    join = st.radio("Would you like to join?", ["Yes","No"], key="join", index=None)
    track = symptoms = goal = notes = ""
    if join == "Yes":
        track = st.radio("How do you track symptoms?",["App","Manual","Not yet","Other"], key="track", index=None)
        symptoms = st.multiselect("Which symptoms affect you most?",[
            "Irregular cycles","Acne","Bloating","Fatigue","Mood swings","Cravings","Anxiety","Brain fog","Sleep issues"], key="symptoms")
        goal = st.radio("Main health goal?",["Understand cycle","Reduce symptoms","Get diagnosis","Personalized plan","Other"], key="goal", index=None)
        notes = st.text_area("Additional notes", key="notes")
    if st.button("📧 Save & Finish"):
        if sheet:
            row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + list(st.session_state.info.values())
            row += [st.session_state.answers[q[0]] for q in questions]
            row += [diagnosis, join or "", track or "", ", ".join(symptoms), goal or "", notes or ""]
            sheet.append_row(row)
            st.success("✅ Saved! We'll be in touch 💌")
        else:
            st.error("❌ Couldn't connect. Please try again later.")
        st.session_state.clear()
        st.rerun()
