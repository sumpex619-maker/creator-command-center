import streamlit as st
import utils

st.set_page_config(page_title="Creator Command Center", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# ==============================================================================
# LOGIN-PRÜFUNG
# ==============================================================================
if not st.session_state["logged_in"]:
    st.title("🔒 Creator Command Center")
    st.write("Bitte melde dich an oder erstelle einen neuen Account.")
    
    col_login, _ = st.columns([1, 2])
    with col_login:
        tab_login, tab_register = st.tabs(["🔑 Anmelden", "📝 Registrieren"])
        
        conn = utils.get_db_connection()
        cursor = conn.cursor()
        
        with tab_login:
            user_login = st.text_input("Benutzername", key="login_user")
            pwd_login = st.text_input("Passwort", type="password", key="login_pwd")
            if st.button("Einloggen", type="primary", use_container_width=True):
                cursor.execute("SELECT password FROM users WHERE username = %s", (user_login,))
                row = cursor.fetchone()
                
                if row and row["password"] == utils.hash_password(pwd_login):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user_login
                    st.rerun()
                else:
                    st.error("❌ Benutzername oder Passwort falsch.")
                    
        with tab_register:
            user_reg = st.text_input("Wunsch-Benutzername", key="reg_user")
            pwd_reg = st.text_input("Passwort wählen", type="password", key="reg_pwd")
            if st.button("Account erstellen", use_container_width=True):
                if user_reg and pwd_reg:
                    cursor.execute("SELECT username FROM users WHERE username = %s", (user_reg,))
                    if cursor.fetchone():
                        st.error("❌ Dieser Benutzername ist leider schon vergeben.")
                    else:
                        hashed_pwd = utils.hash_password(pwd_reg)
                        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user_reg, hashed_pwd))
                        conn.commit()
                        st.success("✅ Account erfolgreich erstellt! Du kannst dich jetzt einloggen.")
                else:
                    st.warning("⚠️ Bitte fülle alle Felder aus.")
                    
        cursor.close()
        conn.close()
    
    st.stop()  # Zwingt Streamlit hier anzuhalten, wenn der User nicht eingeloggt ist!

# ==============================================================================
# AB HIER: BEREICH FÜR EINGELOGGTE NUTZER (Kein Einrücken nötig!)
# ==============================================================================
current_user = st.session_state["username"]

# --------------------------------------------------------------------------
# DESIGN & CUSTOM STYLING (Theme-Engine)
# --------------------------------------------------------------------------
user_settings = utils.load_user_settings(current_user)
theme_choice = user_settings.get("theme", "Dark")
accent_choice = user_settings.get("accent", "Karibik Türkis")

active_color_hex = utils.THEME_COLORS.get(accent_choice, "#46A5B8")

if theme_choice == "Dark":
    bg_color = "#121212"
    sidebar_bg = "#1E1E1E"
    text_color = "#FFFFFF"
else:
    bg_color = "#FFFFFF"
    sidebar_bg = "#F4F6F7"
    text_color = "#111111"
    
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; }}
    h1, h2, h3, h4, h5, h6, label, li, div[data-testid="stMarkdownContainer"] {{ color: {text_color} !important; }}
    .stButton>button[kind="primary"] {{ background-color: {active_color_hex} !important; border: 1px solid {active_color_hex} !important; color: #FFFFFF !important; }}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# STARTSEITE & ANLEITUNG
# --------------------------------------------------------------------------
st.title("🎬 Creator Command Center")
st.markdown(f"**Eingeloggt als:** `{current_user}`")

with st.expander("📖 Kurzanleitung: So nutzt du das Tool", expanded=True):
    st.markdown(f"""
    Willkommen in deiner Kommandozentrale! Hier sind die ersten Schritte:
    
    1. **Discord-Webhooks:** Gehe in der Seitenleiste auf `📢_Discord_Webhooks` und lege dort dein erstes Webhook-Profil an (URL aus den Discord-Kanaleinstellungen kopieren).
    
    2. **Sendeplan:** Unter `📅_Sendeplan` kannst du deine Woche strukturieren und deine Community per Mausklick automatisch über Discord informieren.
    
    3. **Stats-Tracking:** Nutze das Tool `📊_Stats`, um deine Social-Media-Zahlen manuell zu loggen oder vollautomatisch per YouTube-Schnittstelle abzurufen.
       
       **💡 Anleitung für den automatischen YouTube-Abruf:**
       * **YouTube Channel ID (Kanal-ID):** Logge dich bei YouTube ein und rufe deine erweiterten Kontoeinstellungen unter [youtube.com/account_advanced](https://www.youtube.com/account_advanced) auf. Kopiere dort die ID, die mit **"UC..."** beginnt.
       * **YouTube API Key (API-Schlüssel):** Melde dich in der kostenlosen [Google Cloud Console](https://console.cloud.google.com/) an, erstelle ein neues Projekt, suche nach **"YouTube Data API v3"** und aktiviere diese. Unter *Anmeldedaten -> Anmeldedaten erstellen -> API-Schlüssel* erhältst du deinen persönlichen Key.
    
    4. **Ideen:** Unter `📝_Ideen_und_ToDos` verlierst du nie wieder einen kreativen Geistesblitz oder ein wichtiges ToDo.
    
    *Tipp: Du kannst links über die Seitenleiste jederzeit flexibel zwischen allen Funktionen wechseln.*
    """)