import streamlit as st
import utils
import os

st.set_page_config(page_title="Creator Command Center", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")
utils.apply_modern_css()

if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""

# ==============================================================================
# BEREICH: AUSGELOGGT (LOGIN)
# ==============================================================================
if not st.session_state["logged_in"]:
    st.markdown("<div style='text-align: center; margin-top: 5vh; margin-bottom: 40px;'><h1 style='font-size: 50px;'>Creator <span style='color: #00E5FF; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);'>Command Center</span></h1><p style='font-size: 18px; color: #888;'>System Online. Bitte autorisieren.</p></div>", unsafe_allow_html=True)
    
    _, col_auth, _ = st.columns([1, 1.5, 1])
    with col_auth:
        t_login, t_register = st.tabs(["🔒 SYSTEM LOGIN", "📝 NEUER NUTZER"])
        
        with t_login:
            with st.container(border=True):
                with st.form("login_form"):
                    u = st.text_input("Benutzername")
                    p = st.text_input("Passwort", type="password")
                    if st.form_submit_button("Uplink Herstellen", type="primary", use_container_width=True):
                        if u and p:
                            conn = utils.get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (u, utils.hash_password(p)))
                            if cursor.fetchone():
                                st.session_state["logged_in"], st.session_state["username"] = True, u
                                st.rerun()
                            else: st.error("❌ Zugriff verweigert.")
                            cursor.close(); conn.close()
                            
        with t_register:
            with st.container(border=True):
                with st.form("reg_form"):
                    nu = st.text_input("Neuer Benutzername")
                    np = st.text_input("Sicheres Passwort", type="password")
                    if st.form_submit_button("Registrieren", use_container_width=True):
                        if nu and np:
                            conn = utils.get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT username FROM users WHERE username = %s", (nu,))
                            if cursor.fetchone(): st.error("⚠️ Benutzername existiert bereits.")
                            else:
                                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (nu, utils.hash_password(np)))
                                st.success("🎉 Autorisiert! Bitte im Reiter 'Login' anmelden.")
                            cursor.close(); conn.close()
    st.stop()

# ==============================================================================
# BEREICH: EINGELOGGT (DAS DASHBOARD)
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['username']}")
    st.markdown("---")
    if st.button("🚪 Ausloggen", use_container_width=True):
        st.session_state["logged_in"], st.session_state["username"] = False, ""
        st.rerun()

st.markdown(f"<h1>HQ Status: <span style='color: #00E5FF;'>{st.session_state['username']}</span></h1>", unsafe_allow_html=True)
st.markdown("Wähle ein Modul, um fortzufahren.")
st.markdown("---")

def get_page_path(keyword):
    if os.path.exists("pages"):
        for file in os.listdir("pages"):
            if keyword.lower() in file.lower() and file.endswith(".py"):
                return f"pages/{file}"
    return None

# Die "Knöpfe" sind jetzt die Boxen selbst!
c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        path = get_page_path("stats")
        if path: st.page_link(path, label="📊 Analytics & Stats")
        st.markdown("<p style='font-size: 14px; color:#888;'>Manuelles Tracking & Performance Charts.</p>", unsafe_allow_html=True)
        
    with st.container(border=True):
        path = get_page_path("sendeplan")
        if path: st.page_link(path, label="🗓️ Sendeplan")
        st.markdown("<p style='font-size: 14px; color:#888;'>Plane deine Streams und Community-Events.</p>", unsafe_allow_html=True)

with c2:
    with st.container(border=True):
        path = get_page_path("ideen")
        if path: st.page_link(path, label="📝 Ideen & ToDos")
        st.markdown("<p style='font-size: 14px; color:#888;'>SEO-Keywords und Skripte speichern.</p>", unsafe_allow_html=True)
        
    with st.container(border=True):
        path = get_page_path("post")
        if path: st.page_link(path, label="📢 Post Creator")
        st.markdown("<p style='font-size: 14px; color:#888;'>Sende Alerts direkt an deinen Discord.</p>", unsafe_allow_html=True)

with c3:
    with st.container(border=True):
        path = get_page_path("business")
        if path: st.page_link(path, label="💼 Business Hub")
        st.markdown("<p style='font-size: 14px; color:#888;'>Partner-Links, Steuern und Setup.</p>", unsafe_allow_html=True)
        
    with st.container(border=True):
        path = get_page_path("academy")
        if path: st.page_link(path, label="🎓 Academy")
        st.markdown("<p style='font-size: 14px; color:#888;'>Guides für Chatbots, Alerts & OBS.</p>", unsafe_allow_html=True)