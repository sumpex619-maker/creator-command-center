import streamlit as st
import pandas as pd
import utils

# ==============================================================================
# SEITEN-KONFIGURATION & LOGIN-CHECK
# ==============================================================================
current_user = utils.check_login()

st.title("💼 Creator Business Hub")
st.markdown("Dein roter Faden vom Hobby-Streamer zum professionellen Creator-Setup.")

t_fahrplan, t_wissen, t_links = st.tabs(["🗺️ Roadmap Checkliste", "📖 Business-Wissen", "🔗 Partner-Links"])

# ------------------------------------------------------------------------------
# TAB 1: ROADMAP (CHECKLISTE)
# ------------------------------------------------------------------------------
with t_fahrplan:
    st.subheader("🚀 Deine Business-Roadmap")
    st.markdown("Hake ab, was du erledigt hast. Das Tool speichert deinen Fortschritt.")
    
    progress = utils.load_data("business_progress", dict)
    
    steps = {
        "step_1": "Hobby vs. Gewerbe geprüft (Pflicht bei Monetarisierung!)",
        "step_2": "Gewerbe angemeldet (Tipp: Kleinunternehmer-Regelung)",
        "step_3": "Rechtssicheres Impressum eingerichtet",
        "step_4": "Professionelle Business-E-Mail (@deinedomain.de) angelegt",
        "step_5": "Datenschutzkonforme Link-in-Bio Seite erstellt"
    }
    
    for k, v in steps.items():
        if k not in progress: 
            progress[k] = False
            
    # Modulares Side-by-Side Design für die Checkliste vs. Fortschrittsbalken
    col_checks, col_score = st.columns([2, 1])
    
    with col_checks:
        for k, v in steps.items():
            new_val = st.checkbox(v, value=progress[k], key=f"check_{k}")
            if new_val != progress[k]:
                progress[k] = new_val
                utils.save_data("business_progress", progress)
                st.rerun()
                
    with col_score:
        score = sum(progress.values())
        prozent = int(score / len(steps) * 100)
        st.markdown("### 📊 Status")
        st.progress(prozent / 100)
        st.markdown(f"**Fertiggestellt: {prozent}%**")
        if prozent == 100:
            st.success("🎉 Komplettes Setup abgeschlossen!")

# ------------------------------------------------------------------------------
# TAB 2: BUSINESS WISSEN
# ------------------------------------------------------------------------------
with t_wissen:
    st.subheader("📚 Experten-Tipps kompakt")
    
    # Kacheln im modernen Look
    with st.expander("⚖️ 1. Wann muss ich ein Gewerbe anmelden?"):
        st.markdown("""
        Sobald eine **Gewinnerzielungsabsicht** vorliegt, musst du ein Gewerbe anmelden. 
        Sobald du z.B. den Affiliate-Status bei Twitch annimmst oder YouTube-Monetarisierung einschaltest, *beabsichtigst* du, Geld zu verdienen. Das kostet beim Gewerbeamt deiner Stadt ca. 15–40 € und dauert 10 Minuten. Nutze als Anfänger die **Kleinunternehmerregelung**.
        """)
        
    with st.expander("📧 2. Die professionelle Business-Mail"):
        st.markdown("""
        Sichere dir eine eigene Domain (z.B. `deincreatorname.de`) bei Anbietern wie Strato oder Ionos. Richte dir dort eine Mailadresse ein, wie z.B. `business@deincreatorname.de`. Das erhöht deine Chancen auf Zusagen von Marken drastisch!
        """)

    with st.expander("🔗 3. Die 'Link-in-Bio'-Falle"):
        st.markdown("""
        Viele US-Tools wie Linktree sind in Deutschland wegen der DSGVO datenschutzrechtlich schwierig. Am sichersten ist eine eigene, kleine, cleane Website für deine Links.
        """)

# ------------------------------------------------------------------------------
# TAB 3: PARTNER-LINKS
# ------------------------------------------------------------------------------
with t_links:
    st.subheader("🔗 Affiliate- & Partner-Links verwalten")
    
    with st.form("add_link_form", clear_on_submit=True):
        # Side-by-Side Eingabe
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name des Partners / Produkts", placeholder="z.B. Mein Mikrofon")
            kategorie = st.selectbox("Kategorie", ["Hardware", "Games", "Merch", "Sonstiges"])
        with c2:
            url = st.text_input("Dein Affiliate-Link", placeholder="https://...")
            code = st.text_input("Rabatt-Code (falls vorhanden)", placeholder="z.B. CREATOR10")
            
        if st.form_submit_button("💾 Link speichern", type="primary", use_container_width=True):
            if name and url:
                links = utils.load_data("affiliate_links", list)
                links.append({"name": name, "url": url, "kategorie": kategorie, "code": code})
                utils.save_data("affiliate_links", links)
                st.success("✅ Partner-Link gespeichert!")
                st.rerun()
            else:
                st.error("Bitte Partner-Name und Link ausfüllen.")
    
    st.markdown("---")
    
    links = utils.load_data("affiliate_links", list)
    if not links:
        st.info("Noch keine Partner-Links hinterlegt.")
    else:
        df_links = pd.DataFrame(links)
        # Sortieren nach Kategorie
        for kat, sub_df in df_links.groupby("kategorie"):
            st.markdown(f"#### 📁 {kat}")
            for _, row in sub_df.iterrows():
                # Side-by-Side Darstellung der gespeicherten Links
                col_view1, col_view2 = st.columns([3, 1])
                with col_view1:
                    st.markdown(f"**{row['name']}**")
                    st.code(row['url'])
                    if row.get('code'):
                        st.markdown(f"Code: `{row['code']}`")
                with col_view2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{row['name']}", use_container_width=True):
                        links = [l for l in links if l['name'] != row['name']]
                        utils.save_data("affiliate_links", links)
                        st.rerun()
                st.divider()