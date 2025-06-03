import streamlit as st

st.set_page_config(page_title="InBalance Hormonal Quiz", layout="centered")

# --- STYLES ---
st.markdown("""
    <style>
        h1, h2, h3, .stTextInput label, .stRadio label {
            color: #D12C66;
            font-family: 'Helvetica', sans-serif;
        }
        .stButton>button {
            background-color: #D12C66;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            padding: 0.5em 1em;
        }
        .stButton>button:hover {
            background-color: #b41f53;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.image("https://i.imgur.com/rGcyEhR.png", width=100)  # Replace with your logo if needed
st.markdown("<h1 style='text-align: center;'>InBalance Hormonal Health Quiz</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Your hormones. Your symptoms. Your cycle — in sync.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- QUIZ QUESTIONS ---
cycle = st.radio("1. How regular was your menstrual cycle in the past year?", [
    "Does not apply (on hormonal treatment or pregnant)",
    "Regular (25–35 days)",
    "Often irregular (<25 or >35 days)",
    "Rarely got my period (<6 times/year)"])

hair = st.radio("2. Do you notice thick black hair on your face, chest, or back?", [
    "No",
    "Yes, but well-controlled",
    "Yes, hard to manage",
    "Yes + scalp hair loss"])

acne = st.radio("3. Have you had acne or oily skin in the past year?", [
    "No",
    "Yes, mild",
    "Yes, moderate",
    "Yes, severe and resistant to treatment"])

weight = st.radio("4. Have you experienced weight changes recently?", [
    "No, stable",
    "Stable with effort",
    "Struggling to maintain",
    "Struggling to lose despite effort"])

fatigue = st.radio("5. Do you feel tired or sleepy after meals?", [
    "No",
    "Sometimes after heavy meals",
    "Often regardless of food",
    "Almost daily"])

# --- SUBMIT BUTTON ---
if st.button("🔍 Show My Result"):
    # Scoring dictionaries
    cycle_scores = {
        "Does not apply (on hormonal treatment or pregnant)": 0,
        "Regular (25–35 days)": 1,
        "Often irregular (<25 or >35 days)": 6,
        "Rarely got my period (<6 times/year)": 8
    }
    hair_scores = {"No": 1, "Yes, but well-controlled": 5, "Yes, hard to manage": 7, "Yes + scalp hair loss": 8}
    acne_scores = {"No": 1, "Yes, mild": 4, "Yes, moderate": 6, "Yes, severe and resistant to treatment": 8}
    weight_scores = {"No, stable": 1, "Stable with effort": 2, "Struggling to maintain": 5, "Struggling to lose despite effort": 7}
    fatigue_scores = {"No": 1, "Sometimes after heavy meals": 2, "Often regardless of food": 4, "Almost daily": 6}

    # Calculate cluster scores
    CA = cycle_scores[cycle] * 4
    HYPRA = hair_scores[hair] * 4 + acne_scores[acne] * 3
    PCOMIR = weight_scores[weight] * 2 + fatigue_scores[fatigue]

    # Diagnosis logic
    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        result = "🌀 PCOS-like Pattern"
        message = "Your answers suggest a hormonal pattern often seen in PCOS: irregular cycles, androgen symptoms, and metabolic imbalance."
    elif CA >= 20 and HYPRA >= 20:
        result = "⚠️ Hyperandrogenism + Irregular Cycles"
        message = "You may be dealing with excess androgens and ovulatory disruption — signs often missed in basic checkups."
    elif HYPRA >= 20 and PCOMIR >= 10:
        result = "⚖️ Hormonal + Metabolic Imbalance"
        message = "This profile may reflect elevated androgens with insulin resistance — common in acne, cravings, and stubborn weight."
    elif PCOMIR >= 10:
        result = "🔻 Metabolic Imbalance / Insulin Resistance"
        message = "You show signs of metabolic disruption, which may be influencing your hormones and energy."
    elif CA >= 20:
        result = "🔄 Irregular Cycles / Anovulation"
        message = "Your cycle pattern suggests ovulatory irregularity — a key early sign of hormonal imbalance."
    else:
        result = "✅ No Strong Indicators of Hormonal Imbalance"
        message = "Your responses don’t point to significant hormonal issues right now, but continue to track for changes."

    # Display result
    st.markdown(f"<h2 style='color:#D12C66'>{result}</h2>", unsafe_allow_html=True)
    st.success(message)

    st.markdown("---")
    st.markdown("💡 Want smarter tracking + expert support? Join the InBalance waitlist below!")
    st.markdown("[📲 Tap here to join the waitlist](https://linktr.ee/Inbalance.ai)")

    # QR code
    st.image("https://i.imgur.com/61X1h0K.png", width=150, caption="Scan to Join the Waitlist")  # Use your QR image URL here
