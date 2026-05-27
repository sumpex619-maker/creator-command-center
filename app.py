import streamlit as st
import utils

# ==============================================================================
# 1. PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Creator Command Center", 
    page_icon="🎬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. 2026 MIDNIGHT ENGINE (Globale Styles)
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
    h1, h2, h3 {{ font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: #FFFFFF !important; }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_NAVY} !important; border-right: 1px solid rgba(255, 255, 255, 0.05); }}

    /* Bento-Card Look für Expander & Widgets */
    div[data-testid="stExpander"], .stAlert {{
        background-color: rgba(30, 41, 59, 0.5) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }}

    /* Moderne Buttons */
    .stButton>button {{
        border-radius: 10px !important;
        background-color: {SIDEBAR_NAVY} !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease;
        font-family: 'Outfit', sans-serif !important;
    }}
    .stButton>button:hover {{ border-color: {PRIMARY_BLUE} !important; box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important; }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important; border: none !important; }}

    /* Tabs & Inputs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px !important; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {SIDEBAR_NAVY} !important; border-radius: 8px 8px 0 0 !important; padding: 10px 20px !important; }}
    .stTabs [aria-selected="true"] {{ background-color: {PRIMARY_BLUE} !important; color: {BG_DEEP_NAVY} !important; }}
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR_NAVY} !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; }}
</style>
""", unsafe_allow_html=True)

# --- LOGIN LOGIK ---
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""

if not st.session_state["logged_in"]:
    st.markdown("<br><br><h1 style='text-align: center;'>🎬 Command Center</h1>", unsafe_allow_html=True)
    c_login, c_reg = st.columns(2)
    with c_login:
        st.markdown("### 🔑 Login")
        with st.form("l_form"):
            u, p = st.text_input("User"), st.text_input("PW", type="password")
            if st.form_submit_button("System starten", type="primary", use_container_width=True):
                conn = utils.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE username = %s", (u,))
                row = cursor.fetchone()
                if row and row["password"] == utils.hash_password(p):
                    st.session_state["logged_in"], st.session_state["username"] = True, u
                    st.rerun()
                else: st.error("Falsche Daten!")
    with c_reg:
        st.markdown("### 📝 Registrieren")
        with st.form("r_form", clear_on_submit=True):
            nu, np, npc = st.text_input("New User"), st.text_input("New PW", type="password"), st.text_input("Confirm", type="password")
            if st.form_submit_button("Account erstellen", use_container_width=True):
                if np == npc and nu:
                    conn = utils.get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (nu, utils.hash_password(np)))
                    st.success("Erstellt! Bitte links einloggen.")
                else: st.error("Fehler!")
    st.stop()

# --- DASHBOARD ---
st.title(f"🚀 Dashboard | {st.session_state['username']}")
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("### Willkommen zurück!")
    st.write("Deine Systeme laufen stabil auf der Cloud-Datenbank.")
with col_b:
    with st.expander("Deine Schnellzugriffe", expanded=True):
        st.write("- 📊 Stats prüfen\n- 📝 Neue Video-Idee\n- 💼 Business Roadmap")

---

### 2. `pages/3_📊_Stats.py` (Modernisierte Charts)
Hier habe ich die Charts auf das neue Design angepasst (transparente Hintergründe, helle Texte).

```python
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import utils

current_user = utils.check_login()
st.title("📊 Stats & Community Health")

t1, t2 = st.tabs(["📝 Datenerfassung", "📈 Analyse"])

with t1:
    with st.form("stats_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Performance")
            plat = st.selectbox("Plattform", ["Twitch", "YouTube", "TikTok", "Instagram"])
            views = st.number_input("Views", min_value=0)
        with c2:
            st.markdown("### Health")
            chat = st.number_input("Chatter", min_value=0)
            discord = st.number_input("Neue Discord-Member", min_value=0)
        if st.form_submit_button("Daten sichern", type="primary", use_container_width=True):
            data = utils.load_data("stats", list)
            data.append({"datum": str(datetime.now()), "plattform": plat, "views": views, "chat": chat, "discord": discord})
            utils.save_data("stats", data)
            st.success("Gespeichert!")

with t2:
    stats = utils.load_data("stats", list)
    if stats:
        df = pd.DataFrame(stats)
        # Modernes Chart-Layout
        fig = px.line(df, x="datum", y="views", color="plattform", template="plotly_dark")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC"))
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Noch keine Daten.")

### 3. `pages/4_📝_Ideen_und_ToDos.py` (Bento-Planer)
Die Ideen-Seite nutzt jetzt konsequent Side-by-Side Kacheln.

```python
import streamlit as st
import utils
from datetime import datetime

current_user = utils.check_login()
st.title("📝 Ideen-Schmiede & SEO")

t1, t2 = st.tabs(["💡 Neue Idee", "📋 Archiv"])

with t1:
    with st.form("idea_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titel = st.text_input("Arbeitstitel")
            notizen = st.text_area("Inhalt")
        with c2:
            key = st.text_input("Fokus-Keyword")
            prob = st.text_input("Zuschauer-Problem")
        if st.form_submit_button("Idee sichern", type="primary", use_container_width=True):
            ideas = utils.load_data("ideas", list)
            ideas.append({"id": str(datetime.now()), "titel": titel, "notizen": notizen, "key": key, "prob": prob})
            utils.save_data("ideas", ideas)
            st.success("Idee gespeichert!")

with t2:
    ideas = utils.load_data("ideas", list)
    for i in reversed(ideas):
        with st.expander(f"📌 {i.get('titel')}"):
            c_a, c_b = st.columns(2)
            c_a.write(i.get("notizen"))
            c_b.code(f"Keyword: {i.get('key')}")

### 4. `pages/5_💼_Business_Hub.py` (Roadmap)
Die Business-Seite ist nun klar strukturiert und nutzt Fortschrittsbalken.

```python
import streamlit as st
import utils

current_user = utils.check_login()
st.title("💼 Business Hub")

t1, t2 = st.tabs(["🗺️ Roadmap", "🔗 Affiliate"])

with t1:
    st.markdown("### Dein Weg zum Profi")
    progress = utils.load_data("biz_prog", dict)
    for step in ["Gewerbe", "Impressum", "Business Mail", "Link-in-Bio"]:
        progress[step] = st.checkbox(step, value=progress.get(step, False))
    utils.save_data("biz_prog", progress)
    score = sum(progress.values())
    st.progress(score / 4)
    st.write(f"Fortschritt: {int(score/4*100)}%")

with t2:
    with st.form("link_form"):
        n, u = st.text_input("Partner"), st.text_input("Link")
        if st.form_submit_button("Link speichern"):
            links = utils.load_data("links", list)
            links.append({"n": n, "u": u})
            utils.save_data("links", links)
    for l in utils.load_data("links", list):
        with st.expander(l['n']): st.code(l['u'])

Deine neue 2026er Benutzeroberfläche ist nun bereit! Durch die konsistente Verwendung von Spalten, modernen Schriftarten und der Cloud-Anbindung ist das Tool nun absolut zukunftssicher. Schau dir das neue Design in Ruhe an – es wird dein Workflow-Gefühl massiv verbessern!