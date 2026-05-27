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
# 2. GLOBALES 2026 DESIGN SYSTEM (Midnight Navy & Sky Blue)
# ==============================================================================
PRIMARY_BLUE = "#38BDF8"
BG_DEEP_NAVY = "#0F172A"
SIDEBAR_NAVY = "#1E293B"
TEXT_SLATE = "#F8FAFC"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');

    /* Globales Text- & Hintergrund-Styling */
    html, body, [class*="css"], .stMarkdown {{
        font-family: 'Inter', sans-serif !important;
        color: {TEXT_SLATE} !important;
    }}
    .stApp {{ background-color: {BG_DEEP_NAVY} !important; }}
    
    /* Überschriften */
    h1, h2, h3 {{ 
        font-family: 'Outfit', sans-serif !important; 
        font-weight: 700 !important; 
        color: #FFFFFF !important; 
        letter-spacing: -0.5px !important;
    }}
    
    /* Linke Navigations-Sidebar */
    [data-testid="stSidebar"] {{ 
        background-color: {SIDEBAR_NAVY} !important; 
        border-right: 1px solid rgba(255, 255, 255, 0.05); 
    }}

    /* Bento-Card-Look für Boxen & Expander */
    div[data-testid="stExpander"], .stAlert, div[style*="border"] {{
        background-color: rgba(30, 41, 59, 0.4) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }}

    /* Interaktive Buttons */
    .stButton>button {{
        border-radius: 10px !important;
        background-color: {SIDEBAR_NAVY} !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease;
        font-family: 'Outfit', sans-serif !important;
        padding: 10px 20px !important;
    }}
    .stButton>button:hover {{ 
        border-color: {PRIMARY_BLUE} !important; 
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important; 
        transform: translateY(-1px);
    }}
    .stButton>button[kind="primary"] {{ 
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important; 
        border: none !important; 
    }}

    /* Formularfelder & Inputs */
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div, .stNumberInput>div>div {{ 
        border-radius: 10px !important; 
        background-color: {SIDEBAR_NAVY} !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        color: {TEXT_SLATE} !important;
    }}
    
    /* Tabs (Registerkarten) */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px !important; }}
    .stTabs [data-baseweb="tab"] {{ 
        background-color: rgba(30, 41, 59, 0.5) !important; 
        border-radius: 8px 8px 0 0 !important; 
        padding: 10px 20px !important; 
        color: #94A3B8 !important;
    }}
    .stTabs [aria-selected="true"] {{ 
        background-color: {PRIMARY_BLUE} !important; 
        color: {BG_DEEP_NAVY} !important; 
        font-weight: 600 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. DYNAMISCHE SESSION-STATE LOGIK
# ==============================================================================
if "logged_in" not in st.session_state: 
    st.session_state["logged_in"] = False
if "username" not in st.session_state: 
    st.session_state["username"] = ""

# ==============================================================================
# 4. LOGIN- & REGISTRIERUNGS-OBERFLÄCHE
# ==============================================================================
if not st.session_state["logged_in"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>🎬 Creator Command Center</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 18px;'>Deine Schaltzentrale für Content, Automation & Business.</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Modernes Side-by-Side Layout für Login und Registrierung
    col_login, col_register = st.columns(2)
    
    # --- LINKE SEITE: LOGIN ---
    with col_login:
        st.markdown("### 🔑 System-Login")
        with st.form("login_form"):
            user_input = st.text_input("Benutzername", placeholder="Dein Username", key="l_user")
            pw_input = st.text_input("Passwort", type="password", placeholder="••••••••", key="l_pw")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("🚀 System starten", type="primary", use_container_width=True):
                if user_input and pw_input:
                    conn = utils.get_db_connection()
                    cursor = conn.cursor()
                    
                    # Passwort hashen und in der Neon-Datenbank prüfen
                    hashed_pw = utils.hash_password(pw_input)
                    cursor.execute("SELECT password FROM users WHERE username = %s", (user_input,))
                    row = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    
                    if row and row["password"] == hashed_pw:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = user_input
                        st.success("✅ Zugriff gewährt!")
                        st.rerun()
                    else:
                        st.error("❌ Falscher Benutzername oder Passwort!")
                else:
                    st.error("⚠️ Bitte fülle alle Felder aus!")
                    
    # --- RECHTE SEITE: REGISTRIERUNG ---
    with col_register:
        st.markdown("### 📝 Account erstellen")
        with st.form("register_form", clear_on_submit=True):
            new_user = st.text_input("Wunsch-Benutzername", placeholder="z.B. CreatorXY", key="r_user")
            new_pw = st.text_input("Sicheres Passwort", type="password", placeholder="••••••••", key="r_pw")
            new_pw_confirm = st.text_input("Passwort bestätigen", type="password", placeholder="••••••••", key="r_pw_conf")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾 Registrierung abschließen", use_container_width=True):
                if not new_user or not new_pw:
                    st.error("⚠️ Bitte alle Felder ausfüllen!")
                elif new_pw != new_pw_confirm:
                    st.error("❌ Die Passwörter stimmen nicht überein!")
                else:
                    conn = utils.get_db_connection()
                    cursor = conn.cursor()
                    
                    # Prüfen, ob der Username bereits existiert
                    cursor.execute("SELECT username FROM users WHERE username = %s", (new_user,))
                    if cursor.fetchone():
                        st.error("⚠️ Dieser Benutzername ist leider schon vergeben!")
                        cursor.close()
                        conn.close()
                    else:
                        # User sicher in der Cloud anlegen
                        secure_pw = utils.hash_password(new_pw)
                        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (new_user, secure_pw))
                        cursor.close()
                        conn.close()
                        st.success("🎉 Account erfolgreich in der Cloud gesichert! Logge dich jetzt links ein.")

    # Verhindert, dass nicht eingeloggte Nutzer den Dashboard-Inhalt sehen
    st.stop()

# ==============================================================================
# 5. MAIN DASHBOARD HUB (Sichtbar nach erfolgreichem Login)
# ==============================================================================
current_user = st.session_state["username"]

# Sidebar-Willkommensgruß & Logout
with st.sidebar:
    st.markdown(f"### 👤 Angemeldet als:\n`{current_user}`")
    if st.button("🚪 Abmelden", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

# Hauptseite Überschrift
st.title("🎬 Creator Command Center")
st.markdown(f"**System-Status:** `Online` | Modern 2026 UI Engine")
st.markdown("---")

# Bento-Grid Layout für die Zentrale (Side-by-Side Kacheln)
col_welcome, col_overview = st.columns(2)

with col_welcome:
    st.markdown("### 🚀 Willkommen in deiner Schaltzentrale!")
    st.markdown(f"""
    Hallo **{current_user}**! Alle deine Einstellungen, Anmeldedaten und Inhalte sind sicher mit deiner Cloud-Datenbank synchronisiert. 
    Egal welche Updates wir am Code vornehmen – deine Daten bleiben ab jetzt immer bestehen.
    
    Nutze das **Seitenmenü links**, um nahtlos zwischen deinen Modulen zu wechseln. Jede Unterseite schützt deine Privatsphäre und lädt ausschließlich deine persönlichen Daten.
    """)

with col_overview:
    with st.expander("📖 Modul-Übersicht: Schnellzugriff", expanded=True):
        st.markdown("""
        * **📊 Stats & Health:** Analysiere deine Reichweite und Community-Wachstum.
        * **📝 Ideen & ToDos:** Plane deine nächsten Video-Projekte inklusive SEO-Fokus.
        * **🤖 Discord Webhooks:** Automatisiere Benachrichtigungen direkt auf deinen Server.
        * **🗓️ Sendeplan:** Behalte deine Streamingzeiten und Rennpläne im Griff.
        * **💼 Business Hub:** Verwalte Verträge, Meilensteine und Affiliate-Partnerschaften.
        """)

st.success("✨ Das System läuft fehlerfrei und ist voll einsatzbereit. Viel Erfolg bei deinem Content!")