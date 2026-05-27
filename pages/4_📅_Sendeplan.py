import streamlit as st
import utils

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
    div[data-testid="stExpander"], .stAlert {{ background-color: rgba(30, 41, 59, 0.4) !important; border-radius: 16px !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; }}
    .stButton>button {{ border-radius: 10px !important; background-color: {SIDEBAR_NAVY} !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; font-family: 'Outfit', sans-serif !important; }}
    .stButton>button:hover {{ border-color: {PRIMARY_BLUE} !important; box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important; }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important; border: none !important; }}
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR_NAVY} !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: {TEXT_SLATE} !important; }}
</style>
""", unsafe_allow_html=True)

current_user = utils.check_login()

st.title("🗓️ Sendeplan- & Rennplan-Manager")
st.markdown("Koordiniere deine Zeiten und behalte die Übersicht über anstehende Events.")
st.markdown("---")

# Sendeplan-Daten laden (gesichert pro User in der Cloud)
sendeplan = utils.load_data("sendeplan", dict)

col_plan_form, col_plan_view = st.columns([1, 1.5])

with col_plan_form:
    st.markdown("### 🛠️ Slot eintragen / bearbeiten")
    with st.form("sendeplan_form"):
        tag = st.selectbox("Wochentag", utils.WOCHENTAGE)
        uhrzeit = st.text_input("Uhrzeit / Zeitraum", placeholder="z.B. 19:00 - 22:00 Uhr")
        inhalt = st.text_area("Geplanter Inhalt / Event", placeholder="z.B. SimRacing Meisterschaft - Lauf 3")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Tag im Plan updaten", type="primary", use_container_width=True):
            sendeplan[tag] = {"uhrzeit": uhrzeit, "inhalt": inhalt}
            utils.save_data("sendeplan", sendeplan)
            st.success(f"✅ {tag} erfolgreich im Plan aktualisiert!")
            st.rerun()

with col_plan_view:
    st.markdown("### 📅 Deine aktuelle Wochenübersicht")
    
    # Bento-Grid-Look für die Wochentage
    for tag in utils.WOCHENTAGE:
        slot = sendeplan.get(tag, {"uhrzeit": "Keine Termine", "inhalt": "Streaming-frei oder Flexibel"})
        
        with st.expander(f"🔹 {tag}", expanded=True):
            c_time, c_content = st.columns([1, 2])
            c_time.markdown(f"**⏰ Zeit:**\n`{slot['uhrzeit']}`")
            c_content.markdown(f"**🎬 Aktivität:**\n{slot['inhalt']}")