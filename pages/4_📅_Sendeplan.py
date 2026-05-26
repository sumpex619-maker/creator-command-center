import streamlit as st
from datetime import time
import utils

st.set_page_config(page_title="Sendeplan - Command Center", layout="wide")
username = utils.check_login()

st.title("📅 Sendeplan & Kalender")

schedule_file = utils.get_user_filepath(username, "schedule")
webhook_file = utils.get_user_filepath(username, "webhooks")

sendeplan_daten = utils.load_data(schedule_file, lambda: {tag: {"aktiv": False, "zeit": "19:00", "game": "", "infos": ""} for tag in utils.WOCHENTAGE})
webhook_profile = utils.load_data(webhook_file, dict)

st.subheader("Wochenübersicht bearbeiten")
cols_tage = st.columns(7)

for idx, tag in enumerate(utils.WOCHENTAGE):
    with cols_tage[idx]:
        st.markdown(f"### {tag}")
        t_aktiv = st.checkbox("Live / Event", value=sendeplan_daten[tag]["aktiv"], key=f"ak_{tag}")
        sendeplan_daten[tag]["aktiv"] = t_aktiv
        
        if t_aktiv:
            try:
                h, m = map(int, sendeplan_daten[tag]["zeit"].split(":"))
                default_time = time(h, m)
            except:
                default_time = time(19, 0)
                
            t_zeit = st.time_input("Uhrzeit", value=default_time, key=f"zt_{tag}")
            sendeplan_daten[tag]["zeit"] = t_zeit.strftime("%H:%M")
            
            t_game = st.text_input("Spiel / Thema", value=sendeplan_daten[tag]["game"], key=f"gm_{tag}")
            sendeplan_daten[tag]["game"] = t_game
            
            t_info = st.text_input("Zusatz-Info", value=sendeplan_daten[tag]["infos"], key=f"if_{tag}", placeholder="z.B. Community Day")
            sendeplan_daten[tag]["infos"] = t_info
        else:
            st.caption("😴 Off-Day / Pause")

if st.button("💾 Sendeplan-Änderungen lokal speichern", type="secondary", use_container_width=True):
    utils.save_data(schedule_file, sendeplan_daten)
    st.success("✓ Sendeplan erfolgreich auf dem Server gesichert!")
    st.rerun()

st.write("---")
st.subheader("📢 Sendeplan auf Discord posten")

if not webhook_profile:
    st.error("⚠️ Du musst zuerst ein Webhook-Profil im Tab 'Discord Webhooks' anlegen!")
else:
    selected_plan_prof = st.selectbox("Sendeplan-Webhook auswählen:", list(webhook_profile.keys()))
    act_plan_prof = webhook_profile[selected_plan_prof]
    
    plan_ping_text = f"<@&{act_plan_prof['role_id']}> " if act_plan_prof["role_id"] and act_plan_prof["role_id"].lower() not in ["everyone", "here"] else (f"@{act_plan_prof['role_id']} " if act_plan_prof["role_id"] else "")
    
    edit_plan_ping = st.text_input("Ping-Text für Discord", value=f"{plan_ping_text}📅 Mein Sendeplan für diese Woche!")
    edit_plan_title = st.text_input("Discord Embed Titel", value="🗓️ STREAMPLAN / TERMINE")
    
    # Generiere Beschreibung aus Daten
    plan_desc = ""
    for tag in utils.WOCHENTAGE:
        if sendeplan_daten[tag]["aktiv"]:
            plan_desc += f"🔴 **{tag}:** ab **{sendeplan_daten[tag]['zeit']}** Uhr\n🎮 *{sendeplan_daten[tag]['game']}*"
            if sendeplan_daten[tag]["infos"]: plan_desc += f" | *{sendeplan_daten[tag]['infos']}*"
            plan_desc += "\n\n"
        else:
            plan_desc += f"😴 **{tag}:** *🔑 Off-Day / Pause*\n\n"
            
    edit_plan_desc = st.text_area("Vorschau des Sendeplans (Anpassen erlaubt)", value=plan_desc, height=250)
    
    if st.button("🚀 Sendeplan an Discord übertragen", type="primary", use_container_width=True):
        success, msg = utils.send_discord_webhook(
            act_plan_prof["url"], 
            text_content=edit_plan_ping, 
            embed_data={
                "title": edit_plan_title, 
                "description": edit_plan_desc, 
                "color": utils.COLORS["Sendeplan / Kalender"]
            }
        )
        if success: st.success("🚀 Sendeplan wurde erfolgreich auf Discord gepostet!")
        else: st.error(msg)