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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_credentials (
        username TEXT,
        platform TEXT,
        channel_id TEXT,
        api_key TEXT,
        PRIMARY KEY (username, platform)
    )""")
    cursor.close()
    conn.close()

init_db()

# ==============================================================================
# 🎨 ZENTRALES DESIGN-SYSTEM (MODERN 2.0 & SLIDING EFFECTS)
# ==============================================================================
def apply_modern_css():
    if "theme" not in st.session_state: st.session_state["theme"] = "Midnight (Dark)"
    
    if st.session_state["theme"] == "Midnight (Dark)":
        BG_COLOR = "#0B0F19"; SIDEBAR_BG = "#111827"; CARD_BG = "rgba(30, 41, 59, 0.6)"
        TEXT_COLOR = "#F8FAFC"; BORDER_COLOR = "rgba(255, 255, 255, 0.05)"
        GLOW = "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
    else:
        BG_COLOR = "#F3F4F6"; SIDEBAR_BG = "#FFFFFF"; CARD_BG = "rgba(255, 255, 255, 0.8)"
        TEXT_COLOR = "#111827"; BORDER_COLOR = "rgba(0, 0, 0, 0.05)"
        GLOW = "0 8px 32px 0 rgba(31, 38, 135, 0.07)"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;500;600&display=swap');
        
        /* Basis */
        html, body, [class*="css"], .stMarkdown {{ font-family: 'Inter', sans-serif !important; color: {TEXT_COLOR} !important; }}
        .stApp {{ background-color: {BG_COLOR} !important; background-image: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.05) 0%, transparent 50%); }}
        h1, h2, h3, h4 {{ font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; color: {TEXT_COLOR} !important; letter-spacing: -0.5px; }}
        [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG} !important; border-right: 1px solid {BORDER_COLOR}; }}
        
        /* Karten & Container mit Fade/Slide-In */
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(15px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Das ist neu: Native Streamlit-Container (.stVerticalBlockBorderWrapper) sehen nun aus wie Bento-Karten! */
        .bento-card, div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stExpander"], .stAlert, div[data-testid="stForm"] {{ 
            background: {CARD_BG} !important; 
            backdrop-filter: blur(12px) !important; 
            border-radius: 20px !important; 
            border: 1px solid {BORDER_COLOR} !important; 
            padding: 24px !important; 
            box-shadow: {GLOW} !important;
            margin-bottom: 15px; 
            animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }}
        
        /* Page Links als interaktive Überschriften in den Boxen */
        a[data-testid="stPageLink-NavLink"] {{
            background-color: transparent !important;
            padding: 0 !important;
            border: none !important;
        }}
        a[data-testid="stPageLink-NavLink"] p {{
            font-family: 'Outfit', sans-serif !important; 
            font-weight: 800 !important; 
            font-size: 22px !important;
            color: #38BDF8 !important;
            margin: 0 !important;
            transition: color 0.2s ease-in-out, transform 0.2s ease-in-out;
        }}
        a[data-testid="stPageLink-NavLink"]:hover p {{
            color: #818CF8 !important;
            transform: translateX(5px);
        }}
        
        /* Buttons */
        .stButton>button {{ 
            border-radius: 12px !important; 
            background-color: transparent !important; 
            color: {TEXT_COLOR} !important; 
            border: 1px solid rgba(129, 140, 248, 0.5) !important; 
            font-family: 'Outfit', sans-serif !important; 
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out; 
        }}
        .stButton>button:hover {{ border-color: #38BDF8 !important; background-color: rgba(56, 189, 248, 0.1) !important; transform: translateY(-2px); }}
        .stButton>button[kind="primary"] {{ background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important; border: none !important; color: white !important; box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4) !important; }}
        
        /* Inputs */
        .stTextInput>div>div, .stSelectbox>div>div, .stTextArea>div>div, .stNumberInput>div>div {{ 
            border-radius: 12px !important; background-color: {SIDEBAR_BG} !important; border: 1px solid {BORDER_COLOR} !important; color: {TEXT_COLOR} !important; 
        }}
        
        /* Tabs Styling (Cleaner) */
        .stTabs [data-baseweb="tab-list"] {{ gap: 15px !important; background: transparent !important; }}
        .stTabs [data-baseweb="tab"] {{ background-color: transparent !important; border: none !important; color: {TEXT_COLOR} !important; opacity: 0.6; font-family: 'Outfit', sans-serif !important; font-weight: 600 !important; padding-bottom: 10px !important; }}
        .stTabs [aria-selected="true"] {{ opacity: 1 !important; border-bottom: 2px solid #38BDF8 !important; color: #38BDF8 !important; }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# DATENBANK & HILFSFUNKTIONEN
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
    cursor.close(); conn.close()
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
        ON CONFLICT (username, data_type) DO UPDATE SET json_content = EXCLUDED.json_content
    """, (username, data_type, json_string))
    cursor.close(); conn.close()

def send_discord_webhook(url, text_content=None, embed_data=None):
    payload = {}
    full_text_check = f"{text_content or ''} "
    if embed_data: full_text_check += f"{embed_data.get('title', '')} {embed_data.get('description', '')}"
    has_media_link = any(x in full_text_check for x in ["youtube.com/", "youtu.be/", "x.com/", "twitter.com/"])
    if has_media_link and embed_data:
        text_pieces = [text_content.strip()] if text_content else []
        if embed_data.get("title"): text_pieces.append(f"**{embed_data['title'].strip()}**")
        if embed_data.get("description"): text_pieces.append(embed_data["description"].strip())
        payload["content"] = "\n\n".join(text_pieces)
    else:
        if text_content: payload["content"] = text_content
        if embed_data: payload["embeds"] = [embed_data]
    try:
        response = requests.post(url, json=payload)
        if response.status_code in [200, 204]: return True, "🚀 Erfolgreich an Discord gesendet!"
        return False, f"Discord-Fehler: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Verbindungsfehler: {str(e)}"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("🔒 Bitte logge dich über die Hauptseite ein!")
        st.stop()
    # HIER WAR DER FEHLER: Das "utils." davor wurde entfernt.
    apply_modern_css() 
    return st.session_state["username"]

def save_api_credentials(username, platform, channel_id, api_key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO api_credentials (username, platform, channel_id, api_key)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username, platform) DO UPDATE SET channel_id = EXCLUDED.channel_id, api_key = EXCLUDED.api_key
    """, (username, platform, channel_id, api_key))
    cursor.close(); conn.close()

def load_api_credentials(username, platform):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, api_key FROM api_credentials WHERE username = %s AND platform = %s", (username, platform))
    row = cursor.fetchone()
    cursor.close(); conn.close()
    return row