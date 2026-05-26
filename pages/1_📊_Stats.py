import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import utils

st.set_page_config(page_title="Stats & Posts - Command Center", layout="wide")
username = utils.check_login()

st.title("📊 Social Media Stats & Content-Bewerbung")

# Datenpfade für den Nutzer
stats_file = utils.get_user_filepath(username, "stats")
queue_file = utils.get_user_filepath(username, "social_posts_queue")
webhook_file = utils.get_user_filepath(username, "webhooks")

# Daten laden
stats_daten = utils.load_data(stats_file, list)
social_queue = utils.load_data(queue_file, list)
webhook_profile = utils.load_data(webhook_file, dict)

tab_tracker, tab_charts, tab_discord = st.tabs(["📝 Eingabe & Historie", "📈 Visuelle Auswertung", "📢 Content-Release bewerben"])

with tab_tracker:
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

    if st.button("Daten speichern", type="primary", key="save_stats"):
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
            utils.save_data(stats_file, stats_daten)
            st.success("✓ Daten erfolgreich gespeichert!")
            st.rerun()

    st.write("---")
    st.write("### 🗄️ Daten-Historie")
    if stats_daten: st.dataframe(stats_daten, use_container_width=True)

with tab_charts:
    st.subheader("📈 Performance Übersicht")
    if not stats_daten:
        st.info("Noch keine Daten für Diagramme vorhanden. Trage zuerst Statistiken ein!")
    else:
        df = pd.DataFrame(stats_daten)
        df["datum"] = pd.to_datetime(df["datum"])
        
        col_filter, _ = st.columns([1, 2])
        with col_filter:
            zeitraum = st.selectbox("📅 Zeitraum filtern:", ["Alle Daten", "Letzte 7 Tage", "Letzte 30 Tage", "Letzte 90 Tage"], index=0)
        
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
            fig_views = px.bar(views_df, x="plattform", y="views", color="plattform", color_discrete_map=utils.PLOT_COLORS, text_auto=True)
            fig_views.update_layout(xaxis_title="Plattform", yaxis_title="Gesamte Views", showlegend=False)
            st.plotly_chart(fig_views, use_container_width=True)
            
            st.write("---")

            st.markdown("### 🔥 Engagement-Rate im Verlauf")
            df_sorted = df.sort_values(by="datum")
            fig_eng = px.line(df_sorted, x="datum", y="engagement_rate_pct", color="plattform", color_discrete_map=utils.PLOT_COLORS, markers=True, hover_name="titel")
            fig_eng.update_layout(xaxis_title="Datum / Uhrzeit", yaxis_title="Engagement-Rate (%)")
            st.plotly_chart(fig_eng, use_container_width=True)

with tab_discord:
    st.subheader("📢 Content-Release bewerben")
    st.info("YouTube, X & Co. generieren in Discord automatisch ein Thumbnail, da wir die Links in den Ping-Text setzen.")
    
    col_queue_form, col_queue_view = st.columns([1, 1])
    with col_queue_form:
        p_plattform = st.selectbox("Plattform", ["Twitch", "YouTube", "Instagram", "TikTok", "Kick", "X"], key="q_plat")
        p_titel = st.text_input("Titel des Videos / Beitrags", key="q_tit")
        p_format = st.text_input("Format (z.B. Reel, Short)", key="q_form")
        p_link = st.text_input("Link zum Beitrag (Wichtig für Vorschau)", key="q_link")
        p_text = st.text_area("Beitragstext / Caption (Optional)", key="q_text")
        
        if st.button("➕ Beitrag in Warteschlange", type="secondary"):
            if not p_titel: st.error("Titel fehlt!")
            else:
                social_queue.append({
                    "id": str(datetime.now().timestamp()), "plattform": p_plattform, "titel": p_titel, 
                    "format": p_format if p_format else "Beitrag", "link": p_link, "text": p_text
                })
                utils.save_data(queue_file, social_queue)
                st.success("Zur Liste hinzugefügt!")
                st.rerun()
                
    with col_queue_view:
        if not social_queue: st.info("Keine unveröffentlichten Beiträge in der Liste.")
        else:
            for p in social_queue:
                cq1, cq2 = st.columns([5, 1])
                cq1.markdown(f"📱 **{p['plattform']}** ({p['format']}) — *{p['titel']}*")
                if cq2.button("🗑️", key=f"del_{p['id']}"):
                    social_queue = [item for item in social_queue if item["id"] != p["id"]]
                    utils.save_data(queue_file, social_queue)
                    st.rerun()

    st.write("---")
    if not webhook_profile:
        st.error("⚠️ Bitte lege zuerst ein Profil im Tab 'Webhook Verwaltung' an!")
    elif social_queue:
        selected_soc_prof = st.selectbox("Webhook-Profil nutzen:", list(webhook_profile.keys()))
        active_soc_profile = webhook_profile[selected_soc_prof]
        soc_ping_text = f"<@&{active_soc_profile['role_id']}> " if active_soc_profile["role_id"] and active_soc_profile["role_id"].lower() not in ["everyone", "here"] else (f"@{active_soc_profile['role_id']} " if active_soc_profile["role_id"] else "")
        soc_post_mode = st.radio("Sende-Format wählen:", ["Alle zusammen posten", "Nur einen Beitrag picken"], horizontal=True)
        
        if soc_post_mode == "Alle zusammen posten":
            default_bulk_desc = "Frischer Content auf meinen Kanälen:\n\n"
            bulk_links = []
            for p in social_queue: 
                default_bulk_desc += f"📱 **{p['plattform']} [{p['format']}]**\n📌 *{p['titel']}*\n"
                if p.get("text"): default_bulk_desc += f"💬 *{p['text']}*\n\n"
                else: default_bulk_desc += "\n"
                if p['link']: bulk_links.append(p['link'])
            
            default_ping = f"{soc_ping_text}🔥 CONTENT OUT NOW!\n\n" + "\n".join(bulk_links)
            edit_soc_ping = st.text_area("Ping & Links", value=default_ping, height=100)
            edit_soc_title = st.text_input("Embed-Titel", value="🎬 NEUE POSTS")
            edit_soc_desc = st.text_area("Embed-Beschreibung", value=default_bulk_desc, height=250)
            
            if st.button("📢 Bulk senden", type="primary"):
                success, msg = utils.send_discord_webhook(active_soc_profile["url"], text_content=edit_soc_ping, embed_data={"title": edit_soc_title, "description": edit_soc_desc, "color": utils.COLORS.get(active_soc_profile["plattform"], utils.COLORS["Allgemein"])})
                if success: st.success("Gesendet!")
                else: st.error(msg)

        elif soc_post_mode == "Nur einen Beitrag picken":
            post_options = {f"{p['plattform']} - {p['titel']}": p for p in social_queue}
            chosen_post_key = st.selectbox("Beitrag laden:", list(post_options.keys()))
            sel_p = post_options[chosen_post_key]
            
            default_single_desc = f"🔹 **Format:** {sel_p['format']}\n📌 **Thema:** {sel_p['titel']}"
            if sel_p.get("text"): default_single_desc += f"\n\n💬 **Infos:**\n{sel_p['text']}"
            default_ping = f"{soc_ping_text}Neues Video!\n{sel_p['link']}" if sel_p['link'] else f"{soc_ping_text}Neues Video!"
            
            edit_soc_ping = st.text_input("Ping & Link", value=default_ping)
            edit_soc_title = st.text_input("Embed-Titel", value=f"🎬 NEW UPLOAD: {sel_p['plattform'].upper()}")
            edit_soc_desc = st.text_area("Embed-Beschreibung", value=default_single_desc, height=200)
            
            if st.button("📢 Einzeln senden", type="primary"):
                embed_payload = {"title": edit_soc_title, "description": edit_soc_desc, "color": utils.COLORS.get(sel_p["plattform"], utils.COLORS["Allgemein"])}
                if sel_p['link']: embed_payload["url"] = sel_p['link']
                success, msg = utils.send_discord_webhook(active_soc_profile["url"], text_content=edit_soc_ping, embed_data=embed_payload)
                if success: st.success("Gesendet!")
                else: st.error(msg)