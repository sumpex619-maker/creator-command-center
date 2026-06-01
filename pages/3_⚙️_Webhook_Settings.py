import streamlit as st
import utils

username = utils.check_login()

st.title("⚙️ Webhook Einstellungen")
st.markdown("Verwalte deine Discord-Webhooks für automatische Streaming-Alerts, Benachrichtigungen und Post-Schedules.")
st.markdown("---")

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
        st.error(f"⚠️ Fehler beim Speichern.")
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
        st.error(f"⚠️ Fehler: Name wird bereits verwendet.")
    finally:
        cursor.close(); conn.close()

col_links, col_rechts = st.columns([3, 2], gap="large")
aktuelle_webhooks = get_webhooks(username)

with col_links:
    st.subheader("📋 Deine aktiven Verbindungen")
    if not aktuelle_webhooks:
        st.info("Du hast aktuell noch keine Webhooks eingerichtet. Nutze das Formular rechts!")
    
    for wh in aktuelle_webhooks:
        wh_id, wh_profile, wh_url, wh_plat, wh_role = wh
        st.markdown(f"""
        <div class="bento-card" style="margin-bottom: 0px; padding-bottom: 10px;">
            <h3 style="margin-top:0;">🔗 {wh_profile}</h3>
            <p style="margin:0;"><b>Plattform:</b> {wh_plat}</p>
            <p style="margin:0;"><b>Rollen-ID:</b> {wh_role if wh_role else 'Kein Ping aktiv'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        c_btn1, c_btn2, _ = st.columns([1, 1, 2])
        edit_state_key = f"edit_active_{wh_id}"
        if edit_state_key not in st.session_state: st.session_state[edit_state_key] = False
        
        with c_btn1:
            if st.button("✏️ Bearbeiten", key=f"btn_edit_{wh_id}", use_container_width=True):
                st.session_state[edit_state_key] = not st.session_state[edit_state_key]
                st.rerun()
        with c_btn2:
            if st.button("🗑️ Löschen", key=f"btn_del_{wh_id}", type="secondary", use_container_width=True):
                delete_webhook(wh_id, username)
        
        if st.session_state[edit_state_key]:
            with st.form(f"form_edit_{wh_id}"):
                edit_profile = st.text_input("Profil-Name", value=wh_profile)
                plattform_liste = ["Twitch", "YouTube", "Kick", "TikTok", "Instagram", "Sendeplan / Kalender", "Allgemein"]
                edit_plat = st.selectbox("Plattform", plattform_liste, index=plattform_liste.index(wh_plat) if wh_plat in plattform_liste else 0)
                edit_url = st.text_input("Webhook URL", value=wh_url)
                edit_role = st.text_input("Rollen-ID", value=wh_role if wh_role else "")
                
                c_sub1, c_sub2 = st.columns(2)
                with c_sub1:
                    if st.form_submit_button("💾 Speichern", use_container_width=True):
                        update_webhook(wh_id, username, edit_profile, edit_url, edit_plat, edit_role)
                with c_sub2:
                    if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                        st.session_state[edit_state_key] = False
                        st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

with col_rechts:
    st.subheader("➕ Neuen Webhook hinzufügen")
    with st.form("add_webhook_form", clear_on_submit=True):
        new_profile = st.text_input("Profil-Name", placeholder="z.B. Twitch-Live-Alerts")
        new_plat = st.selectbox("Plattform", ["Twitch", "YouTube", "Kick", "TikTok", "Instagram", "Sendeplan / Kalender", "Allgemein"])
        new_url = st.text_input("Discord Webhook URL", placeholder="https://discord.com/api/webhooks/...")
        new_role = st.text_input("Discord Rollen-ID (optional)", placeholder="z.B. 1234567890")
        
        if st.form_submit_button("🚀 Verbindung herstellen", type="primary", use_container_width=True):
            if new_profile and new_url: add_webhook(username, new_profile, new_url, new_plat, new_role)
            else: st.error("⚠️ Bitte fülle Profil-Name und Webhook-URL aus!")