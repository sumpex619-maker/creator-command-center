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
st.title("🗓️ Sendeplan & Kalender")

conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, url FROM webhooks WHERE username = %s AND plattform LIKE '%%Sendeplan%%'", (current_user,))
sendeplan_hooks = cursor.fetchall()
cursor.close(); conn.close()

if not sendeplan_hooks:
    st.warning("🛑 Stopp! Du musst zuerst einen Webhook für die Kategorie 'Sendeplan' einrichten, bevor du diesen Kalender nutzen kannst.")
    st.info("Gehe dazu links im Menü auf '⚙️ Webhook Settings'.")
    st.stop()

st.markdown("Plane deine Woche und sende deinen Plan mit einem Klick in deinen Discord.")
st.markdown("---")

sendeplan = utils.load_data("sendeplan", dict)
col_plan, col_view = st.columns([1, 1.5])

with col_plan:
    st.markdown("### 🛠️ Eintrag erstellen")
    with st.form("sendeplan_form"):
        tag = st.selectbox("Wochentag", utils.WOCHENTAGE)
        typ = st.text_input("Kategorie / Art", placeholder="z.B. Rennkalender, Just Chatting, IRL...")
        uhrzeit = st.text_input("Uhrzeit", placeholder="z.B. 19:00 - 22:00 Uhr")
        inhalt = st.text_area("Was genau machst du?", placeholder="Inhalt des Streams...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Speichern", type="primary", use_container_width=True):
            sendeplan[tag] = {"uhrzeit": uhrzeit, "inhalt": inhalt, "typ": typ}
            utils.save_data("sendeplan", sendeplan)
            st.success("Aktualisiert!")
            st.rerun()

with col_view:
    st.markdown("### 📅 Wochenübersicht")
    for tag in utils.WOCHENTAGE:
        slot = sendeplan.get(tag, None)
        with st.expander(f"🔹 {tag}", expanded=True):
            if slot:
                st.markdown(f"**[{slot.get('typ', 'Stream')}]** ⏰ {slot['uhrzeit']}")
                st.write(slot['inhalt'])
                if st.button(f"📢 Nur {tag} posten", key=f"post_{tag}"):
                    msg = f"📅 **Update für {tag}!**\n⏰ {slot['uhrzeit']} | 🎮 {slot.get('typ', 'Stream')}\n{slot['inhalt']}"
                    success, response = utils.send_discord_webhook(sendeplan_hooks[0]["url"], text_content=msg)
                    if success: st.success("Gepostet!")
            else:
                st.write("*Keine Termine eingetragen.*")
                
st.markdown("---")
if st.button("🚀 GESAMTEN WOCHENPLAN IN DISCORD POSTEN", type="primary", use_container_width=True):
    wochen_msg = "📅 **UNSER SENDEPLAN FÜR DIESE WOCHE** 📅\n\n"
    for tag in utils.WOCHENTAGE:
        slot = sendeplan.get(tag, None)
        if slot: wochen_msg += f"**{tag}** ({slot.get('typ', 'Stream')}):\n⏰ {slot['uhrzeit']} - {slot['inhalt']}\n\n"
        else: wochen_msg += f"**{tag}**: ❌ Frei / Spontan\n\n"
    
    success, response = utils.send_discord_webhook(sendeplan_hooks[0]["url"], text_content=wochen_msg)
    if success: st.success("✅ Der komplette Plan ist online!")