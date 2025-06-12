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

# ── DIAGNOSIS LOGIC ──
def determine_diagnosis(a):
    if ("rarely got period" in a["Q1"].lower() and
        ("resistant" in a["Q2"].lower() or "scalp" in a["Q2"].lower())):
        return "Possible PCOS"
    if "often irregular" in a["Q1"].lower() or "rarely got period" in a["Q1"].lower():
        return "Cycle Irregularity"
    if "can't lose with diet/exercise" in a["Q4"].lower():
        return "Metabolic Imbalance"
    if all(val.startswith(("Does not apply", "Regular", "No")) for val in a.values()):
        return "No Major Hormonal Issues"
    return "Mild Hormonal Imbalance"

# ── RECOMMENDATIONS ──
recs_map = {
    "Q1": {
        "Does not apply (e.g., pregnancy or hormonal treatment)": "🧭 Hormonal treatments/pregnancy override natural cycle — track symptoms to spot trends.",
        "Regular (25–35 days)": "✅ Regular cycle — keep tracking to monitor phase-related symptoms.",
        "Often irregular (<25 or >35 days)": "🗓️ Irregular cycles suggest hormonal fluctuations — daily logging can reveal your pattern.",
        "Rarely got period (<6 times/year)": "📉 Infrequent periods may indicate PCOS or low estrogen — consider evaluating hormone levels."
    },
    "Q2": {
        "No": "✅ No unusual hair growth — a sign of healthy androgen levels.",
        "Yes, manageable": "🔍 Mild hair growth is common; monitor for changes in texture or density.",
        "Yes, resistant to removal": "🧬 Resistant hair growth may signal androgen excess — consider medical evaluation.",
        "Yes + scalp thinning/hair loss": "👩‍⚕️ This pattern can indicate androgen imbalance; a specialist review is advisable."
    },
    "Q3": {
        "No": "✅ Clear skin suggests low inflammation and balanced hormones.",
        "Yes, mild": "💡 Occasional breakouts are normal — track hormone phases for correlation.",
        "Yes, frequent despite treatment": "🧪 Persistent acne often reflects hormonal imbalance — a tailored skin & nutrition plan helps.",
        "Yes, severe/persistent": "📋 Severe acne benefits from a combined hormonal, dietary, and clinical approach."
    },
    "Q4": {
        "No, weight is stable": "✅ Stable weight is a good sign — continue healthy routines.",
        "Stable only with effort": "🍽️ If maintaining takes effort, mild insulin resistance may be present — balance meals carefully.",
        "Struggling to maintain": "⚖️ Difficulty maintaining weight suggests a metabolic shift — consider nutrition guidance.",
        "Can't lose with diet/exercise": "📉 Metabolic resistance often indicates hormonal/blood sugar imbalance — support is key."
    },
    "Q5": {
        "No": "✅ Good energy post-meals — indicates balanced blood sugar.",
        "Sometimes": "🥱 Occasional fatigue is normal — pairing carbs with protein/fiber may help.",
        "Yes, frequently": "⚡ Regular post-meal drowsiness suggests sugar dips — try adjusting meal composition.",
        "Yes, daily with low energy": "🩺 Daily crashes may indicate insulin issues — balanced meals + movement recommended."
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
    st.text_input("Phone (optional, no spaces)", key="phone")

    if st.button("Start Quiz"):
        if not st.session_state.fn or not st.session_state.ln or not st.session_state.email:
            st.warning("Please fill in your first name, last name, and email.")
        elif not valid_phone(st.session_state.country, st.session_state.phone):
            st.warning("Invalid phone number for the selected country.")
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
    for qid, text, opts in questions:
        # Use a single radio line without index to avoid prefill color
        st.markdown(f"<b>{text}</b>", unsafe_allow_html=True)
        st.session_state.answers[qid] = st.radio(
            label="", 
            options=opts, 
            key=qid,
            label_visibility="collapsed",  # Hides label padding
            index=None
        )
        st.markdown("<hr style='margin: 4px 0;'>", unsafe_allow_html=True)

    if st.button("Submit Answers"):
        if any(v is None for v in st.session_state.answers.values()):
            st.warning("Please answer every question.")
        else:
            st.session_state.page = "results"
            st.rerun()

# ── RESULTS & WAITLIST ──
elif st.session_state.page == "results":
    a = st.session_state.answers
    diagnosis = determine_diagnosis(a)

    st.subheader(f"🧬 Diagnosis: {diagnosis}")
    st.markdown("### 📌 Personalized Recommendations")
    has_rec = False
    for qid, sel in a.items():
        rec = recs_map[qid].get(sel)
        if rec:
            st.info(rec)
            has_rec = True
    if not has_rec:
        st.success("🎉 Your responses indicate no major hormonal issues. Continue tracking monthly!")

    st.warning("⚠️ Informational only—consult a physician for medical advice.")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🧠 Smart cycle & symptom tracking  
- 🩺 Access to medical experts  
- 🧬 Personalized lifestyle and clinical plans  
- 🔁 Ongoing support  
- 💬 All in one platform
""")
    st.image("qr_code.png", width=240)

    st.markdown("---")
    st.subheader("📥 Join the InBalance Waitlist")
    join = st.radio("Would you like to join?", ["Yes", "No"], key="join")

    track = symptoms = goal = notes = ""
    
    if join == "Yes":
        track = st.radio("How do you track symptoms?", ["App", "Manual", "Not yet", "Other"], key="track", index=None)
        symptoms = st.multiselect("Which symptoms affect you most?", [
        "Irregular cycles", "Acne", "Bloating", "Fatigue", "Mood swings", "Cravings", "Anxiety", "Brain fog", "Sleep issues"], key="symptoms")
        goal = st.radio("Main health goal?", [ "Understand my cycle", "Reduce symptoms", "Get a diagnosis", 
        "Personalized plan", "Other"], key="goal", index=None)
        notes = st.text_area("Any additional info?", key="notes")




    if st.button("📧 Save & Finish"):
        if sheet:
            
            row = [
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    st.session_state.info.get("First Name", ""),
    st.session_state.info.get("Last Name", ""),
    st.session_state.info.get("Email", ""),
    st.session_state.info.get("Country", ""),
    st.session_state.info.get("Phone", "")
] + [st.session_state.answers.get(q[0], "") for q in questions] + [
    diagnosis, join or "", track or "", ", ".join(symptoms), goal or "", notes or ""
]

            try:
                sheet.append_row(row)
                st.success("✅ Saved! We’ll contact you soon 💌")
            except:
                st.error("❌ Save failed. Please try again.")
        else:
            st.error("Spreadsheet connection failed.")
        st.session_state.clear()
        st.rerun()
