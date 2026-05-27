import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import utils

# ==============================================================================
# SEITEN-KONFIGURATION & LOGIN-CHECK
# ==============================================================================
current_user = utils.check_login()

st.title("📊 Stats & Community Health")
st.markdown("Deine Schaltzentrale für Reichweite und Community-Wachstum.")

tab_eingabe, tab_auswertung = st.tabs([
    "📝 Eingabe & Live-Abruf", 
    "📈 Visuelle Auswertung"
])

# ------------------------------------------------------------------------------
# TAB 1: EINGABE & LIVE-ABRUF
# ------------------------------------------------------------------------------
with tab_eingabe:
    with st.expander("⚙️ API-Zugangsdaten & Automatischer YouTube-Abruf", expanded=False):
        yt_creds = utils.load_api_credentials(current_user, "YouTube")
        yt_channel_id = yt_creds["channel_id"] if yt_creds else ""
        yt_api_key = yt_creds["api_key"] if yt_creds else ""
        
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            new_yt_channel = st.text_input("YouTube Channel ID", value=yt_channel_id, key="yt_ch_id")
        with col_api2:
            new_yt_key = st.text_input("YouTube API Key", type="password", value=yt_api_key, key="yt_key")
            
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 API-Daten speichern", use_container_width=True):
                utils.save_api_credentials(current_user, "YouTube", new_yt_channel, new_yt_key)
                st.success("✅ API-Zugangsdaten gespeichert!")
                st.rerun()
                
        with col_btn2:
            if st.button("🚀 YouTube Live-Zahlen abrufen", type="primary", use_container_width=True):
                yt_stats, err = utils.fetch_youtube_stats(current_user)
                if err:
                    st.error(err)
                elif yt_stats:
                    current_stats = utils.load_data("stats", list)
                    auto_entry = {
                        "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "plattform": "YouTube",
                        "titel": f"API-Abruf (Abos: {yt_stats['subscribers']:,})",
                        "views": yt_stats["views"],
                        "chat_aktivitaet": 0,
                        "neue_discord_member": 0,
                        "shares": 0
                    }
                    current_stats.append(auto_entry)
                    utils.save_data("stats", current_stats)
                    st.success(f"📈 Erfolgreich abgerufen! Views insgesamt: {yt_stats['views']:,} | Abos: {yt_stats['subscribers']:,}")
                    st.rerun()

    st.markdown("---")
    st.subheader("✍️ Daten manuell erfassen")

    # Side-by-Side Design beibehalten
    with st.form("manual_stats_form", clear_on_submit=True):
        col_basis, col_health = st.columns(2)
        
        with col_basis:
            st.markdown("### 📈 Performance")
            plattform = st.selectbox("Plattform", ["Twitch", "YouTube", "Instagram", "TikTok", "Kick", "X"])
            titel = st.text_input("Thema / Titel des Beitrags", placeholder="z.B. Rennplan Stream")
            views = st.number_input("Views / Aufrufe", min_value=0, step=1)
            
        with col_health:
            st.markdown("### 🫂 Community Health")
            chat_aktivitaet = st.number_input("Aktive Chatter", min_value=0, step=1)
            neue_discord = st.number_input("Neue Discord-Member", min_value=0, step=1)
            shares_mentions = st.number_input("Shares / Erwähnungen", min_value=0, step=1)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Statistik sichern", type="primary", use_container_width=True):
            new_entry = {
                "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "plattform": plattform,
                "titel": titel,
                "views": views,
                "chat_aktivitaet": chat_aktivitaet,
                "neue_discord_member": neue_discord,
                "shares": shares_mentions
            }
            current_stats = utils.load_data("stats", list)
            current_stats.append(new_entry)
            utils.save_data("stats", current_stats)
            st.success("✅ Daten erfolgreich gespeichert!")
            st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: VISUELLE AUSWERTUNG (MIt 2026 Midnight-Theme für die Charts)
# ------------------------------------------------------------------------------
with tab_auswertung:
    st.subheader("📈 Auswertungen & Trends")
    raw_stats = utils.load_data("stats", list)
    
    if not raw_stats:
        st.info("Noch keine Daten vorhanden.")
    else:
        df = pd.DataFrame(raw_stats)
        df['datum'] = pd.to_datetime(df['datum'])
        df = df.sort_values('datum')
        
        with st.expander("📋 Alle Rohdaten als Tabelle"):
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        st.markdown("---")
        
        # Neues, dunkles Design für Plotly
        CHART_BG = "rgba(0,0,0,0)"
        FONT_COLOR = "#F8FAFC"
        
        st.markdown("#### 👀 Reichweiten-Entwicklung")
        fig_views = px.line(df, x="datum", y="views", color="plattform", markers=True)
        # 2026 Theme anwenden
        fig_views.update_layout(
            plot_bgcolor=CHART_BG, 
            paper_bgcolor=CHART_BG, 
            font=dict(color=FONT_COLOR, family="Inter"),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
        )
        st.plotly_chart(fig_views, use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("#### 🫂 Community Health Trend")
        for col in ["chat_aktivitaet", "neue_discord_member", "shares"]:
            if col not in df.columns:
                df[col] = 0
                
        fig_health = px.bar(
            df, 
            x="datum", 
            y=["chat_aktivitaet", "neue_discord_member", "shares"],
            barmode="group",
            color_discrete_sequence=["#38BDF8", "#818CF8", "#F472B6"] # Passende Blau- und Pinktöne
        )
        fig_health.update_layout(
            plot_bgcolor=CHART_BG, 
            paper_bgcolor=CHART_BG, 
            font=dict(color=FONT_COLOR, family="Inter"),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            legend_title_text="Metriken"
        )
        st.plotly_chart(fig_health, use_container_width=True)