# -------------- RESULTS + DIAGNOSIS + INSIGHTS + QR + WAITLIST --------------
if st.session_state.completed:
    st.success("✅ Quiz complete!")

    st.markdown("## 🧬 Your Diagnosis")

    answers = st.session_state.answers
    diagnosis = ""
    summary = ""

    # Flag pattern detection
    patterns = {
        "irregular_cycle": "irregular" in answers[0].lower() or "rarely" in answers[0].lower(),
        "androgen": "hair loss" in answers[1].lower() or "resistant" in answers[1].lower(),
        "acne": "persistent" in answers[2].lower() or "despite" in answers[2].lower(),
        "weight": "can't lose" in answers[3].lower() or "struggling" in answers[3].lower(),
        "fatigue": "tired" in answers[4].lower() or "daily" in answers[4].lower()
    }

    total_flags = sum(patterns.values())

    if total_flags <= 1:
        diagnosis = "No strong hormonal patterns detected"
        summary = "Your cycle and symptoms seem generally balanced. Keep observing changes month-to-month."
    elif total_flags == 2:
        diagnosis = "Ovulatory Imbalance"
        summary = "You may have subtle hormonal fluctuations. These may cause fatigue, breakouts, or missed ovulation."
    elif total_flags in [3, 4]:
        diagnosis = "HCA-PCO (Possible PCOS)"
        summary = "Several symptoms point to a mild PCOS pattern. Consider confirming this with a clinician."
    else:
        diagnosis = "H-PCO (Androgenic + Metabolic Signs)"
        summary = "You show signs of both hormone and metabolic imbalance. A tailored approach is recommended."

    st.markdown(f"### 🔍 **{diagnosis}**")
    st.write(summary)

    # Personalized guidance
    st.markdown("### 🧬 Personalized Results & Guidance")
    insights = []

    if patterns["irregular_cycle"]:
        insights.append("Your cycle seems irregular or infrequent. This could indicate hormonal disruptions or lack of ovulation.")
    if patterns["androgen"]:
        insights.append("You may be experiencing elevated androgens, often linked to PCOS or other imbalances.")
    if patterns["acne"]:
        insights.append("Chronic acne may point to underlying hormone or inflammation issues.")
    if patterns["weight"]:
        insights.append("You might be facing metabolic challenges — especially related to insulin or cortisol.")
    if patterns["fatigue"]:
        insights.append("Post-meal fatigue is often connected to insulin resistance or blood sugar dysregulation.")

    for tip in insights:
        st.write(f"🔹 {tip}")

    # QR Code after insights
    st.markdown("#### 💡 How InBalance Can Help")
    st.info("InBalance helps you track symptoms, cycles, fatigue, skin changes, and more — and our experts use that data to guide your care.")
    st.image("qr_code.png", width=180)

    # Waitlist
    st.markdown("### 💬 Want to join the InBalance app waitlist?")
    waitlist = st.radio("Would you like to join?", ["Yes", "No"], index=None)

    tracking = ""
    symptoms = []
    goal = ""
    notes = ""

    if waitlist == "Yes":
        tracking = st.radio("Do you currently track your cycle or symptoms?", [
            "Yes, with an app", "Yes, manually",
            "No, but I want to", "No, and I don’t know where to start", "Other"
        ], index=None)
        symptoms = st.multiselect("What symptoms do you deal with most often?", [
            "Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating",
            "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"
        ])
        goal = st.radio("What is your main health goal?", [
            "Understand my cycle", "Reduce symptoms", "Looking for diagnosis",
            "Personalized lifestyle plan", "Just curious", "Other"
        ], index=None)
        notes = st.text_area("Anything else you'd like us to know?")

    # Save button
    if st.button("📩 Finish & Save"):
        try:
            if sheet:
                full_phone = st.session_state.country_code.split(" ")[-1] + st.session_state.phone_number
                sheet.append_row([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    st.session_state.first_name,
                    st.session_state.last_name,
                    st.session_state.email,
                    full_phone,
                    *answers,
                    diagnosis,
                    summary,
                    waitlist,
                    tracking,
                    ", ".join(symptoms),
                    goal,
                    notes
                ])
                st.success("✅ Your responses were saved successfully!")
        except Exception as e:
            st.error(f"❌ Could not save to Google Sheets: {e}")
