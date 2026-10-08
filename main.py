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
    page_title="The Dan Method",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב Dark Mode מודרני, נקי ויוקרתי (RTL)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;800;900&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Heebo', -apple-system, sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background-color: #0b0f17;
        color: #f1f5f9;
    }
    
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-left: 1px solid #1f2937;
    }
    
    div[data-testid="stSlider"] {
        direction: ltr !important;
    }
    div[data-testid="stSlider"] label {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .bsd-text {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .hero-card {
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 32px 28px;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        margin-bottom: 24px;
    }
    
    .hero-card h1 {
        font-size: 2.5rem;
        font-weight: 900;
        letter-spacing: -0.5px;
        color: #ffffff;
        margin-bottom: 8px;
    }
    
    .hero-card p {
        font-size: 1.15rem;
        color: #94a3b8;
        line-height: 1.6;
        margin: 0;
    }
    
    .feature-tile {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 20px;
        height: 100%;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .feature-tile:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }
    
    .feature-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 6px;
    }
    
    .feature-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.5;
        margin: 0;
    }
    
    .zoom-video-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
    }
    
    .video-viewport {
        width: 100%;
        height: 240px;
        border-radius: 12px;
        overflow: hidden;
        background: #000;
        margin-bottom: 12px;
        border: 1px solid #1f2937;
    }
    
    .video-viewport video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #34d399;
        font-size: 0.85rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 10px;
    }
    
    .cheat-box {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-radius: 14px;
        padding: 20px;
        color: #fbbf24;
        margin-top: 14px;
    }
    
    .portal-pill {
        display: inline-block;
        padding: 8px 16px;
        background: #1f2937;
        color: #e2e8f0 !important;
        border: 1px solid #374151;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 600;
        margin-left: 8px;
        margin-bottom: 8px;
        transition: all 0.15s ease;
    }
    .portal-pill:hover {
        background: #374151;
        color: #ffffff !important;
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
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "השליף חירום סגר לי את החומר לפני המבחן בהיסטוריה."},
        {"name": "נועה ל.", "grade": "כיתה י\"א (ביולוגיה)", "rating": 5, "text": "עיצוב טיל וסופר נוח לעבודה."},
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
    st.error("⚠️ מפתח GEMINI_API_KEY אינו מוגדר ב-Secrets של Streamlit.")
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
    st.title("The Dan Method ⚡")
    st.caption("פלטפורמת למידה ממוקדת מחוון")
    st.markdown("---")
    
    st.subheader("פרופיל תלמיד")
    chosen_grade = st.selectbox(
        "שכבת לימוד:",
        ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב (בגרות)"],
        index=2
    )
    
    if chosen_grade in ["כיתה ז'", "כיתה ח'", "כיתה ט'"]:
        math_units = st.selectbox("מתמטיקה:", ["הקבצה א' / מצוינות", "הקבצה ב'", "רמה רגילה"])
        eng_units = st.selectbox("אנגלית:", ["הקבצה א' / דוברי אנגלית", "הקבצה ב'", "רמה רגילה"])
        chosen_major = st.selectbox("מסלול:", [
            "ללא מגמה (מקצועות ליבה)", "מדעי המחשב / סייבר", "מדעים / ביולוגיה", "אמנות ועיצוב", "קולנוע ותקשורת"
        ])
    else:
        math_units = st.selectbox("מתמטיקה:", ["5 יחידות", "4 יחידות", "3 יחידות"])
        eng_units = st.selectbox("אנגלית:", ["5 יחידות / דוברי אנגלית", "4 יחידות (Module E)", "3 יחידות"])
        chosen_major = st.selectbox("מגמה בתיכון:", [
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
    st.subheader("ניווט")
    room = st.radio(
        "בחר כלי:",
        [
            "דף הבית",
            "שיעור וידאו פרטי (Zoom)",
            "סורק תרגילים ודפי עבודה",
            "מבחני דמה (Mock Exam)",
            "ספריית שיעורים מוקלטים",
            "חיבור ל-Classroom וספרים",
            "דפי תרגול להדפסה",
            "מלטשת תשובות למחוון 100",
            "פירוק מתמטיקה ומדעים",
            "שליף חירום למבחן",
            "מתכנן לוח זמנים",
            "משוב והצעות"
        ]
    )
    
    st.markdown("---")
    no_yap = st.toggle("מצב תכל'ס (מענה חד ולעניין)", value=True)

anti_yap_rule = "השב ישירות לתכל'ס, ללא פסקאות פתיחה או סיום מיותרות." if no_yap else ""
student_context = f"שכבת לימוד: {chosen_grade}, מתמטיקה: {math_units}, אנגלית: {eng_units}, מגמה: {chosen_major}."

# ----------------- 0. דף הבית -----------------
if room == "דף הבית":
    st.markdown('<div class="bsd-text">בס״ד</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="hero-card">
            <h1>The Dan Method ⚡</h1>
            <p>
                הסוף לחפירות ולסיכומים מייגעים. 
                פתרונות שלב אחרי שלב, התאמה מלאה לרמת הלימוד והיחידות שלך, ודיוק מושלם למחווני הבדיקה של משרד החינוך.
            </p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
            <div class="feature-tile">
                <div class="feature-title">📹 שיעור וידאו אישי</div>
                <p class="feature-desc">שיחה חיה עם המורה מיה להסבר ממוקד של כל סעיף או תרגיל.</p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class="feature-tile">
                <div class="feature-title">📝 מבחני דמה מדויקים</div>
                <p class="feature-desc">הערכה מלאה של רמת הידע עם בדיקה לפי מחוון, ניקוד ומשוב.</p>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
            <div class="feature-tile">
                <div class="feature-title">📐 פירוק מתמטיקה</div>
                <p class="feature-desc">הצגת כל שלבי החישוב עם נימוק מתמטי קצר ברמת היחידות שלך.</p>
            </div>
        """, unsafe_allow_html=True)

# ----------------- 1. שיעור וידאו פרטי -----------------
elif room == "שיעור וידאו פרטי (Zoom)":
    st.title("שיעור וידאו פרטי")
    st.caption(f"מותאם עבור {chosen_grade} | {math_units} | {chosen_major}")
    
    col_cam, col_conv = st.columns([1.15, 1.85])
    
    with col_cam:
        st.markdown("""
            <div class="zoom-video-card">
                <div class="status-badge">● שידור חי פעיל</div>
                <div class="video-viewport">
                    <video autoplay loop muted playsinline>
                        <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4" type="video/mp4">
                    </video>
                </div>
                <h3 style="margin: 0; color: #ffffff; font-size: 1.25rem; font-weight: 800;">המורה מיה</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin: 4px 0 0 0;">הוראה מותאמת אישית</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.last_voice_reply:
            st.markdown("<br><b>השמעת מענה קולי:</b>", unsafe_allow_html=True)
            audio_url = get_tts_audio_url(st.session_state.last_voice_reply)
            st.audio(audio_url, format="audio/mp3", autoplay=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        z_subject = st.selectbox("מקצוע השיעור:", [
            "מתמטיקה", "אנגלית", chosen_major, "היסטוריה", "אזרחות", "תנ\"ך", "לשון והבעה", "ביולוגיה", "פיזיקה", "מדעי המחשב"
        ])
        z_goal = st.radio("מטרת המפגש:", [
            "הסבר נושא חדש מהבסיס",
            "פתרון שיעורי בית יחד",
            "הכנה למבחן קרוב"
        ])
        
        if st.button("איפוס שיחה", use_container_width=True):
            st.session_state.zoom_chat_history = []
            st.session_state.last_voice_reply = None
            st.rerun()

    with col_conv:
        st.subheader(f"מהלך השיעור: {z_subject}")
        
        chat_box = st.container(height=360)
        with chat_box:
            if not st.session_state.zoom_chat_history:
                st.write(f"👋 **המורה מיה:** היי! אני כאן בשיעור {z_subject}. תגיד לי איזה נושא או תרגיל נרצה לפרק עכשיו?")
            else:
                for m in st.session_state.zoom_chat_history:
                    if m["role"] == "user":
                        with st.chat_message("user"):
                            st.write(m["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(m["content"])

        st.caption("דיבור במיקרופון:")
        audio_prompt = st.audio_input("הקלטה קולית:")

        if audio_prompt is not None:
            with st.spinner("מעבד הקלטה ומכין תשובה..."):
                try:
                    audio_bytes = audio_prompt.read()
                    prompt_audio = (
                        f"את המורה מיה, מורה פרטית ישראלית מקצועית וסבלנית בשיעור עם תלמיד ב-{student_context}.\n"
                        f"מקצוע: {z_subject}. מטרה: {z_goal}.\n"
                        "הקשיבי להקלטה:\n"
                        "1. עני ישירות בקצרה ובפשטות בגובה העיניים (עד 3 משפטים).\n"
                        "2. סיימי בשאלה קצרה כדי לוודא הבנה.\n"
                        f"{anti_yap_rule}"
                    )
                    res_voice = generate_ai([prompt_audio, {"mime_type": "audio/wav", "data": audio_bytes}])
                    reply_text = res_voice.text
                    
                    st.session_state.zoom_chat_history.append({"role": "user", "content": "🎙️ [שאלה קולית]"})
                    st.session_state.zoom_chat_history.append({"role": "assistant", "content": reply_text})
                    st.session_state.last_voice_reply = reply_text
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה: {e}")

        text_spoken = st.chat_input("או כתיבת שאלה כאן...")
        if text_spoken:
            st.session_state.zoom_chat_history.append({"role": "user", "content": text_spoken})
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.zoom_chat_history[-6:]])
            zoom_prompt = (
                f"את המורה מיה בשיעור עם תלמיד.\n"
                f"פרטי התלמיד: {student_context}.\n"
                f"מקצוע: {z_subject}. מטרה: {z_goal}.\n\n"
                "1. דברי בלשון נקבה על עצמך, טבעי ומעודד.\n"
                "2. עני בקצרה (2-3 משפטים) בלי לחפור.\n"
                "3. סיימי בשאלה קצרה לבדיקת הבנה.\n"
                f"{anti_yap_rule}\n\n"
                f"היסטוריה:\n{history_text}\n\nשאלה: {text_spoken}"
            )
            with st.spinner("מכינה מענה..."):
                try:
                    res_zoom = generate_ai(zoom_prompt)
                    st.session_state.zoom_chat_history.append({"role": "assistant", "content": res_zoom.text})
                    st.session_state.last_voice_reply = res_zoom.text
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 2. סורק תרגילים -----------------
elif room == "סורק תרגילים ודפי עבודה":
    st.title("סורק תרגילים ודפי עבודה")
    st.caption("העלאת תמונה ממחברת, ספר לימוד או קישור ישיר.")
    
    photo_topic = st.text_input("מה המקצוע או הנושא הנלמד?", placeholder="למשל: גיאומטריה, חוקי ניוטון, שאלות בגרות בתנ\"ך...")
    input_method = st.radio("מקור התמונה:", ["העלאת קובץ", "קישור (URL)"], horizontal=True)
    
    img_to_solve = None
    if input_method == "העלאת קובץ":
        file = st.file_uploader("בחר קובץ:", type=["png", "jpg", "jpeg"])
        if file:
            try:
                img_to_solve = Image.open(file)
                st.image(img_to_solve, caption="התמונה שנבחרה", width=360)
            except Exception as e:
                st.error(f"שגיאה בפתיחת קובץ: {e}")
    else:
        url_input = st.text_input("כתובת הקישור:", placeholder="https://example.com/homework.jpg")
        if url_input.strip():
            try:
                with st.spinner("טוען תמונה מהקישור..."):
                    response = requests.get(url_input.strip(), timeout=10)
                    response.raise_for_status()
                    img_to_solve = Image.open(BytesIO(response.content))
                    st.image(img_to_solve, caption="תמונה מקישור", width=360)
            except Exception as e:
                st.error(f"לא ניתן לטעון תמונה: {e}")

    action = st.text_input("הנחיה לביצוע:", value="פתור והסבר שלב אחרי שלב בצורה ברורה ומדויקת")
    
    if st.button("פענח ופתור", use_container_width=True):
        if not photo_topic.strip():
            st.warning("נא להזין מקצוע או נושא.")
        elif img_to_solve is None:
            st.warning("נא לספק תמונה תחילה.")
        else:
            with st.spinner("מנתח את התמונה ומחשב פתרון..."):
                try:
                    prompt = f"התלמיד ב-{student_context}. החומר: {photo_topic}. הנחיה: {action}. {anti_yap_rule}"
                    res = generate_ai([prompt, img_to_solve])
                    st.markdown("### פתרון:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 3. מבחני דמה -----------------
elif room == "מבחני דמה (Mock Exam)":
    st.title("מבחני דמה (Mock Exam)")
    st.caption("סימולציית בחינה אינטראקטיבית עם בדיקה אוטומטית לפי מחוון.")
    
    with st.expander("הגדרות מבחן", expanded=(st.session_state.mock_exam_data is None)):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            exam_subject = st.selectbox("מקצוע:", [
                "מתמטיקה", "היסטוריה", "אזרחות", "אנגלית", "תנ\"ך", "לשון והבעה", "ביולוגיה", "פיזיקה", "מדעי המחשב", chosen_major
            ])
            exam_topic = st.text_input("הנושא הנלמד למבחן:", placeholder="למשל: סדרות חשבוניות, העלייה השנייה, חוקי הגנטיקה...")
        with col_m2:
            q_count = st.slider("כמות שאלות:", 2, 5, 3)
            exam_level = st.select_slider("רמת קושי:", ["בסיסית", "רמת כיתה רגילה", "רמת בגרות מלאה"], value="רמת כיתה רגילה")
            
        if st.button("בנה מבחן דמה", use_container_width=True):
            if not exam_topic.strip():
                st.warning("נא להזין נושא למבחן.")
            else:
                prompt_gen = (
                    f"אתה מורה שבונה מבחן דמה לתלמיד ב-{student_context}.\n"
                    f"מקצוע: {exam_subject}, נושא: {exam_topic}, רמה: {exam_level}, שאלות: {q_count}.\n"
                    "החזר אך ורק מערך JSON תקין (ללא markdown וללא הערות מסביב):\n"
                    "[\n"
                    "  {\n"
                    '    "id": 1,\n'
                    '    "type": "multiple_choice",\n'
                    '    "question": "ניסוח שאלה אמריקאית",\n'
                    '    "points": 30,\n'
                    '    "options": ["תשובה א", "תשובה ב", "תשובה ג", "תשובה ד"],\n'
                    '    "correct_answer": "תשובה א",\n'
                    '    "explanation": "הסבר לתשובה הנכונה"\n'
                    "  },\n"
                    "  {\n"
                    '    "id": 2,\n'
                    '    "type": "open",\n'
                    '    "question": "ניסוח שאלה פתוחה",\n'
                    '    "points": 35,\n'
                    '    "ideal_answer": "תשובה מלאה לפי מחוון"\n'
                    "  }\n"
                    "]"
                )
                with st.spinner("בונה שאלות..."):
                    try:
                        res = generate_ai(prompt_gen)
                        st.session_state.mock_exam_data = extract_json(res.text)
                        st.session_state.exam_submitted = False
                        st.success("המבחן מוכן לעבודה.")
                    except Exception as e:
                        st.error(f"שגיאה: {e}")

    if st.session_state.mock_exam_data:
        st.markdown("---")
        st.subheader("שאלון המבחן:")
        
        user_answers = {}
        for q in st.session_state.mock_exam_data:
            st.markdown(f"**שאלה {q['id']} ({q.get('points', 25)} נקודות)**")
            st.write(q['question'])
            
            if q["type"] == "multiple_choice":
                user_answers[q["id"]] = st.radio(
                    f"בחר תשובה לשאלה {q['id']}:",
                    q["options"],
                    key=f"mcq_{q['id']}",
                    index=None
                )
            else:
                user_answers[q["id"]] = st.text_area(
                    f"מענה לשאלה {q['id']}:",
                    key=f"open_{q['id']}",
                    height=90
                )
            st.markdown("<br>", unsafe_allow_html=True)

        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            if st.button("הגש לבדיקה וקבלת ציון", use_container_width=True):
                st.session_state.exam_submitted = True
                st.session_state.submitted_answers = user_answers
        with col_b2:
            if st.button("איפוס והתחלה מחדש", use_container_width=True):
                st.session_state.mock_exam_data = None
                st.session_state.exam_submitted = False
                st.rerun()

        if st.session_state.exam_submitted:
            st.markdown("---")
            with st.spinner("מעריך את המבחן ומחשב ציון..."):
                try:
                    prompt_grade = (
                        f"אתה בוחן שמעריך מבחן דמה עבור תלמיד ב-{student_context}.\n"
                        f"מבחן ומחוון:\n{json.dumps(st.session_state.mock_exam_data, ensure_ascii=False)}\n\n"
                        f"תשובות התלמיד:\n{json.dumps(st.session_state.submitted_answers, ensure_ascii=False)}\n\n"
                        "החזר דוח ציונים מסודר בעברית:\n"
                        "1. ציון סופי משוקלל (מתוך 100)\n"
                        "2. פירוט עבור כל שאלה: מה היה נכון, על מה ירד ניקוד, ונוסח מלא של 100 לפי מחוון\n"
                        "3. דגש עיקרי להצלחה במבחן"
                    )
                    res_feedback = generate_ai(prompt_grade)
                    st.markdown("### דוח תוצאות וציון:")
                    st.markdown(res_feedback.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 4. ספריית שיעורים -----------------
elif room == "ספריית שיעורים מוקלטים":
    st.title("ספריית שיעורים מוקלטים")
    st.caption("סרטונים ממוקדים לפי נושאי לימוד.")
    
    category = st.selectbox("תחום לימוד:", [
        "מתמטיקה: גאומטריה ופיתגורס",
        "מתמטיקה: אלגברה וחדו\"א",
        "אנגלית: זמנים ודקדוק",
        "מדעי המחשב: יסודות תכנות",
        "ביולוגיה ופיזיקה",
        "מדעי החברה וכלכלה",
        "קולנוע, צילום ואמנות",
        "היסטוריה ואזרחות"
    ])
    
    video_db = {
        "מתמטיקה: גאומטריה ופיתגורס": {
            "משפט פיתגורס - חישוב צלעות": "https://www.youtube.com/watch?v=xAgLlIAum3c",
            "משפט תאלס": "https://www.youtube.com/watch?v=sI3q6Q_Hk84",
            "טריגונומטריה במשולש ישר זווית": "https://www.youtube.com/watch?v=aa7bC_rFq4c"
        },
        "מתמטיקה: אלגברה וחדו\"א": {
            "משוואות ממעלה ראשונה": "https://www.youtube.com/watch?v=lj6ONyl932A",
            "משוואה ריבועית ונוסחת שורשים": "https://www.youtube.com/watch?v=fghk_W4x_eM",
            "חקירת פונקציות ונגזרות": "https://www.youtube.com/watch?v=5yflv3j7T30"
        },
        "אנגלית: זמנים ודקדוק": {
            "Present Simple vs Progressive": "https://www.youtube.com/watch?v=L9AWrJnhsRI",
            "Past Simple & Continuous": "https://www.youtube.com/watch?v=0k53_u1N9Yk",
            "כתיבת חיבור דעה (Opinion Essay)": "https://www.youtube.com/watch?v=7P_k3j_4X4w"
        },
        "מדעי המחשב: יסודות תכנות": {
            "מבוא לתכנות ולולאות": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
            "מערכים ומחרוזות": "https://www.youtube.com/watch?v=xk4_1vDrzzo"
        },
        "ביולוגיה ופיזיקה": {
            "חוקי ניוטון": "https://www.youtube.com/watch?v=kKKM8Y-u7ds",
            "מבנה התא ופוטוסינתזה": "https://www.youtube.com/watch?v=68_jtXv9k4c"
        },
        "מדעי החברה וכלכלה": {
            "תיאוריית הצרכים של מאסלו": "https://www.youtube.com/watch?v=O-4ithG_07Q",
            "ביקוש, היצע ושיווי משקל שוק": "https://www.youtube.com/watch?v=g9aDizJpd_s"
        },
        "קולנוע, צילום ואמנות": {
            "זוויות צילום ומשמעותן": "https://www.youtube.com/watch?v=7y90UqWIdvU",
            "קומפוזיציה באמנות": "https://www.youtube.com/watch?v=sOvhb2k1l_8"
        },
        "היסטוריה ואזרחות": {
            "הגורמים למלחמת העולם הראשונה": "https://www.youtube.com/watch?v=SLj5r2nZHB8",
            "שלטון החוק וזכויות אדם": "https://www.youtube.com/watch?v=cMKe0k_k1Qk"
        }
    }
    
    current_videos = video_db.get(category, {})
    chosen_video_title = st.selectbox("בחר שיעור:", list(current_videos.keys()))
    selected_url = current_videos[chosen_video_title]
    
    col_v, col_n = st.columns([1.3, 0.7])
    with col_v:
        st.video(selected_url)
        st.markdown(f"[לצפייה ב-YouTube]({selected_url})")
    with col_n:
        st.subheader("סיכום הנושא")
        if st.button("הפק סיכום מהיר", use_container_width=True):
            prompt = f"סכם ב-4 בולטים ברורים את הנושא: {chosen_video_title} עבור תלמיד ב-{chosen_grade}. {anti_yap_rule}"
            with st.spinner("מכין סיכום..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 5. חיבור ל-Classroom -----------------
elif room == "חיבור ל-Classroom וספרים":
    st.title("חיבור ל-Classroom וספרי לימוד")
    st.caption("גישה מהירה לפורטלים ופענוח מטלות.")
    
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <a class="portal-pill" href="https://classroom.google.com" target="_blank">Google Classroom</a>
            <a class="portal-pill" href="https://www.classoos.com" target="_blank">Classoos (ספרי לימוד)</a>
            <a class="portal-pill" href="https://my.education.gov.il" target="_blank">פורטל משרד החינוך</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("פירוק מטלה או שיעורי בית מהמורה")
    teacher_post = st.text_area("הדבק כאן את נוסח ההודעה שפורסמה:", height=120)
    
    if st.button("פרק למשימות וזמנים", use_container_width=True):
        if not teacher_post.strip():
            st.warning("נא להדביק את הודעת המורה.")
        else:
            prompt = (
                f"התלמיד ב-{student_context} קיבל את המטלה הבאה:\n{teacher_post}\n\n"
                "החזר פירוק פרקטי:\n"
                "1. מועד הגשה מדויק (דד-ליין) ומה בדיוק צריך להגיש\n"
                "2. אילו ספרים, עמודים ותרגילים צריך לפתוח\n"
                "3. שלבי עבודה קצרים לביצוע מהיר\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנתח מטלה..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 6. דפי תרגול להדפסה -----------------
elif room == "דפי תרגול להדפסה":
    st.title("דפי תרגול להדפסה")
    st.caption("הפקת דפי עבודה נקיים שמוכנים להדפסה בבית.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        sheet_topic = st.text_input("נושא דף התרגול:", placeholder="למשל: משוואות ריבועיות, זמנים באנגלית, תורשה...")
        sheet_subject = st.selectbox("מקצוע:", [
            "מתמטיקה", "אנגלית", "מדעי המחשב", "ביולוגיה", "פיזיקה", "פסיכולוגיה", "סוציולוגיה", "כלכלה", "ניהול עסקי", "קולנוע ותקשורת", "צילום", "אמנות", "היסטוריה / אזרחות / תנ\"ך", "לשון"
        ])
    with col_p2:
        sheet_length = st.selectbox("היקף הדף:", ["דף תרגול קצר (4-5 שאלות)", "מבחן מלא כולל ניקוד"])
        include_answers = st.checkbox("הוספת דף תשובות בסוף", value=True)

    if st.button("ייצר דף תרגול", use_container_width=True):
        if not sheet_topic.strip():
            st.warning("נא להזין נושא.")
        else:
            prompt = (
                f"צור דף תרגול ומבחן מעוצב וברור בעברית לתלמיד ב-{student_context}.\n"
                f"מקצוע: {sheet_subject}, נושא: {sheet_topic}, היקף: {sheet_length}.\n"
                "מבנה הדף:\n"
                "1. כותרת עליונה עם שם הדף, כיתה ומקום לציון ולשם תלמיד.\n"
                "2. שאלות מנוסחות ברמות קושי עולות עם מקום לתשובה.\n"
                + ("3. בסוף הדף: מחוון תשובות מלא לבדיקה עצמית.\n" if include_answers else "")
            )
            with st.spinner("מרכיב דף עבודה..."):
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
                <button onclick="window.print()" style="padding: 10px 22px; font-size: 15px; background-color: #38bdf8; color: #0b0f17; border: none; border-radius: 8px; cursor: pointer; font-weight: 800;">
                    🖨️ הדפס דף תרגול
                </button>
            </div>
        """, unsafe_allow_html=True)

# ----------------- 7. מלטשת תשובות -----------------
elif room == "מלטשת תשובות למחוון 100":
    st.title("מלטשת תשובות למחוון 100")
    st.caption("בדיקת תשובה ושדרוג הניסוח למלוא הנקודות.")
    
    ans_topic = st.text_input("מקצוע ונושא השאלה:", placeholder="למשל: אזרחות - עקרון שלטון החוק...")
    q_text = st.text_input("השאלה שנשאלה:")
    user_ans = st.text_area("התשובה שכתבת:", height=120)
    
    if st.button("בדוק ושדרג תשובה", use_container_width=True):
        if not ans_topic.strip() or not user_ans.strip():
            st.warning("נא למלא נושא ותשובה.")
        else:
            prompt = (
                f"אתה בוחן שמעריך תשובה של תלמיד ב-{student_context}.\n"
                f"נושא: {ans_topic}\nשאלה: {q_text}\nתשובת התלמיד: {user_ans}\n\n"
                "החזר:\n"
                "1. ציון מוערך (מתוך 100)\n"
                "2. מה חסר לפי מחוון הבדיקה (קצר ולעניין)\n"
                "3. נוסח תשובה מושלם שסוגר 100 נקודות\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("בודק לפי מחוון..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 8. מעבדת מתמטיקה -----------------
elif room == "פירוק מתמטיקה ומדעים":
    st.title("פירוק מתמטיקה ומדעים")
    st.caption(f"פתרון צעד-אחר-צעד עם נימוק מתמטי מלא עבור {chosen_grade} ({math_units}).")
    
    math_topic = st.text_input("הנושא הנלמד:", placeholder="למשל: חקירת פולינום, טריגונומטריה, תנועה בפיזיקה...")
    math_input = st.text_area("התרגיל או השאלה:", height=110)
    
    if st.button("פרק והסבר תרגיל", use_container_width=True):
        if not math_topic.strip() or not math_input.strip():
            st.warning("נא להזין נושא ותרגיל.")
        else:
            prompt = (
                f"פתור את התרגיל הבא עבור תלמיד ב-{student_context}.\n"
                f"נושא: {math_topic}\nתרגיל: {math_input}\n\n"
                "פתור שלב אחרי שלב בבירור עם נימוק קצר ליד כל שלב, וסמן תוצאה סופית מודגשת.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מחשב ומנמק..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 9. שליף חירום -----------------
elif room == "שליף חירום למבחן":
    st.title("שליף חירום למבחן")
    st.caption("נקודות ברזל קריטיות שחובה לדעת ב-60 שניות לפני הכניסה לכיתה.")
    
    panic_topic = st.text_input("נושא המבחן:", placeholder="למשל: משפט חוצה זווית, מרד בר כוכבא, עקומת תמורה...")
    
    if st.button("הצג שליף ממוקד", use_container_width=True):
        if not panic_topic.strip():
            st.warning("נא להזין נושא.")
        else:
            prompt = (
                f"תלמיד ב-{student_context} נכנס בעוד דקה למבחן על הנושא: {panic_topic}.\n"
                "החזר אך ורק:\n"
                "1. 3 משפטי זהב שחייבים לרשום במבחן כדי לקבל נקודות\n"
                "2. הטעות הנפוצה ביותר שמכשילה תלמידים\n"
                "3. מושג חובה אחד שהבוחן מחפש בעין\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מחלץ נקודות מפתח..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(f'<div class="cheat-box">{res.text}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 10. תכנון לו״ז -----------------
elif room == "מתכנן לוח זמנים":
    st.title("מתכנן לוח זמנים למבחן")
    st.caption("חלוקת עבודה יומית כדי לא להגיע ללילה לפני המבחן בלחץ.")
    
    topics = st.text_area("הנושאים והפרקים שצריך להספיק:", placeholder="למשל: פרקים 1 עד 4 בספר, שאלות בגרות...")
    c1, c2 = st.columns(2)
    with c1:
        exam_subj = st.text_input("מקצוע:", placeholder="מתמטיקה / היסטוריה / ביולוגיה...")
        days = st.number_input("ימים שנותרו:", min_value=1, max_value=30, value=3, step=1)
    with c2:
        hours_selected = st.select_slider(
            "שעות למידה פנויות ביום:",
            options=["שעה אחת", "שעתיים", "3 שעות", "4 שעות", "5 שעות"],
            value="שעתיים"
        )
        
    if st.button("בנה תוכנית למידה", use_container_width=True):
        if not topics.strip():
            st.warning("נא להזין חומר למבחן.")
        else:
            prompt = (
                f"בנה לוח זמנים פרקטי ללימוד למבחן עבור תלמיד ב-{student_context}.\n"
                f"מקצוע: {exam_subj}, ימים: {days}, שעות ביום: {hours_selected}, חומר: {topics}.\n"
                "חלק את המשימות לפי ימים עם זמני מנוחה ותרגול מעשי."
            )
            with st.spinner("מתכנן לו\"ז..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 11. משוב -----------------
elif room == "משוב והצעות":
    st.title("משוב והצעות לשיפור")
    st.caption("כתוב לנו מה כדאי להוסיף או לשפר.")
    
    with st.form("feedback_form", clear_on_submit=True):
        fb_name = st.text_input("שם או כינוי:")
        fb_grade = st.selectbox("כיתה:", ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב"], index=2)
        fb_major = st.text_input("מגמה:", value=chosen_major)
        fb_rating = st.slider("דירוג (כוכבים):", min_value=1, max_value=5, value=5)
        fb_text = st.text_area("מה דעתך על הפלטפורמה? מה לשפר?")
        submitted = st.form_submit_button("שליחת משוב")
        
        if submitted:
            if not fb_text.strip():
                st.warning("נא לכתוב משהו לפני השליחה.")
            else:
                grade_display = f"{fb_grade} ({fb_major})" if fb_major.strip() else fb_grade
                st.session_state.reviews.insert(0, {
                    "name": fb_name if fb_name.strip() else "אנונימי",
                    "grade": grade_display,
                    "rating": fb_rating,
                    "text": fb_text
                })
                st.success("תודה על המשוב!")
                st.balloons()

    st.markdown("---")
    st.subheader("משובים אחרונים:")
    for r in st.session_state.reviews:
        stars = "⭐" * r["rating"]
        st.markdown(f"""
            <div style="background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                <b>{r['name']}</b> ({r['grade']}) — {stars}<br>
                <span style="color: #94a3b8;">{r['text']}</span>
            </div>
        """, unsafe_allow_html=True)
