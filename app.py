import streamlit as st
import utils  # Importiert unsere neue Werkzeugkiste!

st.set_page_config(page_title="Creator Command Center", layout="wide")

# ==============================================================================
# LOGIN & REGISTRIERUNG LOGIK
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

if not st.session_state["logged_in"]:
    st.title("🔒 Creator Command Center")
    st.write("Bitte melde dich an oder erstelle einen neuen Account.")
    
    users_db = utils.load_data(utils.USERS_FILE, dict)
    
    col_login, _ = st.columns([1, 2])
    with col_login:
        tab_login, tab_register = st.tabs(["🔑 Anmelden", "📝 Registrieren"])
        
        with tab_login:
            user_login = st.text_input("Benutzername", key="login_user")
            pwd_login = st.text_input("Passwort", type="password", key="login_pwd")
            if st.button("Einloggen", type="primary", use_container_width=True):
                if user_login in users_db and users_db[user_login] == utils.hash_password(pwd_login):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user_login
                    st.rerun()
                else:
                    st.error("❌ Falscher Benutzername oder Passwort!")
                    
        with tab_register:
            user_reg = st.text_input("Neuer Benutzername", key="reg_user")
            pwd_reg = st.text_input("Neues Passwort", type="password", key="reg_pwd")
            pwd_reg2 = st.text_input("Passwort bestätigen", type="password", key="reg_pwd2")
            if st.button("Konto erstellen", use_container_width=True):
                if not user_reg or not pwd_reg:
                    st.error("⚠️ Bitte alle Felder ausfüllen!")
                elif user_reg in users_db:
                    st.error("⚠️ Dieser Benutzername ist bereits vergeben!")
                elif pwd_reg != pwd_reg2:
                    st.error("⚠️ Die Passwörter stimmen nicht überein!")
                elif len(pwd_reg) < 4:
                    st.error("⚠️ Das Passwort muss mindestens 4 Zeichen lang sein!")
                else:
                    users_db[user_reg] = utils.hash_password(pwd_reg)
                    utils.save_data(utils.USERS_FILE, users_db)
                    st.success("✅ Konto erfolgreich erstellt! Du kannst dich jetzt einloggen.")
    st.stop()

# ==============================================================================
# DESIGN & THEME VERWALTUNG (SEITENLEISTE)
# ==============================================================================
current_user = st.session_state["username"]
settings_db = utils.load_data(utils.SETTINGS_FILE, dict)

if current_user not in settings_db:
    settings_db[current_user] = {"theme": "Dark", "accent": "Pastell Ozean (Blau)"}

with st.sidebar:
    st.header("🎨 Design anpassen")
    current_theme = settings_db[current_user]["theme"]
    current_accent = settings_db[current_user]["accent"]
    
    selected_theme = st.radio("Modus:", ["Dark", "Light"], index=0 if current_theme == "Dark" else 1)
    accent_options = list(utils.THEME_COLORS.keys())
    selected_accent = st.selectbox("Akzentfarbe:", accent_options, index=accent_options.index(current_accent) if current_accent in accent_options else 0)
    
    if st.button("💾 Speichern & Anwenden", use_container_width=True):
        settings_db[current_user]["theme"] = selected_theme
        settings_db[current_user]["accent"] = selected_accent
        utils.save_data(utils.SETTINGS_FILE, settings_db)
        st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

# --- CSS INJECTION FÜR MODUS & FARBEN ---
active_theme = settings_db[current_user]["theme"]
active_color_hex = utils.THEME_COLORS.get(settings_db[current_user]["accent"], "#4A90E2")

if active_theme == "Dark":
    bg_color, sec_bg, text_color = "#0E1117", "#262730", "#FAFAFA"
else:
    bg_color, sec_bg, text_color = "#FFFFFF", "#F0F2F6", "#111111"

st.markdown(f"""
<style>
    :root {{
        --primary-color: {active_color_hex} !important;
        --background-color: {bg_color} !important;
        --secondary-background-color: {sec_bg} !important;
        --text-color: {text_color} !important;
    }}
    .stApp, .main {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {sec_bg} !important; }}
    p, span, h1, h2, h3, h4, h5, h6, label, li, div[data-testid="stMarkdownContainer"] {{ color: {text_color} !important; }}
    .stButton>button[kind="primary"] {{ background-color: {active_color_hex} !important; border: 1px solid {active_color_hex} !important; color: #FFFFFF !important; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# STARTSEITE / ANLEITUNG
# ==============================================================================
st.title("🎬 Creator Command Center")
st.markdown(f"**Eingeloggt als:** `{current_user}`")

st.header(f"Willkommen in deiner Kommandozentrale!")
st.write("Wähle nun links in der Seitenleiste aus, welches Tool du nutzen möchtest.")

st.info("💡 **Tipp:** Wenn du eine Seite nicht siehst, klicke oben links auf den kleinen Pfeil `>_`, um die Seitenleiste auszuklappen!")