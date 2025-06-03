import streamlit as st
from PIL import Image

st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# Initialize session state
if "q" not in st.session_state:
    st.session_state.q = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# Branding
st.image("logo.png", width=200)
st.markdown("""
<h2 style='text-align: center; color: teal;'>InBalance Hormonal Health Quiz</h2>
<p style='text-align: center;'>Quick check-in to see if your symptoms might signal a hormonal imbalance.</p>
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
            "Sometimes after heavy/sugary meals": "🍬 You may be sensitive to sugar spikes — consider tracking your response.",
            "Often, regardless of meals": "⚠️ Frequent post-meal fatigue might reflect blood sugar or insulin issues.",
            "Almost daily, hard to stay alert": "🚨 Persistent energy crashes can indicate insulin resistance."
        }
    }
]

# Tag keywords for suggested pattern
diagnosis_keywords = {
    "Ovulatory Imbalance": ["period", "cycle", "ovulation"],
    "Androgen-Related": ["hair", "acne", "androgen"],
    "Metabolic/Insulin-Related": ["weight", "insulin", "fatigue", "sugar"]
}

# Ask questions
q_index = st.session_state.q
if q_index < len(questions):
    q = questions[q_index]
    st.markdown(f"<h4 style='font-size: 22px; font-weight: bold;'>{q['text']}</h4>", unsafe_allow_html=True)
    selected = st.radio("", list(q["options"].keys()), key=f"q{q_index}")
    if st.button("Next"):
        st.session_state.answers.append((q["options"][selected]))
        st.session_state.q += 1
        st.rerun()

# Final screen
else:
    st.success("✅ You're done! Here's what your responses suggest:")

    tag_collector = []
    for i, feedback in enumerate(st.session_state.answers):
        if feedback:
            st.markdown(f"{feedback}")
            tag_collector.append(feedback.lower())
    st.markdown("---")

    # Simple pattern tag
    summary = "No major imbalance detected."
    for tag, keys in diagnosis_keywords.items():
        if any(k in " ".join(tag_collector) for k in keys):
            summary = tag
            break

    st.markdown(f"""
    <div style='padding: 20px; background-color: #f1fcf9; border-radius: 10px; margin-top: 20px;'>
        <h4 style='color: teal;'>🧠 Hormonal Pattern Likely: <u>{summary}</u></h4>
        <p>This is a simplified health pattern based on your answers — not a diagnosis, but a guide to explore further.</p>
    </div>
    """, unsafe_allow_html=True)

    # How InBalance helps
    st.markdown("""
    <div style='margin-top: 30px; padding: 20px; background-color: #e8f6f6; border-radius: 10px;'>
        <h4 style='color: teal;'>💡 How InBalance Can Help</h4>
        <p>InBalance helps you monitor your cycle, symptoms, skin/hair changes, energy and more. We sync this with your cycle phase — giving you clear, daily recommendations.</p>
        <p>Our team of experts can guide you from diagnosis to treatment through the app. Whether it’s PCOS, fatigue, or just cycle confusion — we’re your personalized companion.</p>
    </div>
    """, unsafe_allow_html=True)

    # QR code
    st.image("qr_code.png", width=300)
    st.markdown("<p style='text-align: center;'>Scan to follow us or join the app waitlist 💙</p>", unsafe_allow_html=True)

    # Restart button
    st.button("🔁 Start Over", on_click=lambda: st.session_state.clear())
