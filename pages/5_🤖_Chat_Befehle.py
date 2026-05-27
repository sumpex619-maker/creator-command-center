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
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px !important; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {CARD} !important; border-radius: 8px 8px 0 0 !important; padding: 10px 20px !important; color: {TEXT} !important; opacity: 0.8; }}
    .stTabs [aria-selected="true"] {{ background-color: {PRIM} !important; color: white !important; font-weight: 600 !important; opacity: 1; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SEITENINHALT
# ==============================================================================
st.title("💬 Chat-Befehle & Simulator")
st.markdown("Verwalte deine Kurzbefehle und teste direkt, ob deine Bot-Variablen funktionieren.")
st.markdown("---")

tab_manage, tab_test, tab_guide = st.tabs(["📝 Befehle verwalten", "🧪 Bot Simulator", "📖 Variablen-Guide (Hilfe)"])

commands = utils.load_data("chat_commands", list)

with tab_manage:
    col_add, col_list = st.columns(2)
    with col_add:
        st.markdown("### ➕ Neuen Befehl anlegen")
        with st.form("command_form", clear_on_submit=True):
            trigger = st.text_input("Befehl (Trigger)", placeholder="z.B. !setup")
            response = st.text_area("Antwort-Text des Bots", placeholder="Hier ist mein Racing-Setup: $(touser)...")
            platform_bot = st.selectbox("Für welchen Bot?", ["StreamElements", "Nightbot", "Botrix"])
            
            if st.form_submit_button("💾 Befehl speichern", type="primary", use_container_width=True):
                if trigger and response:
                    commands = [c for c in commands if c["trigger"].lower() != trigger.lower()]
                    commands.append({"trigger": trigger, "response": response, "platform": platform_bot})
                    utils.save_data("chat_commands", commands)
                    st.success(f"✅ Befehl `{trigger}` gesichert!")
                    st.rerun()
                else:
                    st.error("⚠️ Bitte Befehl und Text ausfüllen!")
                    
    with col_list:
        st.markdown("### 📋 Deine Befehle")
        if commands:
            for cmd in reversed(commands):
                with st.expander(f"🤖 {cmd['trigger']} ({cmd['platform']})", expanded=False):
                    st.markdown(f"**Antwort:**\n`{cmd['response']}`")
                    if st.button("🗑️ Löschen", key=f"del_{cmd['trigger']}"):
                        commands = [c for c in commands if c["trigger"] != cmd["trigger"]]
                        utils.save_data("chat_commands", commands)
                        st.rerun()
        else:
            st.info("ℹ️ Noch keine Befehle angelegt.")

with tab_test:
    st.markdown("### 🧪 Live Simulator")
    st.markdown("Tippe den Befehl so ein, wie ein Zuschauer es im Chat tun würde (z.B. `!shoutout @Zuschauer`), um zu sehen, wie der Bot antwortet.")
    
    if not commands:
        st.warning("Lege zuerst im ersten Tab einen Befehl an, um ihn hier zu testen!")
    else:
        test_input = st.text_input("💬 Chatnachricht tippen:", placeholder="!deinbefehl ...")
        
        if test_input:
            # Suche nach passendem Befehl
            matched_cmd = None
            for cmd in commands:
                if test_input.lower().startswith(cmd["trigger"].lower()):
                    matched_cmd = cmd
                    break
            
            if matched_cmd:
                simulated_response = matched_cmd["response"]
                
                # Variablen simulieren (StreamElements & Nightbot)
                simulated_response = simulated_response.replace("${user}", "TestZuschauer")
                simulated_response = simulated_response.replace("$(user)", "TestZuschauer")
                
                # Prüfen, ob noch ein Argument nach dem Befehl steht (z.B. @Name)
                args = test_input[len(matched_cmd["trigger"]):].strip()
                if args:
                    simulated_response = simulated_response.replace("${1}", args)
                    simulated_response = simulated_response.replace("$(touser)", args)
                else:
                    simulated_response = simulated_response.replace("${1}", "Niemand")
                    simulated_response = simulated_response.replace("$(touser)", "Niemand")

                st.markdown(f"**🤖 {matched_cmd['platform']} antwortet:**")
                st.info(simulated_response)
            else:
                st.error("Dieser Befehl wurde nicht erkannt. Hast du dich vertippt?")

with tab_guide:
    st.markdown("### 📖 Wie funktionieren Bot-Variablen?")
    st.write("Variablen sind Platzhalter, die sich automatisch anpassen (z.B. der Name des Zuschauers). Jeder Bot nutzt etwas andere Klammern!")
    
    col_se, col_nb = st.columns(2)
    with col_se:
        st.markdown('<div class="bento-card"><h4>StreamElements</h4><ul><li><code>${user}</code> = Name des Absenders</li><li><code>${1}</code> = Erstes Wort nach dem Befehl (z.B. beim Shoutout)</li><li><code>${game}</code> = Aktuelles Spiel</li></ul></div>', unsafe_allow_html=True)
    with col_nb:
        st.markdown('<div class="bento-card"><h4>Nightbot</h4><ul><li><code>$(user)</code> = Name des Absenders</li><li><code>$(touser)</code> = Ziel-User (Wort nach dem Befehl)</li><li><code>$(twitch game)</code> = Aktuelles Spiel</li></ul></div>', unsafe_allow_html=True)