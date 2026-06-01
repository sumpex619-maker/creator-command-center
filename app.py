import streamlit as st
import utils
import os

st.set_page_config(page_title="Creator Command Center", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")
utils.apply_modern_css()

# ==============================================================================
# SESSION STATE & AUTH MODUS
# ==============================================================================
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""
if "auth_view" not in st.session_state: st.session_state["auth_view"] = "login"

# ==============================================================================
# BEREICH: AUSGELOGGT (SLIDING AUTHENTIFIZIERUNG)
# ==============================================================================
if not st.session_state["logged_in"]:
    # Sidebar ausblenden, solange nicht eingeloggt
    st.markdown('<style>[data-testid="stSidebar"] {display: none;}</style>', unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; margin-top: 5vh; margin-bottom: 40px;'><h1 style='font-size: 56px; background: -webkit-linear-gradient(45deg, #38BDF8, #818CF8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Creator Command Center</h1><p style='font-size: 20px; opacity: 0.8;'>Dein professionelles HQ für Content, Stats & Streams.</p></div>", unsafe_allow_html=True)
    
    _, col_auth, _ = st.columns([1, 1.5, 1])
    
    with col_auth:
        # Custom Toggle-Buttons für den Slider-Effekt
        c1, c2, c3 = st.columns(3)
        if c1.button("🔒 Einloggen", use_container_width=True, type="primary" if st.session_state["auth_view"]=="login" else "secondary"): 
            st.session_state["auth_view"] = "login"; st.rerun()
        if c2.button("📝 Registrieren", use_container_width=True, type="primary" if st.session_state["auth_view"]=="register" else "secondary"): 
            st.session_state["auth_view"] = "register"; st.rerun()
        if c3.button("🔑 Passwort Reset", use_container_width=True, type="primary" if st.session_state["auth_view"]=="reset" else "secondary"): 
            st.session_state["auth_view"] = "reset"; st.rerun()
            
        st.markdown("<div class='bento-card'>", unsafe_allow_html=True)
        
        # --- LOGIN ---
        if st.session_state["auth_view"] == "login":
            st.subheader("Willkommen zurück")
            with st.form("login_form"):
                u = st.text_input("Benutzername")
                p = st.text_input("Passwort", type="password")
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
                        
        # --- REGISTRIEREN ---
        elif st.session_state["auth_view"] == "register":
            st.subheader("Neues Konto")
            with st.form("reg_form"):
                nu = st.text_input("Dein Wunsch-Name")
                np = st.text_input("Neues Passwort", type="password")
                if st.form_submit_button("✨ Kostenlos registrieren", use_container_width=True):
                    if nu and np:
                        conn = utils.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT username FROM users WHERE username = %s", (nu,))
                        if cursor.fetchone(): st.error("⚠️ Name bereits vergeben.")
                        else:
                            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (nu, utils.hash_password(np)))
                            st.success("🎉 Konto erstellt! Wechsle auf 'Einloggen'.")
                        cursor.close(); conn.close()

        # --- RESET ---
        elif st.session_state["auth_view"] == "reset":
            st.subheader("Passwort vergessen?")
            with st.form("reset_form"):
                res_u = st.text_input("Dein aktueller Benutzername")
                res_p = st.text_input("Dein NEUES Passwort", type="password")
                if st.form_submit_button("🔄 Passwort überschreiben", use_container_width=True):
                    if res_u and res_p:
                        conn = utils.get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT username FROM users WHERE username = %s", (res_u,))
                        if cursor.fetchone():
                            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (utils.hash_password(res_p), res_u))
                            st.success("✅ Passwort zurückgesetzt! Wechsle zum Login.")
                        else: st.error("⚠️ Benutzer existiert nicht.")
                        cursor.close(); conn.close()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# BEREICH: EINGELOGGT (HOMEPAGE DASHBOARD)
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['username']}")
    new_theme = st.selectbox("🎨 App Design", ["Midnight (Dark)", "Clean (Light)"], index=0 if st.session_state.get("theme") == "Midnight (Dark)" else 1)
    if new_theme != st.session_state.get("theme"):
        st.session_state["theme"] = new_theme; st.rerun()
    st.markdown("---")
    if st.button("🚪 Sicher Ausloggen", use_container_width=True):
        st.session_state["logged_in"], st.session_state["username"] = False, ""
        st.rerun()

st.title(f"👋 Willkommen im HQ, {st.session_state['username']}!")
st.markdown("---")

def get_page_path(keyword):
    if os.path.exists("pages"):
        for file in os.listdir("pages"):
            if keyword.lower() in file.lower() and file.endswith(".py"):
                return f"pages/{file}"
    return None

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="bento-card"><h4>📊 Stats & Analytics</h4><p style="font-size: 14px; opacity:0.8;">Manuelles Tracking mit Kommastellen & Charts.</p>', unsafe_allow_html=True)
    path = get_page_path("stats")
    if path: st.page_link(path, label="Stats öffnen", icon="📈")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="bento-card"><h4>🗓️ Sendeplan</h4><p style="font-size: 14px; opacity:0.8;">Plane deine Streams und Events.</p>', unsafe_allow_html=True)
    path = get_page_path("sendeplan")
    if path: st.page_link(path, label="Planer öffnen", icon="📅")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="bento-card"><h4>📝 Ideen & ToDos</h4><p style="font-size: 14px; opacity:0.8;">Keywords und Skripte speichern.</p>', unsafe_allow_html=True)
    path = get_page_path("ideen")
    if path: st.page_link(path, label="Ideen öffnen", icon="💡")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="bento-card"><h4>📢 Post Creator</h4><p style="font-size: 14px; opacity:0.8;">Sende Alerts an deinen Discord.</p>', unsafe_allow_html=True)
    path = get_page_path("post")
    if path: st.page_link(path, label="Posten", icon="🚀")
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="bento-card"><h4>💼 Business Hub</h4><p style="font-size: 14px; opacity:0.8;">Steuern, Links und Setup.</p>', unsafe_allow_html=True)
    path = get_page_path("business")
    if path: st.page_link(path, label="Business öffnen", icon="🤝")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="bento-card"><h4>🎓 Creator Academy</h4><p style="font-size: 14px; opacity:0.8;">Guides für Bots, Alerts & Co.</p>', unsafe_allow_html=True)
    path = get_page_path("academy")
    if path: st.page_link(path, label="Lernen", icon="📚")
    st.markdown('</div>', unsafe_allow_html=True)