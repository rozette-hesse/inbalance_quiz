import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIG ---
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# --- SESSION INIT ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "intro",
        "info": {},
        "answers": {},
        "waitlist": {},
        "diagnosis": None,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

# --- GOOGLE SHEETS ---
try:
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except Exception:
    sheet = None

# --- QUESTIONS ---
questions = [
    ("Q1", "How regular was your menstrual cycle in the past year?", [
        "Does not apply (e.g., hormonal treatment or pregnancy)",
        "Regular (25–35 days)",
        "Often irregular (< 25 or > 35 days)",
        "Rarely got period (< 6 times a year)"
    ]),
    ("Q2", "Do you notice thick black hair on your face or body?", [
        "No, not at all",
        "Yes, manageable with removal",
        "Yes, resistant to removal",
        "Yes + scalp thinning or hair loss"
    ]),
    ("Q3", "Have you had acne or oily skin this year?", [
        "No",
        "Yes, mild but manageable",
        "Yes, often despite treatment",
        "Yes, severe and persistent"
    ]),
    ("Q4", "Experienced difficulty losing weight recently?", [
        "No, weight stable",
        "Yes, with effort",
        "Struggling to maintain weight",
        "Can't lose weight despite diet/exercise"
    ]),
    ("Q5", "Do you feel tired or sleepy after meals?", [
        "No",
        "Sometimes after heavy meals",
        "Often, regardless of food",
        "Almost daily with alertness issues"
    ])
]

# --- HELPERS ---
def get_country_choices():
    choices = []
    for c in pycountry.countries:
        code = phonenumbers.country_code_for_region(c.alpha_2)
        if code:
            emoji = chr(127397 + ord(c.alpha_2[0])) + chr(127397 + ord(c.alpha_2[1]))
            choices.append(f"{emoji} {c.name} (+{code})")
    return sorted(set(choices))

def valid_phone(country_str, num):
    try:
        code = country_str.split("(+")[1].split(")")[0]
        parsed = phonenumbers.parse(f"+{code}{num}")
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

def save_to_sheet():
    if not sheet:
        return False
    row = [
        st.session_state.timestamp,
        *st.session_state.info.values(),
        *st.session_state.answers.values(),
        st.session_state.diagnosis or "",
        st.session_state.waitlist.get("join", ""),
        st.session_state.waitlist.get("tracking", ""),
        ", ".join(st.session_state.waitlist.get("symptoms", [])),
        st.session_state.waitlist.get("goal", ""),
        st.session_state.waitlist.get("notes", "")
    ]
    try:
        sheet.append_row(row)
        return True
    except:
        return False

# --- PAGE 1: INTRO ---
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1‑minute quiz to understand your hormonal health — and how InBalance can help.")
    fn = st.text_input("👩‍🦰 First Name")
    ln = st.text_input("👩‍🦰 Last Name")
    email = st.text_input("📧 Email")
    country = st.selectbox("🌍 Country", get_country_choices())
    phone = st.text_input("📱 Phone (no spaces)")  # optional but validated if provided

    if st.button("Start Quiz"):
        if not fn.strip() or not ln.strip() or not email.strip() or not country:
            st.warning("Please complete all required fields.")
        elif phone and not valid_phone(country, phone):
            st.warning("Invalid phone number for that country.")
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

# --- PAGE 2: QUIZ ---
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    for idx, (key, text, opts) in enumerate(questions):
        st.session_state.answers[key] = st.radio(
            f"**{text}**", opts, key=f"q{idx}", index=None
        )
    if st.button("Submit"):
        if len(st.session_state.answers) < len(questions) or any(v is None for v in st.session_state.answers.values()):
            st.warning("Please answer all questions.")
        else:
            # Diagnose
            a = st.session_state.answers
            if "irregular" in a["Q1"]:
                st.session_state.diagnosis = "Cycle Irregularity"
            elif "resistant" in a["Q2"] or "scalp" in a["Q2"]:
                st.session_state.diagnosis = "Potential PCOS"
            elif "Can't lose weight" in a["Q4"]:
                st.session_state.diagnosis = "Hormonal + Metabolic Imbalance"
            else:
                st.session_state.diagnosis = "Mild Hormonal Imbalance"
            save_to_sheet()  # save at results stage
            st.session_state.page = "results"
            st.rerun()

# --- PAGE 3: RESULTS + WAITLIST ---
elif st.session_state.page == "results":
    st.header(f"🧬 Diagnosis: {st.session_state.diagnosis}")
    st.markdown("### ✅ Recommendations based on your answers:")
    recs = []
    ans = st.session_state.answers
    if "irregular" in ans["Q1"]:
        recs.append("Try tracking basal body temperature and cycle symptoms daily to detect ovulation patterns.")
    if "resistant" in ans["Q2"] or "scalp" in ans["Q2"]:
        recs.append("Thick hair or scalp thinning often point to androgen imbalance—our endocrine team can support you.")
    if "persistent" in ans["Q3"] or "oily" in ans["Q3"]:
        recs.append("Oily or acne-prone skin may reflect chronic hormone shifts—clinical skin plan is beneficial.")
    if "weight" in ans["Q4"]:
        recs.append("Difficulty losing weight might signal insulin resistance—custom metabolic plans help.")
    if "sleepy" in ans["Q5"] or "fatigue" in ans["Q5"]:
        recs.append("Post-meal fatigue could be due to blood sugar dips—targeted nutrition helps.")

    for r in recs:
        st.info(r)
    st.warning("⚠️ Informational only. Always consult your physician before making health decisions.")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🧠 Precision symptom & phase tracking tailored to your cycle  
- 📊 Recommendations that align with your current hormonal phase  
- 🩺 Direct access to gynecologists, endocrinologists, nutritionists & trainers  
- 🧬 Personalized, data-backed lifestyle & clinical support  
- 🔁 Ongoing guidance and support as your health evolves
""")
    st.image("qr_code.png", width=140)

    st.subheader("💬 Join the InBalance Waitlist")
    join = st.radio("Would you like to join?", ["Yes", "No"], key="wait_join")
    if join == "Yes":
        st.session_state.waitlist["tracking"] = st.radio(
            "Do you currently track your cycle/symptoms?", 
            ["Yes, with an app", "Yes, manually", "Not yet", "Other"],
            key="wait_track"
        )
        st.session_state.waitlist["symptoms"] = st.multiselect(
            "Top symptoms you face:", 
            ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog"]
        )
        st.session_state.waitlist["goal"] = st.radio(
            "Main health goal:", 
            ["Understand my cycle", "Reduce symptoms", "Get diagnosis", "Personalized plan", "Just curious"],
            key="wait_goal"
        )
        st.session_state.waitlist["notes"] = st.text_area("Other notes you'd like to share:")
    else:
        st.session_state.waitlist.clear()

    if st.button("📩 Save & Finish"):
        st.session_state.waitlist["join"] = join
        ok = save_to_sheet()
        if ok:
            st.success("✅ Your responses have been saved! We'll be in touch 💌")
        else:
            st.error("❌ Could not save to Google Sheet.")
    
    if st.button("🔁 Restart Quiz"):
        for k in st.session_state.keys():
            del st.session_state[k]
        st.rerun()
