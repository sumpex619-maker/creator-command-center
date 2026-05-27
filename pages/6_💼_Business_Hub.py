import streamlit as st
import utils

# ==============================================================================
# 1. PAGE CONFIGURATION (Muss zwingend an allererster Stelle stehen!)
# ==============================================================================
st.set_page_config(
    page_title="Creator Command Center", 
    page_icon="🎬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. 2026 MODERN UI ENGINE (Midnight Navy & Sky Blue)
# ==============================================================================
PRIMARY_BLUE = "#38BDF8"
BG_DEEP_NAVY = "#0F172A"
SIDEBAR_NAVY = "#1E293B"
TEXT_SLATE = "#F8FAFC"

st.markdown(f"""
<style>
    /* Google Fonts laden */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');

    /* Globales Text- & Hintergrund-Styling */
    html, body, [class*="css"], .stMarkdown {{
        font-family: 'Inter', sans-serif !important;
        color: {TEXT_SLATE} !important;
    }}

    .stApp {{ 
        background-color: {BG_DEEP_NAVY} !important; 
    }}

    /* Überschriften im modernisierten Look */
    h1, h2, h3 {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
        color: #FFFFFF !important;
    }}

    /* Linke Navigations-Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_NAVY} !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}

    /* Interaktive Bento-Buttons */
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

    /* Highlight-Button (Blau-Violetter Gradient) */
    .stButton>button[kind="primary"] {{
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important;
        border: none !important;
        color: white !important;
    }}

    /* Bento-Kacheln (Expander) */
    div[data-testid="stExpander"] {{
        background-color: rgba(30, 41, 59, 0.5) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        margin-bottom: 20px !important;
    }}

    /* Formularfelder & Inputs */
    .stDataFrame, .stTextInput>div>div, .stNumberInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{
        border-radius: 10px !important;
        background-color: {SIDEBAR_NAVY} !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: {TEXT_SLATE} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. LOGIN-LOGIK & SESSION-STATE
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# Falls der User NICHT eingeloggt ist, zeigen wir die Login-Maske
if not st.session_state["logged_in"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Zentrierung des Login-Fensters über Spalten (Side-by-Side Prinzip)
    col_space1, col_login_box, col_space2 = st.columns([1, 2, 1])
    
    with col_login_box:
        st.markdown("<h1 style='text-align: center;'>🔒 Command Center</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8;'>Bitte verifiziere dich, um die Systeme zu starten.</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("Benutzername", placeholder="Dein Username")
            pw_input = st.text_input("Passwort", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("🚀 System starten", type="primary", use_container_width=True):
                # 🛠️ HIER DEINE GEWÜNSCHTEN ZUGANGSDATEN EINTRAGEN:
                # Standardmäßig ist hier "Admin" und "1234" eingestellt.
                if user_input == "Admin" and pw_input == "1234":
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user_input
                    st.success("✅ Zugriff gewährt! Initialisiere Dashboard...")
                    st.rerun()
                else:
                    st.error("❌ Falscher Benutzername oder Passwort!")
                    
    # Das Skript stoppt hier, damit unangemeldete User nichts sehen können
    st.stop()

# ==============================================================================
# 4. MAIN DASHBOARD (Sichtbar nach erfolgreichem Login)
# ==============================================================================
current_user = st.session_state["username"]

st.title("🎬 Creator Command Center")
st.markdown(f"**Status:** `System Online` | **Eingeloggt als:** `{current_user}`")

st.markdown("---")

# Kompaktes Side-by-Side Layout für die Zentrale
col_welcome, col_tools = st.columns(2)

with col_welcome:
    st.markdown("### 🚀 Willkommen im Hub!")
    st.markdown("""
    Egal ob du deinen nächsten **Rennplan** strukturierst, das Community-Engagement über **Discord Webhooks** steuerst 
    oder ein neues Video in der SEO-Werkstatt konzipierst – hier läuft alles im modernen 2026-Standard zusammen.
    
    Nutze das linke Seitenmenü, um direkt zu deinen Werkzeugen zu springen.
    """)
    
with col_tools:
    with st.expander("📖 Übersicht: Deine Werkzeuge", expanded=True):
        st.markdown("""
        * **📊 Stats:** Pflege deine Views und dein Community-Health-Board nebeneinander.
        * **📝 Ideen:** Nutze die SEO-Schmiede für bessere Such-Rankings.
        * **💼 Business:** Überprüfe deinen Fortschritt und verwalte Partner-Links.
        * **🤖 Automationen:** Steuere deine Discord-Schnittstellen und Chat-Befehle.
        """)

st.success("✨ Das System ist voll einsatzbereit. Viel Erfolg beim Erstellen deines Contents!")