import streamlit as st
import utils
import datetime
import time
import uuid

# Login prüfen & Cinematic Design laden
current_user = utils.check_login()

st.title("🗓️ Dynamischer Sendeplan")
st.markdown("Verwalte verschiedene Pläne (z.B. Streams, Rennkalender), verknüpfe sie mit eigenen Webhooks und poste sie als professionelles Embed in Discord.")
st.markdown("---")

# ==============================================================================
# DATEN LADEN & MIGRATION
# ==============================================================================
plan_data = utils.load_data("sendeplan_v2", lambda: {"categories": {"Standard Stream": {"url": "", "role_id": ""}}, "entries": []})

# Migration: Falls alte Kategorien noch als einfache Liste gespeichert sind (aus vorheriger Version)
if isinstance(plan_data.get("categories"), list):
    new_cats = {}
    for cat in plan_data["categories"]:
        new_cats[cat] = {"url": "", "role_id": ""}
    plan_data["categories"] = new_cats
    utils.save_data("sendeplan_v2", plan_data)

categories_list = list(plan_data["categories"].keys())

# ==============================================================================
# TABS FÜR ÜBERSICHTLICHKEIT
# ==============================================================================
tab_eintragen, tab_posten, tab_kategorien = st.tabs(["📝 Termine verwalten", "🚀 Vorschau & Posten", "📁 Pläne & Webhooks Setup"])

# ------------------------------------------------------------------------------
# TAB 1: TERMINE EINTRAGEN & VERWALTEN (STRIKTE TRENNUNG)
# ------------------------------------------------------------------------------
with tab_eintragen:
    if not categories_list:
        st.warning("Bitte lege zuerst im Reiter 'Pläne & Webhooks Setup' einen Plan an.")
    else:
        # ZENTRALE STEUERUNG: Hier wählt man den Plan aus, und alles darunter passt sich an!
        gewaehlter_plan = st.selectbox("📂 Welchen Plan möchtest du bearbeiten und ansehen?", categories_list)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_form, col_list = st.columns([1, 1.2], gap="large")
        
        with col_form:
            st.subheader(f"Neuen Termin anlegen")
            with st.container(border=True):
                with st.form("new_event_form", clear_on_submit=True):
                    # Info-Text, damit man immer weiß, wo man gerade speichert
                    st.info(f"💾 Speichert in: **{gewaehlter_plan}**")
                    titel = st.text_input("Titel des Events", placeholder="z.B. GT3 Ligarennen Spa oder Just Chatting")
                    
                    c_date, c_time = st.columns(2)
                    with c_date: datum = st.date_input("Datum", datetime.date.today())
                    with c_time: uhrzeit = st.time_input("Uhrzeit", datetime.time(19, 0))
                    
                    beschreibung = st.text_area("Kurze Beschreibung", placeholder="Was genau passiert dort? (Wird im Discord angezeigt)")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("💾 Termin speichern", type="primary", use_container_width=True):
                        if titel:
                            new_entry = {
                                "id": str(uuid.uuid4())[:8],
                                "cat": gewaehlter_plan, # Speichert fest im oben gewählten Plan
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
            st.subheader(f"Geplante Termine")
            
            # Filtere die Liste STRIKT nach dem oben ausgewählten Plan
            gefilterte_entries = [e for e in plan_data["entries"] if e["cat"] == gewaehlter_plan]
            
            if not gefilterte_entries:
                st.info(f"Aktuell keine Termine für '{gewaehlter_plan}' eingetragen.")
            else:
                # Sortiere Einträge nach Datum und Uhrzeit
                sorted_entries = sorted(gefilterte_entries, key=lambda x: (x['date'], x['time']))
                
                for entry in sorted_entries:
                    # Datum schön formatieren (DD.MM.YYYY)
                    date_obj = datetime.datetime.strptime(entry['date'], "%Y-%m-%d")
                    ger_date = date_obj.strftime("%d.%m.%Y")
                    
                    with st.expander(f"🗓️ {ger_date} | {entry['time']} Uhr - {entry['title']}"):
                        st.write(entry['desc'] if entry['desc'] else "*Keine Beschreibung hinterlegt.*")
                        
                        if st.button("🗑️ Termin löschen", key=f"del_{entry['id']}", use_container_width=True):
                            plan_data["entries"] = [e for e in plan_data["entries"] if e["id"] != entry["id"]]
                            utils.save_data("sendeplan_v2", plan_data)
                            st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: DISCORD EMBED & POSTEN
# ------------------------------------------------------------------------------
with tab_posten:
    st.subheader("Discord Uplink")
    
    if not categories_list:
        st.warning("⚠️ Es existieren noch keine Pläne.")
    elif not plan_data["entries"]:
        st.info("Trage zuerst Termine ein, bevor du einen Plan posten kannst.")
    else:
        c_setup, c_preview = st.columns([1, 1.5], gap="large")
        
        with c_setup:
            st.markdown("### 1. Plan zum Senden auswählen")
            post_cat = st.selectbox("Welchen Plan möchtest du posten?", categories_list, key="post_cat")
            cat_config = plan_data["categories"][post_cat]
            
            custom_msg = st.text_area("Zusätzliche Nachricht (Optional)", placeholder="Hey Leute, hier ist der Plan für diese Woche!")
            
            # --- DATEN FÜR EMBED ZUSAMMENSTELLEN ---
            entries_to_post = [e for e in sorted_entries if e["cat"] == post_cat] if 'sorted_entries' in locals() else [e for e in plan_data["entries"] if e["cat"] == post_cat]
            # Für Tab 2 nochmal separat sortieren, um sicherzugehen
            entries_to_post = sorted(entries_to_post, key=lambda x: (x['date'], x['time']))
            
            # Embed Struktur für Discord
            embed = {
                "title": f"📅 UPDATE: {post_cat}",
                "color": 5569535, # Cinematic Cyan (#54FBFF)
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
            
            # Warnung, falls kein Webhook für diese Kategorie existiert
            if not cat_config.get("url"):
                st.error(f"⚠️ Dem Plan '{post_cat}' ist keine Webhook-URL zugewiesen. Bitte richte diese im Reiter 'Pläne & Webhooks Setup' ein.")
            else:
                if st.button("🚀 Plan jetzt an Discord senden", type="primary", use_container_width=True):
                    if not entries_to_post:
                        st.error("Dieser Plan hat aktuell keine Termine!")
                    else:
                        # Ping bauen, wenn Rolle existiert
                        role_id = cat_config.get("role_id")
                        ping_text = f"<@&{role_id}>\n" if role_id else ""
                        
                        # Nachrichtentext = Ping + Optionale Custom Message
                        final_content = ping_text + custom_msg
                        if not final_content.strip(): 
                            final_content = None # Wenn leer, nur das Embed schicken
                            
                        success, response_msg = utils.send_discord_webhook(cat_config["url"], text_content=final_content, embed_data=embed)
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
                bg_col = "#0A0A10" if is_dark else "#F2F3F5"
                text_col = "#E0E0E0" if is_dark else "#2E3338"
                embed_bg = "#111827" if is_dark else "#FFFFFF"
                
                role_prev = cat_config.get("role_id")
                ping_str = f"<span style='color: #00E5FF; background-color: rgba(0, 229, 255, 0.1); padding: 2px 6px; border-radius: 4px; font-size: 13px;'>@Rolle ({role_prev})</span><br><br>" if role_prev else ""
                
                # HTML Konstrukt für die Embed-Vorschau
                html_preview = f"""
                <div style="background-color: {bg_col}; padding: 15px; border-radius: 4px; border: 1px solid #1c1c28; font-family: 'Space Grotesk', sans-serif;">
                    <p style="color: #FFFFFF; margin-bottom: 5px; font-weight: bold;">{current_user} <span style="background-color: #00E5FF; color: #000; padding: 2px 5px; border-radius: 3px; font-size: 10px;">BOT</span></p>
                    <p style="color: {text_col}; white-space: pre-wrap; font-size: 14px;">{ping_str}{custom_msg}</p>
                    
                    <div style="background-color: {embed_bg}; border-left: 4px solid #00E5FF; padding: 15px; border-radius: 4px; margin-top: 10px;">
                        <h4 style="color: {'#FFFFFF' if is_dark else '#000000'}; margin: 0 0 15px 0;">{embed['title']}</h4>
                """
                for f in embed["fields"]:
                    html_preview += f"""
                        <div style="margin-bottom: 12px;">
                            <div style="color: {'#FFFFFF' if is_dark else '#000000'}; font-weight: 700; font-size: 14px;">{f['name']}</div>
                            <div style="color: {text_col}; font-size: 13px; white-space: pre-wrap; margin-top: 4px;">{f['value']}</div>
                        </div>
                    """
                html_preview += "</div></div>"
                
                st.markdown(html_preview, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 3: PLÄNE & WEBHOOKS SETUP
# ------------------------------------------------------------------------------
with tab_kategorien:
    st.subheader("📁 Pläne & Webhooks konfigurieren")
    st.write("Lege hier fest, welche Pläne es geben soll und an welchen Discord-Webhook sie verknüpft sind.")
    
    with st.container(border=True):
        st.markdown("#### Neuen Plan erstellen")
        with st.form("new_cat_form", clear_on_submit=True):
            new_cat = st.text_input("Name des Plans (z.B. Rennkalender, Just Chatting)")
            new_url = st.text_input("Discord Webhook URL", placeholder="https://discord.com/api/webhooks/...")
            new_role = st.text_input("Discord Rollen-ID (Optional)", placeholder="z.B. 1234567890")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("➕ Plan hinzufügen", type="primary", use_container_width=True):
                if new_cat and new_url:
                    if new_cat not in plan_data["categories"]:
                        plan_data["categories"][new_cat] = {"url": new_url, "role_id": new_role}
                        utils.save_data("sendeplan_v2", plan_data)
                        st.success(f"Plan '{new_cat}' erfolgreich angelegt!")
                        st.rerun()
                    else:
                        st.error("Ein Plan mit diesem Namen existiert bereits.")
                else:
                    st.error("Bitte einen Namen und eine Webhook-URL eintragen.")
                    
    st.markdown("---")
    st.markdown("#### Aktuelle Pläne verwalten")
    
    if not categories_list:
        st.info("Noch keine Pläne angelegt.")
    else:
        for cat_name, cat_info in plan_data["categories"].items():
            with st.expander(f"⚙️ {cat_name}"):
                edit_key = f"edit_cat_{cat_name}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False
                    
                if not st.session_state[edit_key]:
                    st.markdown(f"**Webhook-URL:** `{cat_info['url']}`")
                    st.markdown(f"**Rollen-ID:** `{cat_info['role_id'] if cat_info['role_id'] else 'Kein Ping'}`")
                    
                    cc1, cc2 = st.columns(2)
                    if cc1.button("✏️ Bearbeiten", key=f"btn_edit_{cat_name}", use_container_width=True):
                        st.session_state[edit_key] = True
                        st.rerun()
                    if cc2.button("🗑️ Löschen", key=f"btn_del_{cat_name}", use_container_width=True):
                        del plan_data["categories"][cat_name]
                        plan_data["entries"] = [e for e in plan_data["entries"] if e["cat"] != cat_name]
                        utils.save_data("sendeplan_v2", plan_data)
                        st.rerun()
                else:
                    with st.form(f"form_edit_{cat_name}"):
                        edit_url = st.text_input("Webhook URL", value=cat_info['url'])
                        edit_role = st.text_input("Rollen-ID", value=cat_info['role_id'])
                        
                        c_sub1, c_sub2 = st.columns(2)
                        if c_sub1.form_submit_button("💾 Speichern", type="primary", use_container_width=True):
                            plan_data["categories"][cat_name] = {"url": edit_url, "role_id": edit_role}
                            utils.save_data("sendeplan_v2", plan_data)
                            st.session_state[edit_key] = False
                            st.rerun()
                        if c_sub2.form_submit_button("❌ Abbrechen", use_container_width=True):
                            st.session_state[edit_key] = False
                            st.rerun()