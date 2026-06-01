import streamlit as st
import utils
import time
import pandas as pd

current_user = utils.check_login()
# Die utils.check_login() führt jetzt auch das CSS aus, das alte CSS fällt hier weg!

# ==============================================================================
# DATEN MANAGEMENT 
# ==============================================================================
stats_data = utils.load_data(f"stats_{current_user}", dict)

st.title("📊 Übersicht & Statistik")
st.markdown("Tracke deine Performance manuell, mit voller Kontrolle über Kommastellen und spezifischen Plattform-Metriken.")
st.markdown("---")

# ==============================================================================
# EBENE 1: EINTRAGEN (DYNAMISCH)
# ==============================================================================
st.subheader("📝 Werte eintragen")
plattform = st.selectbox("Für welche Plattform möchtest du eintragen?", ["YouTube", "Twitch", "TikTok", "Instagram"])

with st.form("stats_entry_form", clear_on_submit=True):
    post_title = st.text_input("Kurzer Titel / Beschreibung", placeholder=f"z.B. Stream vom {time.strftime('%d.%m.')} oder Video-Titel")
    
    c1, c2, c3, c4 = st.columns(4)
    
    # Dynamische Felder je nach Plattform inkl. Float-Support
    if plattform == "YouTube":
        with c1: m1 = st.number_input("Aufrufe", min_value=0, step=1)
        with c2: m2 = st.number_input("Likes", min_value=0, step=1)
        with c3: m3 = st.number_input("Kommentare", min_value=0, step=1)
        with c4: m4 = st.number_input("Ø Watchtime (Min)", min_value=0.0, step=0.1, format="%.2f")
        metrics = {"Aufrufe": m1, "Likes": m2, "Kommentare": m3, "Ø Watchtime": m4}
        
    elif plattform == "Twitch":
        with c1: m1 = st.number_input("Ø Zuschauer (CCV)", min_value=0.0, step=0.1, format="%.2f")
        with c2: m2 = st.number_input("Peak Zuschauer", min_value=0, step=1)
        with c3: m3 = st.number_input("Neue Follower", min_value=0, step=1)
        with c4: m4 = st.number_input("Neue Subs", min_value=0, step=1)
        metrics = {"Ø CCV": m1, "Peak": m2, "Follower": m3, "Subs": m4}
        
    elif plattform == "TikTok" or plattform == "Instagram":
        with c1: m1 = st.number_input("Views", min_value=0, step=1)
        with c2: m2 = st.number_input("Likes", min_value=0, step=1)
        with c3: m3 = st.number_input("Kommentare", min_value=0, step=1)
        with c4: m4 = st.number_input("Shares / Saves", min_value=0, step=1)
        metrics = {"Views": m1, "Likes": m2, "Kommentare": m3, "Shares/Saves": m4}
        
    if st.form_submit_button("💾 Im Archiv speichern", type="primary"):
        if post_title:
            post_id = str(int(time.time()))
            stats_data[post_id] = {
                "title": post_title,
                "platform": plattform,
                "date": time.strftime("%d.%m.%Y"),
                "metrics": metrics
            }
            utils.save_data(f"stats_{current_user}", stats_data)
            st.success("✅ Erfolgreich gespeichert!")
            time.sleep(0.5); st.rerun()
        else:
            st.error("Bitte gib einen Titel an.")

st.markdown("---")

# ==============================================================================
# EBENE 2: CHART & ARCHIV (Getrennt nach Plattformen)
# ==============================================================================
st.subheader("📈 Deine Entwicklung & Archiv")

if not stats_data:
    st.info("Trage oben deine ersten Werte ein, um hier Graphen und dein Archiv zu sehen.")
else:
    # Filter für Charts
    filter_plat = st.selectbox("Plattform filtern:", ["YouTube", "Twitch", "TikTok", "Instagram"])
    
    # Daten für das Chart aufbereiten
    chart_data = []
    archiv_items = []
    
    for p_id, p_info in sorted(stats_data.items(), key=lambda x: x[0]):
        # Abwärtskompatibilität für alte Einträge abfangen, falls nötig
        if "metrics" not in p_info: continue 
        
        if p_info.get("platform") == filter_plat:
            row = {"Eintrag": f"{p_info['date']} - {p_info['title']}"}
            row.update(p_info["metrics"])
            chart_data.append(row)
            
        archiv_items.append((p_id, p_info))
            
    if chart_data:
        df = pd.DataFrame(chart_data)
        # Wähle die Metrik basierend auf den Schlüsseln im DataFrame (ohne 'Eintrag')
        metriken = [col for col in df.columns if col != "Eintrag"]
        gewaehlte_metrik = st.selectbox("Welcher Wert soll als Graph gezeigt werden?", metriken)
        
        st.line_chart(df, x="Eintrag", y=gewaehlte_metrik, use_container_width=True)
    else:
        st.info(f"Noch keine Daten für {filter_plat} vorhanden.")
        
    st.markdown("#### 📋 Komplettes Archiv (Bearbeiten & Löschen)")
    
    for p_id, p_info in reversed(archiv_items):
        with st.expander(f"{p_info['date']} | {p_info['platform']} | {p_info['title']}"):
            met_cols = st.columns(len(p_info["metrics"]))
            for idx, (k, v) in enumerate(p_info["metrics"].items()):
                met_cols[idx].metric(k, f"{v}")
                
            if st.button("🗑️ Diesen Eintrag löschen", key=f"del_{p_id}"):
                del stats_data[p_id]
                utils.save_data(f"stats_{current_user}", stats_data)
                st.rerun()