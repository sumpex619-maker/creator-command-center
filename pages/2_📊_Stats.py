import streamlit as st
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
    
    /* Custom Bento-Kacheln für die Metriken */
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
    .stTextInput>div>div, .stSelectbox>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR_NAVY} !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: {TEXT_SLATE} !important; }}
</style>
""", unsafe_allow_html=True)

current_user = utils.check_login()

st.title("📊 Performance & Analytics Hub")
st.markdown("Behalte deine Reichweite im Blick und verwalte deine API-Schnittstellen.")
st.markdown("---")

# Zwei-Spalten Bento-Layout (Links die Auswertung, rechts die Einstellungen)
col_stats, col_api = st.columns([1.6, 1])

with col_stats:
    st.markdown("### 📈 Live-Kanaldaten")
    
    # YouTube-Statistiken über die utils-Schnittstelle laden
    try:
        stats, error = utils.fetch_youtube_stats(current_user)
    except Exception:
        stats, error = None, "Fehler beim Laden des Statistik-Moduls."

    if stats:
        st.markdown("#### 🎥 YouTube Realtime-Metriken")
        
        # Side-by-Side Kacheln für die einzelnen Werte
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="metric-box">
                <p style="color: #94A3B8; margin: 0; font-size: 14px;">👥 Abonnenten</p>
                <p style="color: #FFFFFF; margin: 5px 0 0 0; font-size: 26px; font-weight: 700;">{stats.get('subscribers', 0):,}</p>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-box">
                <p style="color: #94A3B8; margin: 0; font-size: 14px;">👁️ Gesamt-Aufrufe</p>
                <p style="color: #FFFFFF; margin: 5px 0 0 0; font-size: 26px; font-weight: 700;">{stats.get('views', 0):,}</p>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-box">
                <p style="color: #94A3B8; margin: 0; font-size: 14px;">🎬 Videos online</p>
                <p style="color: #FFFFFF; margin: 5px 0 0 0; font-size: 26px; font-weight: 700;">{stats.get('videos', 0):,}</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("🎯 Live-Daten erfolgreich synchronisiert!")
    else:
        # Schicke Info-Box, falls noch keine API eingerichtet ist
        st.info(error if error else "ℹ️ Bisher sind keine Live-Daten verfügbar. Verknüpfe rechts deinen Kanal, um die Automatisierung zu starten.")

with col_api:
    st.markdown("### 🔑 API-Schnittstellen")
    
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

