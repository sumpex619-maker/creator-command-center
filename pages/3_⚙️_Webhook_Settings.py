import streamlit as st
import utils

current_user = utils.check_login()

# ==============================================================================
# UNIVERSAL DESIGN ENGINE (Light & Dark Mode)
# ==============================================================================
if "theme" not in st.session_state: st.session_state["theme"] = "Midnight (Dark)"
with st.sidebar:
    new_theme = st.selectbox("🎨 Design", ["Midnight (Dark)", "Clean (Light)"], index=0 if st.session_state["theme"] == "Midnight (Dark)" else 1)
    if new_theme != st.session_state["theme"]: st.session_state["theme"] = new_theme; st.rerun()

if st.session_state["theme"] == "Midnight (Dark)":
    BG = "#0F172A"; SIDEBAR = "#1E293B"; CARD = "rgba(30, 41, 59, 0.4)"; TEXT = "#F8FAFC"; BORDER = "rgba(255, 255, 255, 0.08)"; PRIM = "#38BDF8"
else:
    BG = "#F8FAFC"; SIDEBAR = "#F1F5F9"; CARD = "#FFFFFF"; TEXT = "#0F172A"; BORDER = "rgba(0, 0, 0, 0.1)"; PRIM = "#0284C7"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT} !important; }}
    .stApp {{ background-color: {BG} !important; }}
    h1, h2, h3, h4 {{ font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: {TEXT} !important; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR} !important; border-right: 1px solid {BORDER}; }}
    .bento-card, div[data-testid="stExpander"], .stAlert {{ background-color: {CARD} !important; border-radius: 16px !important; border: 1px solid {BORDER} !important; padding: 20px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; margin-bottom: 15px; }}
    .stButton>button {{ border-radius: 10px !important; background-color: {SIDEBAR} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; font-family: 'Outfit', sans-serif !important; transition: all 0.2s; }}
    .stButton>button:hover {{ border-color: {PRIM} !important; transform: translateY(-2px); }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, {PRIM} 0%, #818CF8 100%) !important; border: none !important; color: white !important; }}
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR} !important; border: 1px solid {BORDER} !important; color: {TEXT} !important; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SEITENINHALT
# ==============================================================================
st.title("⚙️ Discord Webhook Setup")
st.markdown("Verbinde deinen Discord-Server mit diesem Tool, um automatisierte Posts senden zu können.")
st.markdown("---")

col_info, col_form = st.columns([1, 1.5])

with col_info:
    st.info("""
    **Wie erstelle ich einen Webhook?**
    1. Gehe in Discord auf deinen Server.
    2. Klicke auf **Servereinstellungen** -> **Integrationen** -> **Webhooks**.
    3. Klicke auf "Neuen Webhook erstellen".
    4. Gib ihm einen Namen (z.B. "Stream-Bot") und wähle den Textkanal aus, in dem er posten soll.
    5. Klicke auf **Webhook-URL kopieren** und füge sie hier rechts ein!
    """)
    st.markdown("💡 *Tipp: Du kannst verschiedene Webhooks für deinen Sendeplan und für normale Social-Media-Posts anlegen.*")

with col_form:
    with st.form("webhook_form", clear_on_submit=True):
        st.markdown("### ➕ Neuen Webhook hinterlegen")
        profile_name = st.text_input("Name für diesen Webhook", placeholder="z.B. Mein Sendeplan-Kanal")
        url = st.text_input("Webhook URL", placeholder="https://discord.com/api/webhooks/...")
        kategorie = st.selectbox("Wofür wird dieser Webhook genutzt?", ["Sendeplan / Kalender", "Social Media Posts (Instagram, X, etc.)", "YouTube/Twitch Live-Alerts"])
        role_id = st.text_input("Rollen-ID für Pings (Optional)", placeholder="1234567890 (Die ID der @everyone oder @Stream-Rolle)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Webhook speichern", type="primary", use_container_width=True):
            if profile_name and url:
                conn = utils.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO webhooks (username, profile_name, url, plattform, role_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (username, profile_name) 
                    DO UPDATE SET url = EXCLUDED.url, plattform = EXCLUDED.plattform, role_id = EXCLUDED.role_id
                """, (current_user, profile_name, url, kategorie, role_id))
                cursor.close(); conn.close()
                st.success(f"✅ Webhook '{profile_name}' gespeichert!")
                st.rerun()
            else:
                st.error("⚠️ Name und URL sind Pflichtfelder!")

st.markdown("---")
st.markdown("### 📋 Deine aktiven Verbindungen")
conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, plattform FROM webhooks WHERE username = %s", (current_user,))
hooks = cursor.fetchall()
cursor.close(); conn.close()

if hooks:
    for h in hooks:
        st.markdown(f"- **{h['profile_name']}** (Kategorie: {h['plattform']})")
else:
    st.warning("Noch keine Webhooks eingerichtet.")