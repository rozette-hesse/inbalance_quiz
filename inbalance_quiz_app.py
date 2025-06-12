if st.button("📧 Save & Finish"):
    if sheet:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            st.session_state.info.get("First Name", ""),
            st.session_state.info.get("Last Name", ""),
            st.session_state.info.get("Email", ""),
            st.session_state.info.get("Country", ""),
            st.session_state.info.get("Phone", ""),
        ] + [st.session_state.answers.get(q[0], "") for q in questions] + [
            diagnosis,
            join or "",
            track or "",
            ", ".join(symptoms),
            goal or "",
            notes or "",
            " | ".join(st.session_state.recommendations)
        ]

        try:
            sheet.append_row(row, value_input_option="USER_ENTERED")
            st.success("✅ Saved! We’ll be in touch soon 💌")
        except Exception as e:
            st.error("❌ Save failed. Please try again.")
            st.exception(e)
    else:
        st.error("Google Sheet not connected.")

    st.session_state.clear()
    st.rerun()
