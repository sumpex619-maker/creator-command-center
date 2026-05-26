import streamlit as st
import utils

st.set_page_config(page_title="Webhook Verwaltung - Command Center", layout="wide")
username = utils.check_login()

st.title("📢 Discord Webhook Profile & Express-Post")

webhook_file = utils.get_user_filepath(username, "webhooks")
webhook_profile = utils.load_data(webhook_file, dict)

col_wh_setup, col_wh_send = st.columns([1, 1])

with col_wh_setup:
    st.subheader("⚙️ Profile anlegen / verwalten")
    with st.expander("➕ Neues Webhook-Profil erstellen", expanded=False):
        prof_name = st.text_input("Profil-Name (z.B. 'Discord Ankündigung')", key="p_name")
        prof_url = st.text_input("Webhook URL von Discord", key="p_url")
        prof_plat = st.selectbox("Zugeordnete Plattform (für Farben)", ["Allgemein", "Twitch", "YouTube", "Kick", "TikTok", "Instagram"], key="p_plat")
        prof_role = st.text_input("Rollen-ID für Pings (Optional)", placeholder="z.B. 123456789012345678", key="p_role")
        
        if st.button("Profil speichern", type="primary"):
            if not prof_name or not prof_url:
                st.error("Bitte Name und URL ausfüllen!")
            else:
                webhook_profile[prof_name] = {"url": prof_url, "plattform": prof_plat, "role_id": prof_role}
                utils.save_data(webhook_file, webhook_profile)
                st.success(f"Profil '{prof_name}' gespeichert!")
                st.rerun()

    if webhook_profile:
        st.write("### 🗂️ Deine Profile")
        for p_name, p_data in list(webhook_profile.items()):
            with st.expander(f"⚙️ {p_name} ({p_data['plattform']})"):
                st.text(f"URL: {p_data['url'][:45]}...")
                if p_data['role_id']: st.text(f"Ping-Rolle: {p_data['role_id']}")
                if st.button("🗑️ Profil löschen", key=f"del_prof_{p_name}"):
                    del webhook_profile[p_name]
                    utils.save_data(webhook_file, webhook_profile)
                    st.rerun()
    else:
        st.info("Noch keine Webhook-Profile eingerichtet.")

with col_wh_send:
    st.subheader("🚀 Express-Nachricht senden")
    if not webhook_profile:
        st.info("Erstelle links ein Profil, um Nachrichten zu senden.")
    else:
        selected_prof = st.selectbox("Senden über Profil:", list(webhook_profile.keys()))
        act_prof = webhook_profile[selected_prof]
        
        ping_text = f"<@&{act_prof['role_id']}> " if act_prof["role_id"] and act_prof["role_id"].lower() not in ["everyone", "here"] else (f"@{act_prof['role_id']} " if act_prof["role_id"] else "")
        
        c_ping = st.text_input("Normaler Text / Ping-Zeile", value=ping_text)
        c_title = st.text_input("Embed-Titel (Fett gedruckte Überschrift)")
        c_desc = st.text_area("Embed-Beschreibung (Haupttext)", height=150)
        
        if st.button("📢 Nachricht jetzt abschicken", type="primary"):
            embed_payload = None
            if c_title or c_desc:
                embed_payload = {
                    "title": c_title if c_title else "",
                    "description": c_desc if c_desc else "",
                    "color": utils.COLORS.get(act_prof["plattform"], utils.COLORS["Allgemein"])
                }
            
            success, msg = utils.send_discord_webhook(act_prof["url"], text_content=c_ping, embed_data=embed_payload)
            if success: st.success(msg)
            else: st.error(msg)