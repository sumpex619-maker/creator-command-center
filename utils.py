import streamlit as st
import json
import os
import hashlib
import requests

# ==============================================================================
# GLOBALE KONFIGURATION & FARBEN
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
# SICHERHEITS-CHECK FÜR UNTERSEITEN
# ==============================================================================
def check_login():
    """Prüft, ob der Nutzer eingeloggt ist. Verhindert direkten Zugriff auf Unterseiten."""
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("🔒 Bitte logge dich über die Hauptseite ein!")
        st.stop()
    return st.session_state["username"]

def get_user_filepath(username, file_type):
    """Generiert einheitlich die Dateipfade für den eingeloggten Nutzer."""
    user_prefix = username.replace(" ", "_").lower()
    return f"data_{user_prefix}_{file_type}.json"