import streamlit as st
import utils
import os

st.set_page_config(page_title="Creator Command Center", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# ==============================================================================
# SESSION STATE & HOMEPAGE DESIGN ENGINE 2.0 (Glassmorphism & Modern UI)
# ==============================================================================
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""
if "theme" not in st.session_state: st.session_state["theme"] = "Midnight (Dark)"

if st.session_state["theme"] == "Midnight (Dark)":
    BG_COLOR = "#0B0F19" # Noch tieferes Blau-Schwarz für besseren Kontrast
    SIDEBAR_BG = "#111827"
    CARD_BG = "rgba(30, 41, 59, 0.6)" # Halbtransparent für Glass-Effekt
    TEXT_COLOR = "#F8FAFC"
    BORDER_COLOR = "rgba(255, 255, 255, 0.05)"
    GLOW = "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
else:
    BG_COLOR = "#F3F4F6"
    SIDEBAR_BG = "#FFFFFF"
    CARD_BG = "rgba(255, 255, 255, 0.8)"
    TEXT_COLOR = "#111827"
    BORDER_COLOR = "rgba(0, 0, 0, 0.05)"
    GLOW = "0 8px 32px 0 rgba(31, 38, 135, 0.07)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT_COLOR} !important; }}
    .stApp {{ background-color: {BG_COLOR} !important; background-image: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.05) 0%, transparent 50%); }}
    
    h1, h2, h3, h4 {{ font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; color: {TEXT_COLOR} !important; letter-spacing: -0.5px; }}
    
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG} !important; border-right: 1px solid {BORDER_COLOR}; }}
    
    /* Moderne schwebende Glaskarten */
    .bento-card, div[data-testid="stExpander"], .stAlert {{ 
        background: {CARD_BG} !important; 
        backdrop-filter: blur(12px) !important; 
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 20px !important; 
        border: 1px solid {BORDER_COLOR} !important; 
        padding: 28px !important; 
        box-shadow: {GLOW} !important; 
        margin-bottom: 20px; 
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .bento-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 40px 0 rgba(56, 189, 248, 0.15) !important; }}
    
    /* 2026 Button Styling */
    .stButton>button {{ 
        border-radius: 12px !important; 
        background-color: transparent !important; 
        color: {TEXT_COLOR} !important; 
        border: 1px solid rgba(129, 140, 248, 0.5) !important; 
        font-family: 'Outfit', sans-serif !important; 
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out; 
    }}
    .stButton>button:hover {{ border-color: #38BDF8 !important; background-color: rgba(56, 189, 248, 0.1) !important; }}
    .stButton>button[kind="primary"] {{ 
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important; 
        border: none !important; 
        color: white !important; 
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4) !important;
    }}
    .stButton>button[kind="primary"]:hover {{ transform: scale(1.02); box-shadow: 0 6px 20px rgba(56, 189, 248, 0.6) !important; }}
    
    /* Saubere Eingabefelder */
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{ 
        border-radius: 12px !important; 
        background-color: {SIDEBAR_BG} !important; 
        border: 1px solid {BORDER_COLOR} !important; 
        color: {TEXT_COLOR} !important; 
        padding: 4px 8px;
    }}
    .stTextInput>div>div:focus-within {{ border-color: #38BDF8 !important; box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# AUTHENTIFIZIERUNG & PASSWORT-RESET
# ==============================================================================
if not st.session_state["logged_in"]:
    st.markdown("<div style='text-align: center; margin-bottom: 40px;'><h1 style='font-size: 48px; background: -webkit-linear-gradient(45deg, #38BDF8, #818CF8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Creator Command Center</h1><p style='font-size: 18px; opacity: 0.8;'>Dein professionelles HQ für Content, Stats & Streams.</p></div>", unsafe_allow_html=True)
    
    # Login zentriert in Spalten
    _, col_login, _ = st.columns([1, 2, 1])
    
    with col_login:
        t_login, t_register, t_reset = st.tabs(["🔒 Einloggen", "📝 Konto erstellen", "🔑 Passwort vergessen"])
        
        with t_login:
            st.markdown("<div class='bento-card'>", unsafe_allow_html=True)
            with st.form("login_form"):
                u = st.text_input("Benutzername")
                p = st.text_input("Passwort", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("🚀 Dashboard betreten", type="primary", use_container_width=True):
                    if u and p:
                        conn = utils.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (u, utils.hash_password(p)))
                        if cursor.fetchone():
                            st.session_state["logged_in"], st.session_state["username"] = True, u
                            st.rerun()
                        else: st.error("❌ Benutzername oder Passwort inkorrekt.")
                        cursor.close(); conn.close()
            st.markdown("</div>", unsafe_allow_html=True)
                        
        with t_register:
            st.markdown("<div class='bento-card'>", unsafe_allow_html=True)
            with st.form("reg_form"):
                nu = st.text_input("Dein Wunsch-Name")
                np = st.text_input("Neues Passwort", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("✨ Kostenlos registrieren", use_container_width=True):
                    if nu and np:
                        conn = utils.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT username FROM users WHERE username = %s", (nu,))
                        if cursor.fetchone(): st.error("⚠️ Dieser Name ist leider schon vergeben.")
                        else:
                            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (nu, utils.hash_password(np)))
                            st.success("🎉 Konto erfolgreich erstellt! Du kannst dich nun im ersten Tab einloggen.")
                        cursor.close(); conn.close()
            st.markdown("</div>", unsafe_allow_html=True)

        with t_reset:
            st.markdown("<div class='bento-card'>", unsafe_allow_html=True)
            st.info("Trage hier deinen genauen Benutzernamen ein, um ein neues Passwort zu vergeben.")
            with st.form("reset_form"):
                res_u = st.text_input("Dein aktueller Benutzername")
                res_p = st.text_input("Dein NEUES Passwort", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("🔄 Passwort überschreiben", type="primary", use_container_width=True):
                    if res_u and res_p:
                        conn = utils.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT username FROM users WHERE username = %s", (res_u,))
                        if cursor.fetchone():
                            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (utils.hash_password(res_p), res_u))
                            st.success("✅ Dein Passwort wurde erfolgreich zurückgesetzt! Logge dich nun ein.")
                        else:
                            st.error("⚠️ Dieser Benutzername existiert nicht im System.")
                        cursor.close(); conn.close()
            st.markdown("</div>", unsafe_allow_html=True)
            
    # DISCLAIMER auf der Startseite
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; opacity: 0.6; font-size: 13px; padding: 20px;'>
        <b>💡 Disclaimer:</b> Das Konzept, die Ideen und das Layout für dieses Creator Dashboard stammen exklusiv aus der Feder des Nutzers. 
        Der zugrundeliegende Programmcode wurde als technischer Assistent von <b>Gemini (Google AI)</b> nach diesen strikten Vorgaben geschrieben und zusammengefügt.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# DASHBOARD STARTSEITE (EINGELOGGT)
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['username']}")
    new_theme = st.selectbox("🎨 App Design", ["Midnight (Dark)", "Clean (Light)"], index=0 if st.session_state["theme"] == "Midnight (Dark)" else 1)
    if new_theme != st.session_state["theme"]:
        st.session_state["theme"] = new_theme
        st.rerun()
    st.markdown("---")
    if st.button("🚪 Sicher Ausloggen", use_container_width=True):
        st.session_state["logged_in"], st.session_state["username"] = False, ""
        st.rerun()

st.title(f"👋 Willkommen im HQ, {st.session_state['username']}!")
st.markdown("---")

st.markdown(f"""
<div class="bento-card">
    <h3 style="margin-top:0; color: #38BDF8;">Dein 2026 Creator Setup</h3>
    <p style="font-size: 16px; line-height: 1.6; margin-bottom: 0;">
        Dieses Dashboard ist deine zentrale Steuerung. Als Anfänger verliert man schnell den Überblick über Links, Termine und Zahlen. 
        Hier trägst du alles zusammen. Klicke unten auf die Module, um direkt dorthin zu springen, oder nutze das Menü links.
    </p>
</div>
""", unsafe_allow_html=True)

def create_safe_link(filepath, label, icon="👉"):
    if os.path.exists(filepath):
        st.page_link(filepath, label=label, icon=icon)
    else:
        st.error(f"⚠️ Datei fehlt oder heißt falsch: `{filepath}`")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="bento-card"><h4>📊 Stats & Analytics</h4><p style="font-size: 14px; opacity:0.8;">Twitch & YouTube Reichweite tracken.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/2_📊_Stats.py", "Stats öffnen", "📈")
    st.markdown('<div class="bento-card" style="margin-top:20px;"><h4>🗓️ Sendeplan</h4><p style="font-size: 14px; opacity:0.8;">Plane deine Streams und Events.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/4_🗓️_Sendeplan.py", "Planer öffnen", "📅")

with c2:
    st.markdown('<div class="bento-card"><h4>📝 Ideen & ToDos</h4><p style="font-size: 14px; opacity:0.8;">Keywords und Skripte speichern.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/1_📝_Ideen_und_ToDos.py", "Ideen öffnen", "💡")
    st.markdown('<div class="bento-card" style="margin-top:20px;"><h4>📢 Post Creator</h4><p style="font-size: 14px; opacity:0.8;">Sende Alerts an deinen Discord.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/7_📢_Post_Creator.py", "Posten", "🚀")

with c3:
    st.markdown('<div class="bento-card"><h4>💼 Business Hub</h4><p style="font-size: 14px; opacity:0.8;">Steuern, Links und Setup.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/6_💼_Business_Hub.py", "Business öffnen", "🤝")
    st.markdown('<div class="bento-card" style="margin-top:20px;"><h4>🎓 Creator Academy</h4><p style="font-size: 14px; opacity:0.8;">Guides für Bots, Alerts & Co.</p></div>', unsafe_allow_html=True)
    create_safe_link("pages/8_🎓_Creator_Academy.py", "Lernen", "📚")