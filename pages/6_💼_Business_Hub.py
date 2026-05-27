import streamlit as st
import pandas as pd
import utils

# ==============================================================================
# SEITEN-KONFIGURATION & LOGIN-CHECK
# ==============================================================================
current_user = utils.check_login()

st.title("💼 Creator Business Hub")
st.markdown("Vom Hobby zum Business. Hier findest du deinen roten Faden für Steuern, Rechtliches und dein professionelles Setup.")

# Tabs im modernen 2026er Clean-Style
tab_fahrplan, tab_wissen, tab_links = st.tabs([
    "🗺️ Der Rote Faden (Checkliste)",
    "📖 Business-Wissen kompakt",
    "🔗 Meine Affiliate- & Partner-Links"
])

# ------------------------------------------------------------------------------
# TAB 1: DER ROTE FADEN (INTERAKTIVE CHECKLISTE)
# ------------------------------------------------------------------------------
with tab_fahrplan:
    st.subheader("🚀 Deine Business-Roadmap")
    st.markdown("Hake die Schritte ab, sobald du sie erledigt hast. Dein Dashboard merkt sich deinen Fortschritt!")

    # Fortschritt aus der Datenbank laden
    progress = utils.load_data("business_progress", dict)
    
    # Standardwerte, falls die DB noch leer ist
    steps = {
        "step_1": "Hobby vs. Gewerbe geprüft (Wann muss ich zum Amt?)",
        "step_2": "Gewerbe angemeldet (Kleinunternehmer-Regelung gewählt)",
        "step_3": "Rechtssicheres Impressum für Social Media erstellt",
        "step_4": "Professionelle Business-E-Mail-Adresse eingerichtet",
        "step_5": "Eigene 'Link-in-Bio'-Seite aufgesetzt",
        "step_6": "Erstes kleines Media-Kit (Zahlen & Fakten) vorbereitet"
    }
    
    # Sicherstellen, dass alle Keys existieren
    for key in steps.keys():
        if key not in progress:
            progress[key] = False

    # Checkboxen anzeigen
    checked_count = 0
    st.markdown("---")
    
    # Wir speichern die Änderungen direkt ab
    for key, text in steps.items():
        # Falls abgehakt, zählen wir es für den Fortschrittsbalken
        current_state = st.checkbox(text, value=progress[key], key=f"cb_{key}")
        if current_state:
            checked_count += 1
        if current_state != progress[key]:
            progress[key] = current_state
            utils.save_data("business_progress", progress)
            st.rerun()

    st.markdown("---")
    # Fortschrittsbalken berechnen
    prozent = int((checked_count / len(steps)) * 100)
    st.markdown(f"**Gesamtfortschritt: {prozent}%**")
    st.progress(prozent / 100)
    
    if prozent == 100:
        st.balloons()
        st.success("🎉 Wahnsinn! Du hast dein Creator-Business komplett professionell aufgestellt!")

# ------------------------------------------------------------------------------
# TAB 2: BUSINESS-WISSEN KOMPAKT
# ------------------------------------------------------------------------------
with tab_wissen:
    st.subheader("📚 Versteckte Hürden einfach erklärt")
    st.markdown("Keine Angst vor Bürokratie. Hier ist das Wichtigste, was du wissen musst:")

    with st.expander("⚖️ 1. Wann muss ich ein Gewerbe anmelden? (Deutschland/DACH)"):
        st.markdown("""
        **Der größte Mythos:** *"Ich muss erst ein Gewerbe anmelden, wenn ich soundsoviel Euro verdiene."* **Das ist falsch!**
        
        In Deutschland gilt: Sobald eine **Gewinnerzielungsabsicht** vorliegt, musst du ein Gewerbe anmelden. 
        * **Hobby:** Du streamst nur zum Spaß und hast alle Einnahmen-Funktionen (Subs, Bits, Werbung, Spenden) deaktiviert.
        * **Gewerbe:** Sobald du den "Affiliate-Status" bei Twitch annimmst, YouTube-Monetarisierung einschaltest oder Spenden-Buttons platzierst, *beabsichtigst* du, Geld zu verdienen. Das kostet beim Gewerbeamt deiner Stadt ca. 15–40 € und dauert 10 Minuten.
        
        **Tipp für Anfänger:** Nutze bei der steuerlichen Erfassung das Feld **Kleinunternehmerregelung (§ 19 UStG)**. Damit musst du keine Umsatzsteuer auf deinen Rechnungen ausweisen und hast viel weniger Papierkram (gilt aktuell bis zu einer Umsatzgrenze von 25.000 € im Jahr).
        """)

    with st.expander("📧 2. Die professionelle Business-Mail"):
        st.markdown("""
        Wenn eine Marke dich für ein Sponsoring anschreiben will, sucht sie im Impressum nach einer Mail. Eine Adresse wie *gamer_creative99@gmail.com* wirkt unprofessionell.
        
        **Der bessere Weg:**
        1. Sichere dir eine eigene Domain (z.B. `deincreatorname.de`) bei Anbietern wie Strato, Ionos oder Nitrado (kostet oft nur 1–2 € im Monat).
        2. Richte dir dort eine Mailadresse ein, wie z.B. `kontakt@deincreatorname.de` oder `business@deincreatorname.de`.
        3. Das erhöht deine Chancen auf Zusagen von Marken drastisch, weil es zeigt: *Ich meine das ernst.*
        """)

    with st.expander("🔗 3. Die 'Link-in-Bio'-Falle (Social Media bündeln)"):
        st.markdown("""
        Instagram, TikTok und YouTube erlauben oft nur *einen einzigen Link* in deiner Profilbeschreibung. Du willst dort aber Twitch, YouTube, Discord und deinen Merch zeigen.
        
        * **Bekannte Tools:** Linktree, Bento.me, Beacons.
        * **⚠️ Achtung Abmahngefahr:** Viele dieser Tools (besonders aus den USA) sind in Deutschland wegen der DSGVO (Datenschutz) in einer rechtlichen Grauzone, wenn sie Tracker nutzen.
        * **Die 2026-Lösung:** Am sichersten fährst du, wenn du dir über eine eigene kleine Website (oder direkt über dieses Dashboard-System in Zukunft) eine eigene, cleane Link-Seite baust, die komplett datenschutzkonform ist.
        """)

    with st.expander("📝 4. Die Impressumspflicht (Vorsicht vor Abmahnungen!)"):
        st.markdown("""
        Sobald du Social-Media-Kanäle "geschäftsmäßig" betreibst (und das tust du, sobald du Geld verdienen *könntest* oder regelmäßig streamst), brauchst du ein **Impressum**.
        
        Das Impressum muss leicht erkennbar und unmittelbar erreichbar sein (maximal 2 Klicks). 
        * **Inhalt:** Dein echter Name, eine ladungsfähige Anschrift (kein reines Postfach!) und eine schnelle Kontaktmöglichkeit (Mail + Telefonnummer).
        * **Tipp für Privatsphäre:** Wenn du deine private Wohnadresse nicht im Internet stehen haben willst, gibt es sogenannte **Impressums-Services** für Creator (z.B. von *Gewerbequadrat* oder *Anwaltskanzleien*). Gegen eine kleine Gebühr stellen sie dir eine rechtssichere Adresse zur Verfügung und leiten Post an dich weiter.
        """)

# ------------------------------------------------------------------------------
# TAB 3: AFFILIATE- & PARTNER-LINKS
# ------------------------------------------------------------------------------
with tab_links:
    st.subheader("🔗 Deine Affiliate- & Partner-Links verwalten")
    st.markdown("Speichere hier deine Empfehlungslinks (z.B. Amazon-Equipment, Instant Gaming, etc.), um sie beim Posten immer sofort griffbereit zu haben.")

    # Formular zum Hinzufügen eines Links
    with st.form("add_link_form", clear_on_submit=True):
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            partner_name = st.text_input("Name des Partners / Produkts", placeholder="z.B. Mein Lenkrad (Amazon)")
            partner_url = st.text_input("Dein Affiliate-Link", placeholder="https://amzn.to/...")
        with col_l2:
            rabatt_code = st.text_input("Rabatt-Code (falls vorhanden)", placeholder="z.B. CREATOR10")
            kategorie = st.selectbox("Kategorie", ["Setup / Hardware", "Spiele / Keys", "Merch", "Sonstiges"])
            
        if st.form_submit_button("💾 Link speichern", type="primary", use_container_width=True):
            if not partner_name or not partner_url:
                st.error("Bitte Name und Link ausfüllen!")
            else:
                new_link = {
                    "name": partner_name,
                    "url": partner_url,
                    "code": rabatt_code,
                    "kategorie": kategorie
                }
                current_links = utils.load_data("affiliate_links", list)
                current_links.append(new_link)
                utils.save_data("affiliate_links", current_links)
                st.success(f"Link für '{partner_name}' gespeichert!")
                st.rerun()

    st.markdown("---")
    
    # Gespeicherte Links anzeigen
    saved_links = utils.load_data("affiliate_links", list)
    if not saved_links:
        st.info("Noch keine Partner-Links hinterlegt.")
    else:
        # In Pandas DataFrame umwandeln für ein schickes Design
        df_links = pd.DataFrame(saved_links)
        
        # Schöne Anzeige pro Kategorie
        for kat, sub_df in df_links.groupby("kategorie"):
            st.markdown(f"### 📁 {kat}")
            for _, row in sub_df.iterrows():
                with st.expander(f"🔗 {row['name']}"):
                    st.markdown(f"**Link:** `{row['url']}`")
                    if row['code']:
                        st.markdown(f"**Rabatt-Code:** `{row['code']}`")
                    
                    # Kleiner Lösch-Button
                    if st.button("🗑️ Link löschen", key=f"del_link_{row['name']}"):
                        saved_links = [l for l in saved_links if l['name'] != row['name']]
                        utils.save_data("affiliate_links", saved_links)
                        st.success("Link gelöscht!")
                        st.rerun()