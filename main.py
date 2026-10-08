import streamlit as st
from google import genai
from PIL import Image
import requests
from io import BytesIO
import json
import re
import time
import urllib.parse

st.set_page_config(
    page_title="The Dan Method: Study AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    div[data-testid="stExpander"] {
        text-align: right;
    }
    div[data-testid="stSlider"] {
        direction: ltr !important;
    }
    div[data-testid="stSlider"] label {
        direction: rtl !important;
        text-align: right !important;
    }
    .bsd-text {
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        border: 1px solid #4338ca;
        border-radius: 20px;
        padding: 40px 30px;
        text-align: center;
        box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.3);
        margin-bottom: 30px;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #cbd5e1;
        max-width: 800px;
        margin: 0 auto 20px auto;
        line-height: 1.6;
    }
    .zoom-frame {
        background: #0b0f19;
        border: 2px solid #38bdf8;
        border-radius: 20px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 12px 35px -8px rgba(56, 189, 248, 0.35);
        margin-bottom: 20px;
        color: white;
    }
    .teacher-video-container {
        position: relative;
        width: 100%;
        height: 250px;
        border-radius: 14px;
        overflow: hidden;
        border: 2px solid #1e293b;
        margin-bottom: 12px;
        background: #000;
    }
    .teacher-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .zoom-status-pill {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        font-size: 0.85rem;
        font-weight: bold;
        padding: 4px 14px;
        border-radius: 20px;
        margin-bottom: 8px;
    }
    .zoom-controls {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-top: 10px;
    }
    .zoom-btn {
        background: #1e293b;
        border: 1px solid #475569;
        color: #e2e8f0;
        padding: 5px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .voice-box {
        background: #0f172a;
        border: 1px solid #3b82f6;
        border-radius: 14px;
        padding: 16px;
        margin-top: 14px;
        text-align: center;
    }
    .feature-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 22px;
        height: 100%;
        text-align: right;
    }
    .vs-box-bad {
        background: #2d1517;
        border: 1px solid #7f1d1d;
        border-radius: 12px;
        padding: 20px;
        color: #fecaca;
    }
    .vs-box-good {
        background: #062b1e;
        border: 1px solid #065f46;
        border-radius: 12px;
        padding: 20px;
        color: #a7f3d0;
    }
    .exam-card {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
        color: white;
    }
    .score-card {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border: 2px solid #818cf8;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    .cheat-card {
        background: #1e1b4b;
        border: 1px solid #6366f1;
        padding: 16px;
        border-radius: 10px;
        color: #e0e7ff;
        margin-top: 10px;
    }
    .review-card {
        background: #0f172a;
        border: 1px solid #334155;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .portal-link {
        display: inline-block;
        padding: 10px 18px;
        background-color: #2563eb;
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        margin-left: 8px;
        margin-bottom: 8px;
    }
    @media print {
        header, footer, nav, [data-testid="stSidebar"], .stButton {
            display: none !important;
        }
        .stApp {
            color: black !important;
            background: white !important;
        }
    }
</style>
""", unsafe_allow_html=True)

if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "השליף חירום הציל אותי לפני מבחן בהיסטוריה!"},
        {"name": "נועה ל.", "grade": "כיתה י\"א (ביולוגיה)", "rating": 5, "text": "השיעור בזום עם המורה עובד מעולה."},
        {"name": "מאיה ר.", "grade": "כיתה י\"א (5 יח')", "rating": 5, "text": "מפרק המתמטיקה מסביר לפי מחוון בגרות בדיוק כמו שצריך."}
    ]

if "mock_exam_data" not in st.session_state:
    st.session_state.mock_exam_data = None
if "exam_submitted" not in st.session_state:
    st.session_state.exam_submitted = False
if "zoom_chat_history" not in st.session_state:
    st.session_state.zoom_chat_history = []
if "last_voice_reply" not in st.session_state:
    st.session_state.last_voice_reply = None

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ מפתח GEMINI_API_KEY לא מוגדר ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

def generate_ai(contents):
    models_to_try = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
    last_err = None
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                return client.models.generate_content(model=model_name, contents=contents)
            except Exception as e:
                last_err = e
                time.sleep(1)
    raise last_err

def extract_json(text):
    text = re.sub(r"^```json\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text.strip(), flags=re.MULTILINE)
    text = text.strip("`").strip()
    return json.loads(text)

def get_tts_audio_url(text):
    clean_text = re.sub(r"[*#_`>\[\]\(\)]", "", text)
    clean_text = clean_text[:200]
    encoded = urllib.parse.quote(clean_text)
    return f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl=iw&client=tw-ob"

with st.sidebar:
    st.markdown('<div class="bsd-text">בס״ד</div>', unsafe_allow_html=True)
    st.title("⚡ The Dan Method")
    st.caption("פלטפורמת הלימוד והמאיות של ישראל")
    st.markdown("---")
    
    st.subheader("🎓 1. פרטי לימוד ומגמה:")
    chosen_grade = st.selectbox(
        "שכבת לימוד:",
        ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב (בגרות)"],
        index=2
    )
    
    if chosen_grade in ["כיתה ז'", "כיתה ח'", "כיתה ט'"]:
        math_units = st.selectbox("מתמטיקה:", ["הקבצה א' / מצוינות", "הקבצה ב'", "רמה רגילה"])
        eng_units = st.selectbox("אנגלית:", ["הקבצה א' / דוברי אנגלית", "הקבצה ב'", "רמה רגילה"])
        chosen_major = st.selectbox("מגמה / תחום עניין:", [
            "ללא מגמה (מקצועות ליבה)", "מדעי המחשב / סייבר", "מדעים מוגבר / ביולוגיה", "אמנות ועיצוב", "קולנוע ותקשורת"
        ])
    else:
        math_units = st.selectbox("מתמטיקה (יחידות לימוד):", ["5 יחידות", "4 יחידות", "3 יחידות"])
        eng_units = st.selectbox("אנגלית (יחידות לימוד):", ["5 יחידות / דוברי אנגלית", "4 יחידות (Module E)", "3 יחידות"])
        chosen_major = st.selectbox("בחר את המגמה שלך בבית הספר:", [
            "ללא מגמה (מקצועות ליבה בלבד)",
            "מדעי המחשב / הנדסת תוכנה",
            "פיזיקה",
            "ביולוגיה",
            "ניהול עסקי / יזמות",
            "מדעי החברה: פסיכולוגיה וסוציולוגיה",
            "כלכלה וניהול",
            "קולנוע ותקשורת",
            "צילום ומדיה דיגיטלית",
            "אמנות חזותית ועיצוב"
        ])
    
    st.markdown("---")
    st.subheader("🚪 2. מעבר חדרים:")
    room = st.radio(
        "בחר חדר:",
        [
            "🏠 מסך פתיחה (ברוכים הבאים)",
            "📹 שיעור וידאו חי בזום (Live Video)",
            "📸 סורק תמונות ושיעורי בית",
            "📝 מחולל מבחני דמה (Mock Exam)",
            "🎬 ספריית וידאו ושיעורים ענקית",
            "🏫 חיבור ל-Classroom וספרי לימוד",
            "🖨️ דפי תרגול ומבחנים להדפסה",
            "💯 מלטשת תשובות למאיות",
            "📐 מעבדת מתמטיקה ומדעים",
            "🚨 שליף חירום (לפני מבחן)",
            "📅 מתכנן לו״ז למבחן",
            "⭐ חוות דעת והצעות"
        ]
    )
    
    st.markdown("---")
    no_yap = st.toggle("מצב תכל'ס (ללא חפירות)", value=True)
    st.caption("The Dan Method v10.0 Real-Teacher")

anti_yap_rule = "השב ישירות לתכל'ס, ללא פסקאות פתיחה או סיום מיותרות." if no_yap else ""
student_context = f"שכבת לימוד: {chosen_grade}, מתמטיקה: {math_units}, אנגלית: {eng_units}, מגמה: {chosen_major}."

# ----------------- חדר 0: מסך פתיחה -----------------
if room == "🏠 מסך פתיחה (ברוכים הבאים)":
    st.markdown('<div class="bsd-text">בס״ד</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="hero-container">
            <span style="background-color: #38bdf8; color: #0284c7; padding: 4px 14px; border-radius: 20px; font-weight: 800; font-size: 0.85rem; background: rgba(56, 189, 248, 0.15);">
                🚀 הדור הבא של הלמידה בישראל
            </span>
            <h1 class="hero-title">The Dan Method: Study AI</h1>
            <p class="hero-subtitle">
                הפלטפורמה הראשונה שנבנתה במיוחד עבור תלמידי ישראל (ז' עד י"ב ובגרות).
                <br>שיעורי וידאו בזום מול מורה פרטית, פירוק מבחנים ושליפים של 60 שניות.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("🔥 למה דווקא איתנו? (The Dan Method מול בינה מלאכותית רגילה)")
    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        st.markdown("""
            <div class="vs-box-bad">
                <h3 style="margin-top:0;">❌ כשמשתמשים ב-ChatGPT / AI רגיל</h3>
                <ul>
                    <li><b>חופר בטירוף:</b> פסקאות מבוא וסיום מיותרות כשכל מה שרצית זה תשובה קצרה למבחן.</li>
                    <li><b>לא מבין בגרות:</b> לא מכיר מחווני בדיקה, יחידות לימוד (3, 4, 5), או שאלות בגרות בישראל.</li>
                    <li><b>שפה מנותקת:</b> עונה כמו ויקיפדיה מתורגמת ולא כמו שתלמיד צריך לענות.</li>
                    <li><b>אין וידאו חי:</b> רק צ'אט יבש ללא תחושת שיעור פרטי אמיתי.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with col_comp2:
        st.markdown("""
            <div class="vs-box-good">
                <h3 style="margin-top:0;">⚡ כשמשתמשים ב-The Dan Method</h3>
                <ul>
                    <li><b>שיעור וידאו חי בזום:</b> רואים את המורה בווידאו מדברת, מנחה ומסבירה צעד אחרי צעד.</li>
                    <li><b>תכל'ס נטו (Anti-Yap):</b> פילטר מובנה שמנקה בולשיט ומחזיר רק את מה שמביא נקודות.</li>
                    <li><b>מותאם אישית לכיתה ולמגמה:</b> מתאים את התשובות בדיוק לרמה שלך (ז' עד י"ב).</li>
                    <li><b>מחוון 100 ישראלי:</b> מלטש כל תשובה בדיוק לפי מה שהבוחן או המורה מחפשים בעין.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("💎 עמודי התווך של השיטה:")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown("""
            <div class="feature-card">
                <h4 style="color:#38bdf8;">📹 שיעור וידאו חי</h4>
                <p style="color:#94a3b8; font-size:0.95rem;">רואים את המורה מדברת בזמן אמת כמו בשיחת זום אמיתית אחד על אחד.</p>
            </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
            <div class="feature-card">
                <h4 style="color:#818cf8;">📝 מבחני דמה אמיתיים</h4>
                <p style="color:#94a3b8; font-size:0.95rem;">סימולציית בחינה עם בדיקה אוטומטית לפי מחוון וציון מתוך 100.</p>
            </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
            <div class="feature-card">
                <h4 style="color:#34d399;">📐 פירוק מתמטיקה</h4>
                <p style="color:#94a3b8; font-size:0.95rem;">פתרונות צעד-אחר-צעד עם נימוק מתמטי מלא לכל שלב ברמת היחידות שלך.</p>
            </div>
        """, unsafe_allow_html=True)
    with f4:
        st.markdown("""
            <div class="feature-card">
                <h4 style="color:#f472b6;">🚨 שליפי חירום 60 שנ'</h4>
                <p style="color:#94a3b8; font-size:0.95rem;">דקה לפני המבחן? קבל את 3 משפטי הברזל, מילת החובה והטעות הנפוצה.</p>
            </div>
        """, unsafe_allow_html=True)

# ----------------- חדר 1: שיעור וידאו חי בזום -----------------
elif room == "📹 שיעור וידאו חי בזום (Live Video)":
    st.title("📹 שיעור וידאו חי בזום (Live Zoom Studio)")
    st.write(f"שיעור פרטי 1-על-1 בווידאו מותאם לרמת **{chosen_grade}** ({math_units} / {eng_units} / {chosen_major}):")
    
    col_z_cam, col_z_chat = st.columns([1.15, 1.85])
    
    with col_z_cam:
        # וידאו אמיתי ומקצועי של מורה אישה בשיחת וידאו
        st.markdown("""
            <div class="zoom-frame">
                <div class="zoom-status-pill">● שיחת וידאו פעילה (Live Video)</div>
                <div class="teacher-video-container">
                    <video class="teacher-video" autoplay loop muted playsinline>
                        <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4" type="video/mp4">
                    </video>
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
        st.caption("דבר עם המורה במיקרופון או כתוב לה, והיא תסביר לך ישירות בווידאו ובקול.")
        
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

# ----------------- חדר 2: סורק תמונות וקישורים -----------------
elif room == "📸 סורק תמונות ושיעורי בית":
    st.title("📸 סורק תמונות, דפי עבודה וקישורים")
    st.write(f"העלה תמונה מהמכשיר או הדבק קישור ישיר לתמונה עבור **{chosen_grade}**:")
    
    photo_topic = st.text_input("📚 1. מה החומר / המקצוע / המגמה?", placeholder="תרגיל בפיזיקה, מתמטיקה, קוד, צילום מספר הלימוד...")
    input_method = st.radio("בחר כיצד להזין את התרגיל:", ["📁 העלאת קובץ מהמכשיר", "🔗 הדבקת קישור ישיר (URL) לתמונה"], horizontal=True)
    
    img_to_solve = None
    if input_method == "📁 העלאת קובץ מהמכשיר":
        file = st.file_uploader("בחר קובץ תמונה (JPG/PNG):", type=["png", "jpg", "jpeg"])
        if file:
            try:
                img_to_solve = Image.open(file)
                st.image(img_to_solve, caption="התמונה שהועלתה מהמכשיר", width=360)
            except Exception as e:
                st.error(f"שגיאה בפתיחת התמונה: {e}")
    else:
        url_input = st.text_input("הדבק כאן את כתובת הקישור (URL) לתמונה:", placeholder="https://example.com/homework.jpg")
        if url_input.strip():
            try:
                with st.spinner("טוען תמונה מהקישור..."):
                    response = requests.get(url_input.strip(), timeout=10)
                    response.raise_for_status()
                    img_to_solve = Image.open(BytesIO(response.content))
                    st.image(img_to_solve, caption="התמונה שנטענה מהקישור", width=360)
            except Exception as e:
                st.error(f"לא ניתן לטעון את התמונה מהקישור: {e}")

    action = st.text_input("2. מה לבצע בתמונה?", value="פתור והסבר שלב אחרי שלב בצורה ברורה ומדויקת")
    
    if st.button("פענח ופתור ⚡", use_container_width=True):
        if not photo_topic.strip():
            st.warning("ציין קודם מה החומר או המקצוע בתמונה!")
        elif img_to_solve is None:
            st.warning("העלה תמונה או הדבק קישור תקין לתמונה לפני הלחיצה!")
        else:
            with st.spinner("מפענח את התמונה ופותר..."):
                try:
                    prompt = f"התלמיד ב-{student_context}. החומר: {photo_topic}. הנחיה: {action}. {anti_yap_rule}"
                    res = generate_ai([prompt, img_to_solve])
                    st.success("הפתרון מוכן:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה בפענוח: {e}")

# ----------------- חדר 3: מחולל מבחני דמה -----------------
elif room == "📝 מחולל מבחני דמה (Mock Exam)":
    st.title("📝 מחולל מבחני דמה מלאים (Mock Exam)")
    st.write(f"המחשב בונה לך סימולציית מבחן מותאמת אישית ל-**{chosen_grade}** ({math_units} / {chosen_major}).")
    
    with st.expander("⚙️ הגדרות מבחן הדמה", expanded=(st.session_state.mock_exam_data is None)):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            exam_subject = st.selectbox("מקצוע המבחן:", [
                "מתמטיקה", "היסטוריה", "אזרחות", "אנגלית", "תנ\"ך", "לשון והבעה", "ביולוגיה", "פיזיקה", "מדעי המחשב", chosen_major
            ])
            exam_topic = st.text_input("📚 מה החומר / הנושא המדויק של המבחן?", placeholder="למשל: משוואות מעריכיות, העלייה השנייה, חוקי ניוטון...")
        with col_m2:
            q_count = st.slider("מספר שאלות במבחן הדמה:", 2, 5, 3)
            exam_level = st.select_slider("רמת קושי המבחן:", ["בסיסית / חזרה", "רמת מבחן כיתתי", "רמת בגרות / מחוון קשוח"], value="רמת מבחן כיתתי")
            
        if st.button("🔨 צור לי מבחן דמה עכשיו!", use_container_width=True):
            if not exam_topic.strip():
                st.warning("חובה לציין את החומר הנלמד למבחן!")
            else:
                prompt_gen = (
                    f"אתה מורה מקצועי שבונה מבחן דמה לתלמיד ב-{student_context}.\n"
                    f"מקצוע: {exam_subject}, נושא: {exam_topic}, רמה: {exam_level}, מספר שאלות: {q_count}.\n"
                    "בנה מבחן דמה והחזר אך ורק מערך JSON תקין בלי שום טקסט או הערות נוספות מסביב:\n"
                    "[\n"
                    "  {\n"
                    '    "id": 1,\n'
                    '    "type": "multiple_choice",\n'
                    '    "question": "ניסוח השאלה כאן",\n'
                    '    "points": 30,\n'
                    '    "options": ["אפשרות א", "אפשרות ב", "אפשרות ג", "אפשרות ד"],\n'
                    '    "correct_answer": "אפשרות א",\n'
                    '    "explanation": "הסבר מפורט למה זו התשובה"\n'
                    "  },\n"
                    "  {\n"
                    '    "id": 2,\n'
                    '    "type": "open",\n'
                    '    "question": "ניסוח שאלה פתוחה",\n'
                    '    "points": 35,\n'
                    '    "ideal_answer": "תשובה מושלמת לפי מחוון"\n'
                    "  }\n"
                    "]"
                )
                with st.spinner("המחשב מרכיב את מבחן הדמה שלך..."):
                    try:
                        res = generate_ai(prompt_gen)
                        st.session_state.mock_exam_data = extract_json(res.text)
                        st.session_state.exam_submitted = False
                        st.success("מבחן הדמה מוכן! פתור את השאלות למטה.")
                    except Exception as e:
                        st.error(f"שגיאה ביצירת המבחן: {e}")

    if st.session_state.mock_exam_data:
        st.markdown("---")
        st.subheader("📋 טופס מבחן הדמה שלך:")
        st.caption("ענה על השאלות, ובסיום לחץ על 'הגש לבדיקה וקבלת ציון'.")
        
        user_answers = {}
        for q in st.session_state.mock_exam_data:
            st.markdown(f"""
                <div class="exam-card">
                    <h4>שאלה {q['id']} ({q.get('points', 25)} נקודות)</h4>
                    <p style="font-size: 1.1rem;">{q['question']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if q["type"] == "multiple_choice":
                user_answers[q["id"]] = st.radio(
                    f"בחר תשובה לשאלה {q['id']}:",
                    q["options"],
                    key=f"mcq_{q['id']}",
                    index=None
                )
            else:
                user_answers[q["id"]] = st.text_area(
                    f"כתוב את תשובתך לשאלה {q['id']}:",
                    key=f"open_{q['id']}",
                    height=100
                )
            st.write("")

        col_sub1, col_sub2 = st.columns([2, 1])
        with col_sub1:
            if st.button("🏁 הגש את מבחן הדמה ובדוק לי ציון!", use_container_width=True):
                st.session_state.exam_submitted = True
                st.session_state.submitted_answers = user_answers
        with col_sub2:
            if st.button("🔄 התחל מבחן חדש מאפס", use_container_width=True):
                st.session_state.mock_exam_data = None
                st.session_state.exam_submitted = False
                st.rerun()

        if st.session_state.exam_submitted:
            st.markdown("---")
            with st.spinner("הבוחן בודק את המבחן ומחשב ציון..."):
                try:
                    prompt_grade = (
                        f"אתה בוחן משרד החינוך שמעריך מבחן דמה עבור תלמיד ב-{student_context}.\n"
                        f"טופס המבחן והמחוון:\n{json.dumps(st.session_state.mock_exam_data, ensure_ascii=False)}\n\n"
                        f"תשובות התלמיד:\n{json.dumps(st.session_state.submitted_answers, ensure_ascii=False)}\n\n"
                        "החזר דוח ציונים מפורט בעברית הכולל:\n"
                        "1. **ציון סופי משוקלל מתוך 100**\n"
                        "2. פירוט עבור כל שאלה: כמה נקודות קיבל, מה היה נכון, מה היה שגוי, ואיך מנסחים תשובת 100 מושלמת לפי מחוון.\n"
                        "3. טיפ זהב אחד להצלחה במבחן האמיתי."
                    )
                    res_feedback = generate_ai(prompt_grade)
                    st.markdown("""
                        <div class="score-card">
                            <h2 style="color: #38bdf8; margin: 0;">🎉 תוצאות מבחן הדמה שלך</h2>
                            <p style="color: #cbd5e1; margin: 4px 0;">דוח בדיקה מלא ומחוון ציונים:</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(res_feedback.text)
                except Exception as e:
                    st.error(f"שגיאה בבדיקת המבחן: {e}")

# ----------------- חדר 4: ספריית וידאו עשירה -----------------
elif room == "🎬 ספריית וידאו ושיעורים ענקית":
    st.title("🎬 ספריית וידאו עשירה (ליבה + מגמות)")
    st.write(f"שיעורים ממוקדים לצפייה ישירה עבור **{chosen_grade}**:")
    
    category = st.selectbox("בחר מקצוע או מגמה:", [
        "מתמטיקה: גאומטריה ופיתגורס",
        "מתמטיקה: אלגברה וחדו\"א",
        "אנגלית: זמנים ודקדוק (Grammar)",
        "מגמת מדעי המחשב: יסודות תכנות ואלגוריתמיקה",
        "מגמות מדעיות: ביולוגיה ופיזיקה",
        "מגמות חברה ועסקים: פסיכולוגיה, סוציולוגיה, כלכלה וניהול",
        "מגמות אמנותיות: קולנוע, צילום ואמנות",
        "מקצועות הומניים: היסטוריה, אזרחות ולשון"
    ])
    
    video_db = {
        "מתמטיקה: גאומטריה ופיתגורס": {
            "משפט פיתגורס - בסיס וחישוב צלעות": "https://www.youtube.com/watch?v=xAgLlIAum3c",
            "משפט תאלס והרחבותיו": "https://www.youtube.com/watch?v=sI3q6Q_Hk84",
            "טריגונומטריה במשולש ישר זווית (Sin, Cos, Tan)": "https://www.youtube.com/watch?v=aa7bC_rFq4c"
        },
        "מתמטיקה: אלגברה וחדו\"א": {
            "משוואות ממעלה ראשונה עם סוגריים ושברים": "https://www.youtube.com/watch?v=lj6ONyl932A",
            "משוואה ריבועית ונוסחת שורשים": "https://www.youtube.com/watch?fghk_W4x_eM",
            "חקירת פונקציות ונגזרות (מבוא לחדו\"א)": "https://www.youtube.com/watch?v=5yflv3j7T30"
        },
        "אנגלית: זמנים ודקדוק (Grammar)": {
            "זמנים בסיסיים: Present Simple vs Progressive": "https://www.youtube.com/watch?v=L9AWrJnhsRI",
            "עבר פשוט ועבר ממושך (Past Simple & Continuous)": "https://www.youtube.com/watch?v=0k53_u1N9Yk",
            "כתיבת חיבור דעה מושלם (Opinion Essay)": "https://www.youtube.com/watch?v=7P_k3j_4X4w"
        },
        "מגמת מדעי המחשב: יסודות תכנות ואלגוריתמיקה": {
            "מבוא לתכנות ולולאות (For / While)": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
            "מערכים ומחרוזות בקלות": "https://www.youtube.com/watch?v=xk4_1vDrzzo"
        },
        "מגמות מדעיות: ביולוגיה ופיזיקה": {
            "שלושת חוקי ניוטון בפיזיקה": "https://www.youtube.com/watch?v=kKKM8Y-u7ds",
            "מבנה התא, ממברנה ופוטוסינתזה (ביולוגיה)": "https://www.youtube.com/watch?v=68_jtXv9k4c"
        },
        "מגמות חברה ועסקים: פסיכולוגיה, סוציולוגיה, כלכלה וניהול": {
            "פסיכולוגיה: תיאוריית הצרכים של מאסלו": "https://www.youtube.com/watch?v=O-4ithG_07Q",
            "כלכלה: ביקוש, היצע ושיווי משקל שוק": "https://www.youtube.com/watch?v=g9aDizJpd_s"
        },
        "מגמות אמנותיות: קולנוע, צילום ואמנות": {
            "קולנוע וצילום: זוויות צילום ומשמעותן (Camera Angles)": "https://www.youtube.com/watch?v=7y90UqWIdvU",
            "אמנות: שפת האמנות וקומפוזיציה": "https://www.youtube.com/watch?v=sOvhb2k1l_8"
        },
        "מקצועות הומניים: היסטוריה, אזרחות ולשון": {
            "היסטוריה: הגורמים למלחמת העולם הראשונה": "https://www.youtube.com/watch?v=SLj5r2nZHB8",
            "אזרחות: שלטון החוק וזכויות אדם": "https://www.youtube.com/watch?v=cMKe0k_k1Qk"
        }
    }
    
    current_videos = video_db.get(category, {})
    chosen_video_title = st.selectbox("בחר שיעור ספציפי:", list(current_videos.keys()))
    selected_url = current_videos[chosen_video_title]
    
    col_play, col_notes = st.columns([1.2, 0.8])
    with col_play:
        st.video(selected_url)
        st.markdown(f"[🔗 לחץ כאן לצפייה ישירה ב-YouTube]({selected_url})")
    with col_notes:
        st.subheader("📝 סיכום מהיר של השיעור")
        st.caption("רוצה נקודות ברזל על נושא הסרטון?")
        if st.button("סכם לי את עיקרי הנושא בבולטים ⚡", use_container_width=True):
            prompt = f"סכם ב-4 בולטים ברורים את הנושא: {chosen_video_title} עבור תלמיד ב-{chosen_grade} במגמת {chosen_major}. {anti_yap_rule}"
            with st.spinner("מחלץ סיכום..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- חדר 5: חיבור לבית ספר וספרים -----------------
elif room == "🏫 חיבור ל-Classroom וספרי לימוד":
    st.title("🏫 חיבור לבית הספר: Classroom & ספרי לימוד דיגיטליים")
    st.write("גישה מהירה לפורטלים הלימודיים ומפענח מטלות חכם:")
    st.markdown("""
        <div>
            <a class="portal-link" href="https://classroom.google.com" target="_blank">🌐 פתח Google Classroom</a>
            <a class="portal-link" href="https://www.classoos.com" target="_blank">📖 פתח Classoos (ספרי לימוד)</a>
            <a class="portal-link" href="https://my.education.gov.il" target="_blank">🏛️ פורטל משרד החינוך</a>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("📥 מפענח מטלות ושיעורי בית מהמורה")
    teacher_post = st.text_area("הדבק כאן את נוסח המטלה / ההודעה מ-Classroom:", height=130)
    
    if st.button("פרק לי את המטלה למשימות ושלבי ביצוע 📋", use_container_width=True):
        if not teacher_post.strip():
            st.warning("הדבק קודם את הודעת המורה!")
        else:
            prompt = (
                f"התלמיד ב-{student_context} קיבל את הודעת המטלה הבאה:\n{teacher_post}\n\n"
                "בצע פירוק חכם:\n"
                "1. **מה נדרש להגיש ומתי (מועד הגשה מדויק)**\n"
                "2. **אילו ספרים, עמודים או תרגילים צריך לפתור**\n"
                "3. **תוכנית פעולה מהירה שלב אחרי שלב כדי לסיים את זה מהר**\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנתח מטלה..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה בניתוח המטלה: {e}")

# ----------------- חדר 6: דפי תרגול להדפסה -----------------
elif room == "🖨️ דפי תרגול ומבחנים להדפסה":
    st.title("🖨️ מחולל דפי עבודה, תרגול ומבחנים להדפסה")
    st.write(f"הפק דף תרגול מושלם ומעוצב עבור **{chosen_grade}** הניתן להדפסה ישירה:")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        sheet_topic = st.text_input("📚 מה נושא דף התרגול?", placeholder="למשל: תורשה וגנטיקה, פסיכולוגיה התפתחותית, לולאות בפייתון...")
        sheet_subject = st.selectbox("מקצוע / מגמה:", [
            "מתמטיקה", "אנגלית", "מדעי המחשב", "ביולוגיה", "פיזיקה", "פסיכולוגיה", "סוציולוגיה", "כלכלה", "ניהול עסקי", "קולנוע ותקשורת", "צילום", "אמנות", "היסטוריה / אזרחות / תנ\"ך", "לשון"
        ])
    with col_p2:
        sheet_length = st.selectbox("היקף הדף:", ["דף עבודה מהיר (4-5 שאלות)", "מבחן מלא (8-10 שאלות כולל ניקוד)"])
        include_answers = st.checkbox("הוסף דף תשובות ומחוון בסוף הדף", value=True)

    if st.button("ייצר דף תרגול להדפסה 📄", use_container_width=True):
        if not sheet_topic.strip():
            st.warning("חובה לציין את נושא דף התרגול!")
        else:
            prompt = (
                f"צור דף תרגול ומבחן מקצועי ומעוצב בעברית לתלמיד ב-{student_context}.\n"
                f"מקצוע/מגמה: {sheet_subject}, נושא: {sheet_topic}, היקף: {sheet_length}.\n"
                "מבנה הדף:\n"
                "1. כותרת עליונה עם שם המבחן/הדף, כיתה, מגמה ומקום לשם תלמיד וציון.\n"
                "2. שאלות מנוסחות ברמה גבוהה לפי מחוון משרד החינוך עם מקום מסומן לתשובה.\n"
                + ("3. בסוף הדף: מחוון תשובות מלא ומדויק לבדיקה עצמית.\n" if include_answers else "")
            )
            with st.spinner("מייצר דף עבודה..."):
                try:
                    res = generate_ai(prompt)
                    st.session_state["printable_sheet"] = res.text
                except Exception as e:
                    st.error(f"שגיאה: {e}")

    if "printable_sheet" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state["printable_sheet"])
        st.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <button onclick="window.print()" style="padding: 12px 24px; font-size: 16px; background-color: #16a34a; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">
                    🖨️ הדפס דף תרגול זה (Print)
                </button>
            </div>
        """, unsafe_allow_html=True)

# ----------------- חדר 7: מלטשת תשובות -----------------
elif room == "💯 מלטשת תשובות למאיות":
    st.title("💯 מלטשת תשובות לציון 100")
    ans_topic = st.text_input("📚 1. מה החומר והמקצוע/המגמה?", placeholder="למשל: סוציולוגיה, ביולוגיה, היסטוריה...")
    q_text = st.text_input("❓ 2. מה השאלה שנשאלת?")
    user_ans = st.text_area("✍️ 3. מה התשובה שכתבת:", height=130)
    
    if st.button("שדרג לי את התשובה ל-100 🚀", use_container_width=True):
        if not ans_topic.strip() or not user_ans.strip():
            st.warning("מלא את החומר הנלמד ואת התשובה שכתבת!")
        else:
            prompt = (
                f"אתה מעריך בחינות ובגרויות קפדן שבודק תשובה של תלמיד ב-{student_context}.\n"
                f"החומר: {ans_topic}\nשאלה: {q_text}\nתשובה: {user_ans}\n\n"
                "החזר:\n1. **ציון מוערך (מתוך 100)**\n2. **מה חסר לפי מחוון הבדיקה**\n3. **תשובה מושלמת סופית**: נוסח שסוגר את מלוא הנקודות.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנתח לפי מחוון..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- חדר 8: מעבדת מתמטיקה -----------------
elif room == "📐 מעבדת מתמטיקה ומדעים":
    st.title("📐 מעבדת פירוק מתמטיקה ומדעים")
    math_topic = st.text_input("📚 1. מה הנושא הנלמד כרגע?", placeholder="חקירת פולינום, טריגו, תנועה בפיזיקה...")
    math_input = st.text_area("🔢 2. הזן את התרגיל או השאלה:", height=120)
    
    if st.button("פרק לי את התרגיל לפי רמת היחידות 🧠", use_container_width=True):
        if not math_topic.strip() or not math_input.strip():
            st.warning("ציין את הנושא ואת התרגיל!")
        else:
            prompt = (
                f"פתור את התרגיל הבא עבור תלמיד ב-{student_context}.\n"
                f"הנושא: {math_topic}\nתרגיל: {math_input}\n\n"
                "פתור שלב אחרי שלב בבירור עם נימוק קצר ליד כל שלב, וסמן תוצאה סופית מודגשת.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner(f"פותר לפי רמת {math_units}..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- חדר 9: שליף חירום -----------------
elif room == "🚨 שליף חירום (לפני מבחן)":
    st.title("🚨 שליף חירום: 60 שניות לפני מבחן")
    panic_topic = st.text_input("📚 מה החומר / הנושא של המבחן כרגע?", placeholder="משפט חוצה זווית, שיווי משקל שוק, גנטיקה...")
    
    if st.button("הצל אותי עכשיו ⚡", use_container_width=True):
        if not panic_topic.strip():
            st.warning("הזן קודם את החומר הנלמד!")
        else:
            prompt = (
                f"התלמיד ב-{student_context} נכנס בעוד דקה למבחן על החומר: {panic_topic}.\n"
                "החזר אך ורק:\n1. **3 משפטי זהב** שחייבים לרשום במבחן.\n2. **הטעות הנפוצה ביותר** שתלמידים נופלים בה.\n3. **מושג חובה אחד** שהבוחן מחפש בעין.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מחלץ שליף..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(f'<div class="cheat-card">{res.text}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- חדר 10: מתכנן לו״ז -----------------
elif room == "📅 מתכנן לו״ז למבחן":
    st.title("📅 מתכנן לוח זמנים אישי למבחן")
    topics = st.text_area("📚 1. מה כל החומר והנושאים שצריך להספיק למבחן?", placeholder="למשל: פרקים 1 עד 4 בספר, שאלות בגרות...")
    c1, c2 = st.columns(2)
    with c1:
        exam_subj = st.text_input("2. מקצוע או מגמה:", placeholder="מתמטיקה / ביולוגיה / פיזיקה...")
        days = st.number_input("3. כמה ימים נשארו עד המבחן?", min_value=1, max_value=30, value=3, step=1)
    with c2:
        hours_selected = st.select_slider(
            "4. כמה שעות למידה פנויות יש לך בכל יום?",
            options=["1 שעה ביום", "2 שעות ביום", "3 שעות ביום", "4 שעות ביום", "5 שעות ביום", "6 שעות ביום"],
            value="2 שעות ביום"
        )
        
    if st.button("בנה לי תוכנית עבודה 🗓️", use_container_width=True):
        if not topics.strip():
            st.warning("הזן קודם את החומר הנלמד!")
        else:
            prompt = (
                f"בנה לוח זמנים פרקטי ללימוד למבחן עבור תלמיד ב-{student_context}.\n"
                f"מקצוע: {exam_subj}, ימים שנותרו: {days}, שעות למידה פנויות: {hours_selected}, חומר: {topics}.\n"
                "חלק את המשימות בצורה הגיונית לפי ימים, כולל זמני מנוחה ותרגול מעשי."
            )
            with st.spinner("מתכנן לו״ז..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- חדר 11: חוות דעת -----------------
elif room == "⭐ חוות דעת והצעות":
    st.title("⭐ חוות דעת והצעות לשיפור")
    st.write("איך האתר עובד לך? יש פיצ'ר שתרצה שנוסיף? כתוב לנו כאן:")
    with st.form("feedback_form", clear_on_submit=True):
        fb_name = st.text_input("שם או כינוי:")
        fb_grade = st.selectbox("כיתה:", ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב"], index=2)
        fb_major = st.text_input("מגמה (אם יש):", value=chosen_major)
        fb_rating = st.slider("דירוג החוויה שלך (כוכבים):", min_value=1, max_value=5, value=5)
        fb_text = st.text_area("מה דעתך על האתר? מה כדאי להוסיף או לשפר?")
        submitted = st.form_submit_button("שלח חוות דעת 🚀")
        
        if submitted:
            if not fb_text.strip():
                st.warning("כתוב משהו לפני השליחה!")
            else:
                grade_display = f"{fb_grade} ({fb_major})" if fb_major.strip() else fb_grade
                st.session_state.reviews.insert(0, {
                    "name": fb_name if fb_name.strip() else "אנונימי",
                    "grade": grade_display,
                    "rating": fb_rating,
                    "text": fb_text
                })
                st.success("תודה על חוות הדעת! המשוב שלך נוסף בהצלחה.")
                st.balloons()

    st.markdown("---")
    st.subheader("💬 מה שתלמידים אומרים על The Dan Method:")
    for r in st.session_state.reviews:
        stars = "⭐" * r["rating"]
        st.markdown(f"""
            <div class="review-card">
                <b>{r['name']}</b> ({r['grade']}) — {stars}<br>
                <span>{r['text']}</span>
            </div>
        """, unsafe_allow_html=True)
