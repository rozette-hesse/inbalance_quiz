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
def determine_diagnosis(answers):
    option_weights = {
        "Q1": {
            "Does not apply (e.g., pregnancy or hormonal treatment)": 0,
            "Regular (25–35 days)": 1,
            "Often irregular (<25 or >35 days)": 6,
            "Rarely got period (<6 times/year)": 8
        },
        "Q2": {
            "No": 1,
            "Yes, manageable": 5,
            "Yes, resistant to removal": 7,
            "Yes + scalp thinning/hair loss": 8
        },
        "Q3": {
            "No": 1,
            "Yes, mild": 4,
            "Yes, frequent despite treatment": 6,
            "Yes, severe/persistent": 8
        },
        "Q4": {
            "No, weight is stable": 1,
            "Stable only with effort": 2,
            "Struggling to maintain": 5,
            "Can't lose with diet/exercise": 7
        },
        "Q5": {
            "No": 1,
            "Sometimes": 2,
            "Yes, frequently": 4,
            "Yes, daily with low energy": 6
        }
    }

    mc = option_weights["Q1"].get(answers["Q1"], 0)
    hair = option_weights["Q2"].get(answers["Q2"], 0)
    acne = option_weights["Q3"].get(answers["Q3"], 0)
    weight = option_weights["Q4"].get(answers["Q4"], 0)
    fatigue = option_weights["Q5"].get(answers["Q5"], 0)

    # Cluster scores
    CA = mc * 4
    HYPRA = hair * 4 + acne * 3
    PCOMIR = weight * 2 + fatigue * 1

    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        return "HCA-PCO (Chronic Anovulation + HyperAndrogenism + PCOM/IR)"
    elif CA >= 20 and HYPRA >= 20 and PCOMIR < 10:
        return "H-CA (Chronic Anovulation + HyperAndrogenism)"
    elif CA < 20 and HYPRA >= 20 and PCOMIR >= 10:
        return "H-PCO (HyperAndrogenism + PCOM/IR)"
    elif CA >= 20 and HYPRA < 20 and PCOMIR >= 10:
        return "PCO-CA (Anovulation + PCOM/IR)"
    else:
        return "No strong hormonal patterns detected"

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
    diagnosis = determine_diagnosis(st.session_state.answers)
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
    all_recs = []
    for qid, sel in st.session_state.answers.items():
        r = recs_map[qid].get(sel)
        if r:
            all_recs.append(r)
            recommendation_text = " | ".join(all_recs)


    
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
            row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"),st.session_state.info.get("First Name", ""),st.session_state.info.get("Last Name", ""),st.session_state.info.get("Email", ""),st.session_state.info.get("Country", ""),st.session_state.info.get("Phone", "")]
            for qid, _, _ in questions:
                row.append(st.session_state.answers.get(qid, ""))

            row.append(diagnosis)
            row.append(join or "")
            row.append(track or "")
            row.append(", ".join(symptoms) if symptoms else "")
            row.append(goal or "")
            row.append(notes or "")

            recommendation_list = []
            for qid, sel in st.session_state.answers.items():
                msg = recs_map.get(qid, {}).get(sel, "")
                if msg:
                    recommendation_list.append(msg)
            row.append(" | ".join(recommendation_list))
            try:
                sheet.append_row(row)
                st.success("✅ Saved! We’ll contact you soon 💌")
            except:
                st.error("❌ Save failed. Please try again.")


        else:
            st.error("Connection Failed")
        st.session_state.clear()
        st.rerun()












        
    
