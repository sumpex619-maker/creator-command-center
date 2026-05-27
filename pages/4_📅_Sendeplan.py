import streamlit as st
import utils

current_user = utils.check_login()
st.title("🗓️ Sendeplan & Kalender")

# PRÜFUNG: Gibt es Webhooks?
conn = utils.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT profile_name, url FROM webhooks WHERE username = %s AND plattform LIKE '%%Sendeplan%%'", (current_user,))
sendeplan_hooks = cursor.fetchall()
cursor.close(); conn.close()

if not sendeplan_hooks:
    st.warning("🛑 Stopp! Du musst zuerst einen Webhook für die Kategorie 'Sendeplan' einrichten, bevor du diesen Kalender posten kannst.")
    st.info("Gehe dazu links im Menü auf '⚙️ Webhook Settings'.")
    st.stop()

st.markdown("Plane deine Woche und sende deinen Plan mit einem Klick in deinen Discord.")
st.markdown("---")

sendeplan = utils.load_data("sendeplan", dict)

col_plan, col_view = st.columns([1, 1.5])
with col_plan:
    st.markdown("### 🛠️ Eintrag erstellen")
    with st.form("sendeplan_form"):
        tag = st.selectbox("Wochentag", utils.WOCHENTAGE)
        typ = st.text_input("Kategorie / Art", placeholder="z.B. Rennkalender, Just Chatting, IRL...")
        uhrzeit = st.text_input("Uhrzeit", placeholder="z.B. 19:00 - 22:00 Uhr")
        inhalt = st.text_area("Was genau machst du?", placeholder="Inhalt des Streams...")
        
        if st.form_submit_button("💾 Speichern", type="primary", use_container_width=True):
            sendeplan[tag] = {"uhrzeit": uhrzeit, "inhalt": inhalt, "typ": typ}
            utils.save_data("sendeplan", sendeplan)
            st.success("Aktualisiert!")
            st.rerun()

with col_view:
    st.markdown("### 📅 Wochenübersicht")
    for tag in utils.WOCHENTAGE:
        slot = sendeplan.get(tag, None)
        with st.expander(f"🔹 {tag}", expanded=True):
            if slot:
                st.markdown(f"**[{slot.get('typ', 'Stream')}]** ⏰ {slot['uhrzeit']}")
                st.write(slot['inhalt'])
                
                # Einzelnen Tag posten
                if st.button(f"📢 Nur {tag} posten", key=f"post_{tag}"):
                    msg = f"📅 **Update für {tag}!**\n⏰ {slot['uhrzeit']} | 🎮 {slot.get('typ', 'Stream')}\n{slot['inhalt']}"
                    success, response = utils.send_discord_webhook(sendeplan_hooks[0]["url"], text_content=msg)
                    if success: st.success("Gepostet!")
            else:
                st.write("*Keine Termine eingetragen.*")
                
st.markdown("---")
if st.button("🚀 GESAMTEN WOCHENPLAN IN DISCORD POSTEN", type="primary", use_container_width=True):
    wochen_msg = "📅 **UNSER SENDEPLAN FÜR DIESE WOCHE** 📅\n\n"
    for tag in utils.WOCHENTAGE:
        slot = sendeplan.get(tag, None)
        if slot: wochen_msg += f"**{tag}** ({slot.get('typ', 'Stream')}):\n⏰ {slot['uhrzeit']} - {slot['inhalt']}\n\n"
        else: wochen_msg += f"**{tag}**: ❌ Frei / Spontan\n\n"
    
    success, response = utils.send_discord_webhook(sendeplan_hooks[0]["url"], text_content=wochen_msg)
    if success: st.success("✅ Der komplette Plan ist online!")