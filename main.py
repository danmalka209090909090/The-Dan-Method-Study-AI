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
    page_title="Dan Study | סביבת למידה חכמה",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# שפת עיצוב חדשה: מינימליזם מודרני, נקי, רגוע וכיפי לעין
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* רקע כולל רגוע ונקי */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* סרגל צד נקי */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-left: 1px solid #e2e8f0;
    }
    
    div[data-testid="stExpander"] {
        text-align: right;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }
    
    div[data-testid="stSlider"] {
        direction: ltr !important;
    }
    div[data-testid="stSlider"] label {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .bsd-badge {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    
    /* Hero Banner אלגנטי ולא מצועצע */
    .main-hero {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 32px 28px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
        text-align: right;
    }
    .main-hero h1 {
        font-size: 2.3rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 8px;
    }
    .main-hero p {
        font-size: 1.15rem;
        color: #475569;
        margin: 0;
        line-height: 1.6;
    }
    
    /* כרטיסיות נקיות ונעימות */
    .clean-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
    }
    
    .clean-card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    
    .clean-card-desc {
        font-size: 0.95rem;
        color: #64748b;
        line-height: 1.5;
        margin: 0;
    }
    
    /* חלון הזום - עיצוב שיחה מקצועי ונקי */
    .zoom-clean-box {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        text-align: center;
    }
    .zoom-video-frame {
        width: 100%;
        height: 240px;
        border-radius: 12px;
        overflow: hidden;
        background: #0f172a;
        margin-bottom: 12px;
    }
    .zoom-video-frame video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    /* סטייל לשליף חירום */
    .cheat-clean {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 12px;
        padding: 18px;
        color: #92400e;
        margin-top: 12px;
    }
    
    /* כפתורי פורטל */
    .portal-tag {
        display: inline-block;
        padding: 8px 16px;
        background: #f1f5f9;
        color: #334155 !important;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        margin-left: 8px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .portal-tag:hover {
        background: #e2e8f0;
        color: #0f172a !important;
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

# אתחול Session State
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "השליף חירום עזר לי לסגור את כל החומר לפני המבחן."},
        {"name": "נועה ל.", "grade": "כיתה י\"א (ביולוגיה)", "rating": 5, "text": "ממש כיף להשתמש, נקי וסוגר פינות תוך שניות."},
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

# --- סרגל צד (Sidebar) ---
with st.sidebar:
    st.markdown('<div class="bsd-badge">בס״ד</div>', unsafe_allow_html=True)
    st.title("Dan Study 📚")
    st.caption("מרחב למידה אישי וממוקד מחוון")
    st.markdown("---")
    
    st.subheader("הפרופיל שלך")
    chosen_grade = st.selectbox(
        "שכבת לימוד:",
        ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב (בגרות)"],
        index=2
    )
    
    if chosen_grade in ["כיתה ז'", "כיתה ח'", "כיתה ט'"]:
        math_units = st.selectbox("מתמטיקה:", ["הקבצה א' / מצוינות", "הקבצה ב'", "רמה רגילה"])
        eng_units = st.selectbox("אנגלית:", ["הקבצה א' / דוברי אנגלית", "הקבצה ב'", "רמה רגילה"])
        chosen_major = st.selectbox("מסלול עניין:", [
            "ליבה כללית", "מדעי המחשב", "מדעים / ביולוגיה", "אמנות", "תקשורת וקולנוע"
        ])
    else:
        math_units = st.selectbox("מתמטיקה:", ["5 יחידות", "4 יחידות", "3 יחידות"])
        eng_units = st.selectbox("אנגלית:", ["5 יחידות / דוברי אנגלית", "4 יחידות (Module E)", "3 יחידות"])
        chosen_major = st.selectbox("מגמה בבית הספר:", [
            "ללא מגמה (מקצועות ליבה)",
            "מדעי המחשב / הנדסת תוכנה",
            "פיזיקה",
            "ביולוגיה",
            "ניהול עסקי / יזמות",
            "פסיכולוגיה וסוציולוגיה",
            "כלכלה וניהול",
            "קולנוע ותקשורת",
            "צילום ומדיה",
            "אמנות ועיצוב"
        ])
    
    st.markdown("---")
    st.subheader("כלים")
    room = st.radio(
        "מעבר בין כלים:",
        [
            "דף הבית",
            "שיעור פרטי בווידאו",
            "סורק תרגילים ודפי עבודה",
            "סימולציית מבחן (Mock Exam)",
            "ספריית שיעורי וידאו",
            "משימות בית ספר ו-Classroom",
            "דפי עבודה להדפסה",
            "בדיקה ושדרוג תשובות",
            "מעבדת מתמטיקה ומדעים",
            "שליף חירום למבחן",
            "תכנון לוח זמנים",
            "משוב והצעות"
        ]
    )
    
    st.markdown("---")
    no_yap = st.toggle("מענה ממוקד תכל'ס", value=True)

anti_yap_rule = "השב ישירות לתכל'ס, בשפה טבעית ונעימה, ללא הקדמות רובוטיות מיותרות." if no_yap else ""
student_context = f"שכבת לימוד: {chosen_grade}, מתמטיקה: {math_units}, אנגלית: {eng_units}, מגמה: {chosen_major}."

# ----------------- 0. דף הבית -----------------
if room == "דף הבית":
    st.markdown('<div class="bsd-badge">בס״ד</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="main-hero">
            <h1>מרחב הלמידה שלך למבחנים ובגרויות</h1>
            <p>
                בלי חפירות, בלי תשובות ארוכות שמבזבזות זמן. 
                פתרונות מפורטים לפי שלבים, התאמה מלאה לרמת הלימוד שלך בבית הספר וכלים אמיתיים שמכינים אותך להצליח.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="clean-card">
                <div class="clean-card-title">📹 שיעור פרטי אישי</div>
                <div class="clean-card-desc">שיחה ישירה מול מורה פרטית להסבר כל נושא שנתקעת בו שלב אחרי שלב.</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="clean-card">
                <div class="clean-card-title">📝 מבחני דמה אמיתיים</div>
                <div class="clean-card-desc">בדיקת רמת מוכנות למבחן עם ציונים, הערות מחוון ומשוב אמיתי.</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="clean-card">
                <div class="clean-card-title">📐 מתמטיקה ומדעים</div>
                <div class="clean-card-desc">פירוק כל תרגיל ומשוואה עם נימוקים קצרים וברורים לכל שלב.</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("💡 טיפ ללמידה נכונה היום:")
    st.info("בחר כלי בסרגל הצד, ציין את הנושא הנלמד וקבל בדיוק את מה שאתה צריך כדי לסגור את החומר.")

# ----------------- 1. שיעור פרטי בווידאו -----------------
elif room == "שיעור פרטי בווידאו":
    st.title("שיעור פרטי אישי")
    st.caption(f"התאמה מלאה עבור {chosen_grade} | {math_units} | {chosen_major}")
    
    col_v1, col_v2 = st.columns([1.1, 1.9])
    
    with col_v1:
        st.markdown("""
            <div class="zoom-clean-box">
                <div style="color: #059669; font-weight: 700; font-size: 0.85rem; margin-bottom: 8px;">● שיחה פעילה</div>
                <div class="zoom-video-frame">
                    <video autoplay loop muted playsinline>
                        <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4" type="video/mp4">
                    </video>
                </div>
                <h3 style="margin: 0; font-size: 1.2rem; color: #0f172a; font-weight: 700;">המורה מיה</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin: 4px 0 0 0;">ליווי אישי לבגרויות ולחטיבה</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.last_voice_reply:
            st.markdown("<br><b>האזנה לתשובה:</b>", unsafe_allow_html=True)
            audio_url = get_tts_audio_url(st.session_state.last_voice_reply)
            st.audio(audio_url, format="audio/mp3", autoplay=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        z_subject = st.selectbox("מקצוע הלימוד:", [
            "מתמטיקה", "אנגלית", chosen_major, "היסטוריה", "אזרחות", "תנ\"ך", "לשון והבעה", "ביולוגיה", "פיזיקה", "מדעי המחשב"
        ])
        z_goal = st.radio("במה נתמקד?", [
            "הסבר נושא חדש מהבסיס",
            "פתרון שיעורי בית יחד",
            "הכנה למבחן קרוב"
        ])
        
        if st.button("איפוס שיחה", use_container_width=True):
            st.session_state.zoom_chat_history = []
            st.session_state.last_voice_reply = None
            st.rerun()

    with col_v2:
        st.subheader(f"שיחה בנושא {z_subject}")
        
        chat_box = st.container(height=360)
        with chat_box:
            if not st.session_state.zoom_chat_history:
                st.write(f"👋 **המורה מיה:** היי! אני כאן איתך בשיעור {z_subject}. תגיד לי איזה נושא או שאלה נרצה לעבור עליהם עכשיו?")
            else:
                for m in st.session_state.zoom_chat_history:
                    if m["role"] == "user":
                        with st.chat_message("user"):
                            st.write(m["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(m["content"])

        st.caption("שאלה בדיבור קולי:")
        audio_prompt = st.audio_input("הקלטת שאלה:")

        if audio_prompt is not None:
            with st.spinner("מקשיבה לשאלה שלך..."):
                try:
                    audio_bytes = audio_prompt.read()
                    prompt_audio = (
                        f"את המורה מיה, מורה פרטית ישראלית מקצועית, סבלנית וחמה בשיעור עם תלמיד ב-{student_context}.\n"
                        f"מקצוע: {z_subject}. מטרה: {z_goal}.\n"
                        "הקשיבי לשאלת התלמיד בהקלטה:\n"
                        "1. עני ישירות, בצורה בהירה ופשוטה בגובה העיניים (עד 3 משפטים).\n"
                        "2. סיימי בשאלה קצרה כדי לוודא שהתלמיד הבין וממשיך איתך.\n"
                        f"{anti_yap_rule}"
                    )
                    res_voice = generate_ai([prompt_audio, {"mime_type": "audio/wav", "data": audio_bytes}])
                    reply_text = res_voice.text
                    
                    st.session_state.zoom_chat_history.append({"role": "user", "content": "🎙️ [שאלה קולית שהוקלטה]"})
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
                f"את המורה מיה, מורה פרטית ישראלית מקצועית וסבלנית בשיעור עם תלמיד.\n"
                f"פרטי התלמיד: {student_context}.\n"
                f"מקצוע: {z_subject}. מטרה: {z_goal}.\n\n"
                "1. דברי בלשון נקבה על עצמך, בצורה טבעית ונעימה.\n"
                "2. עני בקצרה (2-3 משפטים בכל פעם) בלי לחפור.\n"
                "3. סיימי בשאלה קצרה כדי לבדוק שהתלמיד איתך.\n"
                f"{anti_yap_rule}\n\n"
                f"היסטוריית השיחה:\n{history_text}\n\nשאלה: {text_spoken}"
            )
            with st.spinner("מכינה מענה..."):
                try:
                    res_zoom = generate_ai(zoom_prompt)
                    st.session_state.zoom_chat_history.append({"role": "assistant", "content": res_zoom.text})
                    st.session_state.last_voice_reply = res_zoom.text
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 2. סורק תרגילים ודפי עבודה -----------------
elif room == "סורק תרגילים ודפי עבודה":
    st.title("סורק תרגילים ודפי עבודה")
    st.caption("העלאת צילום של עמוד מספר, מחברת או דף עבודה, או הזנת קישור ישיר.")
    
    photo_topic = st.text_input("מה הנושא או המקצוע?", placeholder="למשל: גיאומטריה, חוקי ניוטון, שאלות תנ\"ך...")
    input_method = st.radio("אופן הזנת התמונה:", ["העלאת קובץ", "קישור לתמונה (URL)"], horizontal=True)
    
    img_to_solve = None
    if input_method == "העלאת קובץ":
        file = st.file_uploader("בחר קובץ תמונה:", type=["png", "jpg", "jpeg"])
        if file:
            try:
                img_to_solve = Image.open(file)
                st.image(img_to_solve, caption="התמונה שנבחרה", width=360)
            except Exception as e:
                st.error(f"שגיאה בפתיחת הקובץ: {e}")
    else:
        url_input = st.text_input("קישור לתמונה:", placeholder="https://example.com/sheet.jpg")
        if url_input.strip():
            try:
                with st.spinner("טוען תמונה..."):
                    response = requests.get(url_input.strip(), timeout=10)
                    response.raise_for_status()
                    img_to_solve = Image.open(BytesIO(response.content))
                    st.image(img_to_solve, caption="התמונה מהקישור", width=360)
            except Exception as e:
                st.error(f"לא ניתן לטעון את התמונה: {e}")

    action = st.text_input("הנחיה לפתרון:", value="פתור והסבר שלב אחרי שלב בצורה ברורה ומדויקת")
    
    if st.button("פענח ופתור", use_container_width=True):
        if not photo_topic.strip():
            st.warning("נא לציין את הנושא או המקצוע.")
        elif img_to_solve is None:
            st.warning("נא להעלות תמונה או לספק קישור תקין.")
        else:
            with st.spinner("מפענח את השאלות ומחשב פתרון..."):
                try:
                    prompt = f"התלמיד ב-{student_context}. החומר: {photo_topic}. הנחיה: {action}. {anti_yap_rule}"
                    res = generate_ai([prompt, img_to_solve])
                    st.markdown("### פתרון מפורט:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 3. סימולציית מבחן -----------------
elif room == "סימולציית מבחן (Mock Exam)":
    st.title("סימולציית מבחן (Mock Exam)")
    st.caption(f"הפקת מבחן דמה אינטראקטיבי מותאם ל-{chosen_grade} עם בדיקה לפי מחוון.")
    
    with st.expander("הגדרות מבחן הדמה", expanded=(st.session_state.mock_exam_data is None)):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            exam_subject = st.selectbox("מקצוע:", [
                "מתמטיקה", "היסטוריה", "אזרחות", "אנגלית", "תנ\"ך", "לשון והבעה", "ביולוגיה", "פיזיקה", "מדעי המחשב", chosen_major
            ])
            exam_topic = st.text_input("החומר למבחן:", placeholder="למשל: בעיות קיצון, מלחמת העולם הראשונה, פוטוסינתזה...")
        with col_m2:
            q_count = st.slider("מספר שאלות:", 2, 5, 3)
            exam_level = st.select_slider("רמת קושי:", ["בסיסית", "רמת מבחן כיתתי", "רמת בגרות מלאה"], value="רמת מבחן כיתתי")
            
        if st.button("צור מבחן דמה", use_container_width=True):
            if not exam_topic.strip():
                st.warning("נא להזין את החומר למבחן.")
            else:
                prompt_gen = (
                    f"אתה מורה שבונה מבחן דמה לתלמיד ב-{student_context}.\n"
                    f"מקצוע: {exam_subject}, נושא: {exam_topic}, רמה: {exam_level}, מספר שאלות: {q_count}.\n"
                    "החזר אך ורק מערך JSON תקין במבנה הבא (ללא טקסט נוסף לפני או אחרי):\n"
                    "[\n"
                    "  {\n"
                    '    "id": 1,\n'
                    '    "type": "multiple_choice",\n'
                    '    "question": "ניסוח שאלה אמריקאית",\n'
                    '    "points": 30,\n'
                    '    "options": ["אופציה 1", "אופציה 2", "אופציה 3", "אופציה 4"],\n'
                    '    "correct_answer": "אופציה 1",\n'
                    '    "explanation": "הסבר קצר לתשובה הנכונה"\n'
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
                with st.spinner("בונה את שאלות המבחן..."):
                    try:
                        res = generate_ai(prompt_gen)
                        st.session_state.mock_exam_data = extract_json(res.text)
                        st.session_state.exam_submitted = False
                        st.success("המבחן מוכן! ענה על השאלות למטה.")
                    except Exception as e:
                        st.error(f"שגיאה: {e}")

    if st.session_state.mock_exam_data:
        st.markdown("---")
        st.subheader("טופס המבחן")
        
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
                    f"התשובה שלך לשאלה {q['id']}:",
                    key=f"open_{q['id']}",
                    height=90
                )
            st.markdown("<br>", unsafe_allow_html=True)

        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            if st.button("הגש מבחן ובדוק ציון", use_container_width=True):
                st.session_state.exam_submitted = True
                st.session_state.submitted_answers = user_answers
        with col_b2:
            if st.button("התחל מבחן חדש", use_container_width=True):
                st.session_state.mock_exam_data = None
                st.session_state.exam_submitted = False
                st.rerun()

        if st.session_state.exam_submitted:
            st.markdown("---")
            with st.spinner("בודק את התשובות ומחשב ציון..."):
                try:
                    prompt_grade = (
                        f"אתה בוחן שמעריך מבחן דמה עבור תלמיד ב-{student_context}.\n"
                        f"המבחן והמחוון:\n{json.dumps(st.session_state.mock_exam_data, ensure_ascii=False)}\n\n"
                        f"תשובות התלמיד:\n{json.dumps(st.session_state.submitted_answers, ensure_ascii=False)}\n\n"
                        "החזר דוח ציונים מסודר בעברית:\n"
                        "1. ציון סופי משוקלל (מתוך 100)\n"
                        "2. פירוט לכל שאלה: מה היה נכון, מה היה שגוי, ונוסח מלא לתשובת 100\n"
                        "3. דגש עיקרי להצלחה במבחן הכיתתי"
                    )
                    res_feedback = generate_ai(prompt_grade)
                    st.markdown("### דוח תוצאות ומשוב:")
                    st.markdown(res_feedback.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 4. ספריית שיעורי וידאו -----------------
elif room == "ספריית שיעורי וידאו":
    st.title("שיעורי וידאו לפי נושאים")
    st.caption("סרטונים ממוקדים לצפייה נוחה וישירה.")
    
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
    chosen_video_title = st.selectbox("בחר שיעור לצפייה:", list(current_videos.keys()))
    selected_url = current_videos[chosen_video_title]
    
    col_p, col_s = st.columns([1.3, 0.7])
    with col_p:
        st.video(selected_url)
        st.markdown(f"[לצפייה ישירה ב-YouTube]({selected_url})")
    with col_s:
        st.subheader("סיכום הנושא")
        if st.button("הפק סיכום נקודתי", use_container_width=True):
            prompt = f"סכם ב-4 נקודות תמציתיות את הנושא: {chosen_video_title} עבור תלמיד ב-{chosen_grade}. {anti_yap_rule}"
            with st.spinner("מכין סיכום..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 5. משימות בית ספר ו-Classroom -----------------
elif room == "משימות בית ספר ו-Classroom":
    st.title("משימות בית ספר וספרים")
    st.caption("גישה מהירה לפורטלים ומפענח שיעורי בית.")
    
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <a class="portal-tag" href="https://classroom.google.com" target="_blank">Google Classroom</a>
            <a class="portal-tag" href="https://www.classoos.com" target="_blank">Classoos (ספרי לימוד)</a>
            <a class="portal-tag" href="https://my.education.gov.il" target="_blank">פורטל משרד החינוך</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("פירוק מטלה או הודעה מהמורה")
    teacher_post = st.text_area("הדבק כאן את נוסח המטלה מ-Classroom או מוואטסאפ:", height=120)
    
    if st.button("פרק למשימות ולוח זמנים", use_container_width=True):
        if not teacher_post.strip():
            st.warning("נא להדביק את הודעת המורה.")
        else:
            prompt = (
                f"התלמיד ב-{student_context} קיבל את המטלה הבאה:\n{teacher_post}\n\n"
                "החזר פירוק ברור ופרקטי:\n"
                "1. מה נדרש להגיש ומתי (דד-ליין מדויק)\n"
                "2. אילו ספרים, עמודים ותרגילים צריך לפתוח\n"
                "3. שלבי ביצוע קצרים וממוקדים לביצוע מהיר\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנתח את המטלה..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 6. דפי עבודה להדפסה -----------------
elif room == "דפי עבודה להדפסה":
    st.title("דפי עבודה ומבחנים להדפסה")
    st.caption(f"הפקת דף תרגול נקי שמוכן להדפסה ישירה במדפסת ביתית.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        sheet_topic = st.text_input("נושא דף העבודה:", placeholder="למשל: חוקי חזקות, זמנים באנגלית, תורשה...")
        sheet_subject = st.selectbox("מקצוע:", [
            "מתמטיקה", "אנגלית", "מדעי המחשב", "ביולוגיה", "פיזיקה", "פסיכולוגיה", "סוציולוגיה", "כלכלה", "ניהול עסקי", "קולנוע ותקשורת", "צילום", "אמנות", "היסטוריה / אזרחות / תנ\"ך", "לשון"
        ])
    with col_p2:
        sheet_length = st.selectbox("היקף הדף:", ["דף עבודה קצר (4-5 שאלות)", "מבחן מלא עם ניקוד"])
        include_answers = st.checkbox("הוספת דף תשובות בסוף", value=True)

    if st.button("ייצר דף עבודה", use_container_width=True):
        if not sheet_topic.strip():
            st.warning("נא להזין נושא.")
        else:
            prompt = (
                f"צור דף תרגול ומבחן מעוצב וברור בעברית לתלמיד ב-{student_context}.\n"
                f"מקצוע: {sheet_subject}, נושא: {sheet_topic}, היקף: {sheet_length}.\n"
                "מבנה הדף:\n"
                "1. כותרת עליונה עם שם הדף, כיתה ומקום לציון ושם תלמיד.\n"
                "2. שאלות מנוסחות היטב ברמות קושי עולות עם שורות לכתיבת תשובה.\n"
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
                <button onclick="window.print()" style="padding: 10px 22px; font-size: 15px; background-color: #0f172a; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 700;">
                    🖨️ הדפסת דף העבודה
                </button>
            </div>
        """, unsafe_allow_html=True)

# ----------------- 7. בדיקה ושדרוג תשובות -----------------
elif room == "בדיקה ושדרוג תשובות":
    st.title("בדיקה ושדרוג תשובות")
    st.caption("התאמת ניסוח התשובה למחוון בחינה לקבלת מלוא הנקודות.")
    
    ans_topic = st.text_input("מקצוע ונושא השאלה:", placeholder="למשל: אזרחות - עקרון שלטון החוק...")
    q_text = st.text_input("השאלה שנשאלה:")
    user_ans = st.text_area("התשובה שכתבת:", height=120)
    
    if st.button("בדוק ושדרג תשובה", use_container_width=True):
        if not ans_topic.strip() or not user_ans.strip():
            st.warning("נא למלא את הנושא ואת התשובה שלך.")
        else:
            prompt = (
                f"אתה בוחן שמעריך תשובה של תלמיד ב-{student_context}.\n"
                f"נושא: {ans_topic}\nשאלה: {q_text}\nתשובת התלמיד: {user_ans}\n\n"
                "החזר:\n"
                "1. ציון מוערך (מתוך 100)\n"
                "2. מה חסר לפי מחוון הבדיקה (קצר ולעניין)\n"
                "3. נוסח תשובה מושלם שסוגר את מלוא הנקודות\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("בודק לפי מחוון..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 8. מעבדת מתמטיקה ומדעים -----------------
elif room == "מעבדת מתמטיקה ומדעים":
    st.title("פירוק מתמטיקה ומדעים")
    st.caption(f"פתרון שלב-אחר-שלב עם נימוקים עבור {chosen_grade} ({math_units}).")
    
    math_topic = st.text_input("נושא התרגיל:", placeholder="למשל: חקירת פולינום, מעגל, קינמטיקה...")
    math_input = st.text_area("התרגיל או הבעיה המילולית:", height=110)
    
    if st.button("פרק והסבר תרגיל", use_container_width=True):
        if not math_topic.strip() or not math_input.strip():
            st.warning("נא להזין את הנושא ואת התרגיל.")
        else:
            prompt = (
                f"פתור את התרגיל הבא עבור תלמיד ב-{student_context}.\n"
                f"נושא: {math_topic}\nתרגיל: {math_input}\n\n"
                "פתור שלב אחרי שלב בבירור עם נימוק קצר ליד כל שלב, וסמן את התוצאה הסופית באופן מודגש.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מחשב ומנמק..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 9. שליף חירום למבחן -----------------
elif room == "שליף חירום למבחן":
    st.title("שליף חירום לפני מבחן")
    st.caption("נקודות ברזל קריטיות שחובה לדעת ב-60 שניות לפני הכניסה לכיתה.")
    
    panic_topic = st.text_input("נושא המבחן:", placeholder="למשל: משפט חוצה זווית, מרד בר כוכבא, עקומת תמורה...")
    
    if st.button("הצג שליף ממוקד", use_container_width=True):
        if not panic_topic.strip():
            st.warning("נא להזין את נושא המבחן.")
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
                    st.markdown(f'<div class="cheat-clean">{res.text}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 10. תכנון לוח זמנים -----------------
elif room == "תכנון לוח זמנים":
    st.title("תכנון לוח זמנים למבחן")
    st.caption("חלוקת עבודה יומית כדי להגיע מוכן בלי לחץ של הרגע האחרון.")
    
    topics = st.text_area("החומר והפרקים שצריך להספיק:", placeholder="למשל: עמודים 40 עד 80 בספר, מבחן בגרות 2024...")
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
            st.warning("נא לציין את החומר למבחן.")
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

# ----------------- 11. משוב והצעות -----------------
elif room == "משוב והצעות":
    st.title("משוב והצעות לשיפור")
    st.caption("נשמח לשמוע איך המערכת עובדת עבורך ומה עוד כדאי להוסיף.")
    
    with st.form("feedback_form", clear_on_submit=True):
        fb_name = st.text_input("שם או כינוי:")
        fb_grade = st.selectbox("כיתה:", ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב"], index=2)
        fb_major = st.text_input("מגמה:", value=chosen_major)
        fb_rating = st.slider("דירוג החוויה (כוכבים):", min_value=1, max_value=5, value=5)
        fb_text = st.text_area("איך החוויה שלך עם האתר? מה כדאי לשפר?")
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
                st.success("תודה רבה על המשוב!")
                st.balloons()

    st.markdown("---")
    st.subheader("מה אומרים תלמידים:")
    for r in st.session_state.reviews:
        stars = "⭐" * r["rating"]
        st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; margin-bottom: 10px;">
                <b>{r['name']}</b> ({r['grade']}) — {stars}<br>
                <span style="color: #475569;">{r['text']}</span>
            </div>
        """, unsafe_allow_html=True)
