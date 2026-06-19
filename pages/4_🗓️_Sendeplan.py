import streamlit as st
import utils
import datetime
import time
import uuid

# Login prüfen
current_user = utils.check_login()

st.title("🗓️ Dynamischer Sendeplan")
st.markdown("Verwalte deine Termine und poste deinen Plan als professionelles Discord-Embed.")
st.markdown("---")

# ==============================================================================
# DATEN LADEN
# ==============================================================================
# Wir strukturieren die Daten etwas flexibler für Multi-User
plan_data = utils.load_data("sendeplan_pro", lambda: {"categories": ["Wochenplan", "Rennkalender", "Special Events"], "entries": []})

tab_eintragen, tab_posten = st.tabs(["📝 Termine verwalten", "🚀 Vorschau & Posten"])

# ------------------------------------------------------------------------------
# TAB 1: TERMINE EINTRAGEN & VERWALTEN
# ------------------------------------------------------------------------------
with tab_eintragen:
    col_form, col_list = st.columns([1, 1.2], gap="large")
    
    with col_form:
        st.subheader("Neuen Termin anlegen")
        with st.container(border=True):
            with st.form("new_event_form", clear_on_submit=True):
                # Dynamische Kategorie-Wahl
                gewaehlter_plan = st.selectbox("📂 Für welchen Plan?", plan_data["categories"])
                
                titel = st.text_input("Titel des Events", placeholder="z.B. GT3 Ligarennen Spa oder Just Chatting")
                
                c_date, c_time = st.columns(2)
                with c_date: datum = st.date_input("Datum", datetime.date.today())
                with c_time: uhrzeit = st.time_input("Uhrzeit", datetime.time(19, 0))
                
                beschreibung = st.text_area("Kurze Beschreibung", placeholder="Was genau passiert dort? (Erscheint im Embed)")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("💾 Termin speichern", type="primary", use_container_width=True):
                    if titel:
                        new_entry = {
                            "id": str(uuid.uuid4())[:8],
                            "cat": gewaehlter_plan, 
                            "date": datum.strftime("%Y-%m-%d"),
                            "time": uhrzeit.strftime("%H:%M"),
                            "title": titel,
                            "desc": beschreibung
                        }
                        plan_data["entries"].append(new_entry)
                        utils.save_data("sendeplan_pro", plan_data)
                        st.success("✅ Termin gespeichert!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("⚠️ Bitte einen Titel eingeben.")

        # Kleine Verwaltung für eigene Kategorien
        with st.expander("⚙️ Neue Plan-Kategorie erstellen"):
            with st.form("new_cat_form", clear_on_submit=True):
                new_cat = st.text_input("Name der neuen Kategorie (z.B. Podcast-Termine)")
                if st.form_submit_button("Hinzufügen"):
                    if new_cat and new_cat not in plan_data["categories"]:
                        plan_data["categories"].append(new_cat)
                        utils.save_data("sendeplan_pro", plan_data)
                        st.rerun()

    with col_list:
        st.subheader("Deine geplanten Termine")
        filter_cat = st.selectbox("Termine filtern nach:", ["Alle anzeigen"] + plan_data["categories"])
        
        gefilterte_entries = plan_data["entries"] if filter_cat == "Alle anzeigen" else [e for e in plan_data["entries"] if e.get("cat") == filter_cat]
        
        if not gefilterte_entries:
            st.info("Aktuell keine Termine eingetragen.")
        else:
            sorted_entries = sorted(gefilterte_entries, key=lambda x: (x['date'], x['time']))
            for entry in sorted_entries:
                date_obj = datetime.datetime.strptime(entry['date'], "%Y-%m-%d")
                ger_date = date_obj.strftime("%d.%m.%Y")
                
                with st.expander(f"🗓️ {ger_date} | {entry['time']} Uhr - {entry['title']} ({entry.get('cat', '')})"):
                    st.write(entry['desc'] if entry['desc'] else "*Keine Beschreibung hinterlegt.*")
                    if st.button("🗑️ Termin löschen", key=f"del_{entry['id']}", use_container_width=True):
                        plan_data["entries"] = [e for e in plan_data["entries"] if e["id"] != entry["id"]]
                        utils.save_data("sendeplan_pro", plan_data)
                        st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: DISCORD EMBED & POSTEN
# ------------------------------------------------------------------------------
with tab_posten:
    st.subheader("Discord Uplink: Sendeplan posten")
    
    # Webhooks aus der zentralen Datenbank abrufen
    conn = utils.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_name, url, role_id FROM webhooks WHERE username = %s", (current_user,))
    all_hooks = cursor.fetchall()
    cursor.close(); conn.close()

    if not all_hooks:
        st.warning("⚠️ Du hast noch keine Webhooks in den Einstellungen hinterlegt.")
    elif not plan_data["entries"]:
        st.info("Trage im ersten Reiter Termine ein, bevor du etwas posten kannst.")
    else:
        c_setup, c_preview = st.columns([1, 1.5], gap="large")
        
        with c_setup:
            st.markdown("#### 1. Setup")
            post_cat = st.selectbox("Welchen Plan möchtest du posten?", plan_data["categories"], key="post_cat")
            
            hook_options = {h["profile_name"]: {"url": h["url"], "role_id": h["role_id"]} for h in all_hooks}
            selected_hook = st.selectbox("An welchen Discord-Kanal senden?", list(hook_options.keys()))
            
            st.markdown("#### 🎨 Design & Text")
            embed_color = st.color_picker("Rahmenfarbe", "#00E5FF", key="plan_color")
            custom_msg = st.text_area("Nachricht (außerhalb des Embeds)", placeholder="Hey Leute, hier ist der Plan für diese Woche!")
            
            # Einträge filtern
            entries_to_post = sorted([e for e in plan_data["entries"] if e.get("cat") == post_cat], key=lambda x: (x['date'], x['time']))
            
            # Embed Paket bauen
            color_int = int(embed_color.lstrip('#'), 16)
            embed = {
                "title": f"📅 UPDATE: {post_cat}",
                "color": color_int,
                "author": {"name": f"{current_user} Command Center"},
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
                    role_id = hook_options[selected_hook].get("role_id")
                    ping_text = f"<@&{role_id}>\n" if role_id else ""
                    final_content = ping_text + custom_msg if custom_msg else ping_text
                    
                    success, response_msg = utils.send_discord_webhook(hook_options[selected_hook]["url"], text_content=final_content, embed_data=embed)
                    if success: 
                        st.success("✅ Plan wurde erfolgreich als Embed gepostet!")
                    else: 
                        st.error(f"Fehler: {response_msg}")
        
        # Lokale Vorschau
        with c_preview:
            st.markdown("#### 👀 Embed Vorschau")
            if not entries_to_post:
                st.info("Keine Termine für diesen Plan vorhanden.")
            else:
                is_dark = st.session_state.get("theme", "Midnight (Dark)") == "Midnight (Dark)"
                bg_col = "#36393F" if is_dark else "#F2F3F5"
                text_col = "#DCDDDE" if is_dark else "#2E3338"
                embed_bg = "#2F3136" if is_dark else "#FFFFFF"
                
                role_prev = hook_options[selected_hook].get("role_id")
                ping_str = f"<span style='color: #7289DA; background-color: rgba(114, 137, 218, 0.1); padding: 0 4px; border-radius: 3px;'>@Rolle ({role_prev})</span><br><br>" if role_prev else ""
                
                html_preview = f"""
                <div style="background-color: {bg_col}; padding: 15px; border-radius: 8px;">
                    <p style="color: {text_col}; margin-bottom: 5px; font-family: 'Space Grotesk', sans-serif;">{ping_str}{custom_msg}</p>
                    <div style="background-color: {embed_bg}; border-left: 4px solid {embed_color}; padding: 15px; border-radius: 4px; font-family: 'Space Grotesk', sans-serif;">
                        <p style="font-size: 12px; font-weight: bold; color: {text_col}; margin-bottom: 5px;">{current_user} Command Center</p>
                        <h4 style="color: #FFFFFF; margin: 0 0 15px 0;">{embed['title']}</h4>
                """
                for f in embed["fields"]:
                    html_preview += f"""
                        <div style="margin-bottom: 12px;">
                            <div style="color: #FFFFFF; font-weight: 700; font-size: 14px;">{f['name']}</div>
                            <div style="color: {text_col}; font-size: 13px; white-space: pre-wrap; margin-top: 4px;">{f['value']}</div>
                        </div>
                    """
                html_preview += "</div></div>"
                
                st.markdown(html_preview, unsafe_allow_html=True)