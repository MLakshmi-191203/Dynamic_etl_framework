import streamlit as st
import pandas as pd
from db import get_pg_engine

def show_ai():
    # -----------------------
    # 🤖 HEADER
    # -----------------------
    st.title("🤖 AI Pipeline Assistant")
    st.markdown('<p style="color:#94a3b8; margin-top:-20px;">Intelligent diagnostics and SQL assistance for your ETL framework</p>', unsafe_allow_html=True)

    st.markdown("""
        <div style="background:rgba(30, 41, 59, 0.4); border-radius:12px; padding:20px; border:1px solid rgba(255, 255, 255, 0.05); margin-bottom:25px;">
            <p style="color:#94a3b8; font-size:14px; margin:0;">
                Ask questions about your data assets, pipeline status, or request SQL fixes. 
                The assistant uses live metadata to provide context-aware insights.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # -----------------------
    # 💬 CHAT INTERFACE
    # -----------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("How can I help with your data pipelines?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing metadata repository..."):
                # Simulating AI response with metadata context
                # In a real implementation, this would call Gemini/Ollama with retrieved context
                response = f"I've analyzed your metadata. It seems you are asking about '{prompt}'. Currently, your framework has 3 active pipelines and 1 pending schema drift in the 'sales_data' table."
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    # -----------------------
    # 🛠️ QUICK ACTIONS
    # -----------------------
    st.sidebar.markdown("### ⚡ Quick Insights")
    if st.sidebar.button("🔍 Check for Failures"):
        st.toast("Analyzing last 24h of logs...")
    if st.sidebar.button("📈 Performance Summary"):
        st.toast("Calculating average duration...")
    if st.sidebar.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()