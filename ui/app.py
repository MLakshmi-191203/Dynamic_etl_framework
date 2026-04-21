import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# -----------------------
# ⚙️ PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Data Drive",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# 🎨 CUSTOM CSS
# -----------------------
st.markdown("""
<style>

/* ❌ REMOVE DEFAULT */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1f2a37, #0f172a);;
    padding: 20px;
}

/* Title */
.logo-title {
    font-size: 26px;
    font-weight: bold;
    color: white;
}

/* Subtitle */
.logo-sub {
    font-size: 14px;
    color: #9ca3af;
}

/* Navigation label */
.nav-title {
    margin-top: 25px;
    margin-bottom: 10px;
    font-size: 16px;
    color: #cbd5e1;
}

/* Custom button style */
div[data-testid="stButton"] button {
    width: 100%;
    text-align: left;
    border: none;
    padding: 10px;
    border-radius: 10px;
    background: transparent;
    color: white;
    font-size: 17px;
}

/* Hover */
div[data-testid="stButton"] button:hover {
    /*background: rgba(255,255,255,0.08);*/
    background: #535657;
}

/* Active highlight */
.active {
    /*background: rgba(255,255,255,0.1) !important;*/
    background: #9FC3CF !important;
    
}

/* Dot */
.dot {
    height: 10px;
    width: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------
# 🧠 SESSION STATE
# -----------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# -----------------------
# 🎯 SIDEBAR HEADER
# -----------------------
st.sidebar.markdown("""
<div style="display:flex; align-items:center; gap:12px;">
    <div style="font-size:30px;">📊</div>
    <div>
        <div class="logo-title">Data Drive</div>
        <div class="logo-sub">Automate Your Data</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------
# 📌 NAV TITLE
# -----------------------
#st.sidebar.markdown('<div class="nav-title">Navigation</div>', unsafe_allow_html=True)

# -----------------------
# 🚀 CUSTOM NAVIGATION
# -----------------------
menu = ["Home", "Config", "Scheduler", "Ask AI"]
icons = ["🏠", "⚙️", "📅", "🤖"]

for i, item in enumerate(menu):

    is_active = st.session_state.page == item

    # Single column (no dot column)
    if st.sidebar.button(f"{icons[i]}  {item}", key=f"nav_{item}"):
        st.session_state.page = item
        st.rerun()

    # Active highlight
    if is_active:
        st.sidebar.markdown(f"""
            <style>
            button[key="nav_{item}"] {{
                background: rgba(255,255,255,0.1) !important;
                border-radius: 10px !important;
            }}
            </style>
        """, unsafe_allow_html=True)

st.sidebar.markdown("---")


# -----------------------
# 🏠 PAGE ROUTING
# -----------------------
page = st.session_state.page

if page == "Home":
    from my_pages.home import show_home
    show_home()

elif page == "Config":
    from my_pages.config import show_config
    show_config()

elif page == "Scheduler":
    from my_pages.scheduler import show_scheduler
    show_scheduler()

elif page == "Ask AI":
    from my_pages.ask_ai import show_ai
    show_ai()