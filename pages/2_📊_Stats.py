import streamlit as st
import pandas as pd
from datetime import datetime
import utils

# ==============================================================================
# GLOBALES 2026 DESIGN SYSTEM (Midnight Navy)
# ==============================================================================
PRIMARY_BLUE = "#38BDF8"
BG_DEEP_NAVY = "#0F172A"
SIDEBAR_NAVY = "#1E293B"
TEXT_SLATE = "#F8FAFC"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT_SLATE} !important; }}
    .stApp {{ background-color: {BG_DEEP_NAVY} !important; }}
    h1, h2, h3 {{ font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: #FFFFFF !important; }}
    
    /* Custom Bento-Kacheln */
    div[data-testid="stExpander"], .stAlert, .metric-box {{ 
        background-color: rgba(30, 41, 59, 0.4) !important; 
        border-radius: 16px !important; 
        border: 1px solid rgba(255, 255, 255, 0.08) !important; 
        padding: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }}
    
    .stButton>button {{ border-radius: 10px !important; background-color: {SIDEBAR_NAVY} !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; font-family: 'Outfit', sans-serif !important; }}
    .stButton>button:hover {{ border-color: {PRIMARY_BLUE} !important; box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important; }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important; border: none !important; }}
    .stTextInput>div>div, .stSelectbox>div>div, .stNumberInput>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR_NAVY} !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: {TEXT_SLATE} !important; }}
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px !important; }}
    .stTabs [data-baseweb="tab"] {{ background-color: rgba(30, 41, 59, 0.5) !important; border-radius: 8px 8px 0 0 !important; padding: 10px 20px !important; color: #94A3B8 !important; }}
    .stTabs [aria-selected="true"] {{ background-color: {PRIMARY_BLUE} !important; color: {BG_DEEP_NAVY} !important; font-weight: 600 !important; }}
</style>
""", unsafe_allow_html=True)

current_user = utils.check_login()

st.title("📊 Performance & Analytics Hub")
st.markdown("Analysiere dein Wachstum schrittweise über automatische APIs oder manuelle Einträge.")
st.markdown("---")

# Aufteilung in Tabs für maximale Übersichtlichkeit
tab_live, tab_manual, tab_charts, tab_api = st.tabs([
    "📈 Live-Kanalstatus", 
    "✍️ Daten manuell eintragen", 
    "📊 Diagramme & Analyse", 
    "🔑 API-Einstellungen"
])

# ==============================================================================
# TAB 1: LIVE KANALSTATUS
# ==============================================================================
with tab_live:
    st.markdown("### 🎥 Echtzeit-API-Abfrage")
    try:
        stats, error = utils.fetch_youtube_stats(current_user)
    except Exception:
        stats, error = None, "Fehler beim Laden des Statistik-Moduls."

    if stats:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-box"><p style="color: #94A3B8; margin: 0; font-size: 14px;">👥 Abonnenten</p><p style="color: #FFFFFF; margin: 5px 0 0 0; font-size: 26px; font-weight: 700;">{stats.get("subscribers", 0):,}</p></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-box"><p style="color: #94A3B8; margin: 0; font-size: 14px;">👁️ Gesamt-Aufrufe</p><p style="color: #FFFFFF; margin: 5px 0 0 0; font-size: 26px; font-weight: 700;">{stats.get("views", 0):,}</p></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-box"><p style="color: #94A3B8; margin: 0; font-size: 14px;">🎬 Videos online</p><p style="color: #FFFFFF; margin: 5px 0 0 0; font-size: 26px; font-weight: 700;">{stats.get("videos", 0):,}</p></div>', unsafe_allow_html=True)
    else:
        st.info(error if error else "ℹ️ Bisher sind keine Live-Daten verfügbar. Nutze den letzten Tab, um deine API zu verbinden.")

# ==============================================================================
# TAB 2: DATEN MANUELL EINTRAGEN
# ==============================================================================
with tab_manual:
    st.markdown("### ✍️ Statistik manuell erfassen")
    st.markdown("Perfekt, um plattformübergreifend Meilensteine festzuhalten.")
    
    with st.form("manual_stats_form", clear_on_submit=True):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            m_plattform = st.selectbox("Plattform", ["Twitch", "YouTube", "Kick", "Instagram", "TikTok", "X"])
            m_followers = st.number_input("Follower / Abonnenten Anzahl", min_value=0, step=1)
        with col_m2:
            m_date = st.text_input("Zeitpunkt / Monat", placeholder=datetime.now().strftime("%B %Y"))
            m_views = st.number_input("Monatliche Aufrufe / Views (optional)", min_value=0, step=1)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Datenpunkt sichern", type="primary", use_container_width=True):
            if m_date:
                manual_data = utils.load_data("manual_stats", list)
                new_entry = {
                    "id": str(datetime.now().timestamp()),
                    "plattform": m_plattform,
                    "followers": m_followers,
                    "views": m_views,
                    "zeitpunkt": m_date
                }
                manual_data.append(new_entry)
                utils.save_data("manual_stats", manual_data)
                st.success(f"✅ Eintrag für {m_plattform} ({m_date}) erfolgreich gesichert!")
                st.rerun()
            else:
                st.error("⚠️ Bitte gib einen Zeitpunkt oder Monat an!")

# ==============================================================================
# TAB 3: DIAGRAMME & ANALYSE
# ==============================================================================
with tab_charts:
    st.markdown("### 📊 Visuelle Auswertung")
    
    manual_data = utils.load_data("manual_stats", list)
    
    if not manual_data:
        st.info("ℹ️ Noch keine manuellen Datenpunkte vorhanden. Trage im vorherigen Reiter Daten ein, um Diagramme zu generieren.")
    else:
        df = pd.DataFrame(manual_data)
        
        with st.expander("📋 Rohdaten anzeigen / Einträge löschen"):
            for entry in manual_data:
                c_info, c_del = st.columns([4, 1])
                c_info.markdown(f"**{entry['plattform']}** ({entry['zeitpunkt']}): `{entry['followers']:,}` Follower | `{entry['views']:,}` Views")
                if c_del.button("🗑️", key=f"del_stat_{entry['id']}"):
                    manual_data = [e for e in manual_data if e['id'] != entry['id']]
                    utils.save_data("manual_stats", manual_data)
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        df_latest = df.sort_values("id").groupby("plattform").last().reset_index()
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### 👥 Follower pro Plattform")
            chart_df = df_latest.set_index("plattform")[["followers"]]
            st.bar_chart(chart_df, color="#38BDF8")
            
        with col_chart2:
            st.markdown("#### 👁️ Views pro Plattform")
            chart_views = df_latest.set_index("plattform")[["views"]]
            st.bar_chart(chart_views, color="#818CF8")

# ==============================================================================
# TAB 4: API-EINSTELLUNGEN
# ==============================================================================
with tab_api:
    st.markdown("### 🔑 API-Schnittstellen verwalten")
    with st.form("api_credentials_form", clear_on_submit=False):
        plattform = st.selectbox("Plattform wählen", ["YouTube"])
        channel_id = st.text_input("Kanal-ID (Channel ID)", placeholder="UC...", help="Deine eindeutige YouTube-Kanal-ID")
        api_key = st.text_input("API-Schlüssel (API Key)", type="password", placeholder="AIzaSy...", help="Dein Google Cloud API-Key")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("🔗 API verbinden", type="primary", use_container_width=True):
            if channel_id and api_key:
                try:
                    conn = utils.get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO api_credentials (username, platform, channel_id, api_key)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (username, platform) 
                        DO UPDATE SET channel_id = EXCLUDED.channel_id, api_key = EXCLUDED.api_key
                    """, (current_user, plattform, channel_id, api_key))
                    cursor.close()
                    conn.close()
                    st.success(f"✅ API-Daten für {plattform} erfolgreich gesichert!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Datenbankfehler: {e}")
            else:
                st.error("⚠️ Bitte fülle alle Felder aus!")