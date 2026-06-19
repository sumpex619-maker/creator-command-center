import streamlit as st
import pandas as pd
import utils
import time
import requests
import plotly.express as px

# Login prüfen
current_user = utils.check_login()

st.title("📊 Analytics & Stats Pro")
st.markdown("Automatisiere dein Tracking: Vom gesamten Kanal bis zum einzelnen Post.")
st.markdown("---")

# ==============================================================================
# DATEN & CREDENTIALS LADEN
# ==============================================================================
stats_data = utils.load_data("stats", dict)
if not isinstance(stats_data, dict): stats_data = {}

conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT platform, channel_id, api_key FROM api_credentials WHERE username = %s", (current_user,))
# Das Dictionary speichert jetzt pro Plattform ID und API Key
creds = {row["platform"]: {"channel_id": row["channel_id"], "api_key": row["api_key"]} for row in cursor.fetchall()}
cursor.close()
conn.close()

# ==============================================================================
# TABS FÜR DIE STRUKTUR
# ==============================================================================
t_kanal, t_post, t_dash = st.tabs(["📡 Kanal-Übersicht", "🎬 Einzelne Posts & Videos", "📈 Interaktive Graphen"])

# ------------------------------------------------------------------------------
# TAB 1: KANAL-WACHSTUM (LIVE SYNC)
# ------------------------------------------------------------------------------
with t_kanal:
    st.subheader("Kanal-Daten synchronisieren")
    st.info("Twitch & YouTube können über APIs live abgerufen werden. Für TikTok & Instagram nutze bitte das Formular unten.")
    
    c_plat, c_btn = st.columns([2, 1])
    with c_plat:
        sync_plat = st.selectbox("Plattform wählen:", ["Twitch", "YouTube", "TikTok", "Instagram", "Kick", "X"], key="c_plat")
    with c_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Kanal abrufen", type="primary", use_container_width=True):
            
            # Channel ID auslesen (funktioniert jetzt sicher für mehrere Nutzer)
            channel_name = creds.get(sync_plat, {}).get("channel_id", "")
            
            if not channel_name and sync_plat in ["Twitch", "YouTube"]:
                st.error(f"Bitte hinterlege deine {sync_plat}-ID in den Einstellungen!")
                
            elif sync_plat == "Twitch":
                with st.spinner("Frage Twitch Server ab..."):
                    try:
                        f_res = requests.get(f"https://decapi.me/twitch/followcount/{channel_name}")
                        v_res = requests.get(f"https://decapi.me/twitch/viewercount/{channel_name}")
                        followers = int(f_res.text) if f_res.text.strip().isdigit() else 0
                        viewers = 0 if "offline" in v_res.text.lower() or "error" in v_res.text.lower() else int(v_res.text) if v_res.text.strip().isdigit() else 0
                        
                        post_id = str(int(time.time()))
                        stats_data[post_id] = {
                            "title": f"Live Kanal-Status", "platform": sync_plat, "date": time.strftime("%d.%m.%Y"),
                            "entry_type": "Kanal", "metrics": {"Follower": followers, "Live-Zuschauer": viewers}
                        }
                        utils.save_data("stats", stats_data)
                        st.success(f"✅ Twitch Update: {followers} Follower gespeichert!")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e: 
                        st.error(f"Fehler beim Abruf der Twitch-Daten: {e}")

            elif sync_plat == "YouTube":
                # API Key aus der nutzereigenen Datenbank lesen!
                yt_api_key = creds.get("YouTube", {}).get("api_key", "")
                
                if not yt_api_key:
                    st.error("⚠️ YouTube API Key fehlt! Bitte in deinen Einstellungen unter 'Verknüpfte Accounts' eintragen.")
                else:
                    with st.spinner("Frage YouTube Server ab..."):
                        try:
                            # YouTube Data API v3 Endpoint
                            url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_name}&key={yt_api_key}"
                            res = requests.get(url).json()
                            
                            if "items" in res and len(res["items"]) > 0:
                                stats = res["items"][0]["statistics"]
                                subs = int(stats.get("subscriberCount", 0))
                                views = int(stats.get("viewCount", 0))
                                videos = int(stats.get("videoCount", 0))
                                
                                post_id = str(int(time.time()))
                                stats_data[post_id] = {
                                    "title": f"Live Kanal-Status", "platform": sync_plat, "date": time.strftime("%d.%m.%Y"),
                                    "entry_type": "Kanal", "metrics": {"Abonnenten": subs, "Aufrufe Gesamt": views, "Videos": videos}
                                }
                                utils.save_data("stats", stats_data)
                                st.success(f"✅ YouTube Update: {subs} Abonnenten gespeichert!")
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error("⚠️ Kanal nicht gefunden. Ist die YouTube Channel-ID in den Einstellungen korrekt?")
                        except Exception as e:
                            st.error(f"Fehler beim Abruf der YouTube-Daten: {e}")
            else:
                st.warning(f"API für {sync_plat} Kanäle aktuell nicht verbunden. Bitte manuellen Modus nutzen.")
                
    # Manueller Fallback
    with st.expander("📝 Manuell eintragen (Falls keine API verfügbar)"):
        with st.form("manual_channel"):
            m_plat = st.selectbox("Plattform", ["TikTok", "Instagram", "Kick", "X", "YouTube"])
            c1, c2 = st.columns(2)
            with c1: f_count = st.number_input("Aktuelle Follower / Abos", min_value=0, step=1)
            with c2: v_count = st.number_input("Profilaufrufe / Ø Zuschauer", min_value=0, step=1)
            if st.form_submit_button("💾 Speichern", use_container_width=True):
                stats_data[str(int(time.time()))] = {
                    "title": "Manuelles Update", "platform": m_plat, "date": time.strftime("%d.%m.%Y"),
                    "entry_type": "Kanal", "metrics": {"Follower": f_count, "Aufrufe / Live": v_count}
                }
                utils.save_data("stats", stats_data)
                st.success("✅ Gespeichert!")
                time.sleep(0.5)
                st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: EINZELNE POSTS (MIT API VORBEREITUNG)
# ------------------------------------------------------------------------------
with t_post:
    st.subheader("Post-Performance erfassen")
    p_plat = st.selectbox("Für welche Plattform?", ["YouTube", "TikTok", "Instagram", "Twitch (VOD)", "X", "Kick"], key="p_plat")
    
    with st.container(border=True):
        st.markdown(f"**URL des {p_plat} Posts einfügen (Für zukünftigen API-Scraper)**")
        c_url, c_sync = st.columns([3, 1])
        with c_url:
            post_url = st.text_input("Link zum Video", placeholder="https://...", label_visibility="collapsed")
        with c_sync:
            if st.button("🚀 Daten ziehen", use_container_width=True):
                if not post_url: 
                    st.error("Bitte Link einfügen.")
                else: 
                    st.info("API-Schnittstelle für Einzelposts auf dieser Plattform in Vorbereitung. Bitte trage die Daten kurz unten ein.")
                
    st.markdown("---")
    with st.form("manual_post_form", clear_on_submit=True):
        post_title = st.text_input("Titel des Posts/Videos", placeholder="z.B. Mein neues Sim-Racing Setup")
        c1, c2, c3, c4 = st.columns(4)
        with c1: m_views = st.number_input("Aufrufe", min_value=0, step=1)
        with c2: m_likes = st.number_input("Likes", min_value=0, step=1)
        with c3: m_comms = st.number_input("Kommentare", min_value=0, step=1)
        with c4: m_shares = st.number_input("Shares / Saves", min_value=0, step=1)
        
        if st.form_submit_button("💾 Post-Daten speichern", type="primary", use_container_width=True):
            if post_title:
                stats_data[str(int(time.time()))] = {
                    "title": post_title, "platform": p_plat, "date": time.strftime("%d.%m.%Y"),
                    "entry_type": "Post", "metrics": {"Aufrufe": m_views, "Likes": m_likes, "Kommentare": m_comms, "Shares": m_shares}
                }
                utils.save_data("stats", stats_data)
                st.success("✅ Erfolgreich gespeichert!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Bitte Titel angeben.")

# ------------------------------------------------------------------------------
# TAB 3: DASHBOARD & GRAPHEN
# ------------------------------------------------------------------------------
with t_dash:
    if not stats_data: 
        st.info("Noch keine Daten vorhanden.")
    else:
        view_type = st.radio("Was möchtest du auswerten?", ["Kanal-Wachstum", "Einzelne Posts"], horizontal=True)
        e_type = "Kanal" if view_type == "Kanal-Wachstum" else "Post"
        
        f_plat = st.selectbox("Plattform filtern:", ["Twitch", "YouTube", "TikTok", "Instagram", "Kick", "X"], key="dash_plat")
        
        chart_data = []
        archiv_items = []
        for p_id, p_info in sorted(stats_data.items(), key=lambda x: x[0]):
            item_type = p_info.get("entry_type", "Kanal" if "Auto-Sync" in p_info.get("title", "") else "Post")
            
            if p_info.get("platform") == f_plat and item_type == e_type:
                row = {"Datum": p_info.get('date', ''), "Eintrag": f"{p_info.get('date', '')} - {p_info.get('title', '')}"}
                row.update(p_info.get("metrics", {}))
                chart_data.append(row)
                archiv_items.append((p_id, p_info))
                
        if chart_data:
            df = pd.DataFrame(chart_data)
            metriken = [col for col in df.select_dtypes(include=['number']).columns if col != "Eintrag"]
            if metriken:
                gewaehlte_metrik = st.selectbox("Graph-Metrik:", metriken)
                fig = px.line(df, x="Eintrag", y=gewaehlte_metrik, markers=True, template="plotly_dark")
                fig.update_traces(line_color='#00E5FF', marker=dict(size=8, color='#FFFFFF', line=dict(width=2, color='#00E5FF')))
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="", font=dict(family="Space Grotesk, sans-serif", color="#E0E0E0"))
                st.plotly_chart(fig, use_container_width=True)
                
            # Archiv Liste
            st.markdown(f"#### 📋 Archiv: {view_type}")
            for p_id, p_info in reversed(archiv_items):
                with st.expander(f"{p_info['date']} | {p_info['title']}"):
                    met_cols = st.columns(len(p_info["metrics"]))
                    for idx, (k, v) in enumerate(p_info["metrics"].items()):
                        if idx < len(met_cols): met_cols[idx].metric(k, f"{v}")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Löschen", key=f"del_{p_id}"):
                        del stats_data[p_id]
                        utils.save_data("stats", stats_data)
                        st.rerun()
        else:
            st.info(f"Aktuell noch keine {view_type}-Daten für {f_plat} gespeichert.")