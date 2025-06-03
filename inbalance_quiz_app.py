import streamlit as st
from PIL import Image

# --- CONFIG ---
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# --- Load images ---
logo = Image.open("logo.png")
qr_code = Image.open("qr_code.png")

st.image(logo,  width=200)

# --- Header ---
st.markdown("<h1 style='text-align: center; color: teal;'>Let’s Understand Your Hormonal Health, Together 💫</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Answer a few quick questions to check for signs of PCOS, hormonal imbalance, or insulin resistance.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Questions ---
questions = [
    {
        "question": "How regular was your menstrual cycle in the past year?",
        "options": [
            ("Does not apply (use of hormonal treatments or pregnancies in the past year)", 0),
            ("Regular most of the time (25–35 days)", 1),
            ("Often irregular (< 25 days or > 35 days)", 6),
            ("I rarely got my period this year (< 6 periods)", 8)
        ]
    },
    {
        "question": "Do you notice excessive thick black hair growth on your face, chest, or back?",
        "options": [
            ("No, not at all.", 1),
            ("Yes, it’s a noticeable issue that is well-controlled with hair removal techniques.", 5),
            ("Yes, it’s a major issue that is resistant to hair removal techniques.", 7),
            ("Yes, excessive hair growth is an issue alongside hair thinning or hair-loss on the scalp", 8)
        ]
    },
    {
        "question": "Have you had issues with acne or oily skin in the past year?",
        "options": [
            ("No, I'm not facing any skin troubles", 1),
            ("Yes, but well controlled with skin treatments", 4),
            ("Yes, often despite regular skin treatments", 6),
            ("Yes, severe and resistant to skin treatments", 8)
        ]
    },
    {
        "question": "Have you experienced weight changes in the past year?",
        "options": [
            ("No, my weight is generally stable.", 1),
            ("No, my weight is more or less stable as long as I work out and eat mindfully.", 2),
            ("Yes, I’m struggling to control my weight without significant changes in diet and/or exercise.", 5),
            ("Yes, I’m struggling to lose weight despite diets and/or regular workouts.", 7)
        ]
    },
    {
        "question": "Do you feel excessively tired or sleepy after meals?",
        "options": [
            ("No, not really.", 1),
            ("Sometimes after heavy or sugary meals.", 2),
            ("Yes, often regardless of what I eat.", 4),
            ("Yes, almost daily with trouble staying alert and awake after meals.", 6)
        ]
    }
]

weights = [4, 3, 2.5, 2, 1]

# --- Session states ---
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
    st.session_state.total_score = 0
    st.session_state.answers = []

# --- Quiz Loop ---
if st.session_state.q_index < len(questions):
    q = questions[st.session_state.q_index]
    st.markdown(f"<h3 style='font-size: 22px; font-weight: bold;'>{q['question']}</h3>", unsafe_allow_html=True)
    selected = st.radio(" ", [opt[0] for opt in q["options"]], index=None)

    if st.button("Next") and selected:
        score = dict(q["options"])[selected]
        st.session_state.total_score += score * weights[st.session_state.q_index]
        st.session_state.answers.append(selected)
        st.session_state.q_index += 1
        st.rerun()

# --- Results ---
else:
    total = st.session_state.total_score
    answers = st.session_state.answers

    if total < 25:
        diagnosis = "No strong hormonal patterns detected"
        detail = "Your symptoms don’t show strong signs of PCOS or major hormonal dysfunction. Keep tracking your cycle and symptoms."
    elif total < 35:
        diagnosis = "Possible Ovulatory Imbalance"
        detail = "Your answers suggest possible ovulatory dysfunction. Cycle tracking and hormonal testing could clarify things."
    elif total < 45:
        diagnosis = "Possible Metabolic-Hormonal Imbalance"
        detail = "You may be experiencing hormonal + metabolic symptoms. Consider lifestyle and lab testing."
    elif total < 55:
        diagnosis = "H-PCO (Androgenic PCOS)"
        detail = "This pattern reflects possible elevated male hormones like testosterone — watch for acne, hair changes, and cycle issues."
    else:
        diagnosis = "HCA-PCO (Classic PCOS)"
        detail = "Your results strongly match classic PCOS symptoms — a medical consult is recommended."

    # --- Result display ---
    st.success("✅ All done! Analyzing your answers…")
    st.markdown(f"<h3 style='color: teal;'>🧬 Result: {diagnosis}</h3>", unsafe_allow_html=True)
    st.write(f"**{detail}**")

    # --- Recommendations (based on selected options only) ---
    recs = []

    if "irregular" in answers[0] or "rarely" in answers[0]:
        recs.append("You may benefit from tracking ovulation and cycle length regularly.")
    if "hair thinning" in answers[1] or "major issue" in answers[1]:
        recs.append("Hair growth changes may signal high androgens — consider lab testing.")
    if "resistant" in answers[2] or "often" in answers[2]:
        recs.append("Persistent acne/oily skin may reflect inflammation or testosterone excess.")
    if "struggling" in answers[3]:
        recs.append("Difficulty losing weight despite effort may signal insulin resistance.")
    if "daily" in answers[4] or "sleepy" in answers[4]:
        recs.append("Post-meal fatigue can point to blood sugar imbalances.")

    # --- Display InBalance section ---
    if recs:
        st.markdown("### 💡 How InBalance Can Help")
        st.info("InBalance helps you track symptoms, cycles, and lifestyle — and supports you with insights.\n\n" +
                "\n".join([f"- {r}" for r in recs]))

    # --- QR + Reset ---
    st.image(qr_code, width=450)
    if st.button("🔁 Start Over"):
        for key in ["q_index", "total_score", "answers"]:
            del st.session_state[key]
        st.rerun()
