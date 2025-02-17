import streamlit as st
import requests
import os

# Configure backend URL
BACKEND_URL = "http://localhost:8000/process-email"

# UI Setup
st.title("📧 Email Automation Agent")
st.markdown("Automatically categorize and respond to emails")

with st.form("email_form"):
    sender = st.text_input("From:")
    subject = st.text_input("Subject:")
    body = st.text_area("Email Body:", height=200)
    submitted = st.form_submit_button("Process Email")

if submitted:
    if not all([sender, subject, body]):
        st.error("Please fill all fields")
    else:
        try:
            with st.spinner("Analyzing email..."):
                response = requests.post(
                    BACKEND_URL,
                    json={
                        "sender": sender,
                        "subject": subject,
                        "body": body
                    }
                )

            if response.status_code == 200:
                result = response.json()
                st.success(f"**Category**: {result['category'].title()}")
                if(result['urgency'].title() == "High"):
                    st.warning(f"**Urgency**: {result['urgency'].title()}")
                else:
                    st.info(f"**Urgency**: {result['urgency'].title()}")

                st.subheader("Suggested Response:")
                st.write(result['response'])

                # Add action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📨 Send Response"):
                        # Add actual email sending logic
                        st.success("Response sent!")
                with col2:
                    if st.button("🔄 Regenerate"):
                        st.experimental_rerun()
                with col3:
                    if st.button("📥 Save Draft"):
                        st.info("Draft saved")
            else:
                st.error(f"Error processing email: {response.text}")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")