import streamlit as st
from datetime import datetime
import utils

st.set_page_config(page_title="Ideen & To-Dos - Command Center", layout="wide")
username = utils.check_login()

st.title("📝 Ideen & To-Dos")

# Datenpfade
ideas_file = utils.get_user_filepath(username, "ideas")
todos_file = utils.get_user_filepath(username, "todos")

# Daten laden
ideas_daten = utils.load_data(ideas_file, list)
todos_daten = utils.load_data(todos_file, list)

col_ideas, col_todos = st.columns([1, 1])

with col_ideas:
    st.subheader("💡 Content Ideen-Pool")
    with st.expander("➕ Neue Idee festhalten", expanded=False):
        idea_title = st.text_input("Idee / Arbeitstitel")
        idea_platform = st.selectbox("Ziel-Plattform", ["Twitch", "YouTube", "TikTok", "Instagram", "Kick", "Sonstiges"])
        idea_notes = st.text_area("Notizen / Konzept-Skizze")
        if st.button("Idee speichern", type="primary"):
            if idea_title:
                ideas_daten.append({
                    "id": str(datetime.now().timestamp()), 
                    "titel": idea_title, 
                    "plattform": idea_platform, 
                    "notizen": idea_notes, 
                    "status": "Geplant"
                })
                utils.save_data(ideas_file, ideas_daten)
                st.rerun()
                
    if ideas_daten:
        for idx, idea in enumerate(ideas_daten):
            with st.expander(f"📌 [{idea['plattform']}] {idea['titel']} ({idea['status']})"):
                st.write(idea['notizen'] if idea['notizen'] else '*Keine Notizen*')
                c1, c2 = st.columns([3, 1])
                neuer_status = c1.selectbox("Status", ["Geplant", "In Arbeit", "Fertig"], index=["Geplant", "In Arbeit", "Fertig"].index(idea["status"]), key=f"st_{idea['id']}")
                if neuer_status != idea["status"]:
                    ideas_daten[idx]["status"] = neuer_status
                    utils.save_data(ideas_file, ideas_daten)
                    st.rerun()
                if c2.button("🗑️", key=f"del_i_{idea['id']}"):
                    ideas_daten = [i for i in ideas_daten if i["id"] != idea["id"]]
                    utils.save_data(ideas_file, ideas_daten)
                    st.rerun()

with col_todos:
    st.subheader("✅ Creator To-Do Liste")
    col_td_input, col_td_btn = st.columns([3, 1])
    neues_todo_text = col_td_input.text_input("Neue Aufgabe...", label_visibility="collapsed")
    
    if col_td_btn.button("Hinzufügen", use_container_width=True) and neues_todo_text:
        todos_daten.append({"id": str(datetime.now().timestamp()), "text": neues_todo_text, "done": False})
        utils.save_data(todos_file, todos_daten)
        st.rerun()
        
    st.write("---")
    offene_todos = [t for t in todos_daten if not t["done"]]
    erledigte_todos = [t for t in todos_daten if t["done"]]
    
    for t in offene_todos:
        ct1, ct2 = st.columns([10, 1])
        if ct1.checkbox(t["text"], value=False, key=f"todo_{t['id']}"):
            for item in todos_daten: 
                if item["id"] == t["id"]: item["done"] = True
            utils.save_data(todos_file, todos_daten)
            st.rerun()
        if ct2.button("🗑️", key=f"del_td_{t['id']}"):
            todos_daten = [item for item in todos_daten if item["id"] != t["id"]]
            utils.save_data(todos_file, todos_daten)
            st.rerun()
    
    if erledigte_todos:
        st.markdown("---")
        for t in erledigte_todos:
            ct1, ct2 = st.columns([10, 1])
            if ct1.checkbox(f"~~{t['text']}~~", value=True, key=f"todo_{t['id']}"):
                for item in todos_daten: 
                    if item["id"] == t["id"]: item["done"] = False
                utils.save_data(todos_file, todos_daten)
                st.rerun()
            if ct2.button("🗑️", key=f"del_td_{t['id']}"):
                todos_daten = [item for item in todos_daten if item["id"] != t["id"]]
                utils.save_data(todos_file, todos_daten)
                st.rerun()
        
        if st.button("🧹 Erledigte aufräumen"):
            todos_daten = [t for t in todos_daten if not t["done"]]
            utils.save_data(todos_file, todos_daten)
            st.rerun()