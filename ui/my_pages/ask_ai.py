import streamlit as st
from rag.run_rag import ask_question

def show_ai():

    st.markdown("## 🤖 Ask AI")

    # -----------------------
    # 🧠 SESSION STATE (CHAT HISTORY)
    # -----------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # -----------------------
    # 💬 DISPLAY CHAT HISTORY
    # -----------------------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # -----------------------
    # 🧾 INPUT BOX (CHAT STYLE)
    # -----------------------
    user_input = st.chat_input("Ask something about pipelines...")

    if user_input:

        # Save user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Show user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # -----------------------
        # 🤖 AI RESPONSE
        # -----------------------
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_question(user_input)

                st.markdown(answer)

        # Save AI response
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })