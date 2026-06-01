import streamlit as st
import utils

current_user = utils.check_login()

# Lokale Variable für die Akzentfarbe der Inline-HTML-Hyperlinks generieren
PRIM = "#38BDF8" if st.session_state.get("theme", "Midnight (Dark)") == "Midnight (Dark)" else "#0284C7"

st.title("🎓 Creator Academy")
st.markdown("Dein Kompendium. Lerne die Tools kennen, die große Streamer nutzen.")
st.markdown("---")

t_bots, t_alerts, t_guide = st.tabs(["🤖 Chat-Bots", "🔔 Alerts & Overlays", "📖 Streamer Basic Guide"])

with t_bots:
    st.markdown("### Welcher Chat-Bot passt zu mir?")
    st.markdown("Ein Bot moderiert deinen Chat, wenn du spielst, und antwortet auf Befehle.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="bento-card"><h4>Nightbot</h4><p>Der Klassiker. Perfekt für Anfänger auf Twitch und YouTube. Sehr einfaches Interface.</p><a href="https://nightbot.tv" style="color:{PRIM}; target="_blank"">Zu Nightbot</a></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="bento-card"><h4>StreamElements</h4><p>Die All-in-One Lösung. Bot, Spenden-Seite und Alerts in einem. Extrem mächtig.</p><a href="https://streamelements.com" style="color:{PRIM}; target="_blank"">Zu StreamElements</a></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="bento-card"><h4>Botrix</h4><p>Pflichtprogramm für Kick und TikTok! Wer auf den neuen Plattformen streamt, kommt an Botrix kaum vorbei.</p><a href="https://botrix.live" style="color:{PRIM}; target="_blank"">Zu Botrix</a></div>', unsafe_allow_html=True)

with t_alerts:
    st.markdown("### Woher bekomme ich Grafiken?")
    st.info("Alerts bindest du über eine 'Browserquelle' (Browser Source) in OBS oder Streamlabs ein.")
    
    with st.expander("Tipp 1: StreamElements (Kostenlos)"):
        st.write("Bietet extrem viele kostenlose, animierte Vorlagen. Du musst nur deinen Kanal verknüpfen, ein Theme auswählen und den Link in dein OBS kopieren.")
    with st.expander("Tipp 2: Own3d.tv (Kostenpflichtig / Premium)"):
        st.write("Wenn du professionelle, aufwendige Grafiken suchst (z.B. spezielle Racing-Alerts), kannst du hier fertige Pakete kaufen. Sehr hochwertig!")

with t_guide:
    st.markdown("### 1x1 für neue Streamer")
    st.markdown("""
    1. **Audio ist wichtiger als Video!** Ein ruckelfreies Bild mit schlechtem, rauschendem Mikrofon wird schneller weggeschaltet als eine mittelmäßige Webcam mit brillantem Ton.
    2. **Konstanz schlägt Motivation.** Streame lieber 2x die Woche fest (und trage das im Sendeplan ein), als eine Woche jeden Tag und dann einen Monat gar nicht.
    3. **Call to Action.** Erinnere deine Zuschauer aktiv daran, dir auf Instagram oder Discord zu folgen (Nutze dafür die Alerts oder Bot-Timer!).
    """)