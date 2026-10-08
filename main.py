# ----------------- חדר 1: שיעור וידאו חי בזום -----------------
elif room == "📹 שיעור וידאו חי בזום (Live Video)":
    st.title("📹 שיעור וידאו חי בזום (Live Zoom Studio)")
    st.write(f"שיעור פרטי 1-על-1 בווידאו חי מותאם לרמת **{chosen_grade}** ({math_units} / {eng_units} / {chosen_major}):")
    
    col_z_cam, col_z_chat = st.columns([1.15, 1.85])
    
    with col_z_cam:
        st.markdown("""
            <div class="zoom-frame">
                <div class="zoom-status-pill">● שיחת וידאו פעילה (Live Video)</div>
                <div class="teacher-video-container">
                    <iframe 
                        src="https://www.youtube.com/embed/jfKfPfyJRdk?autoplay=1&mute=1&controls=0&loop=1&playlist=jfKfPfyJRdk" 
                        style="width: 100%; height: 230px; border: none; border-radius: 12px; pointer-events: none;" 
                        allow="autoplay">
                    </iframe>
                </div>
                <h3 style="margin: 0; color: #38bdf8; font-weight: 800;">המורה מיה (Dan AI)</h3>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin: 4px 0;">מורה פרטית אישית בווידאו</p>
                <div class="zoom-controls">
                    <span class="zoom-btn">🎙️ שמע פעיל</span>
                    <span class="zoom-btn">📹 מצלמה פועלת</span>
                    <span class="zoom-btn">🖥️ שיתוף מסך</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # השמעת הקול המסונכרן של המורה
        if st.session_state.last_voice_reply:
            st.markdown("**🔊 קול המורה מיה (האזן להסבר):**")
            audio_url = get_tts_audio_url(st.session_state.last_voice_reply)
            st.audio(audio_url, format="audio/mp3", autoplay=True)
        
        st.subheader("⚙️ הגדרות השיעור")
        z_subject = st.selectbox("בחר מקצוע לשיעור:", [
            "מתמטיקה", "אנגלית", chosen_major, "היסטוריה", "אזרחות", "תנ\"ך", "לשון והבעה", "ביולוגיה", "פיזיקה", "מדעי המחשב"
        ])
        z_goal = st.radio("מה מטרת השיעור עכשיו?", [
            "הסבר מאפס על נושא חדש שלא הבנתי בכיתה",
            "לפתור ביחד תרגיל או שיעורי בית שלב אחרי שלב",
            "הכנה דחופה לקראת מבחן או בוחן פתע"
        ])
        
        if st.button("🧹 התחל שיעור חדש / נקה לוח", use_container_width=True):
            st.session_state.zoom_chat_history = []
            st.session_state.last_voice_reply = None
            st.rerun()

    with col_z_chat:
        st.subheader(f"💬 שיחת הווידאו: {z_subject}")
        st.caption("דבר עם המורה במיקרופון או כתוב לה, והיא תדבר אליך ותסביר לך ישירות בווידאו.")
        
        # תיבת השיחה
        chat_box = st.container(height=360)
        with chat_box:
            if not st.session_state.zoom_chat_history:
                st.info(f"👋 **המורה מיה:** 'היי! אני איתך כאן בווידאו בשיעור {z_subject}. דבר איתי במיקרופון או כתוב לי מה לא ישב לך טוב בחומר, ונתחיל לפתור!'")
            else:
                for m in st.session_state.zoom_chat_history:
                    if m["role"] == "user":
                        with st.chat_message("user"):
                            st.write(m["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(m["content"])

        # אפשרות דיבור במיקרופון
        st.markdown('<div class="voice-box"><b>🎙️ דבר במיקרופון למורה בווידאו:</b>', unsafe_allow_html=True)
        audio_prompt = st.audio_input("לחץ על המיקרופון ודבר ישירות למורה:")
        st.markdown('</div>', unsafe_allow_html=True)

        if audio_prompt is not None:
            with st.spinner("המורה מיה מקשיבה ומכינה תשובה..."):
                try:
                    audio_bytes = audio_prompt.read()
                    prompt_audio = (
                        f"את המורה מיה, מורה פרטית ישראלית מקצועית, סבלנית וחמה בשיחת וידאו עם תלמיד ב-{student_context}.\n"
                        f"מקצוע: {z_subject}. מטרה: {z_goal}.\n"
                        "הקשיבי לשאלת התלמיד בהקלטה:\n"
                        "1. עני ישירות בקצרה ובפשטות בגובה העיניים (עד 3 משפטים ממוקדים).\n"
                        "2. סיימי בשאלה קצרה כדי לבדוק שהתלמיד הבין.\n"
                        f"{anti_yap_rule}"
                    )
                    res_voice = generate_ai([prompt_audio, {"mime_type": "audio/wav", "data": audio_bytes}])
                    reply_text = res_voice.text
                    
                    st.session_state.zoom_chat_history.append({"role": "user", "content": "🎙️ [שאלה קולית הושמעה בשיעור]"})
                    st.session_state.zoom_chat_history.append({"role": "assistant", "content": reply_text})
                    st.session_state.last_voice_reply = reply_text
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה בעיבוד הקול: {e}")

        # אפשרות כתיבה רגילה
        text_spoken = st.chat_input("או כתוב כאן למורה מיה...")
        if text_spoken:
            st.session_state.zoom_chat_history.append({"role": "user", "content": text_spoken})
            
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.zoom_chat_history[-6:]])
            zoom_prompt = (
                f"את המורה מיה, מורה פרטית ישראלית מקצועית, סבלנית וחמה בשיחת וידאו בזום עם תלמיד.\n"
                f"פרטי התלמיד: {student_context}.\n"
                f"מקצוע השיעור: {z_subject}. מטרת השיעור: {z_goal}.\n\n"
                "הנחיות שיחה חיה:\n"
                "1. דברי בלשון נקבה על עצמך ('אני איתך', 'בוא נראה', 'הסברתי').\n"
                "2. דברי בגובה העיניים, מעודד וקצר (2-3 משפטים ממוקדים בכל פעם).\n"
                "3. בסוף כל תשובה, שאלי שאלה קצרה כדי לוודא שהתלמיד עוקב אחרייך.\n"
                f"{anti_yap_rule}\n\n"
                f"היסטוריה:\n{history_text}\n\n"
                f"מה שהתלמיד אמר: {text_spoken}"
            )
            
            with st.spinner("המורה מיה עונה ומדברת בווידאו..."):
                try:
                    res_zoom = generate_ai(zoom_prompt)
                    st.session_state.zoom_chat_history.append({"role": "assistant", "content": res_zoom.text})
                    st.session_state.last_voice_reply = res_zoom.text
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה בתקשורת: {e}")
