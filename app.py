import streamlit as st
import utils

# ==============================================================================
# SEITEN-KONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Creator Command Center 2026",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# GLOBALES 2026 DESIGN SYSTEM (Midnight Navy)
# ==============================================================================
PRIMARY_BLUE = "#38BDF8"
BG_DEEP_NAVY = "#0F172A"
SIDEBAR_NAVY = "#1E293B"
TEXT_SLATE = "#F8FAFC"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght=300;400;700&family=Inter:wght=400;600&display=swap');
    html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT_SLATE} !important; }}
    .stApp {{ background-color: {BG_DEEP_NAVY} !important; }}
    h1, h2, h3 {{ font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: #FFFFFF !important; }}
    
    /* Bento Box Design */
    .bento-card {{ 
        background-color: rgba(30, 41, 59, 0.4) !important; 
        border-radius: 16px !important; 
        border: 1px solid rgba(255, 255, 255, 0.08) !important; 
        padding: 24px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        margin-bottom: 16px;
    }}
    
    .stButton>button {{ border-radius: 10px !important; background-color: {SIDEBAR_NAVY} !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; font-family: 'Outfit', sans-serif !important; }}
    .stButton>button:hover {{ border-color: {PRIMARY_BLUE} !important; box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important; }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important; border: none !important; }}
    .stTextInput>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR_NAVY} !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: {TEXT_SLATE} !important; }}
    
    /* Tabs für Login/Registrierung */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px !important; }}
    .stTabs [data-baseweb="tab"] {{ background-color: rgba(30, 41, 59, 0.5) !important; border-radius: 8px 8px 0 0 !important; padding: 10px 20px !important; color: #94A3B8 !important; }}
    .stTabs [aria-selected="true"] {{ background-color: {PRIMARY_BLUE} !important; color: {BG_DEEP_NAVY} !important; font-weight: 600 !important; }}
</style>
""", unsafe_allow_html=True)

# Session State initialisieren
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# ==============================================================================
# AUTHENTIFIZIERUNG (LOGIN / REGISTER)
# ==============================================================================
if not st.session_state["logged_in"]:
    st.title("🚀 Creator Command Center")
    st.markdown("Willkommen im intelligenten Dashboard für Content Creator & Streamer. Bitte logge dich ein oder erstelle ein Konto.")
    
    tab_login, tab_register = st.tabs(["🔒 Einloggen", "📝 Registrieren"])
    
    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Benutzername")
            password = st.text_input("Passwort", type="password")
            submit = st.form_submit_button("Anmelden", type="primary", use_container_width=True)
            
            if submit:
                if username and password:
                    hashed_pw = utils.hash_password(password)
                    try:
                        conn = utils.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_pw))
                        user = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        
                        if user:
                            st.session_state["logged_in"] = True
                            st.session_state["username"] = username
                            st.success("Erfolgreich eingeloggt!")
                            st.rerun()
                        else:
                            st.error("❌ Falscher Benutzername oder Passwort.")
                    except Exception as e:
                        st.error(f"Datenbankfehler: {e}")
                else:
                    st.error("⚠️ Bitte alle Felder ausfüllen.")
                    
    with tab_register:
        with st.form("register_form"):
            new_username = st.text_input("Wunsch-Benutzername")
            new_password = st.text_input("Sicheres Passwort", type="password")
            submit_reg = st.form_submit_button("Konto erstellen", use_container_width=True)
            
            if submit_reg:
                if new_username and new_password:
                    hashed_pw = utils.hash_password(new_password)
                    try:
                        conn = utils.get_db_connection()
                        cursor = conn.cursor()
                        
                        # Prüfen ob Nutzer existiert
                        cursor.execute("SELECT username FROM users WHERE username = %s", (new_username,))
                        if cursor.fetchone():
                            st.error("⚠️ Dieser Benutzername ist leider schon vergeben.")
                        else:
                            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (new_username, hashed_pw))
                            st.success("🎉 Konto erfolgreich erstellt! Du kannst dich jetzt im ersten Reiter einloggen.")
                        cursor.close()
                        conn.close()
                    except Exception as e:
                        st.error(f"Datenbankfehler: {e}")
                else:
                    st.error("⚠️ Bitte alle Felder ausfüllen.")
    st.stop()

# ==============================================================================
# DASHBOARD STARTSEITE (WENN EINGELOGGT)
# ==============================================================================
st.title(f"👋 Willkommen zurück, {st.session_state['username']}!")
st.markdown("### 🚀 Deine Creator-Kommandozentrale (Edition 2026)")
st.markdown("---")

st.markdown(f"""
<div class="bento-card">
    <h3 style="margin-top:0; color: #FFFFFF;">✨ Deine neue 2026er Benutzeroberfläche ist nun bereit!</h3>
    <p style="color: #94A3B8; font-size: 16px; line-height: 1.6; margin-bottom: 0;">
        Durch die konsistente Verwendung von modularen Bento-Spalten, modernen Schriftarten und der direkten Cloud-Anbindung an deine Cloud-Datenbank ist dein Tool nun absolut zukunftssicher. Nutze einfach das Menü auf der linken Seite, um schrittweise deine Statistiken, Sendepläne oder Webhooks zu verwalten.
    </p>
</div>
""", unsafe_allow_html=True)

# Übersicht der Module als Bento-Grid
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="bento-card">
        <h4 style="margin-top:0;">📋 Ideen & ToDos</h4>
        <p style="color: #94A3B8; font-size: 14px; margin-bottom:0;">Plane deinen Content, halte Geistesblitze fest und organisiere Checklists für deine Streams.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="bento-card">
        <h4 style="margin-top:0;">📅 Sendeplan</h4>
        <p style="color: #94A3B8; font-size: 14px; margin-bottom:0;">Strukturiere deine Streaming-Woche und verwalte deinen persönlichen Rennkalender.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="bento-card">
        <h4 style="margin-top:0;">📊 Stats & Analytics</h4>
        <p style="color: #94A3B8; font-size: 14px; margin-bottom:0;">Überwache dein Wachstum live per YouTube-API oder halte Meilensteine manuell in Diagrammen fest.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="bento-card">
        <h4 style="margin-top:0;">💬 Chat Befehle</h4>
        <p style="color: #94A3B8; font-size: 14px; margin-bottom:0;">Schneller Zugriff auf deine wichtigsten Chat-Kommandos und Moderatoren-Richtlinien.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="bento-card">
        <h4 style="margin-top:0;">📢 Discord Webhooks</h4>
        <p style="color: #94A3B8; font-size: 14px; margin-bottom:0;">Automatisiere Benachrichtigungen mit optimierten Algorithmus-Vorschauen für Social Media.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="bento-card">
        <h4 style="margin-top:0;">💼 Business Hub</h4>
        <p style="color: #94A3B8; font-size: 14px; margin-bottom:0;">Behalte Kooperationen, Sponsoren-Kontakte und Einnahmen übersichtlich im Griff.</p>
    </div>
    """, unsafe_allow_html=True)

# Logout-Button unten in der Seitenleiste platzieren
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Ausloggen", use_container_width=True):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.rerun()