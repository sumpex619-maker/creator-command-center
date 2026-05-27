import streamlit as st
import utils

# Sicherheits-Check: Nur eingeloggte Nutzer dürfen die Seite sehen
username = utils.check_login()

st.title("⚙️ Webhook Einstellungen")
st.markdown("Verwalte deine Discord-Webhooks für automatische Streaming-Alerts, Benachrichtigungen und Post-Schedules.")
st.markdown("---")

# ==============================================================================
# DATENBANK-FUNKTIONEN (CRUD)
# ==============================================================================
def get_webhooks(user):
    """Holt alle registrierten Webhooks des Nutzers aus der Datenbank."""
    conn = utils.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, profile_name, url, plattform, role_id FROM webhooks WHERE username = %s ORDER BY profile_name", (user,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def delete_webhook(webhook_id, user):
    """Löscht einen Webhook dauerhaft aus der Datenbank."""
    conn = utils.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM webhooks WHERE id = %s AND username = %s", (webhook_id, user))
    cursor.close()
    conn.close()
    st.success("🗑️ Webhook erfolgreich gelöscht!")
    st.rerun()

def update_webhook(webhook_id, user, profile_name, url, plattform, role_id):
    """Aktualisiert die Daten eines bestehenden Webhooks."""
    conn = utils.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE webhooks 
            SET profile_name = %s, url = %s, plattform = %s, role_id = %s 
            WHERE id = %s AND username = %s
        """, (profile_name, url, plattform, role_id, webhook_id, user))
        st.success("💾 Änderungen erfolgreich gespeichert!")
        st.rerun()
    except Exception as e:
        st.error(f"⚠️ Fehler beim Speichern: Ein Profil mit diesem Namen existiert eventuell schon.")
    finally:
        cursor.close()
        conn.close()

def add_webhook(user, profile_name, url, plattform, role_id):
    """Fügt einen neuen Webhook hinzu."""
    conn = utils.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO webhooks (username, profile_name, url, plattform, role_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (user, profile_name, url, plattform, role_id))
        st.success("🎉 Webhook erfolgreich hinzugefügt!")
        st.rerun()
    except Exception as e:
        st.error(f"⚠️ Fehler: Name wird bereits verwendet.")
    finally:
        cursor.close()
        conn.close()

# ==============================================================================
# BENUTZEROBERFLÄCHE (SIDE-BY-SIDE MODULAR DESIGN)
# ==============================================================================
col_links, col_rechts = st.columns([3, 2], gap="large")

# Alle Webhooks aus der Datenbank laden
aktuelle_webhooks = get_webhooks(username)

# --- LINKE SPALTE: Webhooks anzeigen, bearbeiten & löschen ---
with col_links:
    st.subheader("📋 Deine aktiven Verbindungen")
    
    if not aktuelle_webhooks:
        st.info("Du hast aktuell noch keine Webhooks eingerichtet. Nutze das Formular rechts, um deinen ersten Alert-Kanal zu verknüpfen!")
    
    for wh in aktuelle_webhooks:
        wh_id, wh_profile, wh_url, wh_plat, wh_role = wh
        
        # Jedes Webhook-Profil bekommt eine eigene, saubere Box
        with st.container(border=True):
            st.markdown(f"### 🔗 {wh_profile}")
            
            # Detailansicht in zwei Spalten aufgeteilt
            c_det1, c_det2 = st.columns(2)
            with c_det1:
                st.markdown(f"**Plattform:** `{wh_plat}`")
                st.markdown(f"**Rollen-ID:** `{wh_role if wh_role else 'Keine hinterlegt (Ping aus)'}`")
            with c_det2:
                # Lange Webhook-URLs kürzen, damit das Layout sauber bleibt
                gekürzte_url = wh_url[:35] + "..." if len(wh_url) > 35 else wh_url
                st.markdown(f"**Webhook URL:** `{gekürzte_url}`")
            
            # Aktionsbuttons
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            c_btn1, c_btn2, _ = st.columns([1, 1, 2])
            
            # Einzigartigen Zustand für das Bearbeitungs-Fenster erzeugen
            edit_state_key = f"edit_active_{wh_id}"
            if edit_state_key not in st.session_state:
                st.session_state[edit_state_key] = False
            
            with c_btn1:
                if st.button("✏️ Bearbeiten", key=f"btn_edit_{wh_id}", use_container_width=True):
                    st.session_state[edit_state_key] = not st.session_state[edit_state_key]
                    st.rerun()
                    
            with c_btn2:
                if st.button("🗑️ Löschen", key=f"btn_del_{wh_id}", type="secondary", use_container_width=True):
                    delete_webhook(wh_id, username)
            
            # --- Dynamisches Bearbeitungs-Formular (klappt auf Knopfdruck auf) ---
            if st.session_state[edit_state_key]:
                st.markdown("---")
                st.markdown("🔄 **Webhook-Details anpassen:**")
                with st.form(f"form_edit_{wh_id}"):
                    edit_profile = st.text_input("Profil-Name", value=wh_profile)
                    
                    plattform_liste = ["Twitch", "YouTube", "Kick", "TikTok", "Instagram", "Sendeplan / Kalender", "Allgemein"]
                    standard_index = plattform_liste.index(wh_plat) if wh_plat in plattform_liste else 0
                    edit_plat = st.selectbox("Zugehörige Plattform", plattform_liste, index=standard_index)
                    
                    edit_url = st.text_input("Discord Webhook URL", value=wh_url)
                    edit_role = st.text_input("Discord Rollen-ID (optional)", value=wh_role if wh_role else "", help="Die ID der Discord-Rolle, die bei Benachrichtigungen gepingt werden soll.")
                    
                    c_sub1, c_sub2 = st.columns(2)
                    with c_sub1:
                        if st.form_submit_button("💾 Speichern", use_container_width=True):
                            if edit_profile and edit_url:
                                update_webhook(wh_id, username, edit_profile, edit_url, edit_plat, edit_role)
                                st.session_state[edit_state_key] = False
                            else:
                                st.error("⚠️ Name und URL dürfen nicht leer sein!")
                    with c_sub2:
                        if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                            st.session_state[edit_state_key] = False
                            st.rerun()

# --- RECHTE SPALTE: Neuen Webhook hinzufügen ---
with col_rechts:
    st.subheader("➕ Neuen Webhook hinzufügen")
    with st.form("add_webhook_form", clear_on_submit=True):
        new_profile = st.text_input("Profil-Name", placeholder="z.B. Twitch-Live-Alerts", help="Ein eindeutiger Name für dich.")
        new_plat = st.selectbox("Plattform", ["Twitch", "YouTube", "Kick", "TikTok", "Instagram", "Sendeplan / Kalender", "Allgemein"])
        new_url = st.text_input("Discord Webhook URL", placeholder="https://discord.com/api/webhooks/...")
        new_role = st.text_input("Discord Rollen-ID (optional)", placeholder="Leer lassen für keinen Ping", help="Kopiere die ID deiner Discord-Rolle hier rein, um z.B. deine Community direkt zu pingen.")
        
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.form_submit_button("🚀 Verbindung herstellen", type="primary", use_container_width=True):
            if new_profile and new_url:
                add_webhook(username, new_profile, new_url, new_plat, new_role)
            else:
                st.error("⚠️ Bitte fülle mindestens den Profil-Namen und die Webhook-URL aus!")