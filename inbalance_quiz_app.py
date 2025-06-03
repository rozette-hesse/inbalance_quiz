import streamlit as st
from PIL import Image

st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# State initialization
if "q" not in st.session_state:
    st.session_state.q = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# Logo and title
st.image("logo.png", width=140)
st.markdown("""
<h2 style='text-align: center; color: teal;'>InBalance Hormonal Health Quiz</h2>
<p style='text-align: center;'>Explore signs of hormonal imbalance — and how InBalance can help.</p>
""", unsafe_allow_html=True)

# Questions and mapped recommendations
questions = [
    {
        "text": "How regular was your menstrual cycle in the past year?",
        "options": {
            "Does not apply (e.g. pregnant or on hormonal birth control)": None,
            "Regular (25–35 days)": "✅ Your cycle seems balanced. Keep tracking it for changes.",
            "Often irregular (<25 or >35 days)": "🔁 Irregular cycles can suggest ovulatory issues or hormonal imbalance.",
            "Rarely got my period (<6 times/year)": "🚨 Very infrequent periods may signal ovulatory dysfunction or PCOS."
        }
    },
    {
        "text": "Have you experienced excessive hair growth (face, chest, back)?",
        "options": {
            "No, not at all": None,
            "Yes, but managed with removal techniques": "🧔‍♀️ Could be a sign of mild androgen excess.",
            "Yes, and it's hard to control": "⚠️ Persistent hair growth may point to high androgen levels.",
            "Yes, with scalp hair thinning": "🚩 Body + scalp hair changes may signal deeper hormonal imbalances."
        }
    },
    {
        "text": "Have you had acne or oily skin issues recently?",
        "options": {
            "No, my skin is clear": None,
            "Yes, but it’s manageable": "🧴 Mild hormonal acne is common — especially around ovulation.",
            "Yes, it's often persistent": "⚠️ Chronic acne may reflect elevated androgens or inflammation.",
            "Yes, severe and resistant to treatment": "🚨 Severe acne is often tied to hormonal or metabolic dysfunction."
        }
    },
    {
        "text": "Have you struggled with weight changes?",
        "options": {
            "No, stable weight": None,
            "Some changes but manageable": "📉 Slight weight shifts are normal — keep an eye on trends.",
            "Struggling to control weight": "⚠️ Could reflect metabolic slowdown or hormone shifts.",
            "Hard to lose weight despite efforts": "⚖️ Resistance to weight loss may be tied to insulin or cortisol levels."
        }
    },
    {
        "text": "Do you feel unusually tired or sleepy after meals?",
        "options": {
            "No, not really": None,
            "Sometimes after heavy/sugary meals": "🍬 You may be sensitive to sugar spikes — track patterns.",
            "Often, regardless of meals": "⚠️ Frequent post-meal fatigue might reflect blood sugar or insulin issues.",
            "Almost daily, hard to stay alert": "🚨 Persistent energy crashes can indicate insulin resistance."
        }
    }
]

# Simple keyword tagging to define "diagnosis type"
diagnosis_keywords = {
    "Ovulatory Imbalance": ["period", "cycle", "ovulation"],
    "Androgen-Related": ["hair", "acne", "androgen"],
    "Metabolic/Insulin-Related": ["weight", "insulin", "fatigue", "sugar"]
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

# Results screen
else:
    st.success("✅ Here's your personalized feedback:")

    tag_collector = []
    for i, (q_text, choice, feedback) in enumerate(st.session_state.answers):
        st.markdown(f"**Q{i+1}: {q_text}**")
        st.markdown(f"**Your answer:** {choice}")
        if feedback:
            st.markdown(f"🔎 *{feedback}*")
            tag_collector.append(feedback.lower())
        st.markdown("---")

    # Determine diagnosis type
    summary = "No major imbalance detected."
    for dtype, tags in diagnosis_keywords.items():
        if any(tag in " ".join(tag_collector) for tag in tags):
            summary = dtype
            break

    st.markdown(f"""
    <div style='padding: 20px; background-color: #f1fcf9; border-radius: 10px; margin-top: 20px;'>
        <h4 style='color: teal;'>🧠 Likely Hormonal Pattern: <u>{summary}</u></h4>
        <p>This is a general pattern based on your answers. It’s not a diagnosis, but a helpful guide for what to explore next.</p>
    </div>
    """, unsafe_allow_html=True)

    # InBalance Help Section
    st.markdown("""
    <div style='margin-top: 30px; padding: 20px; background-color: #e8f6f6; border-radius: 10px;'>
        <h4 style='color: teal;'>💡 How InBalance Can Help</h4>
        <p>InBalance helps you track symptoms, skin/hair changes, cycle data, fatigue, and weight — all in one app.</p>
        <p>Whether you're trying to understand your symptoms, get a diagnosis, or find expert-backed plans, InBalance guides you every day with personalized insights.</p>
        <p>We're your hormonal health companion.</p>
    </div>
    """, unsafe_allow_html=True)

    # QR Code to Linktree
    st.image("qr_code.png", width=250)
    st.markdown("<p style='text-align: center;'>Scan to follow or join our waitlist 💙</p>", unsafe_allow_html=True)

    # Restart
    st.button("🔁 Start Over", on_click=lambda: st.session_state.clear())
