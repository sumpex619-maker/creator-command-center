import streamlit as st
import utils

current_user = utils.check_login()

st.title("🎓 Creator Academy")
st.markdown("Dein Kompendium. Lerne die Tools kennen, die große Streamer nutzen.")
st.markdown("---")

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
# BEREICH: STEP-BY-STEP SOFTWARE GUIDE
# ==============================================================================
with t_software:
    st.subheader("🛠️ Step-by-Step Einrichtungs-Guide")
    st.markdown("Wähle deine Software und folge der Anleitung Schritt für Schritt, um deinen Stream professionell aufzusetzen.")
    
    software_wahl = st.radio("Welche Software möchtest du einrichten?", ["🎬 OBS Studio (Empfohlen)", "💧 Streamlabs Desktop"], horizontal=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if software_wahl == "🎬 OBS Studio (Empfohlen)":
        with st.expander("Schritt 1: Download & Erste Schritte", expanded=True):
            st.markdown("""
            1. Gehe auf [obsproject.com](https://obsproject.com) und lade die Software herunter.
            2. Beim ersten Start öffnet sich der **Autokonfigurations-Assistent**.
            3. Wähle: **'Für das Streamen optimieren, Aufnehmen ist zweitrangig'**.
            4. Klicke dich durch, bis OBS die optimale Basis-Leistung deines PCs ermittelt hat.
            """)
            
        with st.expander("Schritt 2: Die richtigen Video- & Ausgabe-Einstellungen"):
            st.markdown("""
            Gehe unten rechts auf **Einstellungen** -> **Ausgabe**. Ändere den Ausgabemodus oben auf **Erweitert**.
            * **Encoder:** Wähle deinen Hardware-Encoder (z.B. `NVIDIA NVENC H.264` oder `AMD HW H.264`). Das entlastet deinen Prozessor massiv!
            * **Qualitätsregulierung:** Wähle `CBR` (Constant Bitrate).
            * **Bitrate (Twitch):** Maximal `6000 Kbps` (bei 1080p60fps).
            * **Bitrate (YouTube):** `10000 Kbps` bis `18000 Kbps` (für ein viel schärferes Bild).
            * **Keyframe-Intervall:** Fest auf `2` Sekunden eintragen.
            """)
            
        with st.expander("Schritt 3: Audio-Setup & Mikrofon-Filter"):
            st.markdown("""
            Guter Ton ist das Wichtigste! Gehe auf **Einstellungen** -> **Audio**.
            1. Setze **Desktop-Audio** auf deine Kopfhörer.
            2. Setze **Mikrofon/Auxiliar-Audio** auf dein Mikrofon.
            3. **Geheimtipp für klaren Sound:** Klicke im Audio-Mixer (Hauptfenster) auf die 3 Punkte neben deinem Mikrofon -> **Filter**. 
               Füge folgende Filter über das `+` hinzu:
               * **Rauschunterdrückung:** Entfernt PC-Lüfter-Geräusche (Wähle `RNNoise`).
               * **Kompressor:** Verhindert, dass du übersteuerst, wenn du mal lauter jubelst oder schreist.
            """)
            
        with st.expander("Schritt 4: Szenen & Quellen anlegen"):
            st.markdown("""
            Im Hauptfenster unten links findest du **Szenen** (Ordner) und **Quellen** (die Inhalte darin).
            1. Erstelle eine neue Szene und nenne sie z.B. "In-Game".
            2. Klicke bei den Quellen auf das `+`.
            3. Wähle **Spielaufnahme** (für Vollbildspiele) oder **Bildschirmaufnahme** (um den ganzen Desktop zu zeigen).
            4. Klicke nochmal auf `+` und wähle **Videoaufnahmegerät**, um deine Webcam hinzuzufügen.
            5. Ziehe die Webcam im Vorschaufenster einfach an die gewünschte Position und skaliere sie.
            """)
            
        with st.expander("Schritt 5: Konto verknüpfen & Go Live!"):
            st.markdown("""
            Fast geschafft! Gehe auf **Einstellungen** -> **Stream**.
            1. Wähle deine Plattform (z.B. Twitch oder YouTube).
            2. Klicke auf **Konto verbinden** (empfohlen) ODER trage deinen Stream-Schlüssel manuell ein.
            3. Speichere alles, klicke im Hauptfenster auf **Stream starten** und du bist live!
            """)

    else:
        with st.expander("Schritt 1: Download & Erste Schritte", expanded=True):
            st.markdown("""
            1. Lade Streamlabs Desktop von der offiziellen Seite herunter.
            2. Nach der Installation wirst du direkt aufgefordert, dich mit Twitch, YouTube oder Kick einzuloggen. Das spart dir später das Suchen nach dem Stream-Schlüssel!
            3. Der Assistent fragt dich, ob du Einstellungen aus OBS importieren möchtest oder frisch starten willst. Wähle "Frisch starten".
            """)
            
        with st.expander("Schritt 2: Ausgabe-Einstellungen optimieren"):
            st.markdown("""
            Gehe unten links auf das **Zahnrad (Einstellungen)** -> **Ausgabe**. Ändere den Modus auf **Erweitert**.
            * **Encoder:** Wähle zwingend `NVENC` (Nvidia) oder `AMD`, um über die Grafikkarte zu streamen und Lags zu vermeiden.
            * **Rate Control:** Wähle `CBR`.
            * **Bitrate:** Trage `6000` für Twitch ein (höher erlaubt Twitch oft nicht). Für YouTube kannst du problemlos `12000` eintragen.
            * **Keyframe-Intervall:** `2`.
            """)
            
        with st.expander("Schritt 3: Alerts und Chat integrieren (Der Streamlabs-Vorteil)"):
            st.markdown("""
            Da du Streamlabs nutzt, musst du keine komplizierten Browser-Quellen suchen.
            1. Gehe in deine Quellen (Sources) und klicke auf das `+`.
            2. Unter **Widgets** findest du direkt die **Alertbox** (für Follower, Subs etc.) und die **Chatbox**.
            3. Füge sie hinzu und positioniere sie in deinem Bild. Die Optik kannst du jederzeit über das Streamlabs Dashboard im Browser anpassen.
            """)
            
        with st.expander("Schritt 4: Mikrofon & Gameplay hinzufügen"):
            st.markdown("""
            1. Klicke bei den Quellen auf das `+`.
            2. Wähle **Bildschirmaufnahme** oder **Spielaufnahme** für dein Game.
            3. Wähle **Audioeingabe-Aufnahme**, um dein Mikrofon hinzuzufügen.
            4. Klicke im Audio-Mixer auf das Zahnrad neben deinem Mikrofon -> **Filter bearbeiten** und füge eine `Rauschunterdrückung` hinzu, damit man deine Tastatur nicht hört.
            """)
            
        with st.expander("Schritt 5: Go Live & Stream Info"):
            st.markdown("""
            1. Klicke unten rechts auf den großen, grünen **Go Live** Button.
            2. Es öffnet sich ein Fenster, in dem du direkt deinen Stream-Titel, die Kategorie (welches Spiel du spielst) und deine Tags eintragen kannst.
            3. Bestätigen und du bist auf Sendung!
            """)

# ==============================================================================
# BEREICH: BASIC GUIDE
# ==============================================================================
with t_guide:
    st.subheader("1x1 für neue Streamer")
    with st.container(border=True):
        st.markdown("""
        1. **Audio ist wichtiger als Video!** Ein ruckelfreies Bild mit schlechtem, rauschendem Mikrofon wird schneller weggeschaltet als eine mittelmäßige Webcam mit brillantem Ton.
        2. **Konstanz schlägt Motivation.** Streame lieber 2x die Woche fest (und trage das im Sendeplan ein), als eine Woche jeden Tag und dann einen Monat gar nicht.
        3. **Call to Action.** Erinnere deine Zuschauer aktiv daran, dir auf Instagram oder Discord zu folgen (Nutze dafür die Alerts oder Bot-Timer!).
        4. **Sprich mit dir selbst.** Auch wenn 0 Zuschauer im Stream sind: Kommentiere dein Gameplay laut. Zuschauer entscheiden in den ersten 5 Sekunden, ob sie bleiben. Wenn du in dem Moment stumm bist, sind sie wieder weg.
        """)