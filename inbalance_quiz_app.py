import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# ─── CONFIG ───────────────────────────────────────────────────
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
logo = Image.open("logo.png")
st.image(logo, width=120)

# ─── SESSION INIT ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.answers = {}
    st.session_state.info = {}
    st.session_state.saved = False

# ─── GOOGLE SHEETS SETUP ──────────────────────────────────────
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# ─── DATA ─────────────────────────────────────────────────────
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

def get_countries():
    choices = [""]
    for c in pycountry.countries:
        try:
            code = phonenumbers.country_code_for_region(c.alpha_2)
            emoji = chr(127397 + ord(c.alpha_2[0])) + chr(127397 + ord(c.alpha_2[1]))
            choices.append(f"{emoji} {c.name} (+{code})")
        except:
            continue
    return sorted(choices)

def valid_phone(country, num):
    if not country or not num:
        return True
    try:
        code = int(country.split("(+")[1].split(")")[0])
        p = phonenumbers.parse(f"+{code}{num}")
        return phonenumbers.is_valid_number(p)
    except:
        return False

# ─── INTRO ───────────────────────────────────────────────────
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.text_input("First Name", key="fn")
    st.text_input("Last Name", key="ln")
    st.text_input("Email", key="email")
    st.selectbox("Country (optional)", get_countries(), key="country")
    st.text_input("Phone (no spaces, optional)", key="phone")

    if st.button("Start Quiz"):
        if not st.session_state.fn or not st.session_state.ln or not st.session_state.email:
            st.warning("Please fill in your first name, last name, and email.")
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

# ─── QUIZ ────────────────────────────────────────────────────
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    for idx, (qid, text, opts) in enumerate(questions):
        st.markdown(f"**{text}**")
        st.session_state.answers[qid] = st.radio("", opts, key=qid, index=None)
        st.markdown("---")

    if st.button("Submit Answers"):
        if any(v is None for v in st.session_state.answers.values()):
            st.warning("Please answer every question.")
        else:
            st.session_state.page = "results"
            st.rerun()

# ─── RESULTS & WAITLIST ─────────────────────────────────────
elif st.session_state.page == "results":
    ans = st.session_state.answers
    diagnosis = "Mild Hormonal Imbalance"
    recs = []

    if "irregular" in a["Q1"].lower() or "rarely" in a["Q1"].lower():
        recs.append("🗓️ Your cycle timing varies significantly. Begin daily symptom logging (e.g. basal body temp, cramps, flow changes) to map ovulation and menstrual trends.")
    if "resistant" in a["Q2"].lower() or "scalp" in a["Q2"].lower():
        recs.append("🧬 New or resistant facial/body hair along with thinning may reflect elevated androgen levels. Consider a hormone panel and hair-loss review by a specialist.")
    if "frequent" in a["Q3"].lower() or "persistent" in a["Q3"].lower():
        recs.append("💡 Recurring or treatment-resistant acne often has hormonal roots—ask for a hormonal skin-clearing plan plus nutritional support.")
    if "struggling" in a["Q4"].lower() or "can't" in a["Q4"].lower():
        recs.append("📉 Persistent weight gain despite lifestyle efforts may hint at metabolic imbalance. Tailored nutrition and movement plans can help.")
    if "yes" in a["Q5"].lower():
        recs.append("⚡ Feeling sleepy after meals? A balance of protein, fiber, healthy fats, and post-meal movement can stabilize blood sugar and energy.")

    st.subheader(f"🧬 Diagnosis: {diagnosis}")
    st.markdown("### 📌 Recommendations based on your answers:")
    for r in recs:
        st.info(r)
    st.warning("⚠️ **For informational purposes only—always consult your physician**.")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🧠 Accurate cycle & symptom tracking  
- 🩺 Expert support (gynecologists, endocrinologists, nutritionists, trainers)  
- 📊 Personalized lifestyle & clinical plans  
- 🔄 Continuous monitoring and adjustment  
- 💬 All managed seamlessly in one app
""")

    qr = Image.open("qr_code.png")
    st.image(qr, width=200)

    # Join waitlist
    st.markdown("---")
    st.subheader("📥 Join the InBalance Waitlist")
    join = st.radio("Would you like to join?", ["Yes", "No"], key="join", index=None)

    track = symptoms = goal = notes = ""
    if join == "Yes":
        track = st.radio("Do you track your cycle/symptoms?", ["App-based", "Manual", "Not yet", "Other"], key="track")
        symptoms = st.multiselect("Top symptoms you face:", ["Irregular cycles","Cravings","Low energy","Mood swings","Bloating","Acne","Anxiety","Sleep","Brain fog"], key="symptoms")
        goal = st.radio("Main health goal:", ["Understand my cycle","Reduce symptoms","Get diagnosis","Personalized plan","Just curious"], key="goal")
        notes = st.text_area("Additional notes:", key="notes")

    if st.button("📧 Save & Finish"):
        if sheet:
            row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + list(st.session_state.info.values()) + list(ans.values()) + [diagnosis, join or "", track or "", ", ".join(symptoms), goal or "", notes or ""]
            try:
                sheet.append_row(row)
                st.success("✅ Saved! We'll be in touch soon 💌")
            except:
                st.error("Failed to save. Please try again.")
        else:
            st.error("Spreadsheet not connected.")

        st.session_state.clear()
        st.erun()
