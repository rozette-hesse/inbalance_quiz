import streamlit as st
from PIL import Image

# --------------------- PAGE CONFIG ---------------------
st.set_page_config(page_title="InBalance Quiz", layout="centered")

# --------------------- LOAD IMAGES ---------------------
logo = Image.open("logo.png")
qr_code = Image.open("qr_code.png")

# --------------------- HEADER ---------------------
st.markdown(
    """
    <div style='text-align: center;'>
        <img src='https://raw.githubusercontent.com/rozettesheh/inbalance_quiz/main/Logo-X-2024-01.png' width='160'/>
        <h1 style='color: #008080; font-size: 2.5em;'>InBalance Hormonal Health Quiz</h1>
        <p style='font-size: 1.1em;'>Take a 1-minute check for <strong>hormonal imbalance</strong>, <strong>PCOS</strong> or <strong>insulin resistance</strong>.</p>
    </div>
    """, unsafe_allow_html=True
)

st.markdown("---")

# --------------------- QUESTIONS ---------------------
questions = [
    {
        "question": "🩸 How regular was your menstrual cycle in the past year?",
        "options": [
            ("Does not apply (e.g. on hormonal treatment or pregnant)", 0),
            ("Regular (25–35 days)", 1),
            ("Often irregular (<25 or >35 days)", 6),
            ("Rarely got my period (<6 times/year)", 8),
        ],
        "weight": 4,
        "key": "q1"
    },
    {
        "question": "🧔 Do you notice excessive thick black hair on face, chest, or back?",
        "options": [
            ("No, not at all", 1),
            ("Yes, manageable with hair removal", 5),
            ("Yes, severe and hard to remove", 7),
            ("Yes, and also have scalp hair thinning/loss", 8),
        ],
        "weight": 3,
        "key": "q2"
    },
    {
        "question": "😵‍💫 Have you had acne or oily skin in the past year?",
        "options": [
            ("No skin issues", 1),
            ("Mild, controlled with treatment", 4),
            ("Frequent despite treatment", 6),
            ("Severe and persistent", 8),
        ],
        "weight": 2.5,
        "key": "q3"
    },
    {
        "question": "⚖️ Have you had weight changes in the past year?",
        "options": [
            ("Weight is stable", 1),
            ("Stable with mindful eating/exercise", 2),
            ("Hard to control without effort", 5),
            ("Struggling despite healthy lifestyle", 7),
        ],
        "weight": 2,
        "key": "q4"
    },
    {
        "question": "😴 Do you feel tired/sleepy after meals?",
        "options": [
            ("No, not really", 1),
            ("Sometimes after heavy/sugary meals", 2),
            ("Yes, often", 4),
            ("Yes, almost daily", 6),
        ],
        "weight": 1,
        "key": "q5"
    },
]

# --------------------- SESSION INIT ---------------------
if "q" not in st.session_state:
    st.session_state.q = 0
    st.session_state.answers = []

# --------------------- QUIZ FLOW ---------------------
if st.session_state.q < len(questions):
    q = questions[st.session_state.q]
    st.markdown(f"### {q['question']}")
    selected = st.radio("", [opt[0] for opt in q["options"]], key=q["key"])
    if st.button("Next"):
        score = dict(q["options"])[selected]
        st.session_state.answers.append((score, q["weight"]))
        st.session_state.q += 1
        st.rerun()

else:
    # --------------------- CALCULATE SCORES ---------------------
    st.success("✅ All done! Analyzing your answers…")
    q1_score = st.session_state.answers[0][0] * 4
    q2_score = st.session_state.answers[1][0] * 4
    q3_score = st.session_state.answers[2][0] * 3
    q4_score = st.session_state.answers[3][0] * 2
    q5_score = st.session_state.answers[4][0] * 1

    CA = q1_score
    HYPRA = q2_score + q3_score
    PCOMIR = q4_score + q5_score

    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        result = "HCA-PCO (Possible PCOS)"
    elif CA >= 20 and HYPRA >= 20:
        result = "H-CA (Anovulation + Hyperandrogenism)"
    elif HYPRA >= 20 and PCOMIR >= 10:
        result = "H-PCO (Androgen + Metabolic)"
    elif CA >= 20 and PCOMIR >= 10:
        result = "PCO-CA (Cycle + Metabolic)"
    else:
        result = "No strong hormonal patterns detected."

    st.markdown(f"<h3 style='color: teal;'>🧬 Result: {result}</h3>", unsafe_allow_html=True)

    # --------------------- CALL TO ACTION ---------------------
    st.markdown("---")
    st.markdown("### 💡 Want expert tracking & care?")
    st.markdown("👉 [Join the waitlist here](https://linktr.ee/Inbalance.ai)")
    st.image(qr_code, width=160)

    if st.button("🔁 Start Over"):
        st.session_state.q = 0
        st.session_state.answers = []
        st.rerun()
