import streamlit as st
from datetime import datetime
import re

# ----------------- CONFIG -----------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# ----------------- SESSION STATE INIT -----------------
if 'step' not in st.session_state:
    st.session_state.step = 'start'
    st.session_state.answers = []

# ----------------- QUESTIONS -----------------
questions = [
    {
        "q": "How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (e.g., hormonal treatment or pregnancy)",
            "Regular (25–35 days)",
            "Often irregular (< 25 or > 35 days)",
            "Rarely got period (< 6 times a year)"
        ]
    },
    {
        "q": "Do you notice excessive thick black hair on your face, chest, or back?",
        "options": [
            "No, not at all",
            "Yes, manageable with hair removal",
            "Yes, resistant to hair removal",
            "Yes + scalp thinning or hair loss"
        ]
    },
    {
        "q": "Have you had acne or oily skin this year?",
        "options": [
            "No",
            "Yes, mild but manageable",
            "Yes, often despite treatment",
            "Yes, severe and persistent"
        ]
    },
    {
        "q": "Have you experienced weight changes?",
        "options": [
            "No, stable weight",
            "Stable only with effort",
            "Struggling to maintain weight",
            "Can't lose weight despite diet/exercise"
        ]
    },
    {
        "q": "Do you feel tired or sleepy after meals?",
        "options": [
            "No, not really",
            "Sometimes after heavy meals",
            "Yes, often regardless of food",
            "Yes, almost daily with alertness issues"
        ]
    }
]

# ----------------- STEP: START -----------------
if st.session_state.step == 'start':
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to understand your hormonal health — and how InBalance can help.")

    first_name = st.text_input("👩 First Name")
    last_name = st.text_input("👩 Last Name")
    email = st.text_input("📧 Email Address")
    country_code = st.selectbox("🌍 Country Code", ["+961", "+1", "+44", "+49", "+33", "+966", "+971", "+20", "+91"])
    phone_number = st.text_input("📱 Phone Number (without spaces)")

    def is_valid_email(email):
        return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email)

    if st.button("Start Quiz"):
        if not first_name or not last_name:
            st.warning("Please enter your full name.")
        elif not is_valid_email(email):
            st.warning("Enter a valid email address.")
        elif not phone_number.isdigit() or len(phone_number) < 6:
            st.warning("Enter a valid phone number.")
        else:
            st.session_state.first_name = first_name
            st.session_state.last_name = last_name
            st.session_state.email = email
            st.session_state.country_code = country_code
            st.session_state.phone_number = phone_number
            st.session_state.step = 'quiz'
            st.rerun()

# ----------------- STEP: QUIZ -----------------
elif st.session_state.step == 'quiz':
    st.header("📝 Answer All Questions")

    st.session_state.answers = []
    for i, q in enumerate(questions):
        st.markdown(f"**{i+1}. {q['q']}**")
        response = st.radio("", q["options"], key=f"q{i}")
        st.session_state.answers.append(response)

    if st.button("Submit Answers"):
        if None in st.session_state.answers:
            st.warning("Please answer all questions before continuing.")
        else:
            st.session_state.step = 'results'
            st.experimental_rerun()

# ----------------- STEP: RESULTS -----------------
elif st.session_state.step == 'results':
    st.success("✅ Quiz complete!")

    q1, q2, q3, q4, q5 = st.session_state.answers

    # ----------------- DIAGNOSIS -----------------
    if "Rarely" in q1 or "Often irregular" in q1:
        diagnosis = "H-PCO (Hormonal and Metabolic)"
        rec = "- Your cycle seems irregular or infrequent — could indicate hormonal imbalance or missed ovulation.\n- You may also be experiencing insulin resistance or inflammation, especially if weight and fatigue are issues."
    elif "Yes + scalp thinning" in q2:
        diagnosis = "Androgen Dominance"
        rec = "- Excess hair and scalp thinning suggest androgen excess, often tied to PCOS or adrenal patterns."
    elif "Yes, severe and persistent" in q3:
        diagnosis = "Inflammatory Hormonal Imbalance"
        rec = "- Chronic skin issues point to inflammation driven by hormone imbalance, often related to cortisol or insulin."
    elif "Can't lose weight" in q4:
        diagnosis = "Metabolic Imbalance"
        rec = "- Difficulty losing weight despite efforts may signal insulin resistance or thyroid-related issues."
    else:
        diagnosis = "Ovulatory Imbalance"
        rec = "- Subtle symptoms suggest irregular ovulation or mild estrogen-progesterone imbalance."

    st.markdown(f"### 🧬 Diagnosis: **{diagnosis}**")
    st.info(rec)

    st.warning("**Disclaimer:** This quiz is for informational purposes only and does not constitute medical advice. Please consult with a qualified healthcare provider for personalized guidance.")

    # ----------------- INBALANCE SUPPORT -----------------
    st.markdown("### 💡 How InBalance Can Support You")
    st.info("""
At InBalance, we specialize in assisting women with hormonal imbalances, particularly PCOS. Our comprehensive approach includes:

- **Expert Consultations:** Access to gynecologists, endocrinologists, nutritionists, and personal trainers.
- **Personalized Plans:** Tailored lifestyle and treatment plans based on your unique profile.
- **Ongoing Support:** Continuous monitoring and adjustments to ensure optimal health outcomes.

Join our community and take the first step towards hormonal balance.
""")

    # ----------------- WAITLIST -----------------
    st.markdown("### 💬 Want to join the InBalance waitlist?")
    waitlist_opt_in = st.radio("Would you like to join?", ["Yes", "No"], index=1)

    if waitlist_opt_in == "Yes":
        tracking = st.radio("Do you track your cycle/symptoms?", ["Yes, with an app", "Yes, manually", "No, but I want to", "Other"])
        symptoms = st.multiselect("Symptoms you face:", ["Irregular cycles", "Low energy", "Mood swings", "Acne", "Cravings", "Bloating", "Brain fog"])
        goal = st.radio("Your main health goal?", ["Understand my cycle", "Reduce symptoms", "Looking for diagnosis", "Lifestyle plan", "Other"])
        notes = st.text_area("Anything else you'd like to share?")

        if st.button("📩 Finish & Save"):
            # Here you can add code to save the responses to a database or send an email
            st.success("✅ Your information has been saved successfully!")
    else:
        if st.button("📩 Finish"):
            st.success("✅ Thank you for completing the quiz!")

    # ----------------- RESTART -----------------
    if st.button("🔄 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
