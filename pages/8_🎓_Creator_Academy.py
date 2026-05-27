import streamlit as st
import utils

current_user = utils.check_login()
st.title("🎓 Creator Academy")
st.markdown("Dein Kompendium. Lerne die Tools kennen, die große Streamer nutzen.")
st.markdown("---")

t_bots, t_alerts, t_commands, t_guide = st.tabs(["🤖 Chat-Bots", "🔔 Alerts & Overlays", "💬 Chat-Befehle bauen", "📖 Streamer Basic Guide"])

with t_bots:
    st.markdown("### Welcher Chat-Bot passt zu mir?")
    st.markdown("Ein Bot moderiert deinen Chat, wenn du spielst, und antwortet auf Befehle.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="bento-card"><h4>Nightbot</h4><p>Der Klassiker. Perfekt für Anfänger auf Twitch und YouTube. Sehr einfaches Interface, aber weniger visuelle Funktionen.</p><a href="https://nightbot.tv" target="_blank">Zu Nightbot</a></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="bento-card"><h4>StreamElements</h4><p>Die All-in-One Lösung. Bot, Spenden-Seite und Alerts in einem. Erfordert etwas Einarbeitung, ist aber extrem mächtig.</p><a href="https://streamelements.com" target="_blank">Zu StreamElements</a></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="bento-card"><h4>Botrix</h4><p>Pflichtprogramm für Kick und TikTok! Wer auf den neuen Plattformen streamt, kommt an Botrix kaum vorbei.</p><a href="https://botrix.live" target="_blank">Zu Botrix</a></div>', unsafe_allow_html=True)

with t_alerts:
    st.markdown("### Woher bekomme ich Follow- & Sub-Benachrichtigungen?")
    st.info("Alerts bindest du über eine 'Browserquelle' (Browser Source) in OBS oder Streamlabs ein.")
    
    with st.expander("Tipp 1: StreamElements (Kostenlos)"):
        st.write("Bietet extrem viele kostenlose, animierte Vorlagen. Du musst nur deinen Kanal verknüpfen, ein Theme auswählen und den Link in dein OBS kopieren.")
    with st.expander("Tipp 2: Own3d.tv (Kostenpflichtig / Premium)"):
        st.write("Wenn du professionelle, aufwendige Grafiken suchst (z.B. spezielle Racing-Alerts), kannst du hier fertige Pakete kaufen. Sehr hochwertig!")

with t_commands:
    st.markdown("### Wie baue ich funktionierende Befehle (!commands)?")
    st.write("Um dir eigene Befehle (wie `!discord` oder `!setup`) zu speichern, kannst du links den Reiter **'💬 Chat Befehle'** nutzen. Das dient aber nur als Notizzettel! Um sie aktiv zu machen, musst du sie in deinem Bot eintragen.")
    
    st.markdown("#### Beispiel für StreamElements / Nightbot")
    st.code("!addcmd !discord Tritt meinem Community-Server bei: https://discord.gg/deinlink")
    st.markdown("- **!addcmd** = Sagt dem Bot, dass er einen neuen Befehl lernen soll.\n- **!discord** = Das ist das Wort, das der Zuschauer im Chat tippt.\n- **Der Rest** = Das ist die Antwort des Bots.")
    
with t_guide:
    st.markdown("### 1x1 für neue Streamer")
    st.markdown("""
    1. **Audio ist wichtiger als Video!** Ein ruckelfreies Bild mit schlechtem, rauschendem Mikrofon wird schneller weggeschaltet als eine mittelmäßige Webcam mit brillantem Ton.
    2. **Konstanz schlägt Motivation.** Streame lieber 2x die Woche fest (und trage das im Sendeplan ein), als eine Woche jeden Tag und dann einen Monat gar nicht.
    3. **Call to Action.** Erinnere deine Zuschauer aktiv daran, dir auf Instagram oder Discord zu folgen (Nutze dafür die Alerts oder Bot-Timer!).
    """)