import streamlit as st
import pandas as pd
import utils
import time

# Login prüfen & Cinematic Design laden
current_user = utils.check_login()

st.title("📊 Analytics & Stats")
st.markdown("Tracke deine Performance manuell – mit Fokus auf echte Interaktion und Sichtbarkeit.")
st.markdown("---")

# ==============================================================================
# DATEN LADEN & BEREINIGEN
# ==============================================================================
stats_data = utils.load_data("stats", dict)

if not isinstance(stats_data, dict):
    stats_data = {}

# ==============================================================================
# EBENE 1: EINTRAGEN (INTUITIV & FOKUSSIERT)
# ==============================================================================
st.subheader("📝 Werte eintragen")
plattform = st.selectbox("Für welche Plattform?", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X"])

with st.container(border=True):
    with st.form("stats_entry_form", clear_on_submit=True):
        post_title = st.text_input("Titel / Beschreibung", placeholder=f"z.B. Stream vom {time.strftime('%d.%m.')} oder Video-Titel")
        st.markdown("<br>", unsafe_allow_html=True)
        
        metrics = {}
        
        # ----------------------------------------------------------------------
        # DYNAMISCHE FELDER: YOUTUBE (FOKUS AUF PERFORMANCE & INTERAKTION)
        # ----------------------------------------------------------------------
        if plattform == "YouTube":
            yt_format = st.radio("Welches Format hat das Video?", ["🎬 Normales Video (Longform)", "📱 YouTube Short"], horizontal=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("##### 👁️ Sichtbarkeit & Traffic")
            c1, c2, c3, c4 = st.columns(4)
            
            with c1: m_views = st.number_input("Aufrufe", min_value=0, step=1)
            
            if yt_format == "🎬 Normales Video (Longform)":
                with c2: m_spec = st.number_input("Klickrate (CTR %)", min_value=0.0, step=0.1, format="%.1f")
                spec_name = "Klickrate (CTR %)"
            else:
                with c2: m_spec = st.number_input("Traffic: Shorts-Feed (%)", min_value=0.0, step=0.1, format="%.1f", help="Siehe deinen Screenshot: 'So gelangen Zuschauer zu diesem Kurzvideo'")
                spec_name = "Shorts-Feed (%)"
                
            with c3: m_wt = st.number_input("Watchtime (Std)", min_value=0.0, step=0.1, format="%.2f")
            with c4: m_avd = st.text_input("Ø Wiedergabedauer", placeholder="z.B. 0:45")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 💬 Interaktion & Wachstum")
            c5, c6, c7, c8 = st.columns(4)
            with c5: m_likes = st.number_input("Likes", min_value=0, step=1)
            with c6: m_comms = st.number_input("Kommentare", min_value=0, step=1)
            with c7: m_shares = st.number_input("Geteilt (Shares)", min_value=0, step=1)
            with c8: m_subs = st.number_input("Neue Abonnenten", min_value=0, step=1)
            
            metrics = {
                "Aufrufe": m_views, 
                spec_name: m_spec, 
                "Watchtime (h)": m_wt, 
                "Ø Dauer": m_avd,
                "Likes": m_likes,
                "Kommentare": m_comms,
                "Geteilt": m_shares,
                "Abos": m_subs
            }
            
        # ----------------------------------------------------------------------
        # DYNAMISCHE FELDER: TWITCH / KICK
        # ----------------------------------------------------------------------
        elif plattform in ["Twitch", "Kick"]:
            c1, c2, c3, c4 = st.columns(4)
            with c1: m1 = st.number_input("Ø Zuschauer (CCV)", min_value=0.0, step=0.1, format="%.2f")
            with c2: m2 = st.number_input("Peak Zuschauer", min_value=0, step=1)
            with c3: m3 = st.number_input("Neue Follower", min_value=0, step=1)
            with c4: m4 = st.number_input("Neue Subs", min_value=0, step=1)
            metrics = {"Ø CCV": m1, "Peak": m2, "Follower": m3, "Subs": m4}
            
        # ----------------------------------------------------------------------
        # DYNAMISCHE FELDER: SHORT-FORM (TikTok, Insta, X)
        # ----------------------------------------------------------------------
        else: 
            c1, c2, c3, c4 = st.columns(4)
            with c1: m1 = st.number_input("Views / Impressions", min_value=0, step=1)
            with c2: m2 = st.number_input("Likes", min_value=0, step=1)
            with c3: m3 = st.number_input("Kommentare", min_value=0, step=1)
            with c4: m4 = st.number_input("Shares / Saves", min_value=0, step=1)
            metrics = {"Views": m1, "Likes": m2, "Kommentare": m3, "Shares/Saves": m4}
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Im Archiv speichern", type="primary", use_container_width=True):
            if post_title:
                post_id = str(int(time.time()))
                stats_data[post_id] = {
                    "title": post_title,
                    "platform": plattform,
                    "date": time.strftime("%d.%m.%Y"),
                    "metrics": metrics
                }
                utils.save_data("stats", stats_data)
                st.success("✅ Erfolgreich gespeichert!")
                time.sleep(0.5); st.rerun()
            else:
                st.error("⚠️ Bitte gib einen Titel an.")

st.markdown("---")

# ==============================================================================
# EBENE 2: GRAPH & ARCHIV (GEFILTERT NACH PLATTFORM)
# ==============================================================================
st.subheader("📈 Entwicklung & Archiv")

if not stats_data:
    st.info("Noch keine Daten vorhanden. Trage oben deinen ersten Stream oder Post ein!")
else:
    filter_plat = st.selectbox("Plattform filtern:", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X"])
    
    chart_data = []
    archiv_items = []
    
    for p_id, p_info in sorted(stats_data.items(), key=lambda x: x[0]):
        if not isinstance(p_info, dict) or "metrics" not in p_info: continue 
        
        if p_info.get("platform") == filter_plat:
            row = {"Eintrag": f"{p_info.get('date', '')} - {p_info.get('title', '')}"}
            row.update(p_info.get("metrics", {}))
            chart_data.append(row)
            archiv_items.append((p_id, p_info))
            
    # DIAGRAMM
    if chart_data:
        with st.container(border=True):
            df = pd.DataFrame(chart_data)
            numerische_spalten = df.select_dtypes(include=['number']).columns.tolist()
            metriken = [col for col in numerische_spalten if col != "Eintrag"]
            
            if metriken:
                gewaehlte_metrik = st.selectbox("Metrik für den Graphen:", metriken)
                st.line_chart(df, x="Eintrag", y=gewaehlte_metrik, use_container_width=True)
            else:
                st.info("Für diese Auswahl stehen keine numerischen Daten als Diagramm zur Verfügung.")
    else:
        st.info(f"Noch keine Einträge für {filter_plat} vorhanden.")
        
    # ARCHIV & LÖSCHEN
    st.markdown(f"#### 📋 Letzte Einträge ({filter_plat})")
    for p_id, p_info in reversed(archiv_items):
        with st.expander(f"{p_info['date']} | {p_info['title']}"):
            
            if p_info.get("platform") == "YouTube":
                met_cols_1 = st.columns(4)
                met_cols_2 = st.columns(4)
                
                for idx, (k, v) in enumerate(p_info["metrics"].items()):
                    if idx < 4:
                        met_cols_1[idx].metric(k, f"{v}")
                    else:
                        met_cols_2[idx - 4].metric(k, f"{v}")
            else:
                met_cols = st.columns(len(p_info["metrics"]))
                for idx, (k, v) in enumerate(p_info["metrics"].items()):
                    met_cols[idx].metric(k, f"{v}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Eintrag löschen", key=f"del_{p_id}"):
                del stats_data[p_id]
                utils.save_data("stats", stats_data)
                st.rerun()