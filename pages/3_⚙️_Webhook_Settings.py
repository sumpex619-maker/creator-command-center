import streamlit as st
import utils

# Login & Cinematic Design laden
username = utils.check_login()

st.title("⚙️ Einstellungen & Integrationen")
st.markdown("Verwalte deine verbundenen Accounts und Discord-Webhooks.")
st.markdown("---")

tab_integrations, tab_webhooks = st.tabs(["🔗 Verknüpfte Accounts", "📡 Discord Webhooks"])

# ==============================================================================
# TAB 1: INTEGRATIONEN (TWITCH, YOUTUBE ETC)
# ==============================================================================
with tab_integrations:
    st.subheader("Plattformen verknüpfen")
    st.write("Hinterlege hier deine Kanalnamen, damit das Command Center automatisch Daten für dich abrufen kann.")

    # Aktuelle Credentials aus der Datenbank laden
    conn = utils.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT platform, channel_id FROM api_credentials WHERE username = %s", (username,))
    creds = {row["platform"]: row["channel_id"] for row in cursor.fetchall()}

    with st.container(border=True):
        with st.form("api_creds_form"):
            twitch_name = st.text_input("🟣 Twitch Kanalname", value=creds.get("Twitch", ""), placeholder="z.B. dein_twitch_name")
            youtube_id = st.text_input("🔴 YouTube Channel ID (optional)", value=creds.get("YouTube", ""), placeholder="z.B. UCxyz123...")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾 Verbindungen speichern", type="primary", use_container_width=True):
                # Twitch speichern
                if twitch_name:
                    cursor.execute("INSERT INTO api_credentials (username, platform, channel_id) VALUES (%s, 'Twitch', %s) ON CONFLICT (username, platform) DO UPDATE SET channel_id = EXCLUDED.channel_id", (username, twitch_name))
                # YouTube speichern
                if youtube_id:
                    cursor.execute("INSERT INTO api_credentials (username, platform, channel_id) VALUES (%s, 'YouTube', %s) ON CONFLICT (username, platform) DO UPDATE SET channel_id = EXCLUDED.channel_id", (username, youtube_id))
                
                st.success("✅ Accounts erfolgreich verknüpft!")
                st.rerun()

    cursor.close()
    conn.close()

# ==============================================================================
# TAB 2: DISCORD WEBHOOKS (ALTBESTAND)
# ==============================================================================
with tab_webhooks:
    def get_webhooks(user):
        conn = utils.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, profile_name, url, plattform, role_id FROM webhooks WHERE username = %s ORDER BY profile_name", (user,))
        rows = cursor.fetchall()
        cursor.close(); conn.close()
        return rows

    def delete_webhook(webhook_id, user):
        conn = utils.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM webhooks WHERE id = %s AND username = %s", (webhook_id, user))
        cursor.close(); conn.close()
        st.success("🗑️ Webhook erfolgreich gelöscht!")
        st.rerun()

    def update_webhook(webhook_id, user, profile_name, url, plattform, role_id):
        conn = utils.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE webhooks SET profile_name = %s, url = %s, plattform = %s, role_id = %s WHERE id = %s AND username = %s", (profile_name, url, plattform, role_id, webhook_id, user))
            st.success("💾 Änderungen erfolgreich gespeichert!")
            st.rerun()
        except Exception:
            st.error("⚠️ Fehler beim Speichern.")
        finally:
            cursor.close(); conn.close()

    def add_webhook(user, profile_name, url, plattform, role_id):
        conn = utils.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO webhooks (username, profile_name, url, plattform, role_id) VALUES (%s, %s, %s, %s, %s)", (user, profile_name, url, plattform, role_id))
            st.success("🎉 Webhook erfolgreich hinzugefügt!")
            st.rerun()
        except Exception:
            st.error("⚠️ Fehler: Name wird bereits verwendet.")
        finally:
            cursor.close(); conn.close()

    col_links, col_rechts = st.columns([1.2, 1], gap="large")
    aktuelle_webhooks = get_webhooks(username)

    with col_rechts:
        st.subheader("➕ Neue Verbindung")
        with st.container(border=True):
            with st.form("add_webhook_form", clear_on_submit=True):
                new_profile = st.text_input("Profil-Name", placeholder="z.B. Twitch-Live-Alerts")
                new_plat = st.selectbox("Einsatzzweck", ["Twitch", "YouTube", "Kick", "TikTok", "Instagram", "Sendeplan", "Allgemein"])
                new_url = st.text_input("Discord Webhook URL", placeholder="https://discord.com/api/webhooks/...")
                new_role = st.text_input("Discord Rollen-ID (optional)", placeholder="z.B. 1234567890")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("🚀 Webhook speichern", type="primary", use_container_width=True):
                    if new_profile and new_url: 
                        add_webhook(username, new_profile, new_url, new_plat, new_role)
                    else: 
                        st.error("⚠️ Bitte Profil-Name und Webhook-URL ausfüllen!")

    with col_links:
        st.subheader("🔗 Aktive Webhooks")
        if not aktuelle_webhooks:
            st.info("Noch keine Verbindungen eingerichtet. Nutze das Formular rechts.")
        
        for wh in aktuelle_webhooks:
            wh_id, wh_profile, wh_url, wh_plat, wh_role = wh
            
            with st.expander(f"📡 {wh_profile} ({wh_plat})"):
                st.markdown(f"**Rollen-Ping-ID:** `{wh_role if wh_role else 'Kein Ping'}`")
                
                edit_state_key = f"edit_active_{wh_id}"
                if edit_state_key not in st.session_state: 
                    st.session_state[edit_state_key] = False
                    
                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.button("✏️ Bearbeiten", key=f"btn_edit_{wh_id}", use_container_width=True):
                    st.session_state[edit_state_key] = not st.session_state[edit_state_key]
                    st.rerun()
                if c_btn2.button("🗑️ Löschen", key=f"btn_del_{wh_id}", use_container_width=True):
                    delete_webhook(wh_id, username)
                
                if st.session_state[edit_state_key]:
                    with st.container(border=True):
                        with st.form(f"form_edit_{wh_id}"):
                            edit_profile = st.text_input("Profil-Name", value=wh_profile)
                            plattform_liste = ["Twitch", "YouTube", "Kick", "TikTok", "Instagram", "Sendeplan", "Allgemein"]
                            edit_plat = st.selectbox("Einsatzzweck", plattform_liste, index=plattform_liste.index(wh_plat) if wh_plat in plattform_liste else 0)
                            edit_url = st.text_input("Webhook URL", value=wh_url)
                            edit_role = st.text_input("Rollen-ID", value=wh_role if wh_role else "")
                            
                            c_sub1, c_sub2 = st.columns(2)
                            if c_sub1.form_submit_button("💾 Speichern", type="primary", use_container_width=True):
                                update_webhook(wh_id, username, edit_profile, edit_url, edit_plat, edit_role)
                            if c_sub2.form_submit_button("❌ Abbrechen", use_container_width=True):
                                st.session_state[edit_state_key] = False
                                st.rerun()