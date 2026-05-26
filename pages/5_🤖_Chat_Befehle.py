import streamlit as st

st.set_page_config(page_title="Bot Commands - Command Center", layout="wide")
st.title("🤖 Chat-Befehle Generator")
st.write("Generiere schnell und fehlerfrei fertigen Code für deinen Chat-Bot.")

target_bot = st.radio("Für welchen Bot generieren?", ["Nightbot", "StreamElements", "Fossabot"], horizontal=True)

col_cmd1, col_cmd2 = st.columns([1, 2])
with col_cmd1:
    cmd_name = st.text_input("Befehls-Name", placeholder="z.B. social media")
with col_cmd2:
    cmd_msg = st.text_input("Was soll der Bot antworten?", placeholder="Folgt mir auf YouTube: youtube.com/...")

col_gen1, col_gen2 = st.columns([1, 1])
with col_gen1:
    cmd_userlevel = st.selectbox("Wer darf den Befehl nutzen?", ["Everyone", "Moderator", "Subscriber"])
with col_gen2:
    cmd_cooldown = st.slider("Cooldown (Sekunden)", 5, 300, 15)

if st.button("🚀 Befehl jetzt generieren", type="primary"):
    if not cmd_name or not cmd_msg:
        st.error("⚠️ Bitte gib einen Befehlsnamen und den Text ein!")
    else:
        st.write("### ✅ Dein fertiger Code:")
        final_name = cmd_name if cmd_name.startswith("! ") or cmd_name.startswith("!") else "!" + cmd_name
        
        if target_bot == "Nightbot":
            ul_map = {"Everyone": "everyone", "Moderator": "moderator", "Subscriber": "subscriber"}
            bot_string = f"!addcom {final_name} {cmd_msg} -ul={ul_map[cmd_userlevel]} -cd={cmd_cooldown}"
        elif target_bot == "StreamElements":
            bot_string = f"!command add {final_name} {cmd_msg}"
            st.caption("Hinweis: Bei StreamElements stellst du das Userlevel am besten direkt im Online-Dashboard ein.")
        elif target_bot == "Fossabot":
            bot_string = f"!command add {final_name} {cmd_msg}"
            st.caption("Hinweis: Bei Fossabot stellst du Feinheiten direkt im Web-Interface ein.")
            
        st.code(bot_string, language="text")
        st.success("Kopiere den Text oben und füge ihn einfach in deinen Chat ein!")