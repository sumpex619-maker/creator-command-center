import streamlit as st
import sqlite3
import hashlib
import requests
import json

# ==============================================================================
# GLOBALE KONFIGURATION & FARBEN
# ==============================================================================
DB_FILE = "command_center.db"
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
# DATENBANK INITIALISIERUNG
# ==============================================================================
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Erstellt alle benötigten Tabellen, falls sie noch nicht existieren."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Benutzer-Tabelle
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        theme TEXT DEFAULT 'Dark',
        accent TEXT DEFAULT 'Pastell Ozean (Blau)'
    )""")
    
    # 2. Webhooks-Tabelle
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS webhooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        profile_name TEXT,
        url TEXT,
        plattform TEXT,
        role_id TEXT,
        UNIQUE(username, profile_name)
    )""")
    
    # 3. JSON-Fallback-Tabelle
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_data (
        username TEXT,
        data_type TEXT,
        json_content TEXT,
        PRIMARY KEY (username, data_type)
    )""")
    
    conn.commit()
    conn.close()

# Datenbank sofort beim Import starten
init_db()

# ==============================================================================
# NEUE DATENBANK-FUNKTIONEN (ERSATZ FÜR JSON)
# ==============================================================================
def load_data(file_or_type, default_factory):
    data_type = file_or_type.replace(".json", "").replace("data_", "")
    if "_" in data_type: 
        parts = data_type.split("_")
        if len(parts) > 2: data_type = parts[-1]

    username = st.session_state.get("username", "global")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json_content FROM user_data WHERE username = ? AND data_type = ?", (username, data_type))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        try: return json.loads(row["json_content"])
        except: return default_factory()
    return default_factory()

def save_data(file_or_type, data):
    data_type = file_or_type.replace(".json", "").replace("data_", "")
    if "_" in data_type:
        parts = data_type.split("_")
        if len(parts) > 2: data_type = parts[-1]
        
    username = st.session_state.get("username", "global")
    json_string = json.dumps(data, ensure_ascii=False)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_data (username, data_type, json_content)
        VALUES (?, ?, ?)
    """, (username, data_type, json_string))
    conn.commit()
    conn.close()

# ==============================================================================
# HILFSFUNKTIONEN & DISCORD
# ==============================================================================
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

def check_login():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("🔒 Bitte logge dich über die Hauptseite ein!")
        st.stop()
    return st.session_state["username"]

def get_user_filepath(username, file_type):
    return file_type