import streamlit as st

# ==============================================================================
# 1. GRUNDSETUP
# ==============================================================================
st.set_page_config(page_title="Command Center", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")

# Verstecke Streamlit-Standardelemente (Sidebar, Header, Footer)
st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
        [data-testid="stHeader"] { display: none; }
        footer { display: none; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CINEMATIC DARK DESIGN-SYSTEM
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

    .stApp {
        background-color: #050508 !important;
        color: #E0E0E0 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        background-image: radial-gradient(circle at 50% -20%, #1a0b2e 0%, #050508 50%);
    }

    h1, h2, h3 { color: #FFFFFF !important; text-transform: uppercase; letter-spacing: 1px; }
    h1 span { color: #00E5FF; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }

    /* Container Boxen */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #0A0A10 !important;
        border: 1px solid #1c1c28 !important;
        border-radius: 4px !important;
        padding: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #00E5FF !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.15) !important;
    }

    /* Top-Navigation Buttons (Inaktiv) */
    .stButton>button {
        background-color: #0A0A10 !important;
        color: #6c757d !important;
        border: 1px solid #1c1c28 !important;
        border-radius: 4px !important;
        text-transform: uppercase;
        font-weight: 600 !important;
        letter-spacing: 1px;
        transition: all 0.2s;
    }
    
    /* Hover & Aktiv (Primary) Status */
    .stButton>button:hover {
        color: #00E5FF !important;
        border-color: #00E5FF !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.2) !important;
    }
    .stButton>button[kind="primary"] {
        background-color: rgba(0, 229, 255, 0.1) !important;
        color: #00E5FF !important;
        border: 1px solid #00E5FF !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. STATE MANAGEMENT (Welche Seite ist aktiv?)
# ==============================================================================
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "🏠 Dashboard"

# ==============================================================================
# 4. TOP NAVIGATION
# ==============================================================================
st.markdown("<h1>Creator <span>Command Center</span></h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Menüpunkte definieren
menu_items = ["🏠 Dashboard", "📊 Stats", "🗓️ Sendeplan", "📝 Ideen", "📢 Post Creator", "💼 Setup"]

# Spalten für die Buttons erstellen
cols = st.columns(len(menu_items))

for i, item in enumerate(menu_items):
    # Wenn der Button geklickt wird UND er noch nicht die aktive Seite ist
    is_active = st.session_state["active_page"] == item
    if cols[i].button(item, use_container_width=True, type="primary" if is_active else "secondary"):
        if not is_active:
            st.session_state["active_page"] = item
            st.rerun()

st.markdown("---")

# ==============================================================================
# 5. ROUTING (Inhalt basierend auf Auswahl laden)
# ==============================================================================

if st.session_state["active_page"] == "🏠 Dashboard":
    st.subheader("System Status")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### Willkommen zurück")
            st.write("Wähle oben im Menü ein Modul aus, um zu starten.")
    with c2:
        with st.container(border=True):
            st.markdown("### Schnellzugriff")
            st.write("Hier kommen später deine wichtigsten Live-Daten hin.")

elif st.session_state["active_page"] == "📊 Stats":
    st.subheader("Analytics Modul")
    st.info("Hier bauen wir als nächstes das dynamische, API-freie Stats-Modul ein.")

elif st.session_state["active_page"] == "🗓️ Sendeplan":
    st.subheader("Sendeplan Modul")
    st.info("Platzhalter für den Kalender.")

elif st.session_state["active_page"] == "📝 Ideen":
    st.subheader("Ideen Modul")
    st.info("Platzhalter für deine Skripte und Keywords.")

elif st.session_state["active_page"] == "📢 Post Creator":
    st.subheader("Discord Uplink")
    st.info("Platzhalter für den Webhook-Sender.")

elif st.session_state["active_page"] == "💼 Setup":
    st.subheader("System Setup")
    st.info("Platzhalter für Webhook-Einstellungen und Datenbank-Setup.")