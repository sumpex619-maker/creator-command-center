import streamlit as st
import pandas as pd
from datetime import datetime
import utils

# ==============================================================================
# SEITEN-KONFIGURATION & LOGIN-CHECK
# ==============================================================================
current_user = utils.check_login()

st.title("📝 Ideen-Schmiede & SEO-Werkstatt")
st.markdown("Plane deine Inhalte strategisch, optimiere sie für die Social-Media-Suche und behalte deinen kreativen Workflow im Blick.")

# Zwei Reiter für die Übersichtlichkeit (2026er Clean-Style)
tab_neu, tab_uebersicht = st.tabs([
    "💡 Neue Idee & SEO-Planer",
    "📋 Meine Ideen-Schmiede"
])

# ------------------------------------------------------------------------------
# TAB 1: NEUE IDEE & SEO-PLANER
# ------------------------------------------------------------------------------
with tab_neu:
    st.subheader("🚀 Neue Content-Idee strategisch ausarbeiten")
    
    with st.form("idea_seo_form", clear_on_submit=True):
        col_basis, col_seo = st.columns(2)
        
        # Linke Spalte: Klassische Basis-Infos
        with col_basis:
            st.markdown("### 📋 Basis-Informationen")
            titel = st.text_input("Arbeitstitel / Rohe Idee", placeholder="z.B. Mein perfektes Racing-Setup 2026")
            plattform = st.selectbox("Ziel-Plattform", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X"])
            status = st.selectbox("Produktions-Status", ["💡 Idee", "✍️ Skript & Planung", "🎥 Aufnahme & Schnitt", "✅ Veröffentlicht"])
            notizen = st.text_area("Inhaltliche Notizen / Stichpunkte", placeholder="Worum soll es im Kern gehen? Welche Szenen oder Inhalte planst du?")
            
        # Rechte Spalte: Die 2026 Social-SEO-Optimierung
        with col_seo:
            st.markdown("### 🔍 2026 Social-SEO-Optimierung")
            keyword = st.text_input("🔑 Fokus-Suchbegriff (Keyword)", placeholder="z.B. simracing setup anfänger")
            seo_titel = st.text_input("🎬 Optimierter Titel (Suchmaschinen-Fit)", placeholder="z.B. SimRacing Setup für Anfänger: 5 Fehler, die du vermeiden musst!")
            problem = st.text_area("🎯 Welches Problem löst dieses Video für den Zuschauer?", placeholder="z.B. Anfänger wissen oft nicht, welche Force-Feedback-Einstellungen richtig sind und verzweifeln.")
            hashtags = st.text_input("🏷️ Geplante Tags / Hashtags", placeholder="z.B. #simracing, #gaming, #setup2026")

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("💾 Idee & SEO-Konzept speichern", type="primary", use_container_width=True)
        
        if submit_btn:
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
                
                # Daten über utils laden, anhängen und wieder speichern
                ideas = utils.load_data("ideas", list)
                ideas.append(new_idea)
                utils.save_data("ideas", ideas)
                st.success("✅ Deine Idee wurde erfolgreich SEO-optimiert in der Schmiede hinterlegt!")
                st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: MEINE IDEEN-SCHMIEDE (ÜBERSICHT & WORKFLOW)
# ------------------------------------------------------------------------------
with tab_uebersicht:
    st.subheader("📋 Deine gespeicherten Ideen & Konzepte")
    ideas = utils.load_data("ideas", list)
    
    if not ideas:
        st.info("Noch keine Ideen eingetragen. Nutze den ersten Reiter, um deinen ersten Geistesblitz zu planen!")
    else:
        # Dynamische Filter oben drüber im modernen Design
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_plat = st.multiselect("Filtern nach Plattform", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X"], default=[])
        with col_f2:
            filter_stat = st.multiselect("Filtern nach Status", ["💡 Idee", "✍️ Skript & Planung", "🎥 Aufnahme & Schnitt", "✅ Veröffentlicht"], default=[])
            
        st.markdown("---")
        
        # Ideen anzeigen (Neueste zuerst)
        for idea in reversed(ideas):
            # Filter-Logik anwenden
            if filter_plat and idea.get("plattform") not in filter_plat:
                continue
            if filter_stat and idea.get("status") not in filter_stat:
                continue
                
            # Schicke einklappbare Box pro Idee
            with st.expander(f"{idea.get('status', '💡')} | {idea.get('plattform')} — {idea.get('titel')}"):
                col_view1, col_view2 = st.columns(2)
                
                with col_view1:
                    st.markdown("#### 📋 Details & Inhalt")
                    st.markdown(f"**📅 Erstellt am:** {idea.get('datum')}")
                    st.markdown(f"**📝 Inhaltliche Notizen:**")
                    st.write(idea.get('notizen') if idea.get('notizen') else "*Keine Notizen vorhanden.*")
                    
                with col_view2:
                    st.markdown("#### 🔍 Social SEO-Check")
                    st.markdown(f"**🔑 Haupt-Keyword:** `{idea.get('keyword') if idea.get('keyword') else 'Nicht definiert'}`")
                    st.markdown(f"**🎬 SEO-Titel:** *{idea.get('seo_titel') if idea.get('seo_titel') else 'Nicht definiert'}*")
                    st.markdown(f"**🎯 Gelöstes Problem:** {idea.get('problem') if idea.get('problem') else '*Nicht definiert*'}")
                    st.markdown(f"**🏷️ Hashtags:** `{idea.get('hashtags') if idea.get('hashtags') else 'Keine'}`")
                
                st.markdown("---")
                
                # Interaktions-Buttons unten in der Box
                col_btn1, col_btn2, _ = st.columns([2, 1, 2])
                with col_btn1:
                    # Status direkt in der Übersicht updaten
                    status_liste = ["💡 Idee", "✍️ Skript & Planung", "🎥 Aufnahme & Schnitt", "✅ Veröffentlicht"]
                    aktueller_index = status_liste.index(idea.get('status', "💡 Idee"))
                    
                    neuer_status = st.selectbox(
                        "Status aktualisieren", 
                        status_liste, 
                        index=aktueller_index, 
                        key=f"status_select_{idea.get('id')}"
                    )
                    if neuer_status != idea.get('status'):
                        idea['status'] = neuer_status
                        utils.save_data("ideas", ideas)
                        st.toast(f"Status aktualisiert: {neuer_status}")
                        st.rerun()
                        
                with col_btn2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Löschen", key=f"del_btn_{idea.get('id')}", type="secondary", use_container_width=True):
                        ideas.remove(idea)
                        utils.save_data("ideas", ideas)
                        st.success("Idee gelöscht!")
                        st.rerun()