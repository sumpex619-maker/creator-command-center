import streamlit as st
import pandas as pd
from datetime import datetime
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
st.title("📝 Ideen-Schmiede & SEO-Werkstatt")
st.markdown("Plane strategisch, optimiere für den Algorithmus und verwalte deinen Workflow.")
st.markdown("---")

tab_neu, tab_uebersicht = st.tabs(["💡 Neue Idee & SEO-Planer", "📋 Meine Ideen-Schmiede"])

with tab_neu:
    with st.form("idea_seo_form", clear_on_submit=True):
        col_basis, col_seo = st.columns(2)
        
        with col_basis:
            st.markdown("### 📋 Basis-Informationen")
            titel = st.text_input("Arbeitstitel", placeholder="z.B. Racing-Setup 2026")
            plattform = st.selectbox("Ziel-Plattform", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X"])
            status = st.selectbox("Produktions-Status", ["💡 Idee", "✍️ Skript & Planung", "🎥 Aufnahme & Schnitt", "✅ Veröffentlicht"])
            notizen = st.text_area("Inhaltliche Notizen", height=130, placeholder="Kernpunkte des Videos/Streams...")
            
        with col_seo:
            st.markdown("### 🔍 Social-SEO & Reichweite")
            keyword = st.text_input("🔑 Fokus-Keyword", placeholder="z.B. simracing anfänger")
            seo_titel = st.text_input("🎬 Optimierter Titel", placeholder="z.B. Simracing für Anfänger: Der perfekte Start")
            problem = st.text_input("🎯 Gelöstes Problem", placeholder="Warum klickt der Zuschauer hierauf?")
            hashtags = st.text_input("🏷️ 2026 Hashtag Generator", placeholder="Wird für den 2026 Standard generiert...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Idee & Konzept speichern", type="primary", use_container_width=True):
            if not titel:
                st.error("⚠️ Bitte gib zumindest einen Arbeitstitel ein!")
            else:
                ideas = utils.load_data("ideas", list)
                ideas.append({
                    "id": str(datetime.now().timestamp()),
                    "datum": datetime.now().strftime("%Y-%m-%d"),
                    "titel": titel, "plattform": plattform, "status": status,
                    "notizen": notizen, "keyword": keyword, "seo_titel": seo_titel,
                    "problem": problem, "hashtags": hashtags
                })
                utils.save_data("ideas", ideas)
                st.success("✅ Idee erfolgreich gesichert!")
                st.rerun()

with tab_uebersicht:
    ideas = utils.load_data("ideas", list)
    if not ideas:
        st.info("Noch keine Ideen vorhanden. Leg los und trage deine erste Idee ein!")
    else:
        f_plat, f_stat = st.columns(2)
        p_filter = f_plat.multiselect("Filtern nach Plattform", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X"])
        s_filter = f_stat.multiselect("Filtern nach Status", ["💡 Idee", "✍️ Skript & Planung", "🎥 Aufnahme & Schnitt", "✅ Veröffentlicht"])
        
        st.markdown("---")
        for idea in reversed(ideas):
            if p_filter and idea.get("plattform") not in p_filter: continue
            if s_filter and idea.get("status") not in s_filter: continue
            
            with st.expander(f"{idea.get('status')} | {idea.get('plattform')} — {idea.get('titel')}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### 📋 Inhalt")
                    st.markdown(f"**Erstellt:** {idea.get('datum')}")
                    st.write(idea.get("notizen") if idea.get("notizen") else "*Keine Notizen*")
                with c2:
                    st.markdown("#### 🔍 SEO & Tags")
                    st.markdown(f"**Keyword:** `{idea.get('keyword', '-')}`")
                    st.markdown(f"**SEO-Titel:** *{idea.get('seo_titel', '-')}*")
                    st.markdown(f"**Hashtags:** `{idea.get('hashtags', '-')}`")
                
                st.divider()
                btn_col1, btn_col2 = st.columns([3, 1])
                status_list = ["💡 Idee", "✍️ Skript & Planung", "🎥 Aufnahme & Schnitt", "✅ Veröffentlicht"]
                current_idx = status_list.index(idea.get("status", "💡 Idee")) if idea.get("status") in status_list else 0
                
                new_s = btn_col1.selectbox("Status updaten", status_list, index=current_idx, key=f"s_{idea['id']}")
                if new_s != idea.get("status"):
                    idea["status"] = new_s
                    utils.save_data("ideas", ideas)
                    st.rerun()
                    
                if btn_col2.button("🗑️ Löschen", key=f"d_{idea['id']}", use_container_width=True):
                    ideas.remove(idea)
                    utils.save_data("ideas", ideas)
                    st.rerun()