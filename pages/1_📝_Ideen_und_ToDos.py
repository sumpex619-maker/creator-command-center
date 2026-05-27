import streamlit as st
import pandas as pd
from datetime import datetime
import utils

# ==============================================================================
# SEITEN-KONFIGURATION & LOGIN-CHECK
# ==============================================================================
current_user = utils.check_login()

st.title("📝 Ideen-Schmiede & SEO-Werkstatt")
st.markdown("Plane strategisch, optimiere für die Suche und verwalte deinen Content-Workflow im Side-by-Side Design.")

tab_neu, tab_uebersicht = st.tabs(["💡 Neue Idee & SEO-Planer", "📋 Meine Ideen-Schmiede"])

# ------------------------------------------------------------------------------
# TAB 1: NEUE IDEE
# ------------------------------------------------------------------------------
with tab_neu:
    with st.form("idea_seo_form", clear_on_submit=True):
        # Konsequentes Side-by-Side Layout
        col_basis, col_seo = st.columns(2)
        
        with col_basis:
            st.markdown("### 📋 Basis-Informationen")
            titel = st.text_input("Arbeitstitel", placeholder="z.B. Rennplan Analyse 2026")
            plattform = st.selectbox("Ziel-Plattform", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X"])
            status = st.selectbox("Produktions-Status", ["💡 Idee", "✍️ Skript & Planung", "🎥 Aufnahme & Schnitt", "✅ Veröffentlicht"])
            notizen = st.text_area("Inhaltliche Notizen", height=130, placeholder="Kernpunkte des Videos/Streams...")
            
        with col_seo:
            st.markdown("### 🔍 Social-SEO & Tags")
            keyword = st.text_input("🔑 Fokus-Keyword", placeholder="z.B. simracing anfänger")
            seo_titel = st.text_input("🎬 Optimierter Titel", placeholder="z.B. Simracing für Anfänger: Der perfekte Start")
            problem = st.text_input("🎯 Gelöstes Problem", placeholder="Warum klickt der Zuschauer hierauf?")
            # Vorbereitung für den kommenden 2026 Hashtag Generator
            hashtags = st.text_input("🏷️ 2026 Hashtags (Generator in Planung)", placeholder="#racing #streamer #2026")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Idee & Konzept speichern", type="primary", use_container_width=True):
            if not titel:
                st.error("⚠️ Bitte gib zumindest einen Arbeitstitel ein!")
            else:
                new_idea = {
                    "id": str(datetime.now().timestamp()),
                    "datum": datetime.now().strftime("%Y-%m-%d"),
                    "titel": titel, 
                    "plattform": plattform, 
                    "status": status,
                    "notizen": notizen, 
                    "keyword": keyword, 
                    "seo_titel": seo_titel,
                    "problem": problem, 
                    "hashtags": hashtags
                }
                ideas = utils.load_data("ideas", list)
                ideas.append(new_idea)
                utils.save_data("ideas", ideas)
                st.success("✅ Idee erfolgreich in der Schmiede gesichert!")
                st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: ÜBERSICHT
# ------------------------------------------------------------------------------
with tab_uebersicht:
    ideas = utils.load_data("ideas", list)
    if not ideas:
        st.info("Noch keine Ideen vorhanden. Leg los und trage deine erste Idee ein!")
    else:
        # Side-by-Side Filter
        f_plat, f_stat = st.columns(2)
        p_filter = f_plat.multiselect("Filtern nach Plattform", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X"])
        s_filter = f_stat.multiselect("Filtern nach Status", ["💡 Idee", "✍️ Skript & Planung", "🎥 Aufnahme & Schnitt", "✅ Veröffentlicht"])
        
        st.markdown("---")
        
        for idea in reversed(ideas):
            # Filter anwenden
            if p_filter and idea.get("plattform") not in p_filter: continue
            if s_filter and idea.get("status") not in s_filter: continue
            
            with st.expander(f"{idea.get('status')} | {idea.get('plattform')} — {idea.get('titel')}"):
                # Modulare Side-by-Side Ansicht für die Details
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### 📋 Inhalt")
                    st.markdown(f"**Erstellt:** {idea.get('datum')}")
                    st.write(idea.get("notizen") if idea.get("notizen") else "*Keine Notizen*")
                with c2:
                    st.markdown("#### 🔍 SEO & Tags")
                    st.markdown(f"**Keyword:** `{idea.get('keyword', '-')}`")
                    st.markdown(f"**SEO-Titel:** *{idea.get('seo_titel', '-')}*")
                    st.markdown(f"**Problem:** {idea.get('problem', '-')}")
                    st.markdown(f"**Hashtags:** `{idea.get('hashtags', '-')}`")
                
                st.divider()
                
                # Side-by-Side Interaktion (Status ändern & Löschen)
                btn_col1, btn_col2 = st.columns([3, 1])
                status_list = ["💡 Idee", "✍️ Skript & Planung", "🎥 Aufnahme & Schnitt", "✅ Veröffentlicht"]
                current_idx = status_list.index(idea.get("status", "💡 Idee")) if idea.get("status") in status_list else 0
                
                new_s = btn_col1.selectbox("Status updaten", status_list, index=current_idx, key=f"s_{idea['id']}")
                if new_s != idea.get("status"):
                    idea["status"] = new_s
                    utils.save_data("ideas", ideas)
                    st.rerun()
                    
                st.markdown("<br>", unsafe_allow_html=True)
                if btn_col2.button("🗑️ Löschen", key=f"d_{idea['id']}", type="secondary", use_container_width=True):
                    ideas.remove(idea)
                    utils.save_data("ideas", ideas)
                    st.rerun()