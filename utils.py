import streamlit as st
import psycopg2
from psycopg2.extras import DictCursor
import hashlib
import requests
import json

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

def get_db_connection():
    db_url = st.secrets["DATABASE_URL"]
    conn = psycopg2.connect(db_url, cursor_factory=DictCursor)
    conn.autocommit = True
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, theme TEXT DEFAULT 'Dark', accent TEXT DEFAULT 'Pastell')")
    cursor.execute("CREATE TABLE IF NOT EXISTS webhooks (id SERIAL PRIMARY KEY, username TEXT, profile_name TEXT, url TEXT, plattform TEXT, role_id TEXT, UNIQUE(username, profile_name))")
    cursor.execute("CREATE TABLE IF NOT EXISTS user_data (username TEXT, data_type TEXT, json_content TEXT, PRIMARY KEY (username, data_type))")
    cursor.execute("CREATE TABLE IF NOT EXISTS api_credentials (username TEXT, platform TEXT, channel_id TEXT, api_key TEXT, PRIMARY KEY (username, platform))")
    cursor.close()
    conn.close()

init_db()

# ==============================================================================
# 🎨 CINEMATIC DARK DESIGN-SYSTEM
# ==============================================================================
def apply_modern_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

        .stApp {
            background-color: #050508 !important;
            color: #E0E0E0 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            background-image: radial-gradient(circle at 50% 0%, #1a0b2e 0%, #050508 50%);
        }

        [data-testid="stSidebar"] { background-color: #0A0A10 !important; border-right: 1px solid #1c1c28 !important; }
        
        h1, h2, h3, h4 { color: #FFFFFF !important; text-transform: uppercase; letter-spacing: 1px; }

        div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stForm"], div[data-testid="stExpander"] {
            background-color: #0A0A10 !important;
            border: 1px solid #1c1c28 !important;
            border-radius: 4px !important;
            padding: 20px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
            transition: all 0.3s ease;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #00E5FF !important;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.15) !important;
        }

        a[data-testid="stPageLink-NavLink"] { background-color: transparent !important; padding: 0 !important; border: none !important; }
        a[data-testid="stPageLink-NavLink"] p {
            font-family: 'Space Grotesk', sans-serif !important; 
            font-weight: 700 !important; 
            font-size: 20px !important;
            color: #00E5FF !important;
            margin: 0 !important;
            transition: all 0.2s;
        }
        a[data-testid="stPageLink-NavLink"]:hover p { color: #FFFFFF !important; text-shadow: 0 0 10px #00E5FF; transform: translateX(5px); }

        .stButton>button {
            background-color: transparent !important;
            color: #00E5FF !important;
            border: 1px solid #00E5FF !important;
            border-radius: 4px !important;
            text-transform: uppercase;
            font-weight: 600 !important;
            transition: all 0.2s;
        }
        .stButton>button:hover { background-color: rgba(0, 229, 255, 0.1) !important; box-shadow: 0 0 15px rgba(0, 229, 255, 0.4) !important; }
        .stButton>button[kind="primary"] { background-color: rgba(0, 229, 255, 0.15) !important; box-shadow: 0 0 10px rgba(0, 229, 255, 0.3) !important; }

        .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div, .stNumberInput>div>div { 
            background-color: #050508 !important; border: 1px solid #1c1c28 !important; color: #E0E0E0 !important; border-radius: 4px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# DATENBANK FUNKTIONEN
# ==============================================================================
def load_data(file_or_type, default_factory):
    data_type = file_or_type.replace(".json", "").replace("data_", "")
    if "_" in data_type: data_type = data_type.split("_")[-1]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json_content FROM user_data WHERE username = %s AND data_type = %s", (st.session_state.get("username", "global"), data_type))
    row = cursor.fetchone()
    cursor.close(); conn.close()
    if row:
        try: return json.loads(row["json_content"])
        except: return default_factory()
    return default_factory()

def save_data(file_or_type, data):
    data_type = file_or_type.replace(".json", "").replace("data_", "")
    if "_" in data_type: data_type = data_type.split("_")[-1]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_data (username, data_type, json_content) VALUES (%s, %s, %s) ON CONFLICT (username, data_type) DO UPDATE SET json_content = EXCLUDED.json_content", (st.session_state.get("username", "global"), data_type, json.dumps(data, ensure_ascii=False)))
    cursor.close(); conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("🔒 Bitte logge dich über die Hauptseite ein!")
        st.stop()
    apply_modern_css() 
    return st.session_state["username"]

# ==============================================================================
# DISCORD WEBHOOK FUNKTION (HIER WAR DER FEHLER - FUNKTION IST JETZT WIEDER DA)
# ==============================================================================
def send_discord_webhook(url, text_content=None, embed_data=None):
    payload = {}
    
    # Prüfen, ob ein Medien-Link im Text oder Embed steckt
    full_text_check = f"{text_content or ''} "
    if embed_data:
        full_text_check += f"{embed_data.get('title', '')} {embed_data.get('description', '')}"
        
    has_media_link = any(x in full_text_check for x in ["youtube.com/", "youtu.be/", "x.com/", "twitter.com/"])

    # FALL A: Es ist ein Medien-Link dabei -> Embed auflösen, um Vorschau zu erzwingen
    if has_media_link and embed_data:
        text_pieces = []
        if text_content:
            text_pieces.append(text_content.strip())
        if embed_data.get("title"):
            text_pieces.append(f"**{embed_data['title'].strip()}**")
        if embed_data.get("description"):
            text_pieces.append(embed_data["description"].strip())
            
        payload["content"] = "\n\n".join(text_pieces)

    # FALL B: Normales Update -> Klassischer farbiger Kasten (Embed)
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