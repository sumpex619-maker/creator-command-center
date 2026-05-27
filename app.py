import streamlit as st
import utils
import os  # NEU: Wird für den automatischen Datei-Scanner benötigt

st.set_page_config(page_title="Creator Command Center", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# ==============================================================================
# SESSION STATE & THEME ENGINE
# ==============================================================================
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""
if "theme" not in st.session_state: st.session_state["theme"] = "Midnight (Dark)"

if st.session_state["theme"] == "Midnight (Dark)":
    BG_COLOR = "#0F172A"
    SIDEBAR_BG = "#1E293B"
    CARD_BG = "rgba(30, 41, 59, 0.4)"
    TEXT_COLOR = "#F8FAFC"
    BORDER_COLOR = "rgba(255, 255, 255, 0.08)"
else:
    BG_COLOR = "#F8FAFC"
    SIDEBAR_BG = "#F1F5F9"
    CARD_BG = "#FFFFFF"
    TEXT_COLOR = "#0F172A"
    BORDER_COLOR = "rgba(0, 0, 0, 0.1)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT_COLOR} !important; }}
    .stApp {{ background-color: {BG_COLOR} !important; }}
    h1, h2, h3, h4 {{ font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: {TEXT_COLOR} !important; }}
    
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG} !important; border-right: 1px solid {BORDER_COLOR}; }}
    .bento-card, div[data-testid="stExpander"] {{ background-color: {CARD_BG} !important; border-radius: 16px !important; border: 1px solid {BORDER_COLOR} !important; padding: 24px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; margin-bottom: 16px; }}
    
    .stButton>button {{ border-radius: 10px !important; background-color: {SIDEBAR_BG} !important; color: {TEXT_COLOR} !important; border: 1px solid {BORDER_COLOR} !important; font-family: 'Outfit', sans-serif !important; transition: all 0.2s; }}
    .stButton>button:hover {{ border-color: #38BDF8 !important; transform: translateY(-2px); }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important; border: none !important; color: white !important; }}
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR_BG} !important; border: 1px solid {BORDER_COLOR} !important; color: {TEXT_COLOR} !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px !important; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {CARD_BG} !important; border-radius: 8px 8px 0 0 !important; padding: 10px 20px !important; color: {TEXT_COLOR} !important; opacity: 0.8; }}
    .stTabs [aria-selected="true"] {{ background-color: #38BDF8 !important; color: white !important; font-weight: 600 !important; opacity: 1; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# AUTHENTIFIZIERUNG (LOGIN & REGISTER)
# ==============================================================================
if not st.session_state["logged_in"]:
    st.title("🚀 Creator Command Center")
    st.markdown("Willkommen! Logge dich ein oder erstelle ein Konto.")
    
    t_login, t_register = st.tabs(["🔒 Einloggen", "📝 Registrieren"])
    with t_login:
        with st.form("login_form"):
            u = st.text_input("Benutzername")
            p = st.text_input("Passwort", type="password")
            if st.form_submit_button("Anmelden", type="primary", use_container_width=True):
                if u and p:
                    conn = utils.get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (u, utils.hash_password(p)))
                    if cursor.fetchone():
                        st.session_state["logged_in"], st.session_state["username"] = True, u
                        st.rerun()
                    else: st.error("❌ Falsche Daten.")
                    cursor.close(); conn.close()
    with t_register:
        with st.form("reg_form"):
            nu, np = st.text_input("Wunsch-Name"), st.text_input("Passwort", type="password")
            if st.form_submit_button("Konto erstellen", use_container_width=True):
                if nu and np:
                    conn = utils.get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT username FROM users WHERE username = %s", (nu,))
                    if cursor.fetchone(): st.error("⚠️ Vergeben.")
                    else:
                        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (nu, utils.hash_password(np)))
                        st.success("🎉 Erstellt! Bitte links einloggen.")
                    cursor.close(); conn.close()
    st.stop()

# ==============================================================================
# DASHBOARD STARTSEITE
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['username']}")
    new_theme = st.selectbox("🎨 App Design", ["Midnight (Dark)", "Clean (Light)"], index=0 if st.session_state["theme"] == "Midnight (Dark)" else 1)
    if new_theme != st.session_state["theme"]:
        st.session_state["theme"] = new_theme
        st.rerun()
    st.markdown("---")
    if st.button("🚪 Ausloggen", use_container_width=True):
        st.session_state["logged_in"], st.session_state["username"] = False, ""
        st.rerun()

st.title(f"👋 Willkommen, {st.session_state['username']}!")
st.markdown("---")

st.markdown(f"""
<div class="bento-card">
    <h3 style="margin-top:0;">📖 Wie funktioniert dieses Tool?</h3>
    <p style="font-size: 16px; line-height: 1.6; margin-bottom: 0;">
        Dieses Dashboard ist deine zentrale Steuerung. Als Anfänger verliert man schnell den Überblick über Links, Termine und Zahlen. 
        Hier trägst du alles zusammen. Klicke unten auf die Module, um direkt dorthin zu springen, oder nutze das Menü links. 
        Wenn du gar nicht weißt, wo du anfangen sollst, schau in die <b>Creator Academy</b>!
    </p>
</div>
""", unsafe_allow_html=True)

# 🛠️ Absturzsichere Funktion zum Verlinken der Seiten
def create_safe_link(filepath, label):
    if os.path.exists(filepath):
        st.page_link(filepath, label=label, icon="👉")
    else:
        st.error(f"⚠️ Datei fehlt oder heißt falsch: `{filepath}`")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="bento-card"><h4>📊 Stats & Analytics</h4><p style="font-size: 14px;">Reichweite und Wachstum tracken.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/1_📊_Stats.py", "Stats öffnen")
    
    st.markdown('<div class="bento-card" style="margin-top:20px;"><h4>🗓️ Sendeplan</h4><p style="font-size: 14px;">Plane deine Streams und Events.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/4_🗓️_Sendeplan.py", "Planer öffnen")

with c2:
    st.markdown('<div class="bento-card"><h4>📝 Ideen & ToDos</h4><p style="font-size: 14px;">Keywords und Skripte speichern.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/2_📝_Ideen_und_ToDos.py", "Ideen öffnen")
    
    st.markdown('<div class="bento-card" style="margin-top:20px;"><h4>📢 Post Creator</h4><p style="font-size: 14px;">Sende Alerts an deinen Discord.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/7_📢_Post_Creator.py", "Posten")

with c3:
    st.markdown('<div class="bento-card"><h4>💼 Business Hub</h4><p style="font-size: 14px;">Steuern, Links und Setup.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/6_💼_Business_Hub.py", "Business öffnen")
    
    st.markdown('<div class="bento-card" style="margin-top:20px;"><h4>🎓 Creator Academy</h4><p style="font-size: 14px;">Guides für Bots, Alerts & Co.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/8_🎓_Creator_Academy.py", "Lernen")