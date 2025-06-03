# ---------------------- QUIZ FLOW ----------------------

if st.session_state.q_index < len(questions):
    q = questions[st.session_state.q_index]
    st.markdown(f"<h4 style='font-weight: bold;'>{q['question']}</h4>", unsafe_allow_html=True)

    selected = st.radio(" ", [opt[0] for opt in q["options"]], key=f"q_{st.session_state.q_index}")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("⬅️ Back") and st.session_state.q_index > 0:
            st.session_state.q_index -= 1
            if st.session_state.answers:
                st.session_state.answers.pop()
            st.rerun()

    with col2:
        if st.button("Next ➡️"):
            score = next(val for txt, val in q["options"] if txt == selected)
            st.session_state.answers.append(score)
            st.session_state.q_index += 1
            st.rerun()

elif st.session_state.q_index == len(questions):
    st.markdown("**Would you like to join our app waitlist for expert hormonal tracking?**")
    waitlist_choice = st.radio("Join waitlist?", ["Yes", "No"], key="waitlist")

    if waitlist_choice == "Yes":
        # fix: don't assign into session state here
        track_method = st.radio(
            "Do you currently track your cycle or symptoms?",
            ["Yes, with an app", "Yes, manually", "No, but I want to", "No, and I don’t know where to start", "Other"]
        )

        # ✅ fixed multiselect: store value properly, don't assign directly
        symptoms = st.multiselect(
            "What symptoms do you deal with most often?",
            ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"],
            key="symptoms_select"
        )

        goal = st.radio(
            "What is your main health goal right now?",
            ["Understand my cycle", "Reduce symptoms", "Find medical answers", "Create a personalized plan", "Just curious", "Other"]
        )
        extra_notes = st.text_area("Anything else you'd like to share?", key="extra_notes")

        if st.button("Finish Quiz"):
            st.session_state.extra = {
                "Track Method": track_method,
                "Symptoms": ", ".join(symptoms),
                "Goal": goal,
                "Notes": extra_notes
            }
            st.session_state.completed = True
            st.rerun()
