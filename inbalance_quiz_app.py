import streamlit as st
from PIL import Image

st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# Initialize session state
if "q" not in st.session_state:
    st.session_state.q = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# Load branding
st.image("logo.png", width=140)
st.markdown("""
<h2 style='text-align: center; color: teal;'>InBalance Hormonal Health Quiz</h2>
<p style='text-align: center;'>Check in on signs of <b>hormonal imbalance</b>, <b>PCOS</b>, or <b>insulin resistance</b>.</p>
""", unsafe_allow_html=True)

# Questions with logic
questions = [
    {
        "text": "How regular was your menstrual cycle in the past year?",
        "options": {
            "Does not apply (on hormonal treatment or pregnant)": None,
            "Regular (25–35 days)": "✅ Cycle appears balanced — a healthy sign.",
            "Often irregular (<25 or >35 days)": "🔁 Irregular periods could reflect ovulatory issues or PCOS.",
            "Rarely got my period (<6 times/year)": "🚨 Missing periods may signal ovulatory dysfunction or low hormones."
        }
    },
    {
        "text": "Have you experienced excessive hair growth (face, chest, back)?",
        "options": {
            "No, not at all": None,
            "Yes, but managed with removal techniques": "🧔‍♀️ May be a sign of higher androgen levels.",
            "Yes, and it's hard to control": "⚠️ Uncontrolled hair growth can be linked to androgen excess (like PCOS).",
            "Yes, plus scalp hair thinning": "🚩 Body + scalp hair changes may indicate hormonal imbalance."
        }
    },
    {
        "text": "Have you had acne or oily skin issues recently?",
        "options": {
            "No, my skin is clear": None,
            "Yes, but it’s manageable": "🧴 Mild acne may be connected to hormonal fluctuations.",
            "Yes, it's often persistent": "⚠️ Persistent acne is often a sign of elevated androgens.",
            "Yes, severe and resistant to treatment": "🚨 Severe acne can point to hormonal or insulin-driven issues."
        }
    },
    {
        "text": "Have you struggled with weight changes?",
        "options": {
            "No, stable weight": None,
            "Some changes but manageable": "📉 Slight weight shifts are normal — keep monitoring.",
            "Struggling to control weight": "⚠️ Hard-to-control weight may relate to metabolism or insulin.",
            "Hard to lose weight despite efforts": "⚖️ Weight resistance can be a sign of metabolic or hormonal issues."
        }
    },
    {
        "text": "Do you feel unusually tired or sleepy after meals?",
        "options": {
            "No, not really": None,
            "Sometimes after heavy/sugary meals": "🍬 Sugar sensitivity could be present — consider insulin testing.",
            "Often, regardless of meals": "⚠️ Consistent post-meal fatigue might reflect insulin resistance.",
            "Almost daily, hard to stay alert": "🚨 Daily exhaustion can signal deeper energy regulation problems."
        }
    }
]

# Diagnosis keyword map
diagnosis_keywords = {
    "Androgen-related": ["hair", "acne", "androgen"],
    "Metabolic-related": ["weight", "insulin", "fatigue", "sugar"],
    "Ovulatory-related": ["period", "cycle", "ovulation"],
}

# Show questions
q_index = st.session_state.q
if q_index < len(questions):
    q = questions[q_index]
    selected = st.radio(q["text"], list(q["options"].keys()), key=f"q{q_index}")
    if st.button("Next"):
        st.session_state.answers.append((q["text"], selected, q["options"][selected]))
        st.session_state.q += 1
        st.rerun()
else:
    st.success("✅ You're done! Here's a breakdown of your results:")

    # Collect feedback and diagnosis hints
    diagnosis_tags = []
    all_feedback = []

    for i, (question, choice, feedback) in enumerate(st.session_state.answers):
        st.markdown(f"**Q{i+1}: {question}**")
        st.markdown(f"**Your answer:** {choice}")
        if feedback:
            st.markdown(f"🔎 *{feedback}*")
            all_feedback.append(feedback)
            diagnosis_tags.append(feedback.lower())
        st.markdown("---")

    # Determine diagnosis type
    diagnosis_type = "No major hormonal imbalance detected"
    for d_type, keywords in diagnosis_keywords.items():
        if any(kw in " ".join(diagnosis_tags) for kw in keywords):
            diagnosis_type = d_type.replace("-", " ").title()
            break

    st.markdown(f"""
    <div style='padding: 20px; background-color: #f1fcf9; border-radius: 10px; margin-top: 20px;'>
        <h4 style='color: teal;'>🧠 Summary Diagnosis: <u>{diagnosis_type}</u></h4>
        <p>This is a general indicator based on your answers — not a medical diagnosis.</p>
    </div>
    """, unsafe_allow_html=True)

    # How InBalance Can Help
    st.markdown("""
    <div style='margin-top: 30px; padding: 20px; background-color: #e8f6f6; border-radius: 10px;'>
        <h4 style='color: teal;'>💡 How InBalance Can Help</h4>
        <p>InBalance helps you track symptoms, cycle patterns, skin/hair changes, energy levels, and weight — all in one place.</p>
        <p>Our expert team uses this data to give you personalized insights, care plans, and guidance. Whether you’re exploring PCOS, insulin resistance, or just trying to feel better — we’re here to support you.</p>
    </div>
    """, unsafe_allow_html=True)

    # QR Code
    st.image("qr_code.png", width=180)

    # Restart
    st.button("🔁 Start Over", on_click=lambda: st.session_state.clear())
