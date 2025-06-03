import streamlit as st

st.set_page_config(page_title="InBalance Hormonal Quiz", layout="centered")

st.title("🩺 Is Your Hormonal Health in Balance?")
st.markdown("Answer a few quick questions to discover your hormonal profile.")

# Collect user answers
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

if st.button("🔍 Show My Result"):
    # Scoring logic
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

    # Determine diagnosis
    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        result = "🌀 PCOS-like Pattern"
        message = "Your answers point to a hormonal pattern often linked to PCOS, including irregular cycles, androgen symptoms, and metabolic imbalance."
    elif CA >= 20 and HYPRA >= 20:
        result = "⚠️ Hyperandrogenism + Irregular Cycles"
        message = "You may be dealing with excess androgens and ovulatory dysfunction — patterns often missed in basic checkups."
    elif HYPRA >= 20 and PCOMIR >= 10:
        result = "⚖️ Hormonal + Metabolic Imbalance"
        message = "Your profile shows possible androgen excess and insulin resistance — this may appear as acne, cravings, or stubborn weight."
    elif PCOMIR >= 10:
        result = "🔻 Insulin Resistance / Metabolic Disruption"
        message = "You’re showing signs of metabolic disruption, which often affects hormones too. Early support can make a big difference."
    elif CA >= 20:
        result = "🔄 Irregular Cycles / Anovulation"
        message = "Your cycle history suggests ovulatory disruption — one of the earliest signs of hormonal imbalance."
    else:
        result = "✅ No Strong Signs of Hormonal Imbalance"
        message = "No major signs right now, but continue tracking your symptoms. Hormones shift with age, stress, and lifestyle."

    # Display result
    st.subheader(result)
    st.success(message)
    st.markdown("💡 *Want to go further? Join the InBalance waitlist for expert support and smarter tracking.*")
    st.markdown("[📲 Tap here to join the waitlist](https://yourlinktree.com)")

