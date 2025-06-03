import streamlit as st
from PIL import Image

# Must be first
st.set_page_config(page_title="InBalance Quiz", layout="centered")

# Load images (make sure these are in your GitHub repo)
logo = Image.open("logo.png")
qr_code = Image.open("qr_code.png")

# ---------- HEADER SECTION ----------
st.image(logo, width=240)
st.markdown("""
    <h1 style='text-align: center; color: #007C80;'>InBalance Hormonal Health Quiz</h1>
    <p style='text-align: center; font-size: 1.2em;'>
    Take a 1-minute check for <b>hormonal imbalance</b>, <b>PCOS</b>, or <b>insulin resistance</b>.
    </p>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------- QUESTION SET ----------
questions = [
    {
        "question": "How regular was your menstrual cycle in the past year?",
        "options": [
            ("Does not apply (on hormonal treatment or pregnant)", 0),
            ("Regular (25–35 days)", 1),
            ("Often irregular (<25 or >35 days)", 6),
            ("Rarely got my period (<6 times/year)", 8),
        ],
        "weight": 4
    },
    {
        "question": "Do you notice excessive thick black hair growth on your face, chest, or back?",
        "options": [
            ("No, not at all", 1),
            ("Yes, noticeable but well-controlled with hair removal", 5),
            ("Yes, major issue, resistant to hair removal", 7),
            ("Yes, plus scalp thinning/hair-loss", 8),
        ],
        "weight": 3
    },
    {
        "question": "Have you had issues with acne or oily skin in the past year?",
        "options": [
            ("No skin troubles", 1),
            ("Yes, controlled with treatments", 4),
            ("Yes, often despite treatments", 6),
            ("Yes, severe and resistant", 8),
        ],
        "weight": 2.5
    },
    {
        "question": "Have you experienced weight changes in the past year?",
        "options": [
            ("Weight is stable", 1),
            ("Stable with effort", 2),
            ("Struggling to control weight", 5),
            ("Can't lose weight despite effort", 7),
        ],
        "weight": 2
    },
    {
        "question": "Do you feel excessively tired or sleepy after meals?",
        "options": [
            ("No, not really", 1),
            ("Sometimes after heavy meals", 2),
            ("Yes, often regardless of food", 4),
            ("Yes, almost daily", 6),
        ],
        "weight": 1
    }
]

# Session state to track progress
if "q" not in st.session_state:
    st.session_state.q = 0
    st.session_state.answers = []

# ---------- QUIZ FLOW ----------
if st.session_state.q < len(questions):
    q_data = questions[st.session_state.q]
    st.subheader(q_data["question"])
    selected = st.radio("", [opt[0] for opt in q_data["options"]])
    
    if st.button("Next"):
        # Save the numeric value
        for opt_text, opt_value in q_data["options"]:
            if opt_text == selected:
                st.session_state.answers.append(opt_value)
        st.session_state.q += 1
        st.rerun()

# ---------- RESULTS ----------
else:
    st.success("✅ All done! Analyzing your answers…")

    # Get total cluster scores
    scores = st.session_state.answers
    CA = scores[0] * questions[0]["weight"]
    HYPRA = scores[1] * 4 + scores[2] * 3
    PCOMIR = scores[3] * 2 + scores[4] * 1

    # Determine phenotype
    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        result = "HCA-PCO (All 3: Ovulation, Androgen, Metabolic)"
    elif CA >= 20 and HYPRA >= 20:
        result = "H-CA (Ovulation + Androgen)"
    elif HYPRA >= 20 and PCOMIR >= 10:
        result = "H-PCO (Androgen + Metabolic)"
    elif CA >= 20 and PCOMIR >= 10:
        result = "PCO-CA (Ovulation + Metabolic)"
    else:
        result = "No strong hormonal patterns detected."

    # Show result
    st.markdown(f"""
    ### 🧬 <span style='color:#007C80'>**Result: {result}**</span>
    """, unsafe_allow_html=True)

    # CTA + QR
    st.markdown("---")
    st.markdown("### 💡 Want expert tracking & care?")
    st.markdown("👉 [Join the waitlist here](https://linktr.ee/Inbalance.ai)")

    st.image(qr_code, width=200)

    # Reset option
    if st.button("🔁 Start Over"):
        st.session_state.q = 0
        st.session_state.answers = []
        st.rerun()
