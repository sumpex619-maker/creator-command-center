import streamlit as st
import utils
import time
import pandas as pd
import requests

current_user = utils.check_login()

# ==============================================================================
# HILFSFUNKTION: TWITCH API LOGIK (Absturzsicher)
# ==============================================================================
def get_twitch_data_safe(username):
    try:
        tw_creds = utils.load_api_credentials(username, "Twitch")
        if not tw_creds or not tw_creds.get("channel_id") or not tw_creds.get("api_key"):
            return None, "Bitte API-Schlüssel eintragen."
        
        client_id = tw_creds["channel_id"]
        client_secret = tw_creds["api_key"]
        
        tw_config = utils.load_data(f"tw_config_{username}", dict)
        channel_name = tw_config.get("channel_name", "")
        
        if not channel_name:
            return None, "Kanalname fehlt in den Einstellungen."
            
        auth_url = 'https://id.twitch.tv/oauth2/token'
        auth_response = requests.post(auth_url, params={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }).json()
        
        if 'access_token' not in auth_response:
            return None, "Login fehlgeschlagen. IDs prüfen."
            
        headers = {
            'Client-ID': client_id, 
            'Authorization': f"Bearer {auth_response['access_token']}"
        }
        
        user_res = requests.get(f'https://api.twitch.tv/helix/users?login={channel_name}', headers=headers).json()
        if not user_res.get('data'):
            return None, f"Kanal '{channel_name}' nicht gefunden."
            
        user_id = user_res['data'][0]['id']
        foll_res = requests.get(f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={user_id}', headers=headers).json()
        followers = foll_res.get('total', 0)
        
        return {"followers": followers}, None
        
    except Exception as e:
        return None, "Verbindungsfehler zur API"

# ==============================================================================
# HOMEPAGE DESIGN ENGINE 2.0 (Clean & High Contrast)
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
# DATEN MANAGEMENT (Nur noch Stats, kein Discord mehr)
# ==============================================================================
stats_data = utils.load_data(f"stats_{current_user}", dict)

st.title("📊 Übersicht & Statistik")
st.markdown("Dein zentraler Ort, um deine Entwicklungen auf allen Plattformen zu tracken.")
st.markdown("---")

# ==============================================================================
# EBENE 1: LIVE API-STATISTIKEN (YOUTUBE & TWITCH FOLLOWER)
# ==============================================================================
st.subheader("📡 Aktuelle Live-Daten")

col_live_yt, col_live_tw = st.columns(2)

with col_live_yt:
    yt_stats, yt_error = utils.fetch_youtube_stats(current_user)
    if yt_stats:
        c_api1, c_api2, c_api3 = st.columns(3)
        with c_api1:
            st.markdown(f'<div class="bento-card" style="text-align: center; padding: 15px !important;"><p style="margin:0; font-size:13px; opacity:0.7;">YT Abonnenten</p><h3 style="margin:5px 0 0 0; color:{PRIM}; font-size:24px;">{yt_stats["subscribers"]:,}</h3></div>', unsafe_allow_html=True)
        with c_api2:
            st.markdown(f'<div class="bento-card" style="text-align: center; padding: 15px !important;"><p style="margin:0; font-size:13px; opacity:0.7;">YT Gesamt-Aufrufe</p><h3 style="margin:5px 0 0 0; color:#818CF8; font-size:24px;">{yt_stats["views"]:,}</h3></div>', unsafe_allow_html=True)
        with c_api3:
            st.markdown(f'<div class="bento-card" style="text-align: center; padding: 15px !important;"><p style="margin:0; font-size:13px; opacity:0.7;">YT Videos</p><h3 style="margin:5px 0 0 0; color:#F43F5E; font-size:24px;">{yt_stats["videos"]:,}</h3></div>', unsafe_allow_html=True)
    else:
        st.info("🔴 YouTube API nicht verbunden.")

with col_live_tw:
    tw_stats, tw_error = get_twitch_data_safe(current_user)
    if tw_stats:
        followers = tw_stats.get("followers", 0)
        f_str = f"{followers:,}" if isinstance(followers, int) else followers
        st.markdown(f'<div class="bento-card" style="text-align: center; padding: 15px !important;"><p style="margin:0; font-size:13px; opacity:0.7;">Twitch Live-Follower</p><h3 style="margin:5px 0 0 0; color:#A855F7; font-size:24px;">{f_str}</h3></div>', unsafe_allow_html=True)
    else:
        st.info("🟪 Twitch API nicht verbunden.")

with st.expander("⚙️ API-Schlüssel verwalten"):
    t_yt, t_tw = st.tabs(["YouTube Einstellungen", "Twitch Einstellungen"])
    with t_yt:
        existing_creds = utils.load_api_credentials(current_user, "YouTube")
        with st.form("yt_api_form"):
            new_channel = st.text_input("YouTube Kanal-ID", value=existing_creds["channel_id"] if existing_creds else "")
            new_key = st.text_input("YouTube API-Key", value=existing_creds["api_key"] if existing_creds else "", type="password")
            if st.form_submit_button("Speichern"):
                if new_channel and new_key:
                    utils.save_api_credentials(current_user, "YouTube", new_channel, new_key)
                    st.rerun()
    with t_tw:
        tw_creds = utils.load_api_credentials(current_user, "Twitch")
        tw_config = utils.load_data(f"tw_config_{current_user}", dict)
        with st.form("tw_api_form"):
            tw_name = st.text_input("Twitch Kanalname", value=tw_config.get("channel_name", ""))
            tw_id = st.text_input("Twitch Client-ID", value=tw_creds["channel_id"] if tw_creds else "")
            tw_sec = st.text_input("Twitch Client Secret", value=tw_creds["api_key"] if tw_creds else "", type="password")
            if st.form_submit_button("Speichern"):
                if tw_id and tw_sec and tw_name:
                    utils.save_api_credentials(current_user, "Twitch", tw_id, tw_sec)
                    tw_config["channel_name"] = tw_name
                    utils.save_data(f"tw_config_{current_user}", tw_config)
                    st.rerun()

st.markdown("---")

# ==============================================================================
# EBENE 2: DIE ENTWICKLUNGS-ÜBERSICHT (Visualisierung)
# ==============================================================================
st.subheader("📈 Deine Entwicklung im Überblick")

if stats_data:
    chart_rows = []
    # Nur saubere Einträge verarbeiten
    valid_posts = {k: v for k, v in stats_data.items() if isinstance(v, dict)}
    
    # Historie aufsteigend sortieren für das Diagramm (älteste zuerst)
    sorted_for_chart = sorted(valid_posts.items(), key=lambda x: x[0])
    
    for p_id, p_info in sorted_for_chart:
        chart_rows.append({
            "Eintrag": p_info.get("title", "Ohne Titel"),
            "Aufrufe / Ø Zuschauer": p_info.get("views", 0),
            "Likes / Subs": p_info.get("likes", 0),
            "Kommentare / Follower": p_info.get("comments", 0),
            "Shares / Peak": p_info.get("shares", 0),
            "Plattform": p_info.get("platform", "Allgemein")
        })
        
    if chart_rows:
        df_stats = pd.DataFrame(chart_rows)
        
        c_ctrl1, c_ctrl2 = st.columns([3, 2])
        with c_ctrl1:
            ausgewaehlte_metrik = st.selectbox(
                "Welche Metrik möchtest du vergleichen?",
                ["Aufrufe / Ø Zuschauer", "Likes / Subs", "Kommentare / Follower", "Shares / Peak"]
            )
        
        # Liniendiagramm zeigt die Entwicklung chronologisch
        df_chart = df_stats.set_index("Eintrag")[[ausgewaehlte_metrik]]
        st.line_chart(df_chart, color=PRIM, use_container_width=True)
    else:
        st.info("Deine gespeicherten Daten sind fehlerhaft. Bitte lege neue an.")
else:
    st.info("Trage unten deine ersten Werte ein, um hier deine Entwicklungslinie zu sehen.")

st.markdown("---")

# ==============================================================================
# EBENE 3: SIMPLE EINGABE & SAUBERES ARCHIV
# ==============================================================================
col_eingabe, col_historie = st.columns([2, 3], gap="large")

# --- LINKS: REINE EINGABE ---
with col_eingabe:
    st.subheader("📝 Werte eintragen")
    
    plattform = st.selectbox("Plattform", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X (Twitter)"])
    post_format = st.selectbox("Format", ["Normaler Post / Video", "Short / Reel / TikTok", "Livestream"])
    
    if post_format == "Livestream":
        l_m1, l_m2, l_m3, l_m4 = "Ø Zuschauer (CCV)", "Peak Zuschauer", "Neue Follower", "Neue Subs"
        ph = f"{plattform} Stream"
    else:
        l_m1, l_m2, l_m3, l_m4 = "Views / Klicks", "Likes", "Kommentare", "Shares"
        ph = f"{plattform} Post"
        
    with st.form("stats_entry_form", clear_on_submit=True):
        post_title = st.text_input("Kurzer Titel / Beschreibung", placeholder=ph)
        
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            m1_val = st.number_input(l_m1, min_value=0, step=1, value=0)
            m3_val = st.number_input(l_m3, min_value=0, step=1, value=0)
        with c_m2:
            m2_val = st.number_input(l_m2, min_value=0, step=1, value=0)
            m4_val = st.number_input(l_m4, min_value=0, step=1, value=0)
            
        if st.form_submit_button("💾 Im Archiv speichern", type="primary", use_container_width=True):
            if post_title:
                post_id = str(int(time.time()))
                stats_data[post_id] = {
                    "title": post_title, "format": post_format, "platform": plattform,
                    "views": m1_val, "likes": m2_val, "comments": m3_val, "shares": m4_val,
                    "date": time.strftime("%d.%m.%Y")
                }
                utils.save_data(f"stats_{current_user}", stats_data)
                st.success("Gespeichert!")
                time.sleep(0.3); st.rerun()

# --- RECHTS: KOMPAKTES ARCHIV ---
with col_historie:
    st.subheader("📋 Letzte Einträge")
    
    if not stats_data:
        st.info("Noch keine Einträge vorhanden.")
    else:
        sorted_posts = sorted({k: v for k, v in stats_data.items() if isinstance(v, dict)}.items(), key=lambda x: x[0], reverse=True)
        
        for p_id, p_info in sorted_posts:
            plt_lower = p_info.get("platform", "").lower()
            if "twitch" in plt_lower: icon = "🟪"
            elif "youtube" in plt_lower: icon = "🔴"
            elif "tiktok" in plt_lower: icon = "🎵"
            elif "instagram" in plt_lower: icon = "📸"
            elif "kick" in plt_lower: icon = "🟢"
            elif "twitter" in plt_lower or "x (" in plt_lower: icon = "🐦"
            else: icon = "🎬"
            
            is_live = p_info.get("format") == "Livestream"
            edit_key = f"edit_{p_id}"
            
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False
                
            with st.container(border=True):
                # Header mit Edit-Buttons oben rechts
                head_col1, head_col2, head_col3 = st.columns([6, 1, 1])
                with head_col1:
                    st.markdown(f"**{icon} {p_info.get('title', 'Eintrag')}**")
                    st.caption(f"{p_info.get('date', '')} • {p_info.get('platform', '')}")
                with head_col2:
                    if st.button("✏️", key=f"btn_ed_{p_id}", help="Bearbeiten"):
                        st.session_state[edit_key] = True; st.rerun()
                with head_col3:
                    if st.button("🗑️", key=f"btn_del_{p_id}", help="Löschen"):
                        del stats_data[p_id]
                        utils.save_data(f"stats_{current_user}", stats_data)
                        st.rerun()
                
                # Bearbeitungs-Modus
                if st.session_state[edit_key]:
                    with st.form(f"form_{p_id}"):
                        e_title = st.text_input("Titel", value=p_info.get("title", ""))
                        ce1, ce2 = st.columns(2)
                        with ce1:
                            e_views = st.number_input("Metrik 1 (Views/CCV)", min_value=0, value=p_info.get("views", 0))
                            e_comms = st.number_input("Metrik 3 (Comms/Follow)", min_value=0, value=p_info.get("comments", 0))
                        with ce2:
                            e_likes = st.number_input("Metrik 2 (Likes/Subs)", min_value=0, value=p_info.get("likes", 0))
                            e_shares = st.number_input("Metrik 4 (Shares/Peak)", min_value=0, value=p_info.get("shares", 0))
                        
                        cs1, cs2 = st.columns(2)
                        with cs1:
                            if st.form_submit_button("Speichern", use_container_width=True):
                                stats_data[p_id].update({"title": e_title, "views": e_views, "likes": e_likes, "comments": e_comms, "shares": e_shares})
                                utils.save_data(f"stats_{current_user}", stats_data)
                                st.session_state[edit_key] = False; st.rerun()
                        with cs2:
                            if st.form_submit_button("Abbrechen", use_container_width=True):
                                st.session_state[edit_key] = False; st.rerun()
                                
                # Normale Ansicht (Werte-Raster)
                else:
                    m1, m2, m3, m4 = st.columns(4)
                    if is_live:
                        m1.metric("Ø CCV", f"{p_info.get('views', 0)}")
                        m2.metric("Subs", f"{p_info.get('likes', 0)}")
                        m3.metric("Follow", f"{p_info.get('comments', 0)}")
                        m4.metric("Peak", f"{p_info.get('shares', 0)}")
                    else:
                        m1.metric("Views", f"{p_info.get('views', 0)}")
                        m2.metric("Likes", f"{p_info.get('likes', 0)}")
                        m3.metric("Comms", f"{p_info.get('comments', 0)}")
                        m4.metric("Shares", f"{p_info.get('shares', 0)}")