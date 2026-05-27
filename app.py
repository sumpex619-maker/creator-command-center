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
# 2. 2026 MODERN UI ENGINE (Midnight Navy Theme)
# ==============================================================================
PRIMARY_BLUE = "#38BDF8"
BG_DEEP_NAVY = "#0F172A"
SIDEBAR_NAVY = "#1E293B"
TEXT_SLATE = "#F8FAFC"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"], .stMarkdown {{
        font-family: 'Inter', sans-serif !important;
        color: {TEXT_SLATE} !important;
    }}

    .stApp {{ background-color: {BG_DEEP_NAVY} !important; }}

    h1, h2, h3 {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
        color: #FFFFFF !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_NAVY} !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}

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

    .stButton>button[kind="primary"] {{
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important;
        border: none !important;
        color: white !important;
    }}

    div[data-testid="stExpander"] {{
        background-color: rgba(30, 41, 59, 0.5) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        margin-bottom: 20px !important;
    }}

    .stDataFrame, .stTextInput>div>div, .stNumberInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{
        border-radius: 10px !important;
        background-color: {SIDEBAR_NAVY} !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: {TEXT_SLATE} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. ECHTE DATENBANK-LOGIN- & REGISTRIERUNGS-LOGIK
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

if not st.session_state["logged_in"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>🎬 Creator Command Center</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>Erstelle einen Account oder logge dich ein. Deine Daten werden sicher in der Cloud gespeichert.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Side-by-Side Layout: Links Login, Rechts Registrierung
    col_login, col_register = st.columns(2)
    
    # --- LINKS: LOGIN (PRÜFT DIE ECHTE DATENBANK) ---
    with col_login:
        st.markdown("### 🔑 Einloggen")
        with st.form("login_form"):
            user_input = st.text_input("Benutzername", placeholder="Dein Username", key="login_user")
            pw_input = st.text_input("Passwort", type="password", placeholder="••••••••", key="login_pw")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("🚀 System starten", type="primary", use_container_width=True):
                if user_input and pw_input:
                    # Verbindung zur Neon-Datenbank herstellen
                    conn = utils.get_db_connection()
                    cursor = conn.cursor()
                    
                    # Passwort hashen, um es mit der DB zu vergleichen
                    hashed_input_pw = utils.hash_password(pw_input)
                    
                    cursor.execute("SELECT password FROM users WHERE username = %s", (user_input,))
                    user_row = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    
                    if user_row and user_row["password"] == hashed_input_pw:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = user_input
                        st.success("✅ Zugriff gewährt!")
                        st.rerun()
                    else:
                        st.error("❌ Falscher Benutzername oder Passwort!")
                else:
                    st.error("⚠️ Bitte fülle alle Felder aus!")
                    
    # --- RECHTS: REGISTRIERUNG (SCHREIBT IN DIE ECHTE DATENBANK) ---
    with col_register:
        st.markdown("### 📝 Registrieren")
        with st.form("register_form", clear_on_submit=True):
            new_user = st.text_input("Neuer Benutzername", placeholder="Wunsch-Username", key="reg_user")
            new_pw = st.text_input("Neues Passwort", type="password", placeholder="Sicheres Passwort", key="reg_pw")
            new_pw_confirm = st.text_input("Passwort wiederholen", type="password", placeholder="••••••••", key="reg_pw_conf")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾 Account erstellen", use_container_width=True):
                if not new_user or not new_pw:
                    st.error("⚠️ Bitte fülle alle Felder aus!")
                elif new_pw != new_pw_confirm:
                    st.error("❌ Die Passwörter stimmen nicht überein!")
                else:
                    conn = utils.get_db_connection()
                    cursor = conn.cursor()
                    
                    # Prüfen, ob der Username schon vergeben ist
                    cursor.execute("SELECT username FROM users WHERE username = %s", (new_user,))
                    if cursor.fetchone():
                        st.error("⚠️ Dieser Benutzername existiert bereits!")
                        cursor.close()
                        conn.close()
                    else:
                        # Passwort sicher verschlüsseln (Hashen) vor dem Speichern
                        secure_pw = utils.hash_password(new_pw)
                        
                        # In die echte Benutzertabelle eintragen
                        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (new_user, secure_pw))
                        cursor.close()
                        conn.close()
                        
                        st.success("🎉 Account erfolgreich in der Cloud-Datenbank erstellt! Du kannst dich jetzt links einloggen.")
                        
    # Stoppt das Skript für nicht eingeloggte User
    st.stop()

# ==============================================================================
# 4. MAIN DASHBOARD (Sichtbar NACH erfolgreichem Login)
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
    
    Nutze das linke Seitenmenü, um direkt zu deinen Werkzeugen zu springen. Your data is perfectly synced.
    """)
    
with col_tools:
    with st.expander("📖 Übersicht: Deine Werkzeuge", expanded=True):
        st.markdown("""
        * **📊 Stats:** Pflege deine Views und dein Community-Health-Board nebeneinander.
        * **📝 Ideen:** Nutze die SEO-Schmiede für bessere Such-Rankings.
        * **💼 Business:** Überprüfe deinen Fortschritt und verwalte Partner-Links.
        * **🤖 Automationen:** Steuere deine Discord-Schnittstellen und Chat-Befehle.
        """)

st.success("✨ Das System läuft stabil auf der Cloud-Datenbank. Viel Erfolg beim Erstellen deines Contents!")