import streamlit as st
from PIL import Image
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="InBalance Quiz", layout="centered")

# ---------- LOAD IMAGES ----------
logo = Image.open("logo.png")  # Ensure this file exists in your repo
qr_code = Image.open("qr_code.png")  # Also exists in repo

# ---------- STYLES ----------
st.markdown(
    """
    <style>
        .main { text-align: center; }
        h1, h2, h3 { color: #007C80; }
        .big { font-size: 28px; font-weight: bold; }
        .emoji { font-size: 32px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- LOGO & TITLE ----------
st.image(logo, width=380)
st.markdown("<h1 style='text-align: center;'>InBalance Hormonal Health Quiz</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Take a 1-minute check for <b>hormonal imbalance</b>, <b>PCOS</b> or <b>insulin resistance</b>.</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------- SESSION INITIALIZATION ----------
if "q" not in st.session_state:
    st.session_state.q = 0
    st.session_state.answers = []

# ---------- QUIZ QUESTIONS ----------
questions = [
    {
        "question": "How regular was your menstrual cycle in the past year?",
        "options": [
            ("Does not apply (on hormonal treatment or pregnant)", 0),
            ("Regular (25–35 days)", 1),
            ("Often irregular (<25 or >35 days)", 6),
            ("Rarely got my period (<6 times/year)", 8)
        ],
        "weight": 4,
    },
    {
        "question": "Do you notice excessive thick black hair growth on your face, chest, or back?",
        "options": [
            ("No, not at all", 1),
            ("Yes, noticeable but well-controlled with hair removal", 5),
            ("Yes, major issue, resistant to hair removal", 7),
            ("Yes, with hair thinning/loss on scalp", 8)
        ],
        "weight": 3,
    },
    {
        "question": "Have you had issues with acne or oily skin in the past year?",
        "options": [
            ("No skin issues", 1),
            ("Yes, controlled with treatment", 4),
            ("Yes, frequent despite treatment", 6),
            ("Yes, severe and resistant", 8)
        ],
        "weight": 2.5,
    },
    {
        "question": "Have you experienced weight changes in the past year?",
        "options": [
            ("No, generally stable", 1),
            ("Stable with diet/exercise", 2),
            ("Struggle to control without changes", 5),
            ("Struggle despite diets & workouts", 7)
        ],
        "weight": 2,
    },
    {
        "question": "Do you feel excessively tired or sleepy after meals?",
        "options": [
            ("No, not really", 1),
            ("Sometimes after heavy meals", 2),
            ("Yes, often regardless of food", 4),
            ("Yes, almost daily", 6)
        ],
        "weight": 1,
    }
]

# ---------- DISPLAY CURRENT QUESTION ----------
if st.session_state.q < len(questions):
    q_data = questions[st.session_state.q]
    selected = st.radio(q_data["question"], [opt[0] for opt in q_data["options"]])

    if st.button("Next"):
        for opt_text, opt_value in q_data["options"]:
            if selected == opt_text:
                st.session_state.answers.append((opt_value, q_data["weight"]))
        
        st.markdown("⏳ Loading next question...")
        time.sleep(0.5)
        st.session_state.q += 1
        st.rerun()

# ---------- RESULTS ----------
else:
    st.success("✅ All done! Analyzing your answers…")
    
    # CALCULATE SCORES
    CA = 0  # Anovulation
    HYPRA = 0  # Hyperandrogenism
    PCOMIR = 0  # Insulin Resistance / PCOM

    # Map scores to correct clusters
    for i, (value, weight) in enumerate(st.session_state.answers):
        score = value * weight
        if i == 0:
            CA = score
        elif i == 1:
            HYPRA += value * 4
        elif i == 2:
            HYPRA += value * 3
        elif i == 3:
            PCOMIR += value * 2
        elif i == 4:
            PCOMIR += value * 1

    # DIAGNOSE
    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        result = "HCA-PCO (Possible PCOS)"
    elif CA >= 20 and HYPRA >= 20:
        result = "H-CA (Androgen + Irregular Cycle)"
    elif HYPRA >= 20 and PCOMIR >= 10:
        result = "H-PCO (Androgen + Metabolic)"
    elif CA >= 20 and PCOMIR >= 10:
        result = "PCO-CA (Cycle + Metabolic)"
    else:
        result = "No strong hormonal patterns detected."

    st.markdown(f"<h3 class='big emoji'>🧬 Result: {result}</h3>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h4 class='emoji'>💡 Want expert tracking & care?</h4>", unsafe_allow_html=True)
    st.markdown("👉 [Join the waitlist here](https://linktr.ee/Inbalance.ai)")
    st.image(qr_code, width=380)

    if st.button("🔁 Start Over"):
        st.session_state.q = 0
        st.session_state.answers = []
        st.rerun()
