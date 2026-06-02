import streamlit as st
import pandas as pd
import utils
import time

# Login prüfen & Cinematic Design laden
current_user = utils.check_login()

st.title("📊 Analytics & Stats")
st.markdown("Tracke deine Performance manuell – mit voller Kontrolle über Kommastellen und plattformspezifischen Metriken.")
st.markdown("---")

# ==============================================================================
# DATEN LADEN & BEREINIGEN (BUGFIX)
# ==============================================================================
stats_data = utils.load_data("stats", dict)

# BUGFIX: Falls alte Daten aus vorherigen Versionen versehentlich als Liste 
# (statt als Dictionary) in der Datenbank liegen, wird dies hier abgefangen!
if not isinstance(stats_data, dict):
    stats_data = {}

# ==============================================================================
# EBENE 1: EINTRAGEN (DYNAMISCH & KOMMA-SUPPORT)
# ==============================================================================
st.subheader("📝 Werte eintragen")
# YouTube ist jetzt Standardmäßig direkt als Erstes ausgewählt
plattform = st.selectbox("Für welche Plattform?", ["YouTube", "Twitch", "TikTok", "Instagram", "Kick", "X"])

with st.container(border=True):
    with st.form("stats_entry_form", clear_on_submit=True):
        post_title = st.text_input("Titel / Beschreibung", placeholder=f"z.B. Stream vom {time.strftime('%d.%m.')} oder Video-Titel")
        
        c1, c2, c3, c4 = st.columns(4)
        metrics = {}
        
        # Dynamische Felder je nach Plattform
        if plattform == "YouTube":
            with c1: m1 = st.number_input("Aktive Wiedergaben", min_value=0, step=1)
            with c2: m2 = st.number_input("Einzelne Zuschauer", min_value=0, step=1)
            with c3: m3 = st.number_input("Wiedergabezeit (Stunden)", min_value=0.0, step=0.1, format="%.2f")
            with c4: m4 = st.text_input("Ø Wiedergabedauer", placeholder="z.B. 0:17")
            metrics = {"Aktive Wiedergaben": m1, "Einzelne Zuschauer": m2, "Wiedergabezeit (Std)": m3, "Ø Wiedergabedauer": m4}
            
        elif plattform in ["Twitch", "Kick"]:
            with c1: m1 = st.number_input("Ø Zuschauer (CCV)", min_value=0.0, step=0.1, format="%.2f")
            with c2: m2 = st.number_input("Peak Zuschauer", min_value=0, step=1)
            with c3: m3 = st.number_input("Neue Follower", min_value=0, step=1)
            with c4: m4 = st.number_input("Neue Subs", min_value=0, step=1)
            metrics = {"Ø CCV": m1, "Peak": m2, "Follower": m3, "Subs": m4}
            
        else: # TikTok, Instagram, X
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
    
    # Daten sortieren und filtern
    for p_id, p_info in sorted(stats_data.items(), key=lambda x: x[0]):
        # Schutzmechanismus: Überspringt fehlerhafte Einzeleinträge
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
            
            # DIAGRAMM-SCHUTZ: Wir filtern alle Text-Felder (wie "0:17") heraus, 
            # da ein Graph nur mit echten Zahlen gezeichnet werden kann!
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
            met_cols = st.columns(len(p_info["metrics"]))
            
            for idx, (k, v) in enumerate(p_info["metrics"].items()):
                # Zeigt die Metrik wunderschön im Bento-Look an
                met_cols[idx].metric(k, f"{v}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Eintrag löschen", key=f"del_{p_id}"):
                del stats_data[p_id]
                utils.save_data("stats", stats_data)
                st.rerun()