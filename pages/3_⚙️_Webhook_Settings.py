import streamlit as st
import utils

current_user = utils.check_login()
st.title("⚙️ Discord Webhook Setup")
st.markdown("Verbinde deinen Discord-Server mit diesem Tool, um automatisierte Posts senden zu können.")
st.markdown("---")

col_info, col_form = st.columns([1, 1.5])

with col_info:
    st.info("""
    **Wie erstelle ich einen Webhook?**
    1. Gehe in Discord auf deinen Server.
    2. Klicke auf **Servereinstellungen** -> **Integrationen** -> **Webhooks**.
    3. Klicke auf "Neuen Webhook erstellen".
    4. Gib ihm einen Namen (z.B. "Stream-Bot") und wähle den Textkanal aus, in dem er posten soll.
    5. Klicke auf **Webhook-URL kopieren** und füge sie hier rechts ein!
    """)
    st.markdown("💡 *Tipp: Du kannst verschiedene Webhooks für deinen Sendeplan und für normale Social-Media-Posts anlegen.*")

with col_form:
    with st.form("webhook_form", clear_on_submit=True):
        st.markdown("### ➕ Neuen Webhook hinterlegen")
        profile_name = st.text_input("Name für diesen Webhook", placeholder="z.B. Mein Sendeplan-Kanal")
        url = st.text_input("Webhook URL", placeholder="https://discord.com/api/webhooks/...")
        kategorie = st.selectbox("Wofür wird dieser Webhook genutzt?", ["Sendeplan / Kalender", "Social Media Posts (Instagram, X, etc.)", "YouTube/Twitch Live-Alerts"])
        role_id = st.text_input("Rollen-ID für Pings (Optional)", placeholder="1234567890 (Die ID der @everyone oder @Stream-Rolle)")
        
        if st.form_submit_button("💾 Webhook speichern", type="primary", use_container_width=True):
            if profile_name and url:
                conn = utils.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO webhooks (username, profile_name, url, plattform, role_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (username, profile_name) 
                    DO UPDATE SET url = EXCLUDED.url, plattform = EXCLUDED.plattform, role_id = EXCLUDED.role_id
                """, (current_user, profile_name, url, kategorie, role_id))
                cursor.close(); conn.close()
                st.success(f"✅ Webhook '{profile_name}' gespeichert!")
                st.rerun()
            else:
                st.error("⚠️ Name und URL sind Pflichtfelder!")

st.markdown("---")
st.markdown("### 📋 Deine aktiven Verbindungen")
conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, plattform FROM webhooks WHERE username = %s", (current_user,))
hooks = cursor.fetchall()
cursor.close(); conn.close()

if hooks:
    for h in hooks:
        st.markdown(f"- **{h['profile_name']}** (Kategorie: {h['plattform']})")
else:
    st.warning("Noch keine Webhooks eingerichtet.")