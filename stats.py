import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import utils

# ==============================================================================
# SEITEN-KONFIGURATION & LOGIN-CHECK
# ==============================================================================
current_user = utils.check_login()
st.title("📊 Statistiken & API-Hub")

# ==============================================================================
# 1. API EINSTELLUNGEN (Individuell pro Nutzer)
# ==============================================================================
with st.expander("⚙️ API-Zugangsdaten (Für automatischen Datenabruf)", expanded=False):
    st.markdown("""
    Hier kannst du deine persönlichen Zugangsdaten für Social Media Plattformen hinterlegen.
    Die Daten werden sicher und nur für **deinen** Account in der Datenbank gespeichert.
    """)
    
    # Lade bestehende YouTube Credentials
    yt_creds = utils.load_api_credentials(current_user, "YouTube")
    yt_channel_id = yt_creds["channel_id"] if yt_creds else ""
    yt_api_key = yt_creds["api_key"] if yt_creds else ""
    
    with st.form("api_settings_form"):
        st.subheader("YouTube")
        new_yt_channel = st.text_input("YouTube Channel ID", value=yt_channel_id, help="Z.B. UCxyz123...")
        new_yt_key = st.text_input("YouTube API Key", type="password", value=yt_api_key)
        
        submitted = st.form_submit_button("💾 API-Daten speichern")
        if submitted:
            utils.save_api_credentials(current_user, "YouTube", new_yt_channel, new_yt_key)
            st.success("✅ YouTube API-Daten erfolgreich gespeichert!")
            st.rerun()

# ==============================================================================
# 2. DATEN ABRUFEN & EINGEBEN
# ==============================================================================
st.markdown("---")
st.header("📈 Neue Daten erfassen")

col1, col2 = st.columns(2)

# Spalte 1: Automatischer Abruf (YouTube)
with col1:
    st.subheader("🤖 Auto-Sync (YouTube)")
    if st.button("🔄 YouTube Live-Daten jetzt abrufen", use_container_width=True):
        with st.spinner("Frage YouTube API ab..."):
            stats, error = utils.fetch_youtube_stats(current_user)
            if error:
                st.error(error)
            else:
                st.success("Erfolgreich abgerufen!")
                # Hier wird der automatische Eintrag für die Datenbank vorbereitet
                new_entry = {
                    "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "plattform": "YouTube (Auto-Sync)",
                    "format": "Kanal-Overview",
                    "titel": "Live Stats",
                    "views": stats["views"],
                    "likes": 0, # API liefert keine globalen Likes
                    "kommentare": 0,
                    "saves": stats["subscribers"], # Wir nutzen das 'Saves' Feld hier für Abonnenten
                    "engagement_rate_pct": 0.0
                }
                # Speichern des neuen Eintrags
                current_stats = utils.load_data("stats", list)
                current_stats.append(new_entry)
                utils.save_data("stats", current_stats)
                st.info(f"**Abonnenten:** {stats['subscribers']} | **Views gesamt:** {stats['views']}")
                st.rerun()

# Spalte 2: Manuelle Eingabe (Für Insta & Co)
with col2:
    st.subheader("✍️ Manuelle Eingabe")
    with st.popover("Neuen Beitrag eintragen"):
        with st.form("manual_stats_form"):
            man_plat = st.selectbox("Plattform", ["Instagram", "TikTok", "Twitter", "Twitch"])
            man_format = st.selectbox("Format", ["Feed-Post", "Reel / Short", "Story", "Stream"])
            man_title = st.text_input("Titel / Beschreibung")
            man_views = st.number_input("Views / Reichweite", min_value=0, step=1)
            man_likes = st.number_input("Likes", min_value=0, step=1)
            
            if st.form_submit_button("Eintragen"):
                engagement = (man_likes / man_views * 100) if man_views > 0 else 0
                new_entry = {
                    "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "plattform": man_plat,
                    "format": man_format,
                    "titel": man_title,
                    "views": man_views,
                    "likes": man_likes,
                    "kommentare": 0,
                    "saves": 0,
                    "engagement_rate_pct": round(engagement, 2)
                }
                current_stats = utils.load_data("stats", list)
                current_stats.append(new_entry)
                utils.save_data("stats", current_stats)
                st.success("Eingetragen!")
                st.rerun()

# ==============================================================================
# 3. DATEN-VISUALISIERUNG (Dashboard)
# ==============================================================================
st.markdown("---")
st.header("📊 Dein Dashboard")

# Lade alle Statistiken aus der Datenbank
raw_stats = utils.load_data("stats", list)

if not raw_stats:
    st.info("Noch keine Daten vorhanden. Trage oben manuell etwas ein oder nutze den Auto-Sync!")
else:
    # Verwandle die Daten in ein Pandas DataFrame (perfekt für Diagramme)
    df = pd.DataFrame(raw_stats)
    # Datumstext in echtes Datum umwandeln, damit die Kurve richtig sortiert wird
    df['datum'] = pd.to_datetime(df['datum'])
    df = df.sort_values('datum')
    
    # Tabellen-Ansicht
    with st.expander("📋 Rohdaten ansehen"):
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Diagramm 1: Ansichten über die Zeit (Getrennt nach Plattform)
    st.subheader("👀 Views Entwicklung")
    fig_views = px.line(
        df, 
        x="datum", 
        y="views", 
        color="plattform", 
        markers=True,
        title="Reichweite nach Plattform",
        template="plotly_dark" if utils.load_data("users", list) else "plotly" # Passt sich ans Theme an (Basic)
    )
    st.plotly_chart(fig_views, use_container_width=True)
    
    # Wenn wir YouTube Auto-Sync Daten haben (wo wir Subscriber im "saves" Feld speichern)
    df_yt = df[df["plattform"] == "YouTube (Auto-Sync)"]
    if not df_yt.empty:
        st.subheader("📈 YouTube Abonnenten Wachstum")
        fig_subs = px.area(
            df_yt,
            x="datum",
            y="saves",
            markers=True,
            title="Abonnenten-Kurve",
            color_discrete_sequence=["#FF0000"] # YouTube Rot
        )
        st.plotly_chart(fig_subs, use_container_width=True)