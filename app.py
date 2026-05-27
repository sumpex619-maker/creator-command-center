import streamlit as st
import utils

# ==============================================================================
# PAGE CONFIGURATION (Muss immer ganz oben stehen!)
# ==============================================================================
st.set_page_config(
    page_title="Creator Command Center", 
    page_icon="🎬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2026 MODERN UI ENGINE (Midnight Navy & Sky Blue)
# ==============================================================================
PRIMARY_BLUE = "#38BDF8"
BG_DEEP_NAVY = "#0F172A"
SIDEBAR_NAVY = "#1E293B"
TEXT_SLATE = "#F8FAFC"

st.markdown(f"""
<style>
    /* 1. Google Fonts laden */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');

    /* 2. Globales Styling */
    html, body, [class*="css"], .stMarkdown {{
        font-family: 'Inter', sans-serif !important;
        color: {TEXT_SLATE} !important;
    }}

    /* Haupt-Hintergrund */
    .stApp {{ 
        background-color: {BG_DEEP_NAVY} !important; 
    }}

    /* Überschriften in moderner Outfit-Schrift */
    h1, h2, h3 {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
        color: #FFFFFF !important;
    }}

    /* 3. Sidebar (Linke Navigation) */
    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_NAVY} !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}

    /* 4. Interaktive Buttons */
    .stButton>button {{
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background-color: {SIDEBAR_NAVY} !important;
        color: white !important;
        padding: 10px 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-family: 'Outfit', sans-serif !important;
    }}

    .stButton>button:hover {{
        border-color: {PRIMARY_BLUE} !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;
        transform: translateY(-2px) !important;
    }}

    /* Primär-Button (Das leuchtende Blau) */
    .stButton>button[kind="primary"] {{
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important;
        border: none !important;
        color: white !important;
    }}

    /* 5. Boxen & Kacheln (Bento-Look) */
    div[data-testid="stExpander"] {{
        background-color: rgba(30, 41, 59, 0.5) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        margin-bottom: 20px !important;
    }}

    /* 6. Formular-Felder & Tabs abrunden */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px !important; background-color: transparent !important; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {SIDEBAR_NAVY} !important; border-radius: 8px 8px 0 0 !important; color: #94A3B8 !important; padding: 10px 20px !important; }}
    .stTabs [aria-selected="true"] {{ background-color: {PRIMARY_BLUE} !important; color: {BG_DEEP_NAVY} !important; font-weight: 700 !important; }}

    .stDataFrame, .stTextInput>div>div, .stNumberInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{
        border-radius: 10px !important;
        background-color: {SIDEBAR_NAVY} !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: {TEXT_SLATE} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# LOGIN / SESSION CHECK
# ==============================================================================
current_user = utils.check_login()

# ==============================================================================
# STARTSEITE / DASHBOARD
# ==============================================================================
st.title("🎬 Creator Command Center")
st.markdown(f"**Status:** `System Online` | **Eingeloggt als:** `{current_user}`")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚀 Willkommen im Hub!")
    st.markdown("Egal ob du deinen nächsten Rennplan strukturierst, das Community-Engagement checkst oder ein neues YouTube-Video konzipierst – hier läuft alles zentral zusammen.")
    
with col2:
    with st.expander("📖 Übersicht: Deine Werkzeuge", expanded=True):
        st.markdown("""
        * **📊 Stats:** Pflege deine Views und dein Community-Health-Board (Side-by-Side).
        * **📝 Ideen:** Nutze die SEO-Werkstatt für bessere Such-Rankings.
        * **💼 Business:** Hake deinen Setup-Fortschritt ab und verwalte deine Partner-Links.
        """)

st.success("✨ Das 2026 Midnight-Theme ist aktiv. Wähle links in der Seitenleiste ein Werkzeug aus!")