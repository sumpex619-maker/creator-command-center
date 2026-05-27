import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import utils

# ==============================================================================
# SEITEN-KONFIGURATION & LOGIN-CHECK
# ==============================================================================
current_user = utils.check_login()

# Große Überschrift im 2026er Clean-Style
st.title("📊 Stats & Community Health")
st.markdown("Deine Schaltzentrale für Reichweite und Community-Wachstum.")

# Wir haben das Layout auf 2 Tabs reduziert (Content bewerben ist raus!)
tab_eingabe, tab_auswertung = st.tabs([
    "📝 Eingabe & Live-Abruf", 
    "📈 Visuelle Auswertung"
])

# ------------------------------------------------------------------------------
# TAB 1: EINGABE & LIVE-ABRUF
# ------------------------------------------------------------------------------
with tab_eingabe:
    
    # --- AUTOMATISCHER YOUTUBE ABRUF (DEINE API) ---
    with st.expander("⚙️ API-Zugangsdaten & Automatischer YouTube-Abruf", expanded=False):
        st.markdown("Hier kannst du deine YouTube-Schnittstelle verwalten oder Live-Zahlen ziehen.")
        
        # API Daten laden
        yt_creds = utils.load_api_credentials(current_user, "YouTube")
        yt_channel_id = yt_creds["channel_id"] if yt_creds else ""
        yt_api_key = yt_creds["api_key"] if yt_creds else ""
        
        # Kleine Spalten für die API-Eingabefelder
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
                    # Direkt als neuen Eintrag in die Datenbank sichern
                    current_stats = utils.load_data("stats", list)
                    auto_entry = {
                        "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "plattform": "YouTube",
                        "titel": f"Automatischer API-Abruf (Abonnenten: {yt_stats['subscribers']:,})",
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
    st.markdown("Nutze dieses Formular, um deine Streams, Videos oder Social-Posts zu protokollieren.")

    # --- MODULARES DESIGN: FORMULAR NEBENEINANDER ---
    with st.form("manual_stats_form", clear_on_submit=True):
        col_basis, col_health = st.columns(2)
        
        # Linke Spalte: Klassische Performance
        with col_basis:
            st.markdown("### 📈 Performance")
            plattform = st.selectbox("Plattform", ["Twitch", "YouTube", "Instagram", "TikTok", "Kick", "X"])
            titel = st.text_input("Thema / Titel des Beitrags", placeholder="z.B. Minecraft Stream #12 oder Shorts-Video")
            views = st.number_input("Views / Aufrufe", min_value=0, step=1, help="Gesamte Klicks oder Live-Zuschauer")
            
        # Rechte Spalte: Das neue Community Health Board
        with col_health:
            st.markdown("### 🫂 Community Health")
            chat_aktivitaet = st.number_input("Aktive Chatter", min_value=0, step=1, help="Wie viele Zuschauer haben aktiv im Chat geschrieben?")
            neue_discord = st.number_input("Neue Discord-Member", min_value=0, step=1, help="Wie viele Leute sind heute deinem Discord beigetreten?")
            shares_mentions = st.number_input("Shares / Erwähnungen", min_value=0, step=1, help="Wie oft wurde dein Content geteilt oder du markiert?")
            
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("💾 Statistik & Health-Daten sichern", type="primary", use_container_width=True)
        
        if submit_btn:
            new_entry = {
                "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "plattform": plattform,
                "titel": titel,
                "views": views,
                "chat_aktivitaet": chat_aktivitaet,
                "neue_discord_member": neue_discord,
                "shares": shares_mentions
            }
            # Laden, anhängen, speichern
            current_stats = utils.load_data("stats", list)
            current_stats.append(new_entry)
            utils.save_data("stats", current_stats)
            st.success("✅ Daten erfolgreich in deiner Historie gespeichert!")
            st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: VISUELLE AUSWERTUNG
# ------------------------------------------------------------------------------
with tab_auswertung:
    st.subheader("📈 Deine Auswertungen & Trends")
    raw_stats = utils.load_data("stats", list)
    
    if not raw_stats:
        st.info("Noch keine Daten in der Datenbank vorhanden. Trage im ersten Reiter deine ersten Werte ein!")
    else:
        # Daten in eine filterbare Tabelle umwandeln
        df = pd.DataFrame(raw_stats)
        df['datum'] = pd.to_datetime(df['datum'])
        df = df.sort_values('datum')
        
        # Optionale Rohdaten-Einsicht
        with st.expander("📋 Alle gespeicherten Rohdaten als Tabelle ansehen"):
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        st.markdown("---")
        
        # Grafik 1: Reichweite
        st.markdown("#### 👀 Reichweiten-Entwicklung")
        fig_views = px.line(df, x="datum", y="views", color="plattform", markers=True, template="plotly_dark")
        fig_views.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_views, use_container_width=True)
        
        st.markdown("---")
        
        # Grafik 2: Community Health Trend (Nur anzeigen, wenn Daten vorhanden)
        st.markdown("#### 🫂 Community Health & Engagement Trend")
        
        # Sicherstellen, dass auch alte Daten nicht abstürzen, falls die Spalten fehlen
        for col in ["chat_aktivitaet", "neue_discord_member", "shares"]:
            if col not in df.columns:
                df[col] = 0
                
        fig_health = px.bar(
            df, 
            x="datum", 
            y=["chat_aktivitaet", "neue_discord_member", "shares"],
            barmode="group",
            template="plotly_dark"
        )
        fig_health.update_layout(margin=dict(l=20, r=20, t=20, b=20), legend_title_text="Metriken")
        st.plotly_chart(fig_health, use_container_width=True)