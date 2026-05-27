import streamlit as st
import utils

PRIMARY_BLUE = "#38BDF8"
BG_DEEP_NAVY = "#0F172A"
SIDEBAR_NAVY = "#1E293B"
TEXT_SLATE = "#F8FAFC"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT_SLATE} !important; }}
    .stApp {{ background-color: {BG_DEEP_NAVY} !important; }}
    h1, h2, h3 {{ font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: #FFFFFF !important; }}
    div[data-testid="stExpander"], .stAlert {{ background-color: rgba(30, 41, 59, 0.4) !important; border-radius: 16px !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; }}
    .stButton>button {{ border-radius: 10px !important; background-color: {SIDEBAR_NAVY} !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; font-family: 'Outfit', sans-serif !important; }}
    .stButton>button:hover {{ border-color: {PRIMARY_BLUE} !important; box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important; }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important; border: none !important; }}
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR_NAVY} !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: {TEXT_SLATE} !important; }}
</style>
""", unsafe_allow_html=True)

current_user = utils.check_login()

st.title("💬 Chat-Befehle (Commands)")
st.markdown("Verwalte die wichtigsten Kurzbefehle für deine Chat-Bots an einem zentralen Ort.")
st.markdown("---")

commands = utils.load_data("chat_commands", list)

col_cmd_add, col_cmd_list = st.columns(2)

with col_cmd_add:
    st.markdown("### ➕ Neuen Befehl anlegen")
    with st.form("command_form", clear_on_submit=True):
        trigger = st.text_input("Befehl (Trigger)", placeholder="z.B. !discord")
        response = st.text_area("Antwort-Text des Bots", placeholder="Tritt unserer Community bei: discord.gg/...")
        platform_bot = st.selectbox("Genutzter Bot / Plattform", ["Nightbot", "Streamelements", "Moobot", "Custom Bot"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Befehl speichern", type="primary", use_container_width=True):
            if trigger and response:
                # Prüfen, ob Befehl existiert, sonst überschreiben/hinzufügen
                commands = [c for c in commands if c["trigger"].lower() != trigger.lower()]
                commands.append({"trigger": trigger, "response": response, "platform": platform_bot})
                utils.save_data("chat_commands", commands)
                st.success(f"✅ Befehl `{trigger}` erfolgreich in der Cloud gespeichert!")
                st.rerun()
            else:
                st.error("⚠️ Bitte fülle Befehl und Antwort-Text aus!")

with col_cmd_list:
    st.markdown("### 📋 Deine aktiven Befehle")
    if commands:
        for cmd in reversed(commands):
            with st.expander(f"🤖 {cmd['trigger']} ({cmd['platform']})", expanded=True):
                st.markdown(f"**Antwort:**\n`{cmd['response']}`")
    else:
        st.info("ℹ️ Du hast noch keine Befehle angelegt. Erstelle links deinen ersten Command!")