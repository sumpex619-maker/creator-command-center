import streamlit as st
import utils
import datetime
import time
import uuid

# Login prüfen & Cinematic Design laden
current_user = utils.check_login()

st.title("🗓️ Dynamischer Sendeplan")
st.markdown("Verwalte verschiedene Pläne (z.B. Streams, Rennkalender), setze feste Daten und poste sie als professionelles Embed in Discord.")
st.markdown("---")

# ==============================================================================
# DATEN LADEN
# ==============================================================================
# Neue Struktur: {"categories": ["Main Stream"], "entries": [{"id": "...", "cat": "...", "date": "YYYY-MM-DD", ...}]}
plan_data = utils.load_data("sendeplan_v2", lambda: {"categories": ["Standard Stream"], "entries": []})

# Webhooks für den Nutzer aus der DB holen
conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, url, role_id FROM webhooks WHERE username = %s", (current_user,))
user_hooks = cursor.fetchall()
cursor.close(); conn.close()

# ==============================================================================
# TABS FÜR ÜBERSICHTLICHKEIT
# ==============================================================================
tab_eintragen, tab_posten, tab_kategorien = st.tabs(["📝 Termine verwalten", "🚀 Vorschau & Posten", "📁 Kategorien & Setup"])

# ------------------------------------------------------------------------------
# TAB 1: TERMINE EINTRAGEN & VERWALTEN
# ------------------------------------------------------------------------------
with tab_eintragen:
    col_form, col_list = st.columns([1, 1.2], gap="large")
    
    with col_form:
        st.subheader("Neuen Termin anlegen")
        with st.container(border=True):
            with st.form("new_event_form", clear_on_submit=True):
                kategorie = st.selectbox("Für welchen Plan?", plan_data["categories"])
                titel = st.text_input("Titel des Events", placeholder="z.B. GT3 Ligarennen Spa oder Just Chatting")
                
                c_date, c_time = st.columns(2)
                with c_date: datum = st.date_input("Datum", datetime.date.today())
                with c_time: uhrzeit = st.time_input("Uhrzeit", datetime.time(19, 0))
                
                beschreibung = st.text_area("Kurze Beschreibung", placeholder="Was genau passiert dort? (Wird im Discord angezeigt)")
                
                if st.form_submit_button("💾 Termin speichern", type="primary", use_container_width=True):
                    if titel:
                        new_entry = {
                            "id": str(uuid.uuid4())[:8],
                            "cat": kategorie,
                            "date": datum.strftime("%Y-%m-%d"),
                            "time": uhrzeit.strftime("%H:%M"),
                            "title": titel,
                            "desc": beschreibung
                        }
                        plan_data["entries"].append(new_entry)
                        utils.save_data("sendeplan_v2", plan_data)
                        st.success("✅ Termin gespeichert!")
                        time.sleep(0.5); st.rerun()
                    else:
                        st.error("⚠️ Bitte einen Titel eingeben.")

    with col_list:
        st.subheader("Geplante Termine")
        filter_cat = st.selectbox("Ansicht filtern:", ["Alle Pläne anzeigen"] + plan_data["categories"])
        
        # Sortiere Einträge nach Datum und Uhrzeit
        sorted_entries = sorted(plan_data["entries"], key=lambda x: (x['date'], x['time']))
        
        has_entries = False
        for entry in sorted_entries:
            if filter_cat == "Alle Pläne anzeigen" or entry["cat"] == filter_cat:
                has_entries = True
                
                # Datum schön formatieren (DD.MM.YYYY)
                date_obj = datetime.datetime.strptime(entry['date'], "%Y-%m-%d")
                ger_date = date_obj.strftime("%d.%m.%Y")
                
                with st.expander(f"🗓️ {ger_date} | {entry['time']} Uhr - {entry['title']}"):
                    st.markdown(f"**Kategorie:** `{entry['cat']}`")
                    st.write(entry['desc'] if entry['desc'] else "*Keine Beschreibung.*")
                    
                    if st.button("🗑️ Termin löschen", key=f"del_{entry['id']}"):
                        plan_data["entries"] = [e for e in plan_data["entries"] if e["id"] != entry["id"]]
                        utils.save_data("sendeplan_v2", plan_data)
                        st.rerun()
                        
        if not has_entries:
            st.info("Keine Termine für diese Auswahl gefunden.")

# ------------------------------------------------------------------------------
# TAB 2: DISCORD EMBED & POSTEN
# ------------------------------------------------------------------------------
with tab_posten:
    st.subheader("Discord Uplink")
    
    if not user_hooks:
        st.warning("⚠️ Du hast noch keine Webhooks in deinen Einstellungen (Business/Setup) hinterlegt!")
    elif not plan_data["entries"]:
        st.info("Trage zuerst Termine ein, bevor du einen Plan posten kannst.")
    else:
        c_setup, c_preview = st.columns([1, 1.5], gap="large")
        
        with c_setup:
            st.markdown("### 1. Plan auswählen")
            post_cat = st.selectbox("Welchen Plan möchtest du posten?", plan_data["categories"], key="post_cat")
            
            st.markdown("### 2. Ziel auswählen")
            hook_options = {h["profile_name"]: {"url": h["url"], "role_id": h["role_id"]} for h in user_hooks}
            selected_hook = st.selectbox("In welchen Kanal senden?", list(hook_options.keys()))
            
            custom_msg = st.text_area("Zusätzliche Nachricht (Optional)", placeholder="Hey Leute, hier ist der Plan für diese Woche!")
            
            # --- DATEN FÜR EMBED ZUSAMMENSTELLEN ---
            entries_to_post = [e for e in sorted_entries if e["cat"] == post_cat]
            
            # Embed Struktur für Discord
            embed = {
                "title": f"📅 UPDATE: {post_cat}",
                "color": 5569535, # Ein schönes Cyan-Blau (#54FBFF)
                "fields": []
            }
            
            for e in entries_to_post:
                d_obj = datetime.datetime.strptime(e['date'], "%Y-%m-%d")
                embed["fields"].append({
                    "name": f"🗓️ {d_obj.strftime('%d.%m.%Y')} | ⏰ {e['time']} Uhr",
                    "value": f"**{e['title']}**\n{e['desc']}\n",
                    "inline": False
                })
                
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Plan jetzt an Discord senden", type="primary", use_container_width=True):
                if not entries_to_post:
                    st.error("Dieser Plan hat aktuell keine Termine!")
                else:
                    target_data = hook_options[selected_hook]
                    
                    # Ping bauen, wenn Rolle existiert
                    role_id = target_data.get("role_id")
                    ping_text = f"<@&{role_id}>\n" if role_id else ""
                    
                    # Nachrichtentext = Ping + Optionale Custom Message
                    final_content = ping_text + custom_msg
                    if not final_content.strip(): 
                        final_content = None # Wenn leer, nur das Embed schicken
                        
                    success, response_msg = utils.send_discord_webhook(target_data["url"], text_content=final_content, embed_data=embed)
                    if success: 
                        st.success("✅ Plan wurde erfolgreich als Embed gepostet!")
                    else: 
                        st.error(f"Fehler: {response_msg}")
        
        # --- LOKALE VORSCHAU ---
        with c_preview:
            st.markdown("### 👀 Embed Vorschau")
            if not entries_to_post:
                st.info("Keine Termine in dieser Kategorie zum Anzeigen.")
            else:
                is_dark = st.session_state.get("theme", "Midnight (Dark)") == "Midnight (Dark)"
                bg_col = "#36393F" if is_dark else "#F2F3F5"
                text_col = "#DCDDDE" if is_dark else "#2E3338"
                embed_bg = "#2F3136" if is_dark else "#FFFFFF"
                
                role_prev = hook_options[selected_hook].get("role_id")
                ping_str = f"<span style='color: #7289DA; background-color: rgba(114, 137, 218, 0.1); padding: 0 4px; border-radius: 3px;'>@Rolle ({role_prev})</span><br><br>" if role_prev else ""
                
                # HTML Konstrukt für die Embed-Vorschau
                html_preview = f"""
                <div style="background-color: {bg_col}; padding: 15px; border-radius: 8px; font-family: 'Inter', sans-serif;">
                    <p style="color: #DCAE96; margin-bottom: 5px; font-weight: bold;">{current_user} <span style="background-color: #5865F2; color: white; padding: 2px 5px; border-radius: 3px; font-size: 10px;">BOT</span></p>
                    <p style="color: {text_col}; white-space: pre-wrap; font-size: 14px;">{ping_str}{custom_msg}</p>
                    
                    <div style="background-color: {embed_bg}; border-left: 4px solid #54FBFF; padding: 12px; border-radius: 4px; margin-top: 10px;">
                        <h4 style="color: {'#FFFFFF' if is_dark else '#000000'}; margin: 0 0 10px 0; font-family: 'Inter', sans-serif;">{embed['title']}</h4>
                """
                for f in embed["fields"]:
                    html_preview += f"""
                        <div style="margin-bottom: 12px;">
                            <div style="color: {'#FFFFFF' if is_dark else '#000000'}; font-weight: 600; font-size: 13px;">{f['name']}</div>
                            <div style="color: {text_col}; font-size: 13px; white-space: pre-wrap; margin-top: 2px;">{f['value']}</div>
                        </div>
                    """
                html_preview += "</div></div>"
                
                st.markdown(html_preview, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 3: KATEGORIEN VERWALTEN
# ------------------------------------------------------------------------------
with tab_kategorien:
    st.subheader("📁 Plan-Kategorien anlegen")
    st.write("Hier definierst du die verschiedenen Kalender, die du benötigst.")
    
    with st.container(border=True):
        with st.form("new_cat_form", clear_on_submit=True):
            new_cat = st.text_input("Neue Kategorie (z.B. Podcast, GT3 Liga, Main Channel)")
            if st.form_submit_button("Hinzufügen"):
                if new_cat and new_cat not in plan_data["categories"]:
                    plan_data["categories"].append(new_cat)
                    utils.save_data("sendeplan_v2", plan_data)
                    st.success(f"Kategorie '{new_cat}' hinzugefügt!")
                    st.rerun()
                    
    st.markdown("#### Aktuelle Kategorien")
    for cat in plan_data["categories"]:
        cc1, cc2 = st.columns([4, 1])
        cc1.markdown(f"**{cat}**")
        if len(plan_data["categories"]) > 1:
            if cc2.button("Löschen", key=f"delcat_{cat}"):
                plan_data["categories"].remove(cat)
                # Optionale Bereinigung: Alle Termine dieser Kategorie löschen
                plan_data["entries"] = [e for e in plan_data["entries"] if e["cat"] != cat]
                utils.save_data("sendeplan_v2", plan_data)
                st.rerun()
        else:
            cc2.caption("Letzte nicht löschbar")
        st.divider()