import streamlit as st
from PIL import Image

# ---------- CONFIGURATION ----------
st.set_page_config(page_title="InBalance Quiz", layout="centered")
st.markdown("""
    <style>
        .big-question {
            font-size: 24px !important;
            font-weight: bold;
        }
        .recommend-box {
            background-color: #f0fdfb;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #d2f4ee;
        }
        .diag-box {
            background-color: #e9f7ef;
            padding: 18px;
            border-left: 5px solid teal;
            margin-top: 20px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- LOGO ----------
logo = Image.open("logo.png")
st.image(logo, use_column_width="auto")

st.markdown("<h2 style='text-align:center; color: teal;'>InBalance Hormonal Health Quiz</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Quick check-in to see if your symptoms might signal a hormonal imbalance.</p>", unsafe_allow_html=True)

# ---------- QUESTIONS ----------
questions = [
    {
        "question": "How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (on hormonal treatment or pregnant)",
            "Regular (25–35 days)",
            "Often irregular (<25 or >35 days)",
            "Rarely got my period (<6 times/year)"
        ]
    },
    {
        "question": "Have you experienced excessive hair growth (face, chest, back)?",
        "options": [
            "No, not at all",
            "Yes, but managed with removal techniques",
            "Yes, and it's hard to control",
            "Yes, plus scalp hair thinning"
        ]
    },
    {
        "question": "Have you had acne or oily skin issues recently?",
        "options": [
            "No",
            "Sometimes around period",
            "Yes, it's often persistent",
            "Yes, severe and cystic"
        ]
    },
    {
        "question": "Do you feel fatigued, gain weight easily, or crave sugar often?",
        "options": [
            "No or rarely",
            "Occasionally",
            "Often",
            "Very frequently"
        ]
    },
    {
        "question": "Have you ever been told you may have PCOS or insulin resistance?",
        "options": [
            "No",
            "Maybe – not confirmed",
            "Yes – suspected",
            "Yes – diagnosed"
        ]
    }
]

# ---------- RECOMMENDATIONS ----------
recommendations = [
    "Irregular or missing periods can be a sign of ovulatory or hormonal imbalance.",
    "Hair growth and scalp hair loss may point toward elevated androgen levels.",
    "Persistent acne or oily skin often reflects inflammation or hormonal shifts.",
    "Fatigue and sugar cravings may suggest blood sugar dysregulation or insulin resistance.",
    "A past diagnosis or suspicion of PCOS or insulin resistance warrants regular monitoring."
]

# ---------- SESSION SETUP ----------
if "answers" not in st.session_state:
    st.session_state.answers = []
if "step" not in st.session_state:
    st.session_state.step = 0

# ---------- DISPLAY QUESTIONS ----------
if st.session_state.step < len(questions):
    q = questions[st.session_state.step]
    st.markdown(f"<div class='big-question'>{q['question']}</div>", unsafe_allow_html=True)
    answer = st.radio("", q["options"], key=f"q{st.session_state.step}")

    if st.button("Next"):
        st.session_state.answers.append(answer)
        st.session_state.step += 1
        st.rerun()

# ---------- DISPLAY RESULTS ----------
else:
    answers = st.session_state.answers

    # ----- Score-based Diagnosis -----
    score = 0
    weights = [0, 1, 2, 3]  # For 4-option questions
    for ans_idx, ans in enumerate(answers):
        score += weights[questions[ans_idx]["options"].index(ans)]

    if score >= 11:
        diagnosis = "HCA-PCO (Possible PCOS)"
    elif score >= 8:
        diagnosis = "H-PCO (Androgen + Metabolic)"
    elif score >= 5:
        diagnosis = "H-IR (Insulin-Resistant Type)"
    else:
        diagnosis = "No strong hormonal patterns detected"

    st.markdown(f"<div class='diag-box'><h4>🧬 Result: {diagnosis}</h4></div>", unsafe_allow_html=True)

    # ----- Personalized Recommendation Summary -----
    st.success("Here's your personalized feedback:")

    recs = []
    for i, ans in enumerate(answers):
        if i == 0 and "irregular" in ans.lower():
            recs.append(recommendations[0])
        if i == 1 and "yes" in ans.lower():
            recs.append(recommendations[1])
        if i == 2 and ("persistent" in ans.lower() or "severe" in ans.lower()):
            recs.append(recommendations[2])
        if i == 3 and ("often" in ans.lower() or "very" in ans.lower()):
            recs.append(recommendations[3])
        if i == 4 and ("yes" in ans.lower()):
            recs.append(recommendations[4])

    if recs:
        st.markdown(f"<div class='recommend-box'><ul>" + "".join([f"<li>{r}</li>" for r in recs]) + "</ul></div>", unsafe_allow_html=True)
    else:
        st.info("Your symptoms seem minimal — keep tracking to stay in tune with your cycle.")

    # ----- InBalance Support -----
    st.markdown("""
        <div class='recommend-box'>
            <h5>💡 How InBalance Can Help</h5>
            InBalance helps you track your symptoms, cycle patterns, skin/hair changes, fatigue, and weight — so our team of experts can guide you toward better hormonal balance.<br><br>
            Whether you need to confirm a diagnosis, adjust your diet, or optimize workouts, we’ve got you covered.
        </div>
    """, unsafe_allow_html=True)

    # QR Code
    qr_code = Image.open("qr_code.png")
    st.image(qr_code, width=180)

    # Restart
    if st.button("🔁 Start Over"):
        st.session_state.answers = []
        st.session_state.step = 0
        st.rerun()
