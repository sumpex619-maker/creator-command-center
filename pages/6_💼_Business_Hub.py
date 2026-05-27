import streamlit as st
import pandas as pd
import utils

current_user = utils.check_login()

# ==============================================================================
# UNIVERSAL DESIGN ENGINE (Light & Dark Mode)
# ==============================================================================
if "theme" not in st.session_state: st.session_state["theme"] = "Midnight (Dark)"
with st.sidebar:
    new_theme = st.selectbox("🎨 Design", ["Midnight (Dark)", "Clean (Light)"], index=0 if st.session_state["theme"] == "Midnight (Dark)" else 1)
    if new_theme != st.session_state["theme"]: st.session_state["theme"] = new_theme; st.rerun()

if st.session_state["theme"] == "Midnight (Dark)":
    BG = "#0F172A"; SIDEBAR = "#1E293B"; CARD = "rgba(30, 41, 59, 0.4)"; TEXT = "#F8FAFC"; BORDER = "rgba(255, 255, 255, 0.08)"; PRIM = "#38BDF8"
else:
    BG = "#F8FAFC"; SIDEBAR = "#F1F5F9"; CARD = "#FFFFFF"; TEXT = "#0F172A"; BORDER = "rgba(0, 0, 0, 0.1)"; PRIM = "#0284C7"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT} !important; }}
    .stApp {{ background-color: {BG} !important; }}
    h1, h2, h3, h4 {{ font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: {TEXT} !important; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR} !important; border-right: 1px solid {BORDER}; }}
    .bento-card, div[data-testid="stExpander"], .stAlert {{ background-color: {CARD} !important; border-radius: 16px !important; border: 1px solid {BORDER} !important; padding: 20px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; margin-bottom: 15px; }}
    .stButton>button {{ border-radius: 10px !important; background-color: {SIDEBAR} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; font-family: 'Outfit', sans-serif !important; transition: all 0.2s; }}
    .stButton>button:hover {{ border-color: {PRIM} !important; transform: translateY(-2px); }}
    .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, {PRIM} 0%, #818CF8 100%) !important; border: none !important; color: white !important; }}
    .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div {{ border-radius: 10px !important; background-color: {SIDEBAR} !important; border: 1px solid {BORDER} !important; color: {TEXT} !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px !important; }}
    .stTabs [data-baseweb="tab"] {{ background-color: {CARD} !important; border-radius: 8px 8px 0 0 !important; padding: 10px 20px !important; color: {TEXT} !important; opacity: 0.8; }}
    .stTabs [aria-selected="true"] {{ background-color: {PRIM} !important; color: white !important; font-weight: 600 !important; opacity: 1; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SEITENINHALT
# ==============================================================================
st.title("💼 Creator Business Hub")
st.markdown("Dein roter Faden vom Hobby-Streamer zum professionellen Creator-Setup.")
st.markdown("---")

t_fahrplan, t_wissen, t_links = st.tabs(["🗺️ Roadmap Checkliste", "📖 Business-Wissen", "🔗 Partner-Links"])

with t_fahrplan:
    st.markdown("### 🚀 Deine Business-Roadmap")
    progress = utils.load_data("business_progress", dict)
    steps = {
        "step_1": "Hobby vs. Gewerbe geprüft (Pflicht bei Monetarisierung!)",
        "step_2": "Gewerbe angemeldet (Tipp: Kleinunternehmer-Regelung)",
        "step_3": "Rechtssicheres Impressum eingerichtet",
        "step_4": "Professionelle Business-E-Mail (@deinedomain.de) angelegt",
        "step_5": "Datenschutzkonforme Link-in-Bio Seite erstellt"
    }
    for k, v in steps.items():
        if k not in progress: progress[k] = False
            
    col_checks, col_score = st.columns([2, 1])
    with col_checks:
        for k, v in steps.items():
            new_val = st.checkbox(v, value=progress[k], key=f"check_{k}")
            if new_val != progress[k]:
                progress[k] = new_val; utils.save_data("business_progress", progress); st.rerun()
                
    with col_score:
        score = sum(progress.values())
        prozent = int(score / len(steps) * 100)
        st.markdown("### 📊 Status")
        st.progress(prozent / 100)
        st.markdown(f"**Fertiggestellt: {prozent}%**")
        if prozent == 100: st.success("🎉 Komplettes Setup abgeschlossen!")

with t_wissen:
    st.markdown("### 📚 Experten-Tipps kompakt")
    with st.expander("⚖️ 1. Wann muss ich ein Gewerbe anmelden?"):
        st.markdown("Sobald eine **Gewinnerzielungsabsicht** vorliegt, musst du ein Gewerbe anmelden. Nutze als Anfänger die Kleinunternehmerregelung.")
    with st.expander("📧 2. Die professionelle Business-Mail"):
        st.markdown("Sichere dir eine eigene Domain (z.B. `deincreatorname.de`). Das erhöht deine Chancen auf Zusagen von Marken drastisch!")
    with st.expander("🔗 3. Die 'Link-in-Bio'-Falle"):
        st.markdown("Viele US-Tools sind in Deutschland datenschutzrechtlich schwierig. Am sichersten ist eine eigene, kleine Website für deine Links.")

with t_links:
    st.markdown("### 🔗 Affiliate- & Partner-Links verwalten")
    with st.form("add_link_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name des Partners / Produkts", placeholder="z.B. Mein Mikrofon")
            kategorie = st.selectbox("Kategorie", ["Hardware", "Games", "Merch", "Sonstiges"])
        with c2:
            url = st.text_input("Dein Affiliate-Link", placeholder="https://...")
            code = st.text_input("Rabatt-Code (falls vorhanden)", placeholder="z.B. CREATOR10")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Link speichern", type="primary", use_container_width=True):
            if name and url:
                links = utils.load_data("affiliate_links", list)
                links.append({"name": name, "url": url, "kategorie": kategorie, "code": code})
                utils.save_data("affiliate_links", links)
                st.success("✅ Partner-Link gespeichert!")
                st.rerun()
            else:
                st.error("⚠️ Bitte Partner-Name und Link ausfüllen.")
    
    st.markdown("---")
    links = utils.load_data("affiliate_links", list)
    if not links:
        st.info("Noch keine Partner-Links hinterlegt.")
    else:
        df_links = pd.DataFrame(links)
        for kat, sub_df in df_links.groupby("kategorie"):
            st.markdown(f"#### 📁 {kat}")
            for _, row in sub_df.iterrows():
                col_view1, col_view2 = st.columns([3, 1])
                with col_view1:
                    st.markdown(f"**{row['name']}**")
                    st.code(row['url'])
                    if row.get('code'): st.markdown(f"Code: `{row['code']}`")
                with col_view2:
                    if st.button("🗑️ Löschen", key=f"del_{row['name']}", use_container_width=True):
                        links = [l for l in links if l['name'] != row['name']]
                        utils.save_data("affiliate_links", links)
                        st.rerun()
                st.divider()