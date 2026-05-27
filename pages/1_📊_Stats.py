import streamlit as st
import utils
import time
import pandas as pd

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
# DATEN LADEN & WEBHOOKS HIERARCHIE
# ==============================================================================
conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, url, role_id FROM webhooks WHERE username = %s", (current_user,))
all_hooks = cursor.fetchall()
cursor.close(); conn.close()

# Datenbank-Key ohne Doppel-Unterstrich, um mit utils.load_data kompatibel zu bleiben
stats_data = utils.load_data(f"stats_{current_user}", dict)

st.title("📊 Stats & Content Analytics")
st.markdown("Überwache deine Live-Plattformdaten, vergleiche Formate grafisch und verwalte deine Post-Historie.")
st.markdown("---")

# ==============================================================================
# EBENE 1: LIVE API-STATISTIKEN (YOUTUBE)
# ==============================================================================
st.subheader("🔴 Live-Kanaldaten (YouTube API)")

yt_stats, yt_error = utils.fetch_youtube_stats(current_user)

if yt_stats:
    # Stylischer Bento-Grid-Zähler für die Live-Statistiken
    c_api1, c_api2, c_api3 = st.columns(3)
    with c_api1:
        st.markdown(f'<div class="bento-card" style="text-align: center;"><p style="margin:0; font-size:14px; opacity:0.7;">Abonnenten</p><h2 style="margin:5px 0 0 0; color:{PRIM}; font-size:32px;">{yt_stats["subscribers"]:,}</h2></div>', unsafe_allow_html=True)
    with c_api2:
        st.markdown(f'<div class="bento-card" style="text-align: center;"><p style="margin:0; font-size:14px; opacity:0.7;">Gesamte Aufrufe</p><h2 style="margin:5px 0 0 0; color:#818CF8; font-size:32px;">{yt_stats["views"]:,}</h2></div>', unsafe_allow_html=True)
    with c_api3:
        st.markdown(f'<div class="bento-card" style="text-align: center;"><p style="margin:0; font-size:14px; opacity:0.7;">Veröffentlichte Videos</p><h2 style="margin:5px 0 0 0; color:#F43F5E; font-size:32px;">{yt_stats["videos"]:,}</h2></div>', unsafe_allow_html=True)
else:
    st.info(f"ℹ️ YouTube Live-Daten inaktiv: {yt_error if yt_error else 'Keine Verbindung eingerichtet.'}")

# Ausklappbare API-Verwaltung für den Creator
with st.expander("🔑 YouTube API-Schlüssel einrichten / ändern"):
    existing_creds = utils.load_api_credentials(current_user, "YouTube")
    ex_channel = existing_creds["channel_id"] if existing_creds else ""
    ex_key = existing_creds["api_key"] if existing_creds else ""
    
    with st.form("api_config_form"):
        new_channel = st.text_input("YouTube Kanal-ID (Channel ID)", value=ex_channel, placeholder="UC...", help="Zu finden in den erweiterten YouTube-Kontoeinstellungen.")
        new_key = st.text_input("YouTube API-Key (Google Cloud Console)", value=ex_key, type="password", placeholder="AIzaSy...")
        
        if st.form_submit_button("💾 API-Daten sichern", use_container_width=True):
            if new_channel and new_key:
                utils.save_api_credentials(current_user, "YouTube", new_channel, new_key)
                st.success("✅ API-Zugangsdaten erfolgreich aktualisiert! Lade Daten neu...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("⚠️ Bitte fülle beide Felder aus!")

st.markdown("---")

# ==============================================================================
# EBENE 2: ANALYSEN & GRAFIKEN (VISUALISIERUNG DER POST-PERFORMANCE)
# ==============================================================================
st.subheader("📈 Format-Performance im Vergleich")

if stats_data:
    # Daten für das Diagramm aufbereiten
    chart_rows = []
    for p_id, p_info in stats_data.items():
        chart_rows.append({
            "Format": p_info["format"],
            "Aufrufe (Views)": p_info["views"],
            "Likes": p_info["likes"]
        })
    df_stats = pd.DataFrame(chart_rows)
    
    # Aggregieren nach Format
    df_grouped = df_stats.groupby("Format")[["Aufrufe (Views)", "Likes"]].sum()
    
    # Layout für Grafiken
    c_graph1, c_graph2 = st.columns([2, 1])
    with c_graph1:
        st.markdown("**Gesamte Aufrufe nach Inhaltstyp**")
        st.bar_chart(df_grouped["Aufrufe (Views)"], color=PRIM)
    with c_graph2:
        st.markdown("**Durchschnittliche Performance**")
        df_avg = df_stats.groupby("Format")["Aufrufe (Views)"].mean().round(1)
        for fmt, avg_val in df_avg.items():
            st.markdown(f"**{fmt}:**")
            st.code(f"{int(avg_val):,} Ø Views / Post")
else:
    st.info("📊 Sobald du unten deine ersten Post-Daten einträgst, wird hier automatisch eine visuelle Analyse generiert.")

st.markdown("---")

# ==============================================================================
# EBENE 3: MODULARER POST-MANAGER (SIDE-BY-SIDE DESIGN)
# ==============================================================================
col_eingabe, col_historie = st.columns([2, 3], gap="large")

# --- LINKE SPALTE: POSTS MANUELL ERFASSEN ---
with col_eingabe:
    st.subheader("📝 Neuen Post erfassen")
    with st.form("stats_entry_form", clear_on_submit=True):
        post_title = st.text_input("Titel des Beitrags", placeholder="z.B. Meisterschaftslauf Spa-Francorchamps")
        
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            post_format = st.selectbox("Format (Typ)", ["Short / Reel / TikTok", "Normaler Post / Video", "Livestream"])
        with c_f2:
            plattform = st.selectbox("Plattform", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X (Twitter)", "Allgemein"])
            
        st.markdown("**🔢 Performance-Zahlen**")
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            views = st.number_input("Views / Klicks", min_value=0, step=1, value=0)
            comments = st.number_input("Kommentare", min_value=0, step=1, value=0)
        with c_m2:
            likes = st.number_input("Likes / Gefällt mir", min_value=0, step=1, value=0)
            shares = st.number_input("Teilungen / Shares", min_value=0, step=1, value=0)
            
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Post-Daten speichern", type="primary", use_container_width=True):
            if post_title:
                post_id = str(int(time.time()))
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
                utils.save_data(f"stats_{current_user}", stats_data)
                st.success(f"🎉 '{post_title}' wurde archiviert!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("⚠️ Bitte gib dem Post einen gültigen Titel.")

# --- RECHTE SPALTE: HISTORIE & DISCORD EXPORT ---
with col_historie:
    st.subheader("📋 Beitrags-Archiv & Reports")
    
    if not stats_data:
        st.info("Noch keine Beiträge erfasst. Nutze das linke Menü!")
    else:
        sorted_posts = sorted(stats_data.items(), key=lambda x: x[0], reverse=True)
        
        for p_id, p_info in sorted_posts:
            format_emoji = "🎬" if "Short" in p_info["format"] else ("📹" if "Video" in p_info["format"] else "📺")
            
            with st.container(border=True):
                st.markdown(f"### {format_emoji} {p_info['title']}")
                st.markdown(f"📅 {p_info['date']} | 🌐 `{p_info['platform']}` | 📁 `{p_info['format']}`")
                
                # Performance Grid
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("👀 Views", f"{p_info['views']:,}")
                m2.metric("❤️ Likes", f"{p_info['likes']:,}")
                m3.metric("💬 Komms", f"{p_info['comments']:,}")
                m4.metric("🔗 Shares", f"{p_info['shares']:,}")
                
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                
                # Discord Export Funktionen
                if all_hooks:
                    hook_options = {h[0]: {"url": h[1], "role_id": h[2]} for h in all_hooks}
                    
                    c_sel, c_btn, c_del = st.columns([2, 2, 1])
                    with c_sel:
                        selected_hook = st.selectbox("Kanal wählen", list(hook_options.keys()), key=f"hk_{p_id}")
                    with c_btn:
                        if st.button("🚀 Discord Report", key=f"send_{p_id}", use_container_width=True):
                            hook_data = hook_options[selected_hook]
                            
                            # Automatischer Rollen-Ping Code-Zusammenbau
                            role_ping = f"<@&{hook_data['role_id']}>\n\n" if hook_data["role_id"] else ""
                            
                            discord_msg = (
                                f"{role_ping}📊 **POST PERFORMANCE REPORT** 📊\n\n"
                                f"📌 **Beitrag:** {p_info['title']}\n"
                                f"🌐 **Plattform:** {p_info['platform']} | {format_emoji} **Format:** {p_info['format']}\n"
                                f"----------------------------------------\n"
                                f"👀 **Aufrufe (Views):** {p_info['views']:,}\n"
                                f"❤️ **Gefällt mir (Likes):** {p_info['likes']:,}\n"
                                f"💬 **Kommentare:** {p_info['comments']:,}\n"
                                f"🔗 **Teilungen (Shares):** {p_info['shares']:,}\n\n"
                                f"📈 *Statistiken wurden live über das Creator Dashboard exportiert!*"
                            )
                            
                            success, resp = utils.send_discord_webhook(hook_data["url"], text_content=discord_msg)
                            if success: st.success("Report gesendet!")
                            else: st.error("Fehler beim Senden.")
                    with c_del:
                        if st.button("🗑️", key=f"del_{p_id}", use_container_width=True, help="Eintrag löschen"):
                            del stats_data[p_id]
                            utils.save_data(f"stats_{current_user}", stats_data)
                            st.rerun()
                else:
                    st.caption("ℹ️ Richte in den Webhook-Einstellungen Kanäle ein, um diese Reports an Discord zu senden.")