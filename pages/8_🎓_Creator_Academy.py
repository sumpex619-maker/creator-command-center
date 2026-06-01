import streamlit as st
import utils

current_user = utils.check_login()

st.title("🎓 Creator Academy")
st.markdown("Dein Kompendium. Lerne die Tools kennen, die große Streamer nutzen.")
st.markdown("---")

# Neuer Tab "OBS & Software Guide" wurde hinzugefügt
t_bots, t_alerts, t_software, t_guide = st.tabs(["🤖 Chat-Bots", "🔔 Alerts & Overlays", "🎥 OBS & Software Guide", "📖 Streamer Basic Guide"])

with t_bots:
    st.subheader("Welcher Chat-Bot passt zu mir?")
    st.markdown("Ein Bot moderiert deinen Chat, wenn du spielst, und antwortet auf Befehle.")
    
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        with st.container(border=True):
            st.markdown("#### Nightbot")
            st.write("Der Klassiker. Perfekt für Anfänger auf Twitch und YouTube. Sehr einfaches Interface.")
            st.markdown("[Zu Nightbot](https://nightbot.tv)")
    with c2:
        with st.container(border=True):
            st.markdown("#### StreamElements")
            st.write("Die All-in-One Lösung. Bot, Spenden-Seite und Alerts in einem. Extrem mächtig.")
            st.markdown("[Zu StreamElements](https://streamelements.com)")
    with c3:
        with st.container(border=True):
            st.markdown("#### Botrix")
            st.write("Pflichtprogramm für Kick und TikTok! Wer auf den neuen Plattformen streamt, kommt an Botrix kaum vorbei.")
            st.markdown("[Zu Botrix](https://botrix.live)")

with t_alerts:
    st.subheader("Woher bekomme ich Grafiken?")
    st.info("Alerts bindest du über eine 'Browserquelle' (Browser Source) in OBS oder Streamlabs ein.")
    
    with st.expander("Tipp 1: StreamElements (Kostenlos)"):
        st.write("Bietet extrem viele kostenlose, animierte Vorlagen. Du musst nur deinen Kanal verknüpfen, ein Theme auswählen und den Link in dein OBS kopieren.")
    with st.expander("Tipp 2: Own3d.tv (Kostenpflichtig / Premium)"):
        st.write("Wenn du professionelle, aufwendige Grafiken suchst (z.B. spezielle Racing-Alerts), kannst du hier fertige Pakete kaufen. Sehr hochwertig!")

# ==============================================================================
# NEUER BEREICH: OBS & SOFTWARE GUIDE
# ==============================================================================
with t_software:
    st.subheader("Streaming Software: Einrichtung & Guides")
    st.markdown("Die richtige Software und die passenden Einstellungen sind das Fundament deines Streams.")
    
    c_obs, c_slobs = st.columns(2, gap="large")
    
    with c_obs:
        with st.container(border=True):
            st.markdown("#### 🎬 OBS Studio")
            st.write("Der Branchen-Standard. Komplett kostenlos, ressourcenschonend und durch Plugins unendlich erweiterbar.")
            
            # HIER DEN GEWÜNSCHTEN YOUTUBE-LINK FÜR OBS EINTRAGEN
            st.video("https://www.youtube.com/watch?v=1v1_yB6-0sY") 
            st.caption("Einrichtungsguide für OBS Studio")

    with c_slobs:
        with st.container(border=True):
            st.markdown("#### 💧 Streamlabs Desktop")
            st.write("Basiert auf OBS, hat aber Alerts, Chat und Themes direkt integriert. Sehr anfängerfreundlich, braucht aber mehr PC-Leistung.")
            
            # HIER DEN GEWÜNSCHTEN YOUTUBE-LINK FÜR STREAMLABS EINTRAGEN
            st.video("https://www.youtube.com/watch?v=JmCee4yXzZg")
            st.caption("Einrichtungsguide für Streamlabs Desktop")
            
    st.markdown("### ⚙️ Die wichtigsten Basis-Einstellungen (Standard 2026)")
    with st.container(border=True):
        st.markdown("""
        Egal welche Software du nutzt, diese Werte solltest du in den **Ausgabe-Einstellungen** kontrollieren:
        
        * **Video-Bitrate (Twitch):** Für 1080p bei 60fps solltest du **6000 kbps (CBR)** einstellen. (Twitch-Limit)
        * **Video-Bitrate (YouTube):** Hier kannst du wesentlich höher gehen. **10.000 bis 18.000 kbps** sorgen für ein extrem scharfes Bild, sofern deine Internetleitung das mitmacht.
        * **Encoder:** Wähle **immer** den Hardware-Encoder deiner Grafikkarte aus (NVIDIA NVENC H.264 / AV1 oder AMD HW H.264). Das entlastet deinen Hauptprozessor (CPU) massiv.
        * **Keyframe-Intervall:** Fest auf **2 Sekunden** einstellen.
        * **Audio-Abtastrate:** Unter den Audio-Einstellungen fest auf **48 kHz (Stereo)** stellen.
        """)

with t_guide:
    st.subheader("1x1 für neue Streamer")
    with st.container(border=True):
        st.markdown("""
        1. **Audio ist wichtiger als Video!** Ein ruckelfreies Bild mit schlechtem, rauschendem Mikrofon wird schneller weggeschaltet als eine mittelmäßige Webcam mit brillantem Ton.
        2. **Konstanz schlägt Motivation.** Streame lieber 2x die Woche fest (und trage das im Sendeplan ein), als eine Woche jeden Tag und dann einen Monat gar nicht.
        3. **Call to Action.** Erinnere deine Zuschauer aktiv daran, dir auf Instagram oder Discord zu folgen (Nutze dafür die Alerts oder Bot-Timer!).
        4. **Sprich mit dir selbst.** Auch wenn 0 Zuschauer im Stream sind: Kommentiere dein Gameplay laut. Zuschauer entscheiden in den ersten 5 Sekunden, ob sie bleiben. Wenn du in dem Moment stumm bist, sind sie wieder weg.
        """)