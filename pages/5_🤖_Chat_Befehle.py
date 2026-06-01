import streamlit as st
import utils

current_user = utils.check_login()

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
                st.error("Dieser Befehl wurde nicht erkannt. Hast du dich vertippt?")

with tab_guide:
    st.markdown("### 📖 Wie funktionieren Bot-Variablen?")
    st.write("Variablen sind Platzhalter, die sich automatisch anpassen. Jeder Bot nutzt etwas andere Klammern!")
    
    col_se, col_nb = st.columns(2)
    with col_se:
        st.markdown('<div class="bento-card"><h4>StreamElements</h4><ul><li><code>${user}</code> = Name des Absenders</li><li><code>${1}</code> = Erstes Wort nach dem Befehl</li><li><code>${game}</code> = Aktuelles Spiel</li></ul></div>', unsafe_allow_html=True)
    with col_nb:
        st.markdown('<div class="bento-card"><h4>Nightbot</h4><ul><li><code>$(user)</code> = Name des Absenders</li><li><code>$(touser)</code> = Ziel-User (Wort danach)</li><li><code>$(twitch game)</code> = Aktuelles Spiel</li></ul></div>', unsafe_allow_html=True)