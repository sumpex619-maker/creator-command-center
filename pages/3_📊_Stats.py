import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import utils

# ==============================================================================
# SEITEN-KONFIGURATION & LOGIN-CHECK
# ==============================================================================
current_user = utils.check_login()
st.title("📊 Social Media Stats & Content-Bewerbung")

# ==============================================================================
# TABS FÜR DAS LAYOUT
# ==============================================================================
tab_eingabe, tab_auswertung, tab_bewerben = st.tabs([
    "📝 Eingabe & Historie", 
    "📈 Visuelle Auswertung", 
    "📢 Content-Release bewerben"
])

# ------------------------------------------------------------------------------
# TAB 1: EINGABE & HISTORIE
# ------------------------------------------------------------------------------
with tab_eingabe:
    st.header("Social Media Stats erfassen")
    
    # --- API-Bereich mit integrierter Anleitung ---
    with st.expander("⚙️ API-Zugangsdaten & Automatischer YouTube-Abruf", expanded=False):
        st.markdown("""
        ### 🛠️ Anleitung: Woher bekomme ich die API-Daten?
        
        **1. YouTube Channel ID (Kanal-ID):**
        * Gehe auf YouTube zu deinen **Erweiterten Kontoeinstellungen** unter [youtube.com/account_advanced](https://www.youtube.com/account_advanced).
        * Kopiere den Wert bei **Kanal-ID** (die ID beginnt fast immer mit **UC...**).
        
        **2. YouTube API Key (API-Schlüssel):**
        * Öffne die [Google Cloud Console](https://console.cloud.google.com/).
        * Erstelle oben links ein neues, kostenloses Projekt (z. B. *Creator Center*).
        * Suche in der oberen Suchleiste nach **"YouTube Data API v3"** und klicke auf **Aktivieren**.
        * Wechsel im linken Menü zu **Anmeldedaten** (Credentials) -> Klicke auf **Anmeldedaten erstellen** -> **API-Schlüssel**.
        * Kopiere den erzeugten Schlüssel und füge ihn unten ein.
        """)
        st.markdown("---")
        
        yt_creds = utils.load_api_credentials(current_user, "YouTube")
        yt_channel_id = yt_creds["channel_id"] if yt_creds else ""
        yt_api_key = yt_creds["api_key"] if yt_creds else ""
        
        with st.form("api_settings_form"):
            col_api1, col_api2 = st.columns(2)
            new_yt_channel = col_api1.text_input("YouTube Channel ID", value=yt_channel_id)
            new_yt_key = col_api2.text_input("YouTube API Key", type="password", value=yt_api_key)
            
            if st.form_submit_button("💾 API-Daten保存 (Speichern)"):
                utils.save_api_credentials(current_user, "YouTube", new_yt_channel, new_yt_key)
                st.success("✅ YouTube API-Daten erfolgreich gespeichert!")
                st.rerun()
                
        st.markdown("---")
        if st.button("🔄 YouTube Live-Daten jetzt abrufen", use_container_width=True):
            with st.spinner("Frage YouTube API ab..."):
                stats, error = utils.fetch_youtube_stats(current_user)
                if error:
                    st.error(error)
                else:
                    new_entry = {
                        "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "plattform": "YouTube",
                        "format": "Kanal-Overview (Auto)",
                        "titel": "Live API Abruf",
                        "views": stats["views"],
                        "likes": 0,
                        "kommentare": 0,
                        "saves": stats["subscribers"], # Speichert Abonnenten im Saves-Feld ab
                        "engagement_rate_pct": 0.0
                    }
                    current_stats = utils.load_data("stats", list)
                    current_stats.append(new_entry)
                    utils.save_data("stats", current_stats)
                    st.success(f"Erfolgreich abgerufen! Abonnenten: {stats['subscribers']} | Views: {stats['views']}")
                    st.rerun()

    # --- Manuelle Eingabe ---
    st.markdown("---")
    plattform = st.selectbox("Plattform wählen", ["Twitch", "YouTube", "Instagram", "TikTok", "Twitter", "Kick"])
    titel = st.text_input("Titel / Thema des Contents", placeholder="z.B. Clip vom Let's Play Part 3")
    format_art = st.selectbox("Format", ["Main-Stream", "Feed-Post", "Reel / Short", "Story", "Video"])
    
    col1, col2 = st.columns(2)
    with col1:
        views = st.number_input("Views / Aufrufe", min_value=0, step=1, value=0)
        likes = st.number_input("Likes", min_value=0, step=1, value=0)
    with col2:
        kommentare = st.number_input("Kommentare", min_value=0, step=1, value=0)
        saves = st.number_input("Saves / Shares", min_value=0, step=1, value=0)
        
    engagement = 0.0
    if views > 0:
        engagement = ((likes + kommentare + saves) / views) * 100
        
    st.write(f"Berechnete Engagement-Rate ({plattform})")
    st.subheader(f"{engagement:.2f} %")
    
    if st.button("Daten speichern", type="primary"):
        new_entry = {
            "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "plattform": plattform,
            "format": format_art,
            "titel": titel,
            "views": views,
            "likes": likes,
            "kommentare": kommentare,
            "saves": saves,
            "engagement_rate_pct": round(engagement, 2)
        }
        current_stats = utils.load_data("stats", list)
        current_stats.append(new_entry)
        utils.save_data("stats", current_stats)
        st.success("✅ Daten erfolgreich gespeichert!")
        st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: VISUELLE AUSWERTUNG
# ------------------------------------------------------------------------------
with tab_auswertung:
    st.header("📈 Deine Performance im Überblick")
    
    raw_stats = utils.load_data("stats", list)
    if not raw_stats:
        st.info("Noch keine Daten vorhanden. Trage im ersten Tab etwas ein!")
    else:
        df = pd.DataFrame(raw_stats)
        df['datum'] = pd.to_datetime(df['datum'])
        df = df.sort_values('datum')
        
        with st.expander("📋 Alle Rohdaten als Tabelle ansehen"):
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        st.subheader("👀 Views Entwicklung")
        fig_views = px.line(
            df, 
            x="datum", 
            y="views", 
            color="plattform", 
            markers=True,
            title="Reichweite nach Plattform"
        )
        st.plotly_chart(fig_views, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: CONTENT-RELEASE BEWERBEN
# ------------------------------------------------------------------------------
with tab_bewerben:
    st.header("📢 Content bewerben")
    st.info("Dieses Modul befindet sich noch im Aufbau. Hier kannst du später deine manuell eingetragenen Statistiken direkt per Webhook auf Discord pushen!")