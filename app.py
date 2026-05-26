import streamlit as st
import utils

st.set_page_config(page_title="Creator Command Center", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

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
                    cursor.close()
                    conn.close()
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
                elif pwd_reg != pwd_reg2:
                    st.error("⚠️ Die Passwörter stimmen nicht überein!")
                elif len(pwd_reg) < 4:
                    st.error("⚠️ Das Passwort muss mindestens 4 Zeichen lang sein!")
                else:
                    cursor.execute("SELECT username FROM users WHERE username = %s", (user_reg,))
                    if cursor.fetchone():
                        st.error("⚠️ Dieser Benutzername ist bereits vergeben!")
                    else:
                        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user_reg, utils.hash_password(pwd_reg)))
                        conn.commit()
                        st.success("✅ Konto erfolgreich erstellt! Du kannst dich jetzt einloggen.")
        cursor.close()
        conn.close()
    st.stop()

# ==============================================================================
# DESIGN & THEME VERWALTUNG
# ==============================================================================
current_user = st.session_state["username"]

conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT theme, accent FROM users WHERE username = %s", (current_user,))
user_settings = cursor.fetchone()

if not user_settings:
    cursor.execute("""
        INSERT INTO users (username, theme, accent) 
        VALUES (%s, 'Dark', 'Pastell Ozean (Blau)')
        ON CONFLICT (username) DO UPDATE SET theme = 'Dark', accent = 'Pastell Ozean (Blau)'
    """, (current_user,))
    conn.commit()
    current_theme, current_accent = "Dark", "Pastell Ozean (Blau)"
else:
    current_theme = user_settings["theme"]
    current_accent = user_settings["accent"]

with st.sidebar:
    st.header("🎨 Design anpassen")
    selected_theme = st.radio("Modus:", ["Dark", "Light"], index=0 if current_theme == "Dark" else 1)
    accent_options = list(utils.THEME_COLORS.keys())
    selected_accent = st.selectbox("Akzentfarbe:", accent_options, index=accent_options.index(current_accent) if current_accent in accent_options else 0)
    
    if st.button("💾 Speichern & Anwenden", use_container_width=True):
        cursor.execute("UPDATE users SET theme = %s, accent = %s WHERE username = %s", (selected_theme, selected_accent, current_user))
        conn.commit()
        cursor.close()
        conn.close()
        st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        cursor.close()
        conn.close()
        st.rerun()
cursor.close()
conn.close()

# --- CSS INJECTION ---
active_color_hex = utils.THEME_COLORS.get(current_accent, "#4A90E2")
if current_theme == "Dark":
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
# STARTSEITE & ANLEITUNG
# ==============================================================================
st.title("🎬 Creator Command Center")
st.markdown(f"**Eingeloggt als:** `{current_user}`")

with st.expander("📖 Kurzanleitung: So nutzt du das Tool", expanded=True):
    st.markdown("""
    Willkommen in deiner Kommandozentrale! Hier sind die ersten Schritte:
    1. **Discord-Webhooks:** Gehe in der Seitenleiste auf `📢_Discord_Webhooks` und lege dort dein erstes Webhook-Profil an (URL von Discord kopieren).
    2. **Sendeplan:** Unter `📅_Sendeplan` kannst du deine Woche planen und deine Community automatisch per Discord informieren.
    3. **Stats-Tracking:** Nutze `📊_Stats`, um deine Performance zu erfassen und direkt in Grafiken auszuwerten.
    4. **Ideen:** Unter `📝_Ideen_und_ToDos` verlierst du nie wieder einen Geistesblitz.
    
    *Tipp: Du kannst links über die Seitenleiste jederzeit zwischen den Tools wechseln.*
    """)

st.header(f"Willkommen in deiner Kommandozentrale!")
st.write("Wähle nun links in der Seitenleiste aus, welches Tool du nutzen möchtest.")