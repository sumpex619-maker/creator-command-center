import streamlit as st
import utils

# Design-Engine aktivieren (für einheitlichen Look auf jeder Unterseite)
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

# Login-Schutz prüfen
current_user = utils.check_login()

st.title("🤖 Discord Webhook Zentrale")
st.markdown("Automatisiere deine Community-Benachrichtigungen mit vollem Voransichts-Support.")
st.markdown("---")

col_manage, col_test = st.columns(2)

with col_manage:
    st.markdown("### ⚙️ Webhook einrichten")
    with st.form("webhook_form", clear_on_submit=True):
        profile_name = st.text_input("Profilname", placeholder="z.B. Stream-Ankündigung")
        url = st.text_input("Webhook URL", placeholder="https://discord.com/api/webhooks/...")
        plattform = st.selectbox("Ziel-Plattform", ["Twitch", "YouTube", "Kick", "Instagram", "X (Twitter)", "Allgemein"])
        role_id = st.text_input("Rollen-ID für Ping (optional)", placeholder="123456789012345678")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Webhook speichern", type="primary", use_container_width=True):
            if profile_name and url:
                try:
                    conn = utils.get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO webhooks (username, profile_name, url, plattform, role_id)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (username, profile_name) 
                        DO UPDATE SET url = EXCLUDED.url, plattform = EXCLUDED.plattform, role_id = EXCLUDED.role_id
                    """, (current_user, profile_name, url, plattform, role_id))
                    cursor.close()
                    conn.close()
                    st.success(f"✅ Webhook '{profile_name}' erfolgreich gesichert!")
                except Exception as e:
                    st.error(f"Datenbankfehler: {e}")
            else:
                st.error("⚠️ Profilname und URL sind Pflichtfelder!")

with col_test:
    st.markdown("### 🚀 Schneller Live-Test")
    
    # Vorhandene Webhooks aus DB laden
    conn = utils.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_name, url FROM webhooks WHERE username = %s", (current_user,))
    saved_webhooks = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if saved_webhooks:
        webhook_options = {row["profile_name"]: row["url"] for row in saved_webhooks}
        selected_hook = st.selectbox("Wähle ein Profil für den Test", list(webhook_options.keys()))
        test_msg = st.text_area("Test-Nachricht", placeholder="Hallo Server! Das ist ein Test aus meinem Command Center.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💥 Testnachricht absenden", use_container_width=True):
            if test_msg:
                success, msg = utils.send_discord_webhook(webhook_options[selected_hook], text_content=test_msg)
                if success: st.success(msg)
                else: st.error(msg)
            else:
                st.error("⚠️ Bitte gib eine Nachricht für den Test ein.")
    else:
        st.info("ℹ️ Sobald du links deinen ersten Webhook speicherst, kannst du ihn hier direkt testen!")