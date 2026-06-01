import streamlit as st
import utils

current_user = utils.check_login()

st.title("📢 Social Media Post Creator")
st.markdown("Erstelle Ankündigungen und teile Links direkt in deinen Discord-Kanälen.")
st.markdown("---")

conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, url, role_id FROM webhooks WHERE username = %s", (current_user,))
all_hooks = cursor.fetchall()
cursor.close(); conn.close()

if not all_hooks:
    st.warning("⚠️ Du hast noch keine Webhooks eingerichtet.")
    st.stop()

col_editor, col_preview = st.columns(2)

with col_editor:
    st.markdown("### ✍️ Post entwerfen")
    hook_options = {h["profile_name"]: {"url": h["url"], "role_id": h["role_id"]} for h in all_hooks}
    selected_hook = st.selectbox("In welchen Kanal soll gepostet werden?", list(hook_options.keys()))
    
    post_text = st.text_area("Dein Nachrichtentext", placeholder="Hey Leute! Mein neues Video ist online!", height=150)
    post_link = st.text_input("Link anfügen (Optional)", placeholder="https://youtube.com/...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Jetzt auf Discord posten", type="primary", use_container_width=True):
        if post_text or post_link:
            selected_data = hook_options[selected_hook]
            role_ping = f"<@&{selected_data['role_id']}>\n\n" if selected_data['role_id'] else ""
            base_text = f"{post_text}\n\n{post_link}" if post_link else post_text
            final_msg = f"{role_ping}{base_text}"
            
            success, msg = utils.send_discord_webhook(selected_data["url"], text_content=final_msg)
            if success: st.success("✅ Erfolgreich an Discord gesendet!")
            else: st.error(f"Fehler: {msg}")
        else:
            st.error("⚠️ Bitte gib einen Text oder einen Link ein.")

with col_preview:
    st.markdown("### 👀 Ungefähre Vorschau")
    
    # Lokale Fallbacks für die Discord-interne Container-Vorschau
    is_dark = st.session_state.get("theme", "Midnight (Dark)") == "Midnight (Dark)"
    preview_bg = "#36393F" if is_dark else "#F2F3F5"
    preview_text = "#DCDDDE" if is_dark else "#2E3338"
    
    active_role = hook_options[selected_hook].get("role_id")
    ping_preview = f"<span style='color: #7289DA; background-color: rgba(114, 137, 218, 0.1); padding: 0 4px; border-radius: 3px;'>@Rolle ({active_role})</span><br><br>" if active_role else ""
    
    st.markdown(f"""
    <div style="background-color: {preview_bg}; padding: 15px; border-radius: 8px; border-left: 4px solid #5865F2;">
        <p style="color: #DCAE96; margin-bottom: 5px; font-weight: bold;">{current_user} <span style="background-color: #5865F2; color: white; padding: 2px 5px; border-radius: 3px; font-size: 10px;">BOT</span></p>
        <p style="color: {preview_text}; white-space: pre-wrap; font-family: 'Inter', sans-serif;">{ping_preview}{post_text if post_text else '*Dein Text erscheint hier...*'}</p>
        <p style="color: #00AFF4;">{post_link if post_link else ''}</p>
    </div>
    """, unsafe_allow_html=True)