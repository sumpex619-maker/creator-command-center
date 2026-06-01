import streamlit as st
import utils

current_user = utils.check_login()

st.title("💬 Chat-Befehle & Simulator")
st.markdown("Verwalte deine Kurzbefehle und teste direkt, ob deine Bot-Variablen funktionieren.")
st.markdown("---")

tab_manage, tab_test, tab_guide = st.tabs(["📝 Befehle verwalten", "🧪 Bot Simulator", "📖 Variablen-Guide"])

commands = utils.load_data("chat_commands", list)

with tab_manage:
    col_add, col_list = st.columns(2, gap="large")
    with col_add:
        st.subheader("➕ Neuen Befehl anlegen")
        with st.container(border=True):
            with st.form("command_form", clear_on_submit=True):
                trigger = st.text_input("Befehl (Trigger)", placeholder="z.B. !setup")
                response = st.text_area("Antwort-Text des Bots", placeholder="Hier ist mein Racing-Setup: $(touser)...")
                platform_bot = st.selectbox("Für welchen Bot?", ["StreamElements", "Nightbot", "Botrix"])
                
                st.markdown("<br>", unsafe_allow_html=True)
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
        st.subheader("📋 Deine Befehle")
        if commands:
            for cmd in reversed(commands):
                with st.expander(f"🤖 {cmd['trigger']} ({cmd['platform']})"):
                    st.markdown(f"**Antwort:**\n`{cmd['response']}`")
                    if st.button("🗑️ Löschen", key=f"del_{cmd['trigger']}", use_container_width=True):
                        commands = [c for c in commands if c["trigger"] != cmd["trigger"]]
                        utils.save_data("chat_commands", commands)
                        st.rerun()
        else:
            st.info("ℹ️ Noch keine Befehle angelegt.")

with tab_test:
    st.subheader("🧪 Live Simulator")
    st.markdown("Tippe den Befehl ein, um die Bot-Antwort zu testen (z.B. `!shoutout @Zuschauer`).")
    
    if not commands:
        st.warning("Lege zuerst im ersten Tab einen Befehl an!")
    else:
        with st.container(border=True):
            test_input = st.text_input("💬 Chatnachricht tippen:", placeholder="!deinbefehl ...")
            
            if test_input:
                matched_cmd = None
                for cmd in commands:
                    if test_input.lower().startswith(cmd["trigger"].lower()):
                        matched_cmd = cmd
                        break
                
                if matched_cmd:
                    simulated_response = matched_cmd["response"]
                    simulated_response = simulated_response.replace("${user}", "TestZuschauer").replace("$(user)", "TestZuschauer")
                    
                    args = test_input[len(matched_cmd["trigger"]):].strip()
                    if args:
                        simulated_response = simulated_response.replace("${1}", args).replace("$(touser)", args)
                    else:
                        simulated_response = simulated_response.replace("${1}", "Niemand").replace("$(touser)", "Niemand")

                    st.markdown(f"**🤖 {matched_cmd['platform']} antwortet:**")
                    st.info(simulated_response)
                else:
                    st.error("Dieser Befehl wurde nicht erkannt.")

with tab_guide:
    st.subheader("📖 Wie funktionieren Bot-Variablen?")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.container(border=True):
            st.markdown("#### StreamElements\n* `${user}` = Name des Absenders\n* `${1}` = Erstes Wort nach dem Befehl\n* `${game}` = Aktuelles Spiel")
    with c2:
        with st.container(border=True):
            st.markdown("#### Nightbot\n* `$(user)` = Name des Absenders\n* `$(touser)` = Ziel-User (Wort danach)\n* `$(twitch game)` = Aktuelles Spiel")