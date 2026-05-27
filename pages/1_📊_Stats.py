import streamlit as st
import utils
import time

current_user = utils.check_login()

# ==============================================================================
# UNIVERSAL DESIGN ENGINE (Light & Dark Mode)
# ==============================================================================
if "theme" not in st.session_state: st.session_state["theme"] = "Midnight (Dark)"
with st.sidebar:
    new_theme = st.selectbox("🎨 Design", ["Midnight (Dark)", "Clean (Light)"], index=0 if st.session_state["theme"] == "Midnight (Dark)" else 1)
    if new_theme != st.session_state["theme"]: st.session_state["theme"] = new_theme; st.rerun()

if st.session_state["theme"] == "Midnight (Dark)":
    BG, SIDEBAR, CARD, TEXT, BORDER, PRIM = "#0F172A", "#1E293B", "rgba(30, 41, 59, 0.4)", "#F8FAFC", "rgba(255, 255, 255, 0.08)", "#38BDF8"
else:
    BG, SIDEBAR, CARD, TEXT, BORDER, PRIM = "#F8FAFC", "#F1F5F9", "#FFFFFF", "#0F172A", "rgba(0, 0, 0, 0.1)", "#0284C7"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT} !important; }}
    .stApp {{ background-color: {BG} !important; }}
    h1, h2, h3, h4 {{ font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: {TEXT} !important; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR} !important; border-right: 1px solid {BORDER}; }}
    .bento-card, div[data-testid="stExpander"], .stAlert {{ background-color: {CARD} !important; border-radius: 16px !important; border: 1px solid {BORDER} !important; padding: 20px !important; margin-bottom: 15px; }}
    .stButton>button {{ border-radius: 10px !important; background-color: {SIDEBAR} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; font-family: 'Outfit', sans-serif !important; transition: all 0.2s; }}
    .stButton>button:hover {{ border-color: {PRIM} !important; transform: translateY(-2px); }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, {PRIM} 0%, #818CF8 100%) !important; border: none !important; color: white !important; }}
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div, .stNumberInput>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR} !important; border: 1px solid {BORDER} !important; color: {TEXT} !important; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATA HANDLING & WEBHOOKS FETCH
# ==============================================================================
# Vorhandene Webhooks laden, um Reports senden zu können
conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, url, role_id FROM webhooks WHERE username = %s", (current_user,))
all_hooks = cursor.fetchall()
cursor.close(); conn.close()

# Stats-Datenbank (Nutzerbasiert laden)
stats_data = utils.load_data(f"stats_posts_{current_user}", dict)

st.title("📊 Stats & Content Analytics")
st.markdown("Trage deine Beitragsdaten ein, analysiere die Performance deiner Formate und teile deine Meilensteine direkt auf Discord.")
st.markdown("---")

col_eingabe, col_historie = st.columns([2, 3], gap="large")

# --- LINKE SPALTE: POST-DETAILS EINTRAGEN ---
with col_eingabe:
    st.subheader("📝 Neuen Post erfassen")
    
    with st.form("stats_entry_form", clear_on_submit=True):
        post_title = st.text_input("Titel des Posts / Themas", placeholder="z.B. Mein erstes F1 2026 Rennen!")
        
        c_form1, c_form2 = st.columns(2)
        with c_form1:
            post_format = st.selectbox("Inhaltstyp (Format)", ["Short / Reel / TikTok", "Normaler Post / Video", "Livestream"])
        with c_form2:
            plattform = st.selectbox("Plattform", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X (Twitter)", "Allgemein"])
            
        st.markdown("**🔢 Performance-Metriken**")
        c_met1, c_met2 = st.columns(2)
        with c_met1:
            views = st.number_input("Aufrufe / Views", min_value=0, step=1, value=0)
            comments = st.number_input("Kommentare", min_value=0, step=1, value=0)
        with c_met2:
            likes = st.number_input("Gefällt mir / Likes", min_value=0, step=1, value=0)
            shares = st.number_input("Teilungen / Shares", min_value=0, step=1, value=0)
            
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("💾 Post-Daten speichern", type="primary", use_container_width=True)
        
        if submit_btn:
            if post_title:
                post_id = str(int(time.time()))  # Einzigartige ID auf Zeitstempelbasis
                stats_data[post_id] = {
                    "title": post_title,
                    "format": post_format,
                    "platform": plattform,
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "date": time.strftime("%d.%m.%Y")
                }
                utils.save_data(f"stats_posts_{current_user}", stats_data)
                st.success(f"🎉 '{post_title}' wurde erfolgreich gesichert!")
                st.rerun()
            else:
                st.error("⚠️ Bitte gib dem Post einen Namen oder Titel.")

# --- RECHTE SPALTE: POSTS ANZEIGEN & AUF DISCORD POSTEN ---
with col_historie:
    st.subheader("📋 Gespeicherte Beiträge & Export")
    
    if not stats_data:
        st.info("Noch keine Post-Statistiken erfasst. Nutze das linke Formular, um deine ersten Daten einzutragen.")
    else:
        # Posts sortieren (Neueste zuerst)
        sorted_posts = sorted(stats_data.items(), key=lambda x: x[0], reverse=True)
        
        for p_id, p_info in sorted_posts:
            # Emoji je nach Format wählen
            format_emoji = "🎬" if "Short" in p_info["format"] else ("📹" if "Video" in p_info["format"] else "📺")
            
            with st.container(border=True):
                st.markdown(f"### {format_emoji} {p_info['title']}")
                st.markdown(f"📅 **Datum:** {p_info['date']} | 🌐 **Plattform:** `{p_info['platform']}` | 📁 **Format:** `{p_info['format']}`")
                
                # Werte-Übersicht in Kacheln
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("👀 Views", f"{p_info['views']:,}")
                m2.metric("❤️ Likes", f"{p_info['likes']:,}")
                m3.metric("💬 Komms", f"{p_info['comments']:,}")
                m4.metric("🔗 Shares", f"{p_info['shares']:,}")
                
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                
                # Discord Export Sektion innerhalb der Karte
                if all_hooks:
                    hook_options = {h[0]: {"url": h[1], "role_id": h[2]} for h in all_hooks}
                    
                    c_sel, c_btn, c_del = st.columns([2, 2, 1])
                    with c_sel:
                        selected_hook = st.selectbox("Kanal wählen", list(hook_options.keys()), key=f"hk_{p_id}")
                    with c_btn:
                        if st.button("🚀 Discord Alert", key=f"send_{p_id}", use_container_width=True):
                            hook_data = hook_options[selected_hook]
                            
                            # Rollen-Ping vorbereiten
                            role_ping = f"<@&{hook_data['role_id']}>\n\n" if hook_data["role_id"] else ""
                            
                            # Discord-Nachricht lesbar strukturieren
                            discord_msg = (
                                f"{role_ping}📊 **NEUER STATS-REPORT ONLINE!** 📊\n\n"
                                f"📌 **Beitrag:** {p_info['title']}\n"
                                f"🌐 **Plattform:** {p_info['platform']} | {format_emoji} **Typ:** {p_info['format']}\n"
                                f"----------------------------------------\n"
                                f"👀 **Aufrufe (Views):** {p_info['views']:,}\n"
                                f"❤️ **Gefällt mir (Likes):** {p_info['likes']:,}\n"
                                f"💬 **Kommentare:** {p_info['comments']:,}\n"
                                f"🔗 **Teilungen (Shares):** {p_info['shares']:,}\n\n"
                                f"📈 *Gemeinsam wachsen! Danke für euren Support!*"
                            )
                            
                            success, resp = utils.send_discord_webhook(hook_data["url"], text_content=discord_msg)
                            if success: st.success("Post gesendet!")
                            else: st.error("Fehler beim Senden.")
                    with c_del:
                        if st.button("🗑️", key=f"del_{p_id}", use_container_width=True, help="Eintrag aus Statistik löschen"):
                            del stats_data[p_id]
                            utils.save_data(f"stats_posts_{current_user}", stats_data)
                            st.rerun()
                else:
                    st.caption("ℹ️ Um diese Stats auf Discord zu teilen, richte zuerst einen Webhook in den Einstellungen ein.")