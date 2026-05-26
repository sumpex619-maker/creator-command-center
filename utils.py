import streamlit as st
import psycopg2
from psycopg2.extras import DictCursor
import hashlib
import requests
import json

# ==============================================================================
# GLOBALE KONFIGURATION & FARBEN
# ==============================================================================
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
# SUPABASE POSTGRES CONNECTION
# ==============================================================================
def get_db_connection():
    db_url = st.secrets["DATABASE_URL"]
    # autocommit=True verhindert offene Transaktions-Leichen im Supabase-Pooler
    conn = psycopg2.connect(db_url, cursor_factory=DictCursor)
    conn.autocommit = True
    return conn

def init_db():
    """Erstellt alle benötigten Tabellen in Supabase, falls sie fehlen."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        theme TEXT DEFAULT 'Dark',
        accent TEXT DEFAULT 'Pastell Ozean (Blau)'
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS webhooks (
        id SERIAL PRIMARY KEY,
        username TEXT,
        profile_name TEXT,
        url TEXT,
        plattform TEXT,
        role_id TEXT,
        UNIQUE(username, profile_name)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_data (
        username TEXT,
        data_type TEXT,
        json_content TEXT,
        PRIMARY KEY (username, data_type)
    )""")
    
    cursor.close()
    conn.close()

# Datenbank beim Start prüfen/initialisieren
init_db()

# ==============================================================================
# FUNKTIONEN FÜR DIE UNTERSEITEN (DATENBANK-BACKEND)
# ==============================================================================
def load_data(file_or_type, default_factory):
    data_type = file_or_type.replace(".json", "").replace("data_", "")
    if "_" in data_type: 
        parts = data_type.split("_")
        if len(parts) > 2: data_type = parts[-1]

    username = st.session_state.get("username", "global")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json_content FROM user_data WHERE username = %s AND data_type = %s", (username, data_type))
    row = cursor.fetchone()
    cursor.close()
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
        INSERT INTO user_data (username, data_type, json_content)
        VALUES (%s, %s, %s)
        ON CONFLICT (username, data_type) 
        DO UPDATE SET json_content = EXCLUDED.json_content
    """, (username, data_type, json_string))
    cursor.close()
    conn.close()

# ==============================================================================
# HILFSFUNKTIONEN & DISCORD
# ==============================================================================
def send_discord_webhook(url, text_content=None, embed_data=None):
    payload = {}
    
    # Prüfen, ob irgendwo im Text oder Embed ein Medien-Link (YouTube/X) steckt
    full_text_check = f"{text_content or ''} "
    if embed_data:
        full_text_check += f"{embed_data.get('title', '')} {embed_data.get('description', '')}"
        
    has_media_link = any(x in full_text_check for x in ["youtube.com/", "youtu.be/", "x.com/", "twitter.com/"])

    # FALL A: Es ist ein Video-/Medien-Link dabei -> Embed auflösen, damit Discord die Vorschau generiert!
    if has_media_link and embed_data:
        text_pieces = []
        
        # Pings oder Haupttext ganz nach oben (@community etc.)
        if text_content:
            text_pieces.append(text_content.strip())
            
        # Titel fett als Überschrift formatieren
        if embed_data.get("title"):
            text_pieces.append(f"**{embed_data['title'].strip()}**")
            
        # Beschreibung (wo auch der YouTube-Link drinsteht) anhängen
        if embed_data.get("description"):
            text_pieces.append(embed_data["description"].strip())
            
        # Alles zu einer sauberen Textnachricht zusammenfügen
        payload["content"] = "\n\n".join(text_pieces)
        # WICHTIG: Das 'embeds'-Feld wird bewusst weggelassen, um die Sperre aufzuheben!

    # FALL B: Ganz normales Update ohne Video -> Nutze das klassische, farbige Embed-Design
    else:
        if text_content: 
            payload["content"] = text_content
        if embed_data: 
            payload["embeds"] = [embed_data]
            
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