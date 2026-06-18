import streamlit as st
import utils

current_user = utils.check_login()

st.title("📢 Social Media Post Creator")
st.markdown("Erstelle professionelle Ankündigungen als Rich-Embeds in Discord.")
st.markdown("---")

conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, url, role_id FROM webhooks WHERE username = %s", (current_user,))
all_hooks = cursor.fetchall()
cursor.close()
conn.close()

if not all_hooks:
    st.warning("⚠️ Du hast noch keine Webhooks eingerichtet.")
    st.stop()

col_editor, col_preview = st.columns([1, 1], gap="large")

with col_editor:
    st.markdown("### ✍️ Post entwerfen")
    hook_options = {h["profile_name"]: {"url": h["url"], "role_id": h["role_id"]} for h in all_hooks}
    selected_hook = st.selectbox("In welchen Kanal soll gepostet werden?", list(hook_options.keys()))
    
    st.markdown("#### 🎨 Embed Design")
    embed_title = st.text_input("Titel", placeholder="🔴 LIVE: Neues Video online!")
    post_text = st.text_area("Nachrichtentext", placeholder="Hey Leute! Das Event startet...", height=120)
    
    c1, c2 = st.columns(2)
    with c1:
        post_link = st.text_input("Ziel-Link (Klick auf Titel)", placeholder="https://youtube.com/...")
    with c2:
        embed_color = st.color_picker("Akzentfarbe (Rand)", "#00E5FF")
        
    img_url = st.text_input("Großes Bild (URL)", placeholder="z.B. Link zum YouTube-Thumbnail (Optional)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Jetzt auf Discord posten", type="primary", use_container_width=True):
        if embed_title or post_text:
            selected_data = hook_options[selected_hook]
            role_ping = f"<@&{selected_data['role_id']}>\n" if selected_data['role_id'] else ""
            
            # Farbe von Hex (#00E5FF) zu Dezimal umwandeln (Discord verlangt das so)
            color_int = int(embed_color.lstrip('#'), 16)
            
            # Das JSON-Paket für Discord schnüren
            embed = {
                "title": embed_title,
                "description": post_text,
                "color": color_int,
                "author": {
                    "name": f"{current_user} Command Center"
                }
            }
            if post_link:
                embed["url"] = post_link
            if img_url:
                embed["image"] = {"url": img_url}
                
            success, msg = utils.send_discord_webhook(selected_data["url"], text_content=role_ping, embed_data=embed)
            if success: 
                st.success("✅ Erfolgreich als Rich-Embed an Discord gesendet!")
            else: 
                st.error(f"Fehler: {msg}")
        else:
            st.error("⚠️ Bitte gib zumindest einen Titel oder Text ein.")

with col_preview:
    st.markdown("### 👀 Embed Vorschau")
    
    # Farb-Logik für die lokale Vorschau
    is_dark = st.session_state.get("theme", "Midnight (Dark)") == "Midnight (Dark)"
    preview_bg = "#36393F" if is_dark else "#F2F3F5"
    embed_bg = "#2F3136" if is_dark else "#FFFFFF"
    text_col = "#DCDDDE" if is_dark else "#2E3338"
    
    active_role = hook_options[selected_hook].get("role_id")
    ping_preview = f"<span style='color: #7289DA; background-color: rgba(114, 137, 218, 0.1); padding: 0 4px; border-radius: 3px;'>@Rolle ({active_role})</span><br><br>" if active_role else ""
    
    img_html = f'<img src="{img_url}" style="width: 100%; border-radius: 4px; margin-top: 10px;">' if img_url else ""
    
    # HTML-Struktur, die das typische Discord-Design nachahmt
    st.markdown(f"""
    <div style="background-color: {preview_bg}; padding: 15px; border-radius: 8px;">
        <p style="color: {text_col}; margin-bottom: 5px; font-family: 'Space Grotesk', sans-serif;">{ping_preview}</p>
        <div style="background-color: {embed_bg}; border-left: 4px solid {embed_color}; padding: 15px; border-radius: 4px; font-family: 'Space Grotesk', sans-serif;">
            <p style="font-size: 12px; font-weight: bold; color: {text_col}; margin-bottom: 5px;">{current_user} Command Center</p>
            <h4 style="color: #00AFF4; margin: 0 0 10px 0;">{embed_title if embed_title else 'Titel-Vorschau'}</h4>
            <p style="color: {text_col}; white-space: pre-wrap; font-size: 14px;">{post_text if post_text else 'Dein Text erscheint hier...'}</p>
            {img_html}
        </div>
    </div>
    """, unsafe_allow_html=True)