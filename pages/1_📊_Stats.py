import streamlit as st
import utils
import time
import pandas as pd

current_user = utils.check_login()

# ==============================================================================
# HOMEPAGE DESIGN ENGINE 2.0 (Glassmorphism & High-End UI)
# ==============================================================================
if "theme" not in st.session_state: st.session_state["theme"] = "Midnight (Dark)"
with st.sidebar:
    new_theme = st.selectbox("🎨 Design", ["Midnight (Dark)", "Clean (Light)"], index=0 if st.session_state["theme"] == "Midnight (Dark)" else 1)
    if new_theme != st.session_state["theme"]: st.session_state["theme"] = new_theme; st.rerun()

if st.session_state["theme"] == "Midnight (Dark)":
    BG, SIDEBAR, CARD, TEXT, BORDER, PRIM = "#0B0F19", "#111827", "rgba(30, 41, 59, 0.6)", "#F8FAFC", "rgba(255, 255, 255, 0.05)", "#38BDF8"
    GLOW = "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
else:
    BG, SIDEBAR, CARD, TEXT, BORDER, PRIM = "#F3F4F6", "#FFFFFF", "rgba(255, 255, 255, 0.8)", "#111827", "rgba(0, 0, 0, 0.05)", "#0284C7"
    GLOW = "0 8px 32px 0 rgba(31, 38, 135, 0.07)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT} !important; }}
    .stApp {{ background-color: {BG} !important; background-image: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.05) 0%, transparent 50%); }}
    h1, h2, h3, h4 {{ font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; color: {TEXT} !important; letter-spacing: -0.5px; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR} !important; border-right: 1px solid {BORDER}; }}
    
    .bento-card, div[data-testid="stExpander"], .stAlert, div[data-testid="stForm"] {{ 
        background: {CARD} !important; 
        backdrop-filter: blur(12px) !important; 
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 20px !important; 
        border: 1px solid {BORDER} !important; 
        padding: 24px !important; 
        box-shadow: {GLOW} !important;
        margin-bottom: 15px; 
    }}
    
    .stButton>button {{ 
        border-radius: 12px !important; 
        background-color: transparent !important; 
        color: {TEXT} !important; 
        border: 1px solid rgba(129, 140, 248, 0.5) !important; 
        font-family: 'Outfit', sans-serif !important; 
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out; 
    }}
    .stButton>button:hover {{ border-color: {PRIM} !important; background-color: rgba(56, 189, 248, 0.1) !important; transform: translateY(-2px); }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, {PRIM} 0%, #818CF8 100%) !important; border: none !important; color: white !important; box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4) !important; }}
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div, .stNumberInput>div>div {{ border-radius: 12px !important; background-color: {SIDEBAR} !important; border: 1px solid {BORDER} !important; color: {TEXT} !important; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATEN MANAGEMENT
# ==============================================================================
conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, url, role_id FROM webhooks WHERE username = %s", (current_user,))
all_hooks = cursor.fetchall()
cursor.close(); conn.close()

stats_data = utils.load_data(f"stats_{current_user}", dict)

st.title("📊 Stats & Content Analytics")
st.markdown("Überwache deine Live-Plattformdaten, analysiere Interaktionsraten und vergleiche deine Beiträge einzeln.")
st.markdown("---")

# ==============================================================================
# EBENE 1: API-VERWALTUNG (YOUTUBE & TWITCH)
# ==============================================================================
st.subheader("📡 Live-Plattformdaten & API-Schnittstellen")
yt_stats, yt_error = utils.fetch_youtube_stats(current_user)

if yt_stats:
    c_api1, c_api2, c_api3 = st.columns(3)
    with c_api1:
        st.markdown(f'<div class="bento-card" style="text-align: center;"><p style="margin:0; font-size:14px; opacity:0.7;">Abonnenten</p><h2 style="margin:5px 0 0 0; color:{PRIM}; font-size:32px;">{yt_stats["subscribers"]:,}</h2></div>', unsafe_allow_html=True)
    with c_api2:
        st.markdown(f'<div class="bento-card" style="text-align: center;"><p style="margin:0; font-size:14px; opacity:0.7;">Gesamte Aufrufe</p><h2 style="margin:5px 0 0 0; color:#818CF8; font-size:32px;">{yt_stats["views"]:,}</h2></div>', unsafe_allow_html=True)
    with c_api3:
        st.markdown(f'<div class="bento-card" style="text-align: center;"><p style="margin:0; font-size:14px; opacity:0.7;">Veröffentlichte Videos</p><h2 style="margin:5px 0 0 0; color:#F43F5E; font-size:32px;">{yt_stats["views"]:,}</h2></div>', unsafe_allow_html=True)
else:
    st.info(f"ℹ️ YouTube Live-Daten inaktiv: {yt_error if yt_error else 'Keine Verbindung eingerichtet.'}")

with st.expander("🔑 API-Schlüssel einrichten / ändern (YouTube & Twitch)"):
    t_yt, t_tw = st.tabs(["🔴 YouTube API", "🟪 Twitch API"])
    with t_yt:
        existing_creds = utils.load_api_credentials(current_user, "YouTube")
        ex_channel = existing_creds["channel_id"] if existing_creds else ""
        ex_key = existing_creds["api_key"] if existing_creds else ""
        with st.form("api_config_form"):
            new_channel = st.text_input("YouTube Kanal-ID (Channel ID)", value=ex_channel)
            new_key = st.text_input("YouTube API-Key", value=ex_key, type="password")
            if st.form_submit_button("💾 YouTube Daten sichern", use_container_width=True):
                if new_channel and new_key:
                    utils.save_api_credentials(current_user, "YouTube", new_channel, new_key)
                    st.success("✅ API-Zugangsdaten erfolgreich aktualisiert!")
                    time.sleep(0.5); st.rerun()
    with t_tw:
        st.info("Bereite hier deine Twitch Developer-Verbindung vor, um zukünftig Daten live auszulesen.")
        tw_creds = utils.load_api_credentials(current_user, "Twitch")
        with st.form("tw_api_form"):
            tw_id = st.text_input("Twitch Client-ID", value=tw_creds["channel_id"] if tw_creds else "")
            tw_sec = st.text_input("Twitch Client Secret", value=tw_creds["api_key"] if tw_creds else "", type="password")
            if st.form_submit_button("💾 Twitch Daten sichern", use_container_width=True):
                if tw_id and tw_sec:
                    utils.save_api_credentials(current_user, "Twitch", tw_id, tw_sec)
                    st.success("✅ Twitch-API-Zugangsdaten erfolgreich hinterlegt!")
                    time.sleep(0.5); st.rerun()

st.markdown("---")

# ==============================================================================
# EBENE 2: GRANULARE ANALYSEN & INTERAKTIONS-GRAFIKEN
# ==============================================================================
st.subheader("📈 Beitrags-Performance & Interaktionsrate")

if stats_data:
    chart_rows = []
    for p_id, p_info in stats_data.items():
        v = p_info.get("views", 0)
        interactions = p_info.get("likes", 0) + p_info.get("comments", 0) + p_info.get("shares", 0)
        er = (interactions / v * 100) if v > 0 else 0.0
        
        chart_rows.append({
            "Beitrag": p_info["title"],
            "Format": p_info["format"],
            "Aufrufe / Ø Zuschauer": v,
            "Likes / Neue Subs": p_info.get("likes", 0),
            "Kommentare / Neue Follower": p_info.get("comments", 0),
            "Shares / Peak": p_info.get("shares", 0),
            "Interaktionsrate (%)": round(er, 2)
        })
    df_stats = pd.DataFrame(chart_rows)
    
    c_ctrl1, c_ctrl2 = st.columns([3, 2])
    with c_ctrl1:
        ausgewaehlte_metrik = st.selectbox(
            "📊 Welche Metrik möchtest du im Diagramm vergleichen?",
            ["Aufrufe / Ø Zuschauer", "Likes / Neue Subs", "Kommentare / Neue Follower", "Shares / Peak", "Interaktionsrate (%)"]
        )
    
    df_chart = df_stats.set_index("Beitrag")[[ausgewaehlte_metrik]]
    st.bar_chart(df_chart, color=PRIM, use_container_width=True)
    
    st.markdown("**🎯 Durchschnittliche Interaktionsrate nach Inhaltstyp:**")
    df_avg_er = df_stats.groupby("Format")["Interaktionsrate (%)"].mean().round(2)
    c_fmt1, c_fmt2, c_fmt3 = st.columns(3)
    
    with c_fmt1:
        val = df_avg_er.get("Short / Reel / TikTok", 0.0)
        st.markdown(f"🎬 **Shorts/Reels:** ` {val}% Ø Rate `")
    with c_fmt2:
        val = df_avg_er.get("Normaler Post / Video", 0.0)
        st.markdown(f"📹 **Videos/Posts:** ` {val}% Ø Rate `")
    with c_fmt3:
        val = df_avg_er.get("Livestream", 0.0)
        st.markdown(f"📺 **Livestreams:** ` {val}% Ø Rate `")
else:
    st.info("📊 Sobald du unten Posts einträgst, erscheinen hier die präzisen Einzel-Diagramme und Interaktionsraten.")

st.markdown("---")

# ==============================================================================
# EBENE 3: MODULARER POST-MANAGER (DYNAMISCHE EINGABE & VERLAUF)
# ==============================================================================
col_eingabe, col_historie = st.columns([2, 3], gap="large")

# --- LINKS: DYNAMISCHE STRUKTURIERTE EINGABE ---
with col_eingabe:
    st.subheader("📝 Daten erfassen")
    
    eingabe_typ = st.selectbox("Was möchtest du eintragen?", ["Twitch (Livestream)", "YouTube / Social Media (VOD/Post)"])
    
    if eingabe_typ == "Twitch (Livestream)":
        with st.form("twitch_entry_form", clear_on_submit=True):
            post_title = st.text_input("Stream Titel / Hauptkategorie", placeholder="z.B. Sim-Racing F1 Liga / Spa")
            st.markdown("**🟪 Stream-Metriken**")
            c_tw1, c_tw2 = st.columns(2)
            with c_tw1:
                ccv = st.number_input("Ø Zuschauer (CCV)", min_value=0, step=1, value=0)
                peak = st.number_input("Peak Zuschauer (Höchstwert)", min_value=0, step=1, value=0)
            with c_tw2:
                new_follow = st.number_input("Neue Follower", min_value=0, step=1, value=0)
                new_subs = st.number_input("Neue Subs / Abonnenten", min_value=0, step=1, value=0)
                
            if st.form_submit_button("💾 Stream-Report speichern", type="primary", use_container_width=True):
                if post_title:
                    post_id = str(int(time.time()))
                    stats_data[post_id] = {
                        "title": post_title, "format": "Livestream", "platform": "Twitch",
                        "views": ccv, "likes": new_subs, "comments": new_follow, "shares": peak,
                        "date": time.strftime("%d.%m.%Y")
                    }
                    utils.save_data(f"stats_{current_user}", stats_data)
                    st.success("🎉 Twitch-Stream erfolgreich archiviert!")
                    time.sleep(0.3); st.rerun()
                    
    else:
        with st.form("stats_entry_form", clear_on_submit=True):
            post_title = st.text_input("Titel des Beitrags", placeholder="z.B. Meisterschaftslauf Highlight-Clip")
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                post_format = st.selectbox("Format (Typ)", ["Short / Reel / TikTok", "Normaler Post / Video"])
            with c_f2:
                plattform = st.selectbox("Plattform", ["YouTube", "TikTok", "Instagram", "Kick", "X (Twitter)", "Allgemein"])
                
            st.markdown("**🔢 Performance-Zahlen**")
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                views = st.number_input("Views / Klicks", min_value=0, step=1, value=0)
                comments = st.number_input("Kommentare", min_value=0, step=1, value=0)
            with c_m2:
                likes = st.number_input("Likes / Gefällt mir", min_value=0, step=1, value=0)
                shares = st.number_input("Teilungen / Shares", min_value=0, step=1, value=0)
                
            if st.form_submit_button("💾 Post-Daten speichern", type="primary", use_container_width=True):
                if post_title:
                    post_id = str(int(time.time()))
                    stats_data[post_id] = {
                        "title": post_title, "format": post_format, "platform": plattform,
                        "views": views, "likes": likes, "comments": comments, "shares": shares,
                        "date": time.strftime("%d.%m.%Y")
                    }
                    utils.save_data(f"stats_{current_user}", stats_data)
                    st.success("🎉 Beitrag erfolgreich archiviert!")
                    time.sleep(0.3); st.rerun()

# --- RECHTS: VERLAUF MIT EDITIER-OPTION (AUTOMATISCHE ANPASSUNG AN PLATTFORM)
with col_historie:
    st.subheader("📋 Beitrags-Archiv & Reports")
    
    if not stats_data:
        st.info("Noch keine Einträge erfasst.")
    else:
        sorted_posts = sorted(stats_data.items(), key=lambda x: x[0], reverse=True)
        
        for p_id, p_info in sorted_posts:
            is_twitch = p_info.get("platform") == "Twitch"
            format_emoji = "🟪" if is_twitch else ("🎬" if "Short" in p_info["format"] else "📹")
            
            v_single = p_info.get("views", 0)
            inter_single = p_info.get("likes", 0) + p_info.get("comments", 0) + p_info.get("shares", 0)
            er_single = (inter_single / v_single * 100) if v_single > 0 else 0.0
            
            edit_state_key = f"edit_stat_active_{p_id}"
            if edit_state_key not in st.session_state:
                st.session_state[edit_state_key] = False
                
            with st.container(border=True):
                st.markdown(f"### {format_emoji} {p_info['title']}")
                st.markdown(f"📅 {p_info['date']} | 🌐 `{p_info['platform']}` | 📁 `{p_info['format']}`")
                
                # Metriken je nach Typ umbenennen
                m1, m2, m3 = st.columns(3)
                if is_twitch:
                    m1.metric("🎥 Ø Zuschauer (CCV)", f"{p_info['views']:,}")
                    m2.metric("💎 Neue Subs", f"{p_info['likes']:,}")
                    m3.metric("🎯 Aktivitätsrate", f"{er_single:.2f}%")
                else:
                    m1.metric("👀 Views", f"{p_info['views']:,}")
                    m2.metric("❤️ Likes", f"{p_info['likes']:,}")
                    m3.metric("📈 Interaktionsrate", f"{er_single:.2f}%")
                
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                
                # --- AKTIVER BEARBEITUNGSMODUS ---
                if st.session_state[edit_state_key]:
                    st.markdown("---")
                    st.markdown("**✏️ Daten anpassen**")
                    with st.form(f"form_edit_stat_{p_id}"):
                        edit_title = st.text_input("Titel", value=p_info["title"])
                        
                        if is_twitch:
                            ce1, ce2 = st.columns(2)
                            with ce1:
                                edit_views = st.number_input("Ø Zuschauer (CCV)", min_value=0, value=p_info["views"])
                                edit_comments = st.number_input("Neue Follower", min_value=0, value=p_info.get("comments", 0))
                            with ce2:
                                edit_likes = st.number_input("Neue Subs", min_value=0, value=p_info.get("likes", 0))
                                edit_shares = st.number_input("Peak Zuschauer", min_value=0, value=p_info.get("shares", 0))
                        else:
                            edit_format = st.selectbox("Format", ["Short / Reel / TikTok", "Normaler Post / Video"], index=["Short / Reel / TikTok", "Normaler Post / Video"].index(p_info["format"]) if p_info["format"] in ["Short / Reel / TikTok", "Normaler Post / Video"] else 0)
                            edit_platform = st.selectbox("Plattform", ["YouTube", "TikTok", "Instagram", "Kick", "X (Twitter)", "Allgemein"], index=["YouTube", "TikTok", "Instagram", "Kick", "X (Twitter)", "Allgemein"].index(p_info["platform"]) if p_info["platform"] in ["YouTube", "TikTok", "Instagram", "Kick", "X (Twitter)", "Allgemein"] else 0)
                            ce1, ce2 = st.columns(2)
                            with ce1:
                                edit_views = st.number_input("Views", min_value=0, value=p_info["views"])
                                edit_comments = st.number_input("Kommentare", min_value=0, value=p_info.get("comments", 0))
                            with ce2:
                                edit_likes = st.number_input("Likes", min_value=0, value=p_info.get("likes", 0))
                                edit_shares = st.number_input("Shares", min_value=0, value=p_info.get("shares", 0))
                            
                        c_sub1, c_sub2 = st.columns(2)
                        with c_sub1:
                            if st.form_submit_button("💾 Übernehmen", use_container_width=True):
                                stats_data[p_id] = {
                                    "title": edit_title, 
                                    "format": "Livestream" if is_twitch else edit_format, 
                                    "platform": "Twitch" if is_twitch else edit_platform,
                                    "views": edit_views, "likes": edit_likes, "comments": edit_comments, "shares": edit_shares,
                                    "date": p_info["date"]
                                }
                                utils.save_data(f"stats_{current_user}", stats_data)
                                st.session_state[edit_state_key] = False
                                st.success("Aktualisiert!")
                                time.sleep(0.3); st.rerun()
                        with c_sub2:
                            if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                                st.session_state[edit_state_key] = False; st.rerun()
                
                # --- NORMALANSICHT: DISCORD ALERTS & CONTROL BAR ---
                else:
                    if all_hooks:
                        hook_options = {h[0]: {"url": h[1], "role_id": h[2]} for h in all_hooks}
                        c_sel, c_btn, c_edit, c_del = st.columns([1.5, 1.5, 0.6, 0.6])
                        
                        with c_sel:
                            selected_hook = st.selectbox("Kanal", list(hook_options.keys()), key=f"hk_{p_id}")
                        with c_btn:
                            if st.button("🚀 Report", key=f"send_{p_id}", use_container_width=True):
                                hook_data = hook_options[selected_hook]
                                role_ping = f"<@&{hook_data['role_id']}>\n\n" if hook_data["role_id"] else ""
                                
                                # Discord-Text dynamisch generieren je nach Kanaltyp
                                if is_twitch:
                                    discord_msg = (
                                        f"{role_ping}🟪 **TWITCH STREAM PERFORMANCE REPORT** 🟪\n\n"
                                        f"📌 **Stream:** {p_info['title']}\n"
                                        f"----------------------------------------\n"
                                        f"🎥 **Ø Zuschauer (CCV):** {p_info['views']:,}\n"
                                        f"🔥 **Peak Zuschauer:** {p_info.get('shares', 0):,}\n"
                                        f"💜 **Neue Follower:** {p_info.get('comments', 0):,}\n"
                                        f"💎 **Neue Subs:** {p_info.get('likes', 0):,}\n"
                                        f"🎯 **Aktivitätsrate:** {er_single:.2f}%\n\n"
                                        f"📈 *Statistiken wurden über das Creator Dashboard exportiert!*"
                                    )
                                else:
                                    discord_msg = (
                                        f"{role_ping}📊 **POST PERFORMANCE REPORT** 📊\n\n"
                                        f"📌 **Beitrag:** {p_info['title']}\n"
                                        f"🌐 **Plattform:** {p_info['platform']} | {format_emoji} **Format:** {p_info['format']}\n"
                                        f"----------------------------------------\n"
                                        f"👀 **Aufrufe (Views):** {p_info['views']:,}\n"
                                        f"❤️ **Gefällt mir (Likes):** {p_info['likes']:,}\n"
                                        f"💬 **Kommentare:** {p_info.get('comments', 0):,}\n"
                                        f"🔗 **Teilungen (Shares):** {p_info.get('shares', 0):,}\n"
                                        f"🎯 **Interaktionsrate:** {er_single:.2f}%\n\n"
                                        f"📈 *Statistiken wurden über das Creator Dashboard exportiert!*"
                                    )
                                success, resp = utils.send_discord_webhook(hook_data["url"], text_content=discord_msg)
                                if success: st.success("Gesendet!")
                        with c_edit:
                            if st.button("✏️", key=f"edt_{p_id}", use_container_width=True, help="Daten bearbeiten"):
                                st.session_state[edit_state_key] = True; st.rerun()
                        with c_del:
                            if st.button("🗑️", key=f"del_{p_id}", use_container_width=True, help="Eintrag löschen"):
                                del stats_data[p_id]
                                utils.save_data(f"stats_{current_user}", stats_data)
                                st.rerun()
                    else:
                        st.caption("ℹ️ Richte Webhooks ein, um diese Reports nach Discord zu senden.")