import streamlit as st
import json
import os
import hashlib
from datetime import datetime, time, timedelta
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Creator Command Center", layout="wide")

# ==============================================================================
# GLOBALE KONFIGURATION (Für alle Nutzer geteilt)
# ==============================================================================
USERS_FILE = "users.json"
SETTINGS_FILE = "settings.json" 

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

COLORS = {
    "Twitch": 9520895,   
    "YouTube": 16711680, 
    "Kick": 5504024,     
    "TikTok": 65793,     
    "Instagram": 14619428, 
    "Sendeplan / Kalender": 16766720,
    "Allgemein": 5793266 
}

PLOT_COLORS = {
    "Twitch": "#9146FF",
    "YouTube": "#FF0000",
    "Kick": "#53FC18",
    "TikTok": "#010101",
    "Instagram": "#E1306C",
    "Sendeplan / Kalender": "#FFD700",
    "Sonstiges": "#5865F2"
}

THEME_COLORS = {
    "Pastell Ozean (Blau)": "#4A90E2",
    "Salbeigrün": "#779C7B",
    "Flieder (Lila)": "#9B82C2",
    "Pfirsichrosa": "#D98880",
    "Sandbeige": "#C2B280",
    "Staubiges Rosa": "#C08497",
    "Sanftes Mint": "#6BBF9F",
    "Karibik Türkis": "#46A5B8",
    "Nachtblau": "#34495E",
    "Warmes Senfgelb": "#D4AC0D"
}

# ==============================================================================
# HILFSFUNKTIONEN
# ==============================================================================
def load_data(file, default_factory):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except json.JSONDecodeError: return default_factory()
    return default_factory()

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def send_discord_webhook(url, text_content=None, embed_data=None):
    payload = {}
    if text_content: payload["content"] = text_content
    if embed_data: payload["embeds"] = [embed_data]
    try:
        response = requests.post(url, json=payload)
        if response.status_code in [200, 204]: 
            return True, "🚀 Erfolgreich an Discord gesendet!"
        return False, f"Discord-Fehler: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Verbindungsfehler: {str(e)}"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==============================================================================
# LOGIN & REGISTRIERUNG LOGIK
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

if not st.session_state["logged_in"]:
    st.title("🔒 Creator Command Center")
    st.write("Bitte melde dich an oder erstelle einen neuen Account.")
    
    users_db = load_data(USERS_FILE, dict)
    
    col_login, _ = st.columns([1, 2])
    with col_login:
        tab_login, tab_register = st.tabs(["🔑 Anmelden", "📝 Registrieren"])
        
        with tab_login:
            user_login = st.text_input("Benutzername", key="login_user")
            pwd_login = st.text_input("Passwort", type="password", key="login_pwd")
            if st.button("Einloggen", type="primary", use_container_width=True):
                if user_login in users_db and users_db[user_login] == hash_password(pwd_login):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user_login
                    st.rerun()
                else:
                    st.error("❌ Falscher Benutzername oder Passwort!")
                    
        with tab_register:
            user_reg = st.text_input("Neuer Benutzername", key="reg_user")
            pwd_reg = st.text_input("Neues Passwort", type="password", key="reg_pwd")
            pwd_reg2 = st.text_input("Passwort bestätigen", type="password", key="reg_pwd2")
            if st.button("Konto erstellen", use_container_width=True):
                if not user_reg or not pwd_reg:
                    st.error("⚠️ Bitte alle Felder ausfüllen!")
                elif user_reg in users_db:
                    st.error("⚠️ Dieser Benutzername ist bereits vergeben!")
                elif pwd_reg != pwd_reg2:
                    st.error("⚠️ Die Passwörter stimmen nicht überein!")
                elif len(pwd_reg) < 4:
                    st.error("⚠️ Das Passwort muss mindestens 4 Zeichen lang sein!")
                else:
                    users_db[user_reg] = hash_password(pwd_reg)
                    save_data(USERS_FILE, users_db)
                    st.success("✅ Konto erfolgreich erstellt! Du kannst dich jetzt einloggen.")
    st.stop()

# ==============================================================================
# PRIVATE DATEIPFADE PRO NUTZER (DATEN-TRENNUNG)
# ==============================================================================
current_user = st.session_state["username"]
user_prefix = current_user.replace(" ", "_").lower()

DB_FILE = f"data_{user_prefix}_stats.json"
WEBHOOKS_FILE = f"data_{user_prefix}_webhooks.json"
SCHEDULE_FILE = f"data_{user_prefix}_schedule.json"
SOCIAL_POSTS_FILE = f"data_{user_prefix}_social_posts_queue.json"
IDEAS_FILE = f"data_{user_prefix}_ideas.json"
TODOS_FILE = f"data_{user_prefix}_todos.json"

# ==============================================================================
# DESIGN & THEME VERWALTUNG (SEITENLEISTE)
# ==============================================================================
settings_db = load_data(SETTINGS_FILE, dict)

if current_user not in settings_db:
    settings_db[current_user] = {"theme": "Dark", "accent": "Pastell Ozean (Blau)"}

with st.sidebar:
    st.header("🎨 Design anpassen")
    current_theme = settings_db[current_user]["theme"]
    current_accent = settings_db[current_user]["accent"]
    
    selected_theme = st.radio("Modus:", ["Dark", "Light"], index=0 if current_theme == "Dark" else 1)
    accent_options = list(THEME_COLORS.keys())
    selected_accent = st.selectbox("Akzentfarbe:", accent_options, index=accent_options.index(current_accent) if current_accent in accent_options else 0)
    
    if st.button("💾 Speichern & Anwenden", use_container_width=True):
        settings_db[current_user]["theme"] = selected_theme
        settings_db[current_user]["accent"] = selected_accent
        save_data(SETTINGS_FILE, settings_db)
        st.rerun()

# --- CSS INJECTION FÜR MODUS & FARBEN ---
active_theme = settings_db[current_user]["theme"]
active_color_hex = THEME_COLORS.get(settings_db[current_user]["accent"], "#4A90E2")

if active_theme == "Dark":
    bg_color, sec_bg, text_color = "#0E1117", "#262730", "#FAFAFA"
else:
    bg_color, sec_bg, text_color = "#FFFFFF", "#F0F2F6", "#111111"

st.markdown(f"""
<style>
    :root {{
        --primary-color: {active_color_hex} !important;
        --background-color: {bg_color} !important;
        --secondary-background-color: {sec_bg} !important;
        --text-color: {text_color} !important;
    }}
    .stApp, .main {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {sec_bg} !important;
    }}
    p, span, h1, h2, h3, h4, h5, h6, label, li, div[data-testid="stMarkdownContainer"] {{
        color: {text_color} !important;
    }}
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    div[data-baseweb="tab-highlight"] {{
        background-color: {active_color_hex} !important;
    }}
    button[data-baseweb="tab"] p {{
        color: {text_color} !important;
        font-weight: 600 !important;
    }}
    .stButton>button[kind="primary"] {{
        background-color: {active_color_hex} !important;
        border: 1px solid {active_color_hex} !important;
    }}
    .stButton>button[kind="primary"] p, .stButton>button[kind="primary"] div {{
        color: #FFFFFF !important; 
    }}
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {{
        background-color: {bg_color} !important;
        border-color: {active_color_hex} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HAUPTANWENDUNG
# ==============================================================================
col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title("🎬 Creator Command Center")
with col_logout:
    st.write("") 
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

st.markdown(f"**Eingeloggt als:** `{current_user}`")

tab_anleitung, tab_stats, tab_ideas, tab_discord, tab_schedule, tab_freepost, tab_tools = st.tabs([
    "📖 Anleitung",
    "📊 Social Media Stats", 
    "📝 Ideen & To-Dos",
    "💬 Webhook Verwaltung", 
    "📅 Streaming-Planer",
    "📢 Freies Posten",
    "🛠️ Technik & Tools"
])

# Lade nutzerspezifische Daten
stats_daten = load_data(DB_FILE, list)
webhook_profile = load_data(WEBHOOKS_FILE, dict)
schedule_daten = load_data(SCHEDULE_FILE, list)
social_queue = load_data(SOCIAL_POSTS_FILE, list)
ideas_daten = load_data(IDEAS_FILE, list)
todos_daten = load_data(TODOS_FILE, list)

# ==============================================================================
# TAB 0: ANLEITUNG
# ==============================================================================
with tab_anleitung:
    st.header(f"Willkommen in deiner Kommandozentrale, {current_user}!")
    st.write("Dieses Tool hilft dir, deinen Content effizienter zu planen, deine Erfolge datenbasiert auszuwerten und deine Community vollautomatisch zu informieren.")
    
    st.info("💡 **Tipp für den Start:** Nutze die Seitenleiste links (Pfeil oben links, falls versteckt), um das Design anzupassen (Dark/Light Mode & Akzentfarbe).")

    st.markdown("""
    ### 🗂️ Wie funktioniert das Tool? Hier ist die Übersicht aller Reiter:
    
    * **💬 Webhook Verwaltung:** **WICHTIG! Starte hier.** Hier verknüpfst du das Tool sicher mit deinem Discord-Server. Du hinterlegst hier die geheimen Links (Webhooks) zu deinen Kanälen. (*Wie das geht, wird direkt dort im Tab detailliert erklärt!*)
    * **📊 Social Media Stats:** Trage nach einem Post deine Aufrufe und Likes ein. In der 'Visuellen Auswertung' trackst du dein Wachstum in Graphen. Unter 'Content bewerben' kannst du außerdem neue Uploads an Discord schicken.
    * **📝 Ideen & To-Dos:** Deine Zettelwirtschaft hat ein Ende. Sammle Geistesblitze für neue Videos im Ideen-Pool und hake Aufgaben (z.B. "Thumbnail bauen") vor dem Upload ab.
    * **📅 Streaming-Planer:** Trage deine Stream-Zeiten für die Woche ein und poste den fertigen Kalender mit einem Klick in der passenden Farbe auf Discord.
    * **📢 Freies Posten:** Nutze dieses Tab, um unabhängig von Streams oder Videos spontane Eilmeldungen, Memes oder Gaming-News im schicken "Embed"-Design an deinen Server zu senden.
    * **🛠️ Technik & Tools:** Eine kleine Schatzkiste! Wenn du OBS-Alerts einrichten willst, Empfehlungen für Chat-Bots suchst oder schnell einen neuen Chat-Befehl (wie `!hug` oder `!lurk`) erstellen lassen willst, bist du hier richtig.
    
    ---
    *Sicherheitshinweis: Alle deine Daten, Passwörter und Webhooks werden lokal auf dem Server in kleinen Dateien gespeichert. Alles bleibt in deiner Hand.*
    """)

# ==============================================================================
# TAB 1: SOCIAL MEDIA STATS & POST GENERATOR
# ==============================================================================
with tab_stats:
    subtab_stats_tracker, subtab_charts, subtab_posts_discord = st.tabs(["📝 Eingabe & Historie", "📈 Visuelle Auswertung", "📢 Content-Release bewerben"])
    
    with subtab_stats_tracker:
        st.subheader("Social Media Stats erfassen")
        stats_plattform = st.selectbox("Plattform wählen", ["Twitch", "YouTube", "Instagram", "TikTok", "Kick"])
        post_title = st.text_input("Titel / Thema des Contents", placeholder="z.B. Clip vom Let's Play Part 3")
        
        formate_dict = {
            "Twitch": ["Main-Stream", "Sonder-Stream"],
            "YouTube": ["Langvideo", "Short", "Community-Post"],
            "Instagram": ["Reel", "Feed-Post", "Story"],
            "TikTok": ["Video", "Live-Stream"],
            "Kick": ["Main-Stream"]
        }
        platform_format = st.selectbox("Format", formate_dict.get(stats_plattform, ["Sonstiges"]))

        col1, col2 = st.columns(2)
        with col1:
            views = st.number_input("Views / Aufrufe", min_value=0, value=0, step=1)
            likes = st.number_input("Likes", min_value=0, value=0, step=1)
        with col2:
            comments = st.number_input("Kommentare", min_value=0, value=0, step=1)
            saves = st.number_input("Saves / Shares", min_value=0, value=0, step=1)

        if views > 0: engagement_rate = ((likes + comments + saves) / views) * 100
        else: engagement_rate = 0.0

        st.metric(label=f"Berechnete Engagement-Rate ({stats_plattform})", value=f"{engagement_rate:.2f} %")

        if st.button("Daten speichern", type="primary", key="save_stats_data_btn"):
            if post_title == "": st.error("Bitte gib einen Titel ein!")
            else:
                stats_daten.append({
                    "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "plattform": stats_plattform,
                    "format": platform_format,
                    "titel": post_title,
                    "views": views,
                    "likes": likes,
                    "kommentare": comments,
                    "saves": saves,
                    "engagement_rate_pct": round(engagement_rate, 2)
                })
                save_data(DB_FILE, stats_daten)
                st.success("✓ Daten erfolgreich gespeichert!")
                st.rerun()

        st.write("---")
        st.write("### 🗄️ Daten-Historie")
        if stats_daten: st.dataframe(stats_daten, use_container_width=True)

    with subtab_charts:
        st.subheader("📈 Performance Übersicht")
        if not stats_daten:
            st.info("Noch keine Daten für Diagramme vorhanden. Trage zuerst Statistiken ein!")
        else:
            df = pd.DataFrame(stats_daten)
            df["datum"] = pd.to_datetime(df["datum"])
            
            col_filter, _ = st.columns([1, 2])
            with col_filter:
                zeitraum = st.selectbox("📅 Zeitraum filtern (Growth Tracker):", ["Alle Daten", "Letzte 7 Tage", "Letzte 30 Tage", "Letzte 90 Tage"], index=0)
            
            jetzt = datetime.now()
            if zeitraum == "Letzte 7 Tage": df = df[df["datum"] >= (jetzt - timedelta(days=7))]
            elif zeitraum == "Letzte 30 Tage": df = df[df["datum"] >= (jetzt - timedelta(days=30))]
            elif zeitraum == "Letzte 90 Tage": df = df[df["datum"] >= (jetzt - timedelta(days=90))]

            if df.empty:
                st.warning(f"⚠️ Keine Beiträge im Zeitraum '{zeitraum}' gefunden.")
            else:
                st.info(f"Zeige Auswertung für: **{zeitraum}** ({len(df)} Beiträge erfasst)")
                
                st.markdown("### 👁️ Gesamte Aufrufe nach Plattform")
                views_df = df.groupby("plattform")["views"].sum().reset_index()
                fig_views = px.bar(views_df, x="plattform", y="views", color="plattform", color_discrete_map=PLOT_COLORS, text_auto=True)
                fig_views.update_layout(xaxis_title="Plattform", yaxis_title="Gesamte Views", showlegend=False)
                st.plotly_chart(fig_views, use_container_width=True)
                
                st.write("---")

                st.markdown("### 🔥 Engagement-Rate im Verlauf")
                df_sorted = df.sort_values(by="datum")
                fig_eng = px.line(df_sorted, x="datum", y="engagement_rate_pct", color="plattform", color_discrete_map=PLOT_COLORS, markers=True, hover_name="titel")
                fig_eng.update_layout(xaxis_title="Datum / Uhrzeit", yaxis_title="Engagement-Rate (%)")
                st.plotly_chart(fig_eng, use_container_width=True)

    with subtab_posts_discord:
        st.subheader("📢 Content-Release bewerben")
        col_queue_form, col_queue_view = st.columns([1, 1])
        
        with col_queue_form:
            p_plattform = st.selectbox("Plattform", ["Twitch", "YouTube", "Instagram", "TikTok", "Kick"], key="q_plat")
            p_titel = st.text_input("Titel des Videos / Beitrags", placeholder="z.B. 100 Tage in Minecraft!", key="q_tit")
            p_format = st.text_input("Format (z.B. Reel, Short, XXL-Video)", key="q_form")
            p_link = st.text_input("Link zum Beitrag (Optional)", placeholder="https://...", key="q_link")
            p_text = st.text_area("Beitragstext / Caption (Optional)", placeholder="Schreibe hier einen coolen Text für deine Community...", key="q_text")
            
            if st.button("➕ Beitrag in Warteschlange legen", type="secondary"):
                if not p_titel: st.error("Bitte gib einen Titel an!")
                else:
                    social_queue.append({
                        "id": str(datetime.now().timestamp()), 
                        "plattform": p_plattform, 
                        "titel": p_titel, 
                        "format": p_format if p_format else "Beitrag", 
                        "link": p_link, 
                        "text": p_text
                    })
                    save_data(SOCIAL_POSTS_FILE, social_queue)
                    st.success("✓ Zur Liste hinzugefügt!")
                    st.rerun()
                    
        with col_queue_view:
            if not social_queue: st.info("Aktuell keine unveröffentlichten Beiträge in der Liste.")
            else:
                for p in social_queue:
                    cq1, cq2 = st.columns([5, 1])
                    with cq1: 
                        st.markdown(f"📱 **{p['plattform']}** ({p['format']}) — *{p['titel']}*")
                    with cq2:
                        if st.button("🗑️", key=f"del_queue_{p['id']}"):
                            social_queue = [item for item in social_queue if item["id"] != p["id"]]
                            save_data(SOCIAL_POSTS_FILE, social_queue)
                            st.rerun()

        st.write("---")
        if not webhook_profile:
            st.error("⚠️ Bitte lege zuerst ein Profil im Tab 'Webhook Verwaltung' an!")
        elif not social_queue:
            st.info("Füge oben Beiträge hinzu, um das Sende-Menü freizuschalten.")
        else:
            selected_soc_prof = st.selectbox("Welches Webhook-Profil nutzen?", list(webhook_profile.keys()), key="soc_prof_select")
            active_soc_profile = webhook_profile[selected_soc_prof]
            soc_ping_text = f"<@&{active_soc_profile['role_id']}> " if active_soc_profile["role_id"] and active_soc_profile["role_id"].lower() not in ["everyone", "here"] else (f"@{active_soc_profile['role_id']} " if active_soc_profile["role_id"] else "")
            soc_post_mode = st.radio("Sende-Format wählen:", ["Alle offenen Beiträge zusammen posten", "Nur einen einzelnen Beitrag picken"], horizontal=True)
            
            if soc_post_mode == "Alle offenen Beiträge zusammen posten":
                default_bulk_desc = "Es gibt frischen Content auf meinen Kanälen! Schaut unbedingt mal rein: \n\n"
                for p in social_queue: 
                    default_bulk_desc += f"📱 **{p['plattform']} [{p['format']}]**\n📌 *{p['titel']}*\n"
                    if p.get("text"): default_bulk_desc += f"💬 *{p['text']}*\n"
                    default_bulk_desc += (f"🔗 {p['link']}\n\n" if p['link'] else "\n")
                    
                edit_soc_ping = st.text_input("Ping", value=f"{soc_ping_text}🔥 CONTENT OUT NOW!", key="edit_soc_p_bulk")
                edit_soc_title = st.text_input("Embed-Titel", value="🎬 NEUE POSTS", key="edit_soc_t_bulk")
                edit_soc_desc = st.text_area("Embed-Beschreibung", value=default_bulk_desc, height=250, key="edit_soc_d_bulk")
                if st.button("📢 Bulk senden", type="primary"):
                    success, msg = send_discord_webhook(active_soc_profile["url"], text_content=edit_soc_ping, embed_data={"title": edit_soc_title, "description": edit_soc_desc, "color": COLORS.get(active_soc_profile["plattform"], COLORS["Allgemein"])})
                    if success: st.success("Senden erfolgreich!")
                    else: st.error(msg)

            elif soc_post_mode == "Nur einen einzelnen Beitrag picken":
                post_options = {f"{p['plattform']} - {p['titel']}": p for p in social_queue}
                chosen_post_key = st.selectbox("Beitrag laden:", list(post_options.keys()))
                sel_p = post_options[chosen_post_key]
                default_single_desc = f"Neuer Post online!\n\n🔹 **Format:** {sel_p['format']}\n📌 **Thema:** {sel_p['titel']}"
                if sel_p.get("text"): default_single_desc += f"\n\n💬 **Was gibts dazu zu sagen:**\n{sel_p['text']}"
                default_single_desc += (f"\n\n🔗 **Link:** {sel_p['link']}" if sel_p['link'] else "")
                
                edit_soc_ping = st.text_input("Ping", value=f"{soc_ping_text}Neues Video!", key="edit_soc_p_single")
                edit_soc_title = st.text_input("Embed-Titel", value=f"🎬 NEW UPLOAD: {sel_p['plattform'].upper()}", key="edit_soc_t_single")
                edit_soc_desc = st.text_area("Embed-Beschreibung", value=default_single_desc, height=200, key="edit_soc_d_single")
                if st.button("📢 Einzeln senden", type="primary"):
                    success, msg = send_discord_webhook(active_soc_profile["url"], text_content=edit_soc_ping, embed_data={"title": edit_soc_title, "description": edit_soc_desc, "color": COLORS.get(sel_p["plattform"], COLORS["Allgemein"])})
                    if success: st.success("Senden erfolgreich!")
                    else: st.error(msg)

# ==============================================================================
# TAB 2: IDEEN & TO-DOS
# ==============================================================================
with tab_ideas:
    col_ideas, col_todos = st.columns([1, 1])
    with col_ideas:
        st.subheader("💡 Content Ideen-Pool")
        with st.expander("➕ Neue Idee festhalten", expanded=False):
            idea_title = st.text_input("Idee / Arbeitstitel")
            idea_platform = st.selectbox("Ziel-Plattform", ["Twitch", "YouTube", "TikTok", "Instagram", "Kick", "Sonstiges"])
            idea_notes = st.text_area("Notizen / Konzept-Skizze")
            if st.button("Idee speichern", type="primary"):
                if idea_title:
                    ideas_daten.append({"id": str(datetime.now().timestamp()), "titel": idea_title, "plattform": idea_platform, "notizen": idea_notes, "status": "Geplant"})
                    save_data(IDEAS_FILE, ideas_daten)
                    st.rerun()
        if ideas_daten:
            for idx, idea in enumerate(ideas_daten):
                with st.expander(f"📌 [{idea['plattform']}] {idea['titel']} ({idea['status']})"):
                    st.write(idea['notizen'] if idea['notizen'] else '*Keine Notizen*')
                    c1, c2 = st.columns([3, 1])
                    neuer_status = c1.selectbox("Status", ["Geplant", "In Arbeit", "Fertig"], index=["Geplant", "In Arbeit", "Fertig"].index(idea["status"]), key=f"st_{idea['id']}")
                    if neuer_status != idea["status"]:
                        ideas_daten[idx]["status"] = neuer_status
                        save_data(IDEAS_FILE, ideas_daten)
                        st.rerun()
                    if c2.button("🗑️", key=f"del_i_{idea['id']}"):
                        ideas_daten = [i for i in ideas_daten if i["id"] != idea["id"]]
                        save_data(IDEAS_FILE, ideas_daten)
                        st.rerun()

    with col_todos:
        st.subheader("✅ Creator To-Do Liste")
        col_td_input, col_td_btn = st.columns([3, 1])
        neues_todo_text = col_td_input.text_input("Neue Aufgabe...", label_visibility="collapsed")
        if col_td_btn.button("Hinzufügen", use_container_width=True) and neues_todo_text:
            todos_daten.append({"id": str(datetime.now().timestamp()), "text": neues_todo_text, "done": False})
            save_data(TODOS_FILE, todos_daten)
            st.rerun()
            
        st.write("---")
        offene_todos = [t for t in todos_daten if not t["done"]]
        erledigte_todos = [t for t in todos_daten if t["done"]]
        
        for t in offene_todos:
            ct1, ct2 = st.columns([10, 1])
            if ct1.checkbox(t["text"], value=False, key=f"todo_{t['id']}"):
                for item in todos_daten: 
                    if item["id"] == t["id"]: item["done"] = True
                save_data(TODOS_FILE, todos_daten)
                st.rerun()
            if ct2.button("🗑️", key=f"del_td_{t['id']}"):
                todos_daten = [item for item in todos_daten if item["id"] != t["id"]]
                save_data(TODOS_FILE, todos_daten)
                st.rerun()
        
        if erledigte_todos:
            st.markdown("---")
            for t in erledigte_todos:
                ct1, ct2 = st.columns([10, 1])
                if ct1.checkbox(f"~~{t['text']}~~", value=True, key=f"todo_{t['id']}"):
                    for item in todos_daten: 
                        if item["id"] == t["id"]: item["done"] = False
                    save_data(TODOS_FILE, todos_daten)
                    st.rerun()
                if ct2.button("🗑️", key=f"del_td_{t['id']}"):
                    todos_daten = [item for item in todos_daten if item["id"] != t["id"]]
                    save_data(TODOS_FILE, todos_daten)
                    st.rerun()
            if st.button("🧹 Erledigte aufräumen"):
                todos_daten = [t for t in todos_daten if not t["done"]]
                save_data(TODOS_FILE, todos_daten)
                st.rerun()

# ==============================================================================
# TAB 3: DISCORD WEBHOOK PROFILE (INKL. ANLEITUNG)
# ==============================================================================
with tab_discord:
    st.subheader("Discord Webhook Profile")
    st.write("Lege hier deine Discord-Kanäle an, um Posts und Sendepläne automatisiert versenden zu können.")
    
    with st.expander("❓ Anleitung: Wo finde ich Webhook-URLs und Rollen-IDs?"):
        st.markdown("""
        **🔗 1. Wie erstelle ich eine Webhook-URL?**
        Damit das Tool in einen Discord-Kanal schreiben darf, brauchst du einen Webhook.
        1. Gehe in deinem Discord auf die **Servereinstellungen** (du brauchst Admin-Rechte).
        2. Klicke auf **Integrationen** und dann auf **Webhooks**.
        3. Klicke auf **Neuer Webhook**.
        4. Gib dem Bot einen Namen, wähle den Textkanal aus (z.B. `#ankündigungen`) und klicke auf **Webhook-URL kopieren**.
        5. Füge diesen Link unten bei *Discord Webhook URL* ein.

        **🏷️ 2. Wie finde ich eine Rollen-ID für Pings?**
        Wenn du möchtest, dass beim Senden eine bestimmte Discord-Rolle markiert/gepingt wird, brauchst du ihre ID.
        1. **Entwicklermodus aktivieren:** Klicke in Discord unten links auf das Zahnrad (Benutzereinstellungen) -> **Erweitert** -> Aktiviere den **Entwicklermodus**.
        2. Gehe zurück in deine Servereinstellungen auf den Reiter **Rollen**.
        3. Mache einen **Rechtsklick** auf die Rolle, die gepingt werden soll (z.B. *Stream-Ping*) und klicke auf **Rollen-ID kopieren**.
        4. Füge diese Nummerfolge unten ein (das Tool wandelt sie automatisch in den richtigen Code `<@&123...>` um).
        
        *Tipp: Wenn du stattdessen einfach das Wort `everyone` oder `here` in das Feld einträgst, funktioniert das auch!*
        """)
        
    st.write("---")

    col_manage, col_list = st.columns([1, 1])
    with col_manage:
        new_profile_name = st.text_input("Profilname (z.B. Sendeplan oder YouTube-Uploads)")
        new_platform = st.selectbox("Haupt-Plattform (Für Randfarben der Embeds)", list(COLORS.keys()), key="wh_plat")
        new_url = st.text_input("Discord Webhook URL", type="password", key="wh_url")
        new_role = st.text_input("Rollen-ID für Ping (Optional)", placeholder="z.B. everyone oder 123456789", key="wh_role")
        if st.button("Profil Speichern", key="save_webhook_profile_btn", type="primary"):
            if not new_profile_name or not new_url: st.error("Name & URL sind Pflichtfelder!")
            else:
                webhook_profile[new_profile_name] = {"plattform": new_platform, "url": new_url, "role_id": new_role.strip()}
                save_data(WEBHOOKS_FILE, webhook_profile)
                st.success(f"✓ Profil '{new_profile_name}' gespeichert!")
                st.rerun()

    with col_list:
        st.write("### 💡 Gespeicherte Profile")
        if not webhook_profile: st.info("Noch keine Profile angelegt.")
        else:
            for prof_name, data in webhook_profile.items():
                with st.expander(f"⚙️ {prof_name} ({data['plattform']})"):
                    st.code(f"Rollen-ID: {data['role_id'] if data['role_id'] else 'Keine'}")
                    if st.button("❌ Löschen", key=f"del_prof_{prof_name}"):
                        del webhook_profile[prof_name]
                        save_data(WEBHOOKS_FILE, webhook_profile)
                        st.rerun()

# ==============================================================================
# TAB 4: STREAMING-PLANER (JETZT MIT SMART-WEBHOOK VERBINDUNG)
# ==============================================================================
with tab_schedule:
    subtab_plan, subtab_post = st.tabs(["✍️ Sendeplan erstellen", "🚀 Plan an Discord senden"])
    with subtab_plan:
        col_form, col_view = st.columns([1, 1])
        with col_form:
            stream_title = st.text_input("Stream-Thema", key="sched_tit")
            stream_day = st.selectbox("Wochentag", WOCHENTAGE, key="sched_day")
            stream_time = st.time_input("Startzeit", time(19, 0), key="sched_time")
            stream_platform = st.selectbox("Plattform", ["Twitch", "YouTube", "Kick", "TikTok", "Sonstiges"], key="sched_plat")
            if st.button("➕ In Plan eintragen", type="secondary", key="add_stream_btn"):
                if not stream_title: st.error("Thema fehlt!")
                else:
                    schedule_daten.append({"id": str(datetime.now().timestamp()), "titel": stream_title, "tag": stream_day, "uhrzeit": stream_time.strftime("%H:%M"), "plattform": stream_platform})
                    save_data(SCHEDULE_FILE, schedule_daten)
                    st.success("✓ Eingetragen!")
                    st.rerun()
                    
        with col_view:
            if not schedule_daten: st.info("Dein Plan ist leer.")
            else:
                for tag in WOCHENTAGE:
                    tag_streams = [s for s in schedule_daten if s["tag"] == tag]
                    if tag_streams:
                        st.markdown(f"**🗓️ {tag}**")
                        tag_streams.sort(key=lambda x: x["uhrzeit"])
                        for s in tag_streams:
                            c1, c2 = st.columns([4, 1])
                            c1.markdown(f"• `{s['uhrzeit']}` | **{s['plattform']}** - {s['titel']}")
                            if c2.button("🗑️", key=f"del_{s['id']}"):
                                schedule_daten = [item for item in schedule_daten if item["id"] != s["id"]]
                                save_data(SCHEDULE_FILE, schedule_daten)
                                st.rerun()

    with subtab_post:
        if not webhook_profile: 
            st.error("⚠️ Bitte lege zuerst ein Profil an!")
        elif not schedule_daten: 
            st.info("Dein Sendeplan ist leer.")
        else:
            post_mode = st.radio("Was senden?", ["Ganzen Wochenplan", "Einzelnen Stream"], horizontal=True, key="sched_post_mode")
            prof_keys = list(webhook_profile.keys())
            
            if post_mode == "Ganzen Wochenplan":
                # Smart Default: Sucht nach Profil mit "Sendeplan" im Namen oder Typ "Sendeplan / Kalender"
                default_index = 0
                for i, k in enumerate(prof_keys):
                    if "sendeplan" in k.lower() or webhook_profile[k].get("plattform") == "Sendeplan / Kalender":
                        default_index = i
                        break
                
                selected_prof_name = st.selectbox("Über welches Profil posten?", prof_keys, index=default_index, key="sched_prof_select_bulk")
                active_profile = webhook_profile[selected_prof_name]
                ping_text = f"<@&{active_profile['role_id']}> " if active_profile["role_id"] and active_profile["role_id"].lower() not in ["everyone", "here"] else (f"@{active_profile['role_id']} " if active_profile["role_id"] else "")

                default_desc = ""
                for tag in WOCHENTAGE:
                    tag_streams = [s for s in schedule_daten if s["tag"] == tag]
                    if tag_streams:
                        default_desc += f"\n**🗓️ {tag}**\n"
                        tag_streams.sort(key=lambda x: x["uhrzeit"])
                        for s in tag_streams: default_desc += f"• `{s['uhrzeit']}` | **{s['plattform']}** - {s['titel']}\n"

                edit_ping = st.text_input("Text & Ping", value=f"{ping_text}Hier ist der Sendeplan!", key="ed_p_bulk")
                edit_title = st.text_input("Titel", value="📅 STREAMINGPLAN DIESE WOCHE", key="ed_t_bulk")
                edit_desc = st.text_area("Beschreibung", value=default_desc, height=250, key="ed_d_bulk")
                
                if st.button("📢 Wochenplan absenden", type="primary", key="send_sched_bulk"):
                    success, msg = send_discord_webhook(active_profile["url"], text_content=edit_ping, embed_data={"title": edit_title, "description": edit_desc, "color": COLORS.get(active_profile["plattform"], COLORS["Allgemein"])})
                    if success: st.success("Sendeplan abgeschickt!")
                    else: st.error(msg)

            elif post_mode == "Einzelnen Stream":
                stream_options = {f"{s['tag']} ({s['uhrzeit']}) - {s['titel']}": s for s in schedule_daten}
                chosen_key = st.selectbox("Welchen Stream ankündigen?", list(stream_options.keys()), key="chosen_single_stream")
                chosen_stream = stream_options[chosen_key]
                
                # Smart Default: Versucht den Webhook der exakten Stream-Plattform (z.B. Twitch) zu laden
                default_index = 0
                for i, k in enumerate(prof_keys):
                    if webhook_profile[k].get("plattform").lower() == chosen_stream["plattform"].lower():
                        default_index = i
                        break
                    elif "sendeplan" in k.lower():
                        default_index = i
                
                selected_prof_name = st.selectbox("Über welches Profil posten?", prof_keys, index=default_index, key="sched_prof_select_single")
                active_profile = webhook_profile[selected_prof_name]
                ping_text = f"<@&{active_profile['role_id']}> " if active_profile["role_id"] and active_profile["role_id"].lower() not in ["everyone", "here"] else (f"@{active_profile['role_id']} " if active_profile["role_id"] else "")

                default_desc = f"Am **{chosen_stream['tag']}** gehen wir um **{chosen_stream['uhrzeit']} Uhr** live!\n\n🎮 **Thema:** {chosen_stream['titel']}"
                edit_ping = st.text_input("Text & Ping", value=f"{ping_text}Wir gehen live!", key="ed_p_single")
                edit_title = st.text_input("Titel", value=f"🔔 LIVE-ANKÜNDIGUNG: {chosen_stream['plattform'].upper()}", key="ed_t_single")
                edit_desc = st.text_area("Beschreibung", value=default_desc, height=150, key="ed_d_single")
                
                if st.button("📢 Einzelnen Stream absenden", type="primary", key="send_sched_single"):
                    success, msg = send_discord_webhook(active_profile["url"], text_content=edit_ping, embed_data={"title": edit_title, "description": edit_desc, "color": COLORS.get(chosen_stream["plattform"], COLORS["Allgemein"])})
                    if success: st.success("Ankündigung abgeschickt!")
                    else: st.error(msg)

# ==============================================================================
# TAB 5: FREIES POSTEN / NEWS (MIT EMBEDS)
# ==============================================================================
with tab_freepost:
    st.subheader("📢 Freie Beiträge an Discord senden")
    st.write("Verfasse hier komplett freie Posts (z.B. Gaming News, spontane Updates) und sende sie an deine Webhooks.")

    if not webhook_profile:
        st.error("⚠️ Bitte lege zuerst ein Profil im Tab 'Webhook Verwaltung' an!")
    else:
        selected_free_prof = st.selectbox("Welches Profil möchtest du nutzen?", list(webhook_profile.keys()), key="free_prof_select")
        active_free_prof = webhook_profile[selected_free_prof]
        
        post_style = st.radio("Wie möchtest du posten?", ["Schickes Embed (Empfohlen)", "Nur Text"], horizontal=True)
        
        f_role = active_free_prof['role_id']
        ping_str = f"<@&{f_role}> " if f_role and f_role.lower() not in ["everyone", "here"] else (f"@{f_role} " if f_role else "")

        if post_style == "Schickes Embed (Empfohlen)":
            st.markdown("### 📝 Embed Builder")
            f_ping = st.text_input("Nachricht außerhalb des Embeds (inkl. Ping)", value=f"{ping_str}Neue Info!", key="fp_ping")
            f_title = st.text_input("Titel des Embeds", placeholder="z.B. 🎮 EILMELDUNG: Neues Update ist da!", key="fp_title")
            f_desc = st.text_area("Beschreibung / Text", height=200, placeholder="Schreibe hier deinen ausführlichen Text...", key="fp_desc")
            
            c_img, c_col = st.columns(2)
            with c_img: f_img = st.text_input("Bild-URL (Optional)", placeholder="https://beispiel.de/bild.jpg", key="fp_img")
            with c_col:
                default_hex = PLOT_COLORS.get(active_free_prof.get("plattform", "Sonstiges"), "#9146FF")
                f_color = st.color_picker("Farbe des Embed-Randes", value=default_hex, key="fp_color")
                
            if st.button("🚀 Embed absenden", type="primary", key="btn_send_embed"):
                if not f_title and not f_desc: st.error("Bitte gib mindestens einen Titel oder eine Beschreibung ein!")
                else:
                    try: color_int = int(f_color.lstrip('#'), 16)
                    except: color_int = 5793266
                    
                    embed_payload = {"title": f_title, "description": f_desc, "color": color_int}
                    if f_img: embed_payload["image"] = {"url": f_img}
                        
                    success, msg = send_discord_webhook(active_free_prof["url"], text_content=f_ping, embed_data=embed_payload)
                    if success: st.success("Nachricht erfolgreich gesendet!")
                    else: st.error(msg)
                    
        else:
            st.markdown("### 📝 Text Nachricht")
            f_text = st.text_area("Deine Nachricht", value=ping_str, height=200, key="fp_text_only")
            if st.button("🚀 Text absenden", type="primary", key="btn_send_text"):
                if not f_text: st.error("Die Nachricht darf nicht leer sein!")
                else:
                    success, msg = send_discord_webhook(active_free_prof["url"], text_content=f_text)
                    if success: st.success("Nachricht erfolgreich gesendet!")
                    else: st.error(msg)

# ==============================================================================
# TAB 6: TECHNIK & TOOLS
# ==============================================================================
with tab_tools:
    st.header("🛠️ Technik, Tools & Guides")
    st.write("Eine Anlaufstelle für wichtige Tools und Anleitungen. Perfekt, wenn man gerade erst mit dem Streamen oder der Content-Erstellung anfängt!")
    
    sub_alerts, sub_bots, sub_cmd_gen = st.tabs(["🔔 Interaktiver Alert-Guide", "🤖 Bot-Empfehlungen", "⌨️ !Befehl-Generator"])
    
    with sub_alerts:
        st.subheader("Wie binde ich Follower- & Sub-Alerts in meinen Stream ein?")
        st.write("Wähle hier einfach aus, wo du deine Alerts erstellt hast und mit welchem Programm du streamst. Die Anleitung passt sich automatisch an!")
        
        col_a1, col_a2 = st.columns(2)
        with col_a1: alert_source = st.selectbox("Wo hast du deine Alerts erstellt?", ["StreamElements", "Streamlabs"])
        with col_a2: stream_software = st.selectbox("Welches Programm nutzt du zum Streamen?", ["OBS Studio", "Streamlabs Desktop"])
        
        st.markdown("---")
        st.markdown("### 📋 Deine Schritt-für-Schritt Anleitung:")
        
        if alert_source == "StreamElements":
            st.markdown("""
            **Schritt 1: Den Overlay-Link kopieren (StreamElements)**
            1. Logge dich bei [StreamElements](https://streamelements.com) ein.
            2. Gehe links im Menü auf **Streaming-Tools** -> **Overlays**.
            3. Erstelle ein neues Overlay oder bearbeite dein bestehendes (dort fügst du das Widget 'AlertBox' hinzu).
            4. Klicke oben rechts auf das kleine **Ketten-Symbol** ("Copy Overlay URL"). Der Link ist nun in deiner Zwischenablage.
            """)
        else:
            st.markdown("""
            **Schritt 1: Die Widget-URL kopieren (Streamlabs)**
            1. Logge dich bei [Streamlabs](https://streamlabs.com) ein.
            2. Gehe links im Menü auf **Essentials** -> **Alert Box**.
            3. Oben siehst du ein verschleiertes Feld namens "Widget URL".
            4. Klicke daneben auf den Button **"Kopieren"**. Gib diesen Link niemals an andere weiter!
            """)
            
        if stream_software == "OBS Studio":
            st.markdown("""
            **Schritt 2: Alerts in OBS Studio einbinden**
            1. Öffne **OBS Studio**.
            2. Gehe unten zu deinen **Quellen** (Sources) und klicke auf das **Plus-Symbol (+)**.
            3. Wähle **Browser** (oder Browser-Quelle) aus.
            4. Gib der Quelle einen Namen, z.B. "Alerts".
            5. Es öffnet sich ein Fenster. Bei **URL** löschst du den vorgegebenen Link und drückst `STRG + V`, um deinen kopierten Link einzufügen.
            6. Setze die Breite auf `1920` und die Höhe auf `1080` (Standard für die meisten Overlays).
            7. Klicke auf **OK**. Du kannst die Quelle nun auf deinem Bildschirm verschieben. Teste den Alert über das Dashboard deiner ausgewählten Webseite!
            """)
        else:
            st.markdown("""
            **Schritt 2: Alerts in Streamlabs Desktop einbinden**
            *Hinweis: Wenn du bereits mit Streamlabs Desktop streamst, kannst du die Alert Box oft auch direkt als internes Widget hinzufügen! Falls du dennoch einen Link einfügen willst, geht das so:*
            1. Öffne **Streamlabs Desktop**.
            2. Gehe zu **Quellen** und klicke auf das **Plus-Symbol (+)**.
            3. Wähle unter den Standardquellen **Browser-Quelle** aus.
            4. Klicke auf **Quelle hinzufügen**.
            5. Füge bei **URL** deinen kopierten Link mit `STRG + V` ein.
            6. Passe bei Bedarf Breite (1920) und Höhe (1080) an.
            7. Klicke auf **Fertig**. Teste danach deinen Alert über den "Test Widget" Button unten!
            """)
            
    with sub_bots:
        st.subheader("Die besten Chat-Bots für deinen Kanal")
        st.write("Gerade für Creator mit kleinerer Reichweite ist es wichtig, den Chat sauber zu halten und wiederkehrende Infos automatisiert ausgeben zu lassen:")
        
        st.markdown("#### 🟢 Kostenfrei & Einsteigerfreundlich")
        with st.expander("🦉 Nightbot (Der Klassiker für Twitch & YouTube)"):
            st.markdown("""
            **Warum er gut ist:** Nightbot ist seit Jahren der absolute Standard. Er ist extrem zuverlässig, leicht verständlich und erschlägt dich nicht mit tausenden Untermenüs. Ideal, um Spam zu filtern und einfache `!socials` Befehle zu erstellen.
            * **Plattformen:** Twitch, YouTube
            * **Link:** [nightbot.tv](https://nightbot.tv)
            """)
        with st.expander("💧 StreamElements (Die All-in-One Lösung)"):
            st.markdown("""
            **Warum er gut ist:** Wenn du ohnehin deine Alerts über StreamElements laufen lässt, macht es Sinn, auch den Chat-Bot zu nutzen. Er läuft komplett in der Cloud, bietet Minispiele und ein exzellentes Punkte-System.
            * **Plattformen:** Twitch, YouTube
            * **Link:** [streamelements.com](https://streamelements.com)
            """)
        with st.expander("🤖 Fossabot (Schnell & Twitch-Fokussiert)"):
            st.markdown("""
            **Warum er gut ist:** Fossabot ist unglaublich schnell und wird oft von sehr großen Streamern genutzt, ist aber für kleine Kanäle genauso genial. Er bietet extrem tiefe Anpassungsmöglichkeiten.
            * **Plattformen:** Twitch
            * **Link:** [fossabot.com](https://fossabot.com)
            """)
            
        st.markdown("#### 🟠 Für Fortgeschrittene (Mit Abo- oder Premium-Modellen)")
        with st.expander("💡 Lumia Stream (Für Smart-Home Enthusiasten)"):
            st.markdown("""
            **Warum er gut ist:** Lumia Stream verbindet deinen Stream mit deinen echten Lichtern im Zimmer (Philips Hue, Nanoleaf etc.). Zuschauer können über den Chat deine Raumbeleuchtung ändern!
            * **Modell:** Freemium (Basis gratis, Abo für mehr Integrationen)
            * **Link:** [lumiastream.com](https://lumiastream.com)
            """)
        with st.expander("⚙️ Mix It Up (Die ultimative Macht)"):
            st.markdown("""
            **Warum er gut ist:** Eigentlich komplett kostenlos, aber definitiv eher etwas für "Profis". Mix It Up läuft lokal auf deinem PC und kann *alles*. Von komplexen Wenn-Dann-Schleifen bis zur automatischen Steuerung von OBS.
            * **Modell:** Kostenlos (Donation-Ware)
            * **Link:** [mixitupapp.com](https://mixitupapp.com)
            """)

    with sub_cmd_gen:
        st.subheader("⌨️ Smarter Chat-Befehl Generator")
        st.write("Vergiss komplizierte Codes! Sag dem Tool einfach, was der Befehl tun soll, und es generiert die korrekte Programmierung (mit den richtigen Klammern) für deinen Bot.")
        
        target_bot = st.selectbox("Welchen Bot nutzt du?", ["StreamElements", "Nightbot", "Fossabot"])
        
        # Variablen-Mapping abhängig vom gewählten Bot
        v_user = "${user}" if target_bot == "StreamElements" else "$(user)"
        v_touser = "${touser}" if target_bot == "StreamElements" else "$(touser)"
        v_channel = "${channel}" if target_bot == "StreamElements" else "$(channel)"

        cmd_type = st.radio("Was für eine Art von Befehl möchtest du erstellen?", 
                            ["🫂 Interaktion (Umarmen, High-Five etc.)", "📣 Shoutout (Anderen Streamer empfehlen)", "📝 Einfacher Text"], horizontal=True)

        st.markdown("---")
        
        if cmd_type == "🫂 Interaktion (Umarmen, High-Five etc.)":
            st.info(f"**Beispiel-Ausgabe im Chat:** *DeinName umarmt ZielNutzer ganz doll!*")
            cmd_name = st.text_input("Befehlsname", placeholder="z.B. !hug")
            col_a, col_b = st.columns(2)
            with col_a:
                action_verb = st.text_input("Aktion (Was tust du?)", placeholder="z.B. umarmt, wirft einen Keks auf")
            with col_b:
                action_suffix = st.text_input("Zusatz (Optional)", placeholder="z.B. ganz doll!, und rennt weg.")
            
            cmd_msg = f"{v_user} {action_verb} {v_touser} {action_suffix}".strip()
            
        elif cmd_type == "📣 Shoutout (Anderen Streamer empfehlen)":
            st.info(f"**Beispiel-Ausgabe im Chat:** *Schaut unbedingt vorbei bei ZielNutzer! Link: twitch.tv/ZielNutzer*")
            cmd_name = st.text_input("Befehlsname", value="!so")
            so_text = st.text_input("Dein Empfehlungstext", value="Schaut unbedingt vorbei bei")
            cmd_msg = f"{so_text} {v_touser}! Here lang: https://twitch.tv/{v_touser}"
            
        else: # Einfacher Text
            st.info("Hier kannst du völlig frei schreiben. Wenn du Namen erwähnen willst, nutze die Platzhalter.")
            cmd_name = st.text_input("Befehlsname", placeholder="z.B. !discord")
            cmd_msg = st.text_area("Dein Text", placeholder="Komm auf unseren Server: https://discord.gg/...")
            st.write("*(Tipp: Kopiere diese Platzhalter in deinen Text, wenn du Namen nutzen willst)*")
            st.code(f"Dein eigener Name: {v_user}  |  Der markierte Name: {v_touser}", language="text")

        st.markdown("---")
        col_gen1, col_gen2 = st.columns([1, 1])
        with col_gen1:
            cmd_userlevel = st.selectbox("Wer darf den Befehl nutzen?", ["Everyone", "Moderator", "Subscriber"])
        with col_gen2:
            cmd_cooldown = st.slider("Cooldown (Sekunden)", 5, 300, 15)

        if st.button("🚀 Befehl jetzt generieren", type="primary"):
            if not cmd_name or not cmd_msg:
                st.error("⚠️ Bitte gib einen Befehlsnamen und den Text/die Aktion ein!")
            else:
                st.write("### ✅ Dein fertiger Code:")
                final_name = cmd_name if cmd_name.startswith("!") else "!" + cmd_name
                
                if target_bot == "Nightbot":
                    ul_map = {"Everyone": "everyone", "Moderator": "moderator", "Subscriber": "subscriber"}
                    bot_string = f"!addcom {final_name} {cmd_msg} -ul={ul_map[cmd_userlevel]} -cd={cmd_cooldown}"
                elif target_bot == "StreamElements":
                    bot_string = f"!command add {final_name} {cmd_msg}"
                    st.caption("Hinweis: Bei StreamElements stellst du das Userlevel (Mod/Sub) am besten direkt im Online-Dashboard ein.")
                elif target_bot == "Fossabot":
                    bot_string = f"!command add {final_name} {cmd_msg}"

                st.info("Kopiere diesen kompletten Text und sende ihn einfach direkt in deinen Twitch/YouTube Chat:")
                st.code(bot_string, language="text")