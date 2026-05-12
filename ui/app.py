import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# -----------------------
# ⚙️ PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Data Drive | ETL Orchestrator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# 🎨 ENTERPRISE MATTE DESIGN SYSTEM
# -----------------------
bg_image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFo1NaZW7Gcdf7uGKGSVtqmPiv4Kzq8BRva7MbRWEUpTCjLPzFMQhPOd4&s"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap');

    :root {{
        --primary: #9FC3CF;
        --bg-sidebar: linear-gradient(180deg, #020617 0%, #0f172a 100%);
        --bg-matte: rgba(15, 23, 42, 0.92);
        --text-main: #f8fafc;
        --text-sub: #94a3b8;
        --card-bg: rgba(30, 41, 59, 0.45);
        --card-border: rgba(255, 255, 255, 0.05);
        --transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* Mandatory Field Marker (*) */
    div[data-testid="stWidgetLabel"] p span:contains("*") {{
        color: #f87171 !important;
        margin-left: 4px;
    }}

    /* Global Body & Background */
    .stApp, [data-testid="stAppViewContainer"], .main {{
        background: 
            linear-gradient(var(--bg-matte), var(--bg-matte)),
            url("{bg_image_url}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif;
        color: var(--text-main);
    }}

    /* Remove default Streamlit background colors */
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background: transparent !important;
    }}

    /* Advanced Matte Blur Effect */
    [data-testid="stAppViewContainer"] > .main {{
        backdrop-filter: blur(20px) saturate(160%);
    }}

    /* Typography */
    h1, h2, h3, h4 {{
        font-family: 'Manrope', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: #ffffff !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background: var(--bg-sidebar) !important;
        border-right: 1px solid var(--card-border);
    }}

    .logo-title {{
        font-family: 'Manrope', sans-serif;
        font-size: 24px;
        font-weight: 800;
        color: white;
        background: linear-gradient(90deg, #fff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* Sidebar Buttons (Matte) */
    div[data-testid="stSidebar"] button {{
        background: rgba(148, 163, 184, 0.05) !important;
        border: none !important;
        color: #94a3b8 !important;
        padding: 14px 22px !important;
        margin: 6px 0 !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        transition: var(--transition) !important;
        text-align: left !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        border-radius: 10px !important;
    }}

    div[data-testid="stSidebar"] button:hover {{
        color: white !important;
        background: rgba(255, 255, 255, 0.08) !important;
        transform: translateX(3px);
    }}

    /* Component Styling (Premium Matte) */
    .stButton > button {{
        background-color: rgba(30, 41, 59, 0.6) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: var(--transition) !important;
        border: 1px solid var(--card-border) !important;
        padding: 10px 24px !important;
    }}

    .stButton > button:hover {{
        background-color: var(--primary) !important;
        color: #0f172a !important;
        border-color: var(--primary) !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.4);
    }}

    /* Enterprise KPI Cards (Enhanced Readability) */
    .kpi-card {{
        background: rgba(15, 23, 42, 0.8) !important; /* Darker, more solid for contrast */
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-top: 2px solid var(--primary) !important; /* Subtle top highlight */
        border-radius: 20px !important;
        padding: 30px !important;
        transition: var(--transition) !important;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5) !important;
    }}
    .kpi-card:hover {{
        background: rgba(15, 23, 42, 0.95) !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6) !important;
    }}
    .kpi-label {{
        color: #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        margin-bottom: 15px !important;
    }}
    .kpi-value {{
        font-family: 'Manrope', sans-serif !important;
        font-size: 42px !important; /* Even larger */
        font-weight: 800 !important;
        line-height: 1 !important;
        letter-spacing: -1px !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
    }}

    /* Form Labels & Headings (High Visibility White) */
    div[data-testid="stWidgetLabel"] p, 
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stSubheader"] p,
    div[data-testid="stCheckbox"] p,
    div[data-testid="stRadio"] label p,
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stTextInput"] label p,
    label p,
    .stMarkdown h3, 
    .stSubheader p {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        margin-bottom: 12px !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
    }}

    /* Form Fields & Selectboxes */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] {{
        background-color: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: white !important;
        margin-top: 4px !important;
        transition: var(--transition) !important;
    }}

    div[data-testid="stTextInput"] input:focus {{
        border-color: var(--primary) !important;
        background-color: rgba(15, 23, 42, 0.8) !important;
    }}

    /* Dataframe & Tables (Azure Style) */
    div[data-testid="stDataFrame"] {{
        background: rgba(15, 23, 42, 0.4) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 8px !important;
    }}
    div[data-testid="stDataFrame"] [data-testid="stTable"] {{
        color: #f8fafc !important;
    }}

    /* Alerts (Clean & Professional) */
    div[data-testid="stAlert"] {{
        background: rgba(30, 41, 59, 0.8) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: #f8fafc !important;
        padding: 1rem !important;
    }}
    div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {{
        font-weight: 500 !important;
    }}

    /* Tabs (Minimalist) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 28px;
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 55px;
        background-color: transparent !important;
        border-bottom: 2px solid transparent !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: var(--transition) !important;
    }}
    .stTabs [aria-selected="true"] {{
        border-bottom: 2px solid var(--primary) !important;
        color: #ffffff !important;
    }}

    /* Hide Defaults */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
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
<div style="display:flex; align-items:center; gap:12px; padding: 10px 0 30px 0;">
    <div style="font-size:32px;">💎</div>
    <div>
        <div class="logo-title">Data Drive</div>
        <div style="font-size:12px; color:#64748b; font-weight:500; text-transform:uppercase; letter-spacing:1px;">Enterprise ETL</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------
# 🚀 CUSTOM NAVIGATION
# -----------------------
menu = ["Home", "Config", "Metadata", "Run Pipeline", "Scheduler", "Ask AI"]
icons = ["🏠", "⚙️", "🗂️", "🚀", "📅", "🤖"]

# Calculate the active index for CSS targeting
# Logo (1) + 1 = 2 (Home button index)
active_idx = menu.index(st.session_state.page) + 2

# Inject navigation CSS globally to avoid shifting sidebar element indices
st.markdown(f"""
    <style>
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child({active_idx}) button {{
        background: rgba(159, 195, 207, 0.25) !important;
        color: #ffffff !important;
        border-left: 6px solid #9FC3CF !important;
        padding-left: 24px !important;
        font-weight: 700 !important;
        box-shadow: 
            0 10px 20px -5px rgba(0, 0, 0, 0.5) !important,
            inset 0 0 10px rgba(159, 195, 207, 0.1) !important;
        transform: translateX(6px) !important;
        border-radius: 0 14px 14px 0 !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child({active_idx}) button p {{
        color: #ffffff !important;
        font-weight: 700 !important;
    }}
    </style>
""", unsafe_allow_html=True)

for i, item in enumerate(menu):
    if st.sidebar.button(f"{icons[i]}  {item}", key=f"nav_{item}"):
        st.session_state.page = item
        st.rerun()

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

elif page == "Metadata":
    from my_pages.metadata_manager import show_metadata_manager
    show_metadata_manager()

elif page == "Run Pipeline":
    from my_pages.execution import show_execution
    show_execution()

elif page == "Scheduler":
    from my_pages.scheduler import show_scheduler
    show_scheduler()

elif page == "Ask AI":
    from my_pages.ask_ai import show_ai
    show_ai()
# Reload triggered