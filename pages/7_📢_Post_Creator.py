import streamlit as st
import utils

current_user = utils.check_login()

# ==============================================================================
# UNIVERSAL DESIGN ENGINE (Light & Dark Mode)
# ==============================================================================
if "theme" not in st.session_state: st.session_state["theme"] = "Midnight (Dark)"
with st.sidebar:
    new_theme = st.selectbox("🎨 Design", ["Midnight (Dark)", "Clean (Light)"], index=0 if st.session_state["theme"] == "Midnight (Dark)" else 1)
    if new_theme != st.session_state["theme"]: st.session_state["theme"] = new_theme; st.rerun()

if st.session_state["theme"] == "Midnight (Dark)":
    BG = "#0F172A"; SIDEBAR = "#1E293B"; CARD = "rgba(30, 41, 59, 0.4)"; TEXT = "#F8FAFC"; BORDER = "rgba(255, 255, 255, 0.08)"; PRIM = "#38BDF8"
else:
    BG = "#F8FAFC"; SIDEBAR = "#F1F5F9"; CARD = "#FFFFFF"; TEXT = "#0F172A"; BORDER = "rgba(0, 0, 0, 0.1)"; PRIM = "#0284C7"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT} !important; }}
    .stApp {{ background-color: {BG} !important; }}
    h1, h2, h3, h4 {{ font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: {TEXT} !important; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR} !important; border-right: 1px solid {BORDER}; }}
    .bento-card, div[data-testid="stExpander"], .stAlert {{ background-color: {CARD} !important; border-radius: 16px !important; border: 1px solid {BORDER} !important; padding: 20px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; margin-bottom: 15px; }}
    .stButton>button {{ border-radius: 10px !important; background-color: {SIDEBAR} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; font-family: 'Outfit', sans-serif !important; transition: all 0.2s; }}
    .stButton>button:hover {{ border-color: {PRIM} !important; transform: translateY(-2px); }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, {PRIM} 0%, #818CF8 100%) !important; border: none !important; color: white !important; }}
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR} !important; border: 1px solid {BORDER} !important; color: {TEXT} !important; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SEITENINHALT
# ==============================================================================
st.title("📢 Social Media Post Creator")
st.markdown("Erstelle Ankündigungen und teile Links direkt in deinen Discord-Kanälen.")
st.markdown("---")

conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, url FROM webhooks WHERE username = %s", (current_user,))
all_hooks = cursor.fetchall()
cursor.close(); conn.close()

if not all_hooks:
    st.warning("⚠️ Du hast noch keine Webhooks eingerichtet.")
    st.info("Gehe links im Menü auf '⚙️ Webhook Settings', um deinen Discord-Kanal zu verbinden.")
    st.stop()

col_editor, col_preview = st.columns(2)

with col_editor:
    st.markdown("### ✍️ Post entwerfen")
    hook_options = {h["profile_name"]: h["url"] for h in all_hooks}
    selected_hook = st.selectbox("In welchen Kanal soll gepostet werden?", list(hook_options.keys()))
    
    post_text = st.text_area("Dein Nachrichtentext", placeholder="Hey Leute! Mein neues Video ist online! @everyone", height=150)
    post_link = st.text_input("Link anfügen (Optional)", placeholder="https://youtube.com/...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Jetzt auf Discord posten", type="primary", use_container_width=True):
        if post_text or post_link:
            final_msg = f"{post_text}\n\n{post_link}" if post_link else post_text
            success, msg = utils.send_discord_webhook(hook_options[selected_hook], text_content=final_msg)
            if success: st.success("✅ Erfolgreich an Discord gesendet!")
            else: st.error(f"Fehler: {msg}")
        else:
            st.error("⚠️ Bitte gib einen Text oder einen Link ein.")

with col_preview:
    st.markdown("### 👀 Ungefähre Vorschau")
    st.info("So ähnlich wird dein Post in Discord aussehen:")
    
    # Vorschau-Mockup (passt sich dem Dark/Light Mode an)
    preview_bg = "#36393F" if st.session_state["theme"] == "Midnight (Dark)" else "#F2F3F5"
    preview_text = "#DCDDDE" if st.session_state["theme"] == "Midnight (Dark)" else "#2E3338"
    
    st.markdown(f"""
    <div style="background-color: {preview_bg}; padding: 15px; border-radius: 8px; border-left: 4px solid #5865F2;">
        <p style="color: #DCAE96; margin-bottom: 5px; font-weight: bold;">{current_user} <span style="background-color: #5865F2; color: white; padding: 2px 5px; border-radius: 3px; font-size: 10px;">BOT</span></p>
        <p style="color: {preview_text}; white-space: pre-wrap;">{post_text if post_text else '*Dein Text erscheint hier...*'}</p>
        <p style="color: #00AFF4;">{post_link if post_link else ''}</p>
    </div>
    """, unsafe_allow_html=True)