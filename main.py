import streamlit as st
from google import genai
from PIL import Image
import requests
from io import BytesIO
import json
import re
import time
import urllib.parse

# קוד גישה סודי לחדר מורים והנהלה
TEACHER_ACCESS_CODE = "DAN100"

st.set_page_config(
    page_title="The Dan Method | לומדים. מתקדמים.",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# שפת עיצוב LearnIt / The Dan Method מלאה בכל המסכים והחדרים
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700;800;900&display=swap');

    * {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* הסתרת סרגלי Streamlit מובנים */
    header, 
    [data-testid="stHeader"], 
    .stAppHeader, 
    div[data-testid="stToolbar"], 
    .stAppToolbar, 
    div[class*="stToolbar"],
    div[class*="StatusWidget"],
    #MainMenu, 
    footer,
    [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        padding: 0 !important;
        margin: 0 !important;
        opacity: 0 !important;
    }

    .stApp {
        margin-top: -45px !important;
        padding-top: 0px !important;
        direction: rtl;
        text-align: right;
        background-color: #f8fafc;
        color: #0f172a;
    }

    .main .block-container {
        padding-top: 1.5rem !important;
        max-width: 1160px;
        margin: 0 auto;
    }

    /* סרגל צד תואם מותג */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-left: 1px solid #e2e8f0;
        min-width: 280px !important;
        max-width: 320px !important;
        white-space: normal !important;
    }

    [data-testid="stSidebar"] * {
        word-break: normal !important;
        white-space: normal !important;
    }

    /* כיוון סליידרים תקין */
    div[data-testid="stSlider"] > div {
        direction: ltr !important;
    }
    div[data-testid="stSlider"] label {
        direction: rtl !important;
        text-align: right !important;
    }

    /* סרגל עליון */
    .learnit-navbar {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 12px 22px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(15, 43, 92, 0.04);
    }
    .brand-logo-container {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        direction: ltr;
    }
    .brand-main-name {
        font-size: 1.3rem;
        font-weight: 900;
        letter-spacing: -0.4px;
        color: #0f2b5c;
    }
    .brand-sub-badge {
        font-size: 0.65rem;
        font-weight: 800;
        color: #2563eb;
        letter-spacing: 1.5px;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(rgba(255, 255, 255, 0.90), rgba(255, 255, 255, 0.95)), 
                    url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80') center/cover no-repeat;
        border: 1px solid #e2e8f0;
        border-radius: 24px;
        padding: 40px 24px 24px 24px;
        box-shadow: 0 4px 24px rgba(15, 43, 92, 0.04);
        margin-bottom: 20px;
        text-align: center;
    }
    .hero-main-title {
        font-size: 2.8rem;
        font-weight: 900;
        color: #0f2b5c;
        line-height: 1.25;
        margin-bottom: 10px;
    }
    .hero-desc {
        font-size: 1.15rem;
        color: #475569;
        margin-bottom: 16px;
        font-weight: 500;
    }

    /* סרט יתרונות */
    .features-ribbon {
        display: flex;
        justify-content: space-around;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 14px 20px;
        margin-bottom: 24px;
        box-shadow: 0 2px 10px rgba(15, 43, 92, 0.03);
    }
    .ribbon-item {
        display: flex;
        align-items: center;
        gap: 12px;
        text-align: right;
    }
    .ribbon-icon-circle {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }

    /* תיבת המותג הראשית */
    .story-card {
        background: linear-gradient(135deg, #0f2b5c 0%, #1e3a8a 100%);
        color: #ffffff;
        border-radius: 20px;
        padding: 28px 30px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(15, 43, 92, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .story-title {
        font-size: 1.55rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .story-p {
        font-size: 1.05rem;
        color: #e2e8f0;
        line-height: 1.7;
        margin: 0;
    }

    /* טבלת השוואה בצבעי האתר */
    .compare-container {
        margin-bottom: 30px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 26px;
        box-shadow: 0 4px 16px rgba(15, 43, 92, 0.03);
    }
    .compare-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        text-align: right;
    }
    .compare-table th {
        padding: 12px;
        border-bottom: 2px solid #e2e8f0;
        color: #64748b;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .compare-table td {
        padding: 14px 12px;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.95rem;
    }

    /* כרטיסיות חדרים בדף הבית */
    .room-tile {
        border-radius: 16px;
        padding: 18px 14px;
        text-align: center;
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
        background: #ffffff;
        box-shadow: 0 2px 8px rgba(15, 43, 92, 0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .room-tile:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(15, 43, 92, 0.08);
    }

    /* תיבות תוכן אחידות בכל החדרים בצבעי המותג */
    .room-card-dan {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-right: 5px solid #2563eb;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 4px 14px rgba(15, 43, 92, 0.04);
        margin-bottom: 20px;
        color: #0f172a;
        line-height: 1.7;
    }

    .room-highlight-box {
        background: #f0f7ff;
        border: 1px solid #bfdbfe;
        border-radius: 14px;
        padding: 18px 20px;
        margin-top: 15px;
        color: #1e3a8a;
    }

    .room-header-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #e0f2fe;
        color: #0369a1;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }

    /* שקופית מצגות */
    .slide-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(15, 43, 92, 0.04);
        border-right: 5px solid #0f2b5c;
    }
    .slide-speaker-notes {
        background: #f0f7ff;
        border: 1px dashed #93c5fd;
        border-radius: 12px;
        padding: 14px;
        margin-top: 12px;
        color: #1e3a8a;
        font-size: 0.95rem;
    }

    /* חדר זום */
    .zoom-learnit-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(15, 43, 92, 0.04);
        text-align: center;
    }
    .teacher-circle-box {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        margin: 0 auto 12px auto;
        overflow: hidden;
        border: 3px solid #2563eb;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
    }
    .teacher-circle-box img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* כפתור וואטסאפ */
    .whatsapp-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: #25d366;
        color: white !important;
        padding: 9px 18px;
        border-radius: 10px;
        font-weight: 700;
        text-decoration: none;
        font-size: 0.95rem;
        margin-top: 10px;
        box-shadow: 0 2px 8px rgba(37, 211, 102, 0.3);
    }

    /* התאמת כפתורי Streamlit לצבע כחול עמוק של המותג */
    div.stButton > button {
        background-color: #0f2b5c !important;
        color: #ffffff !important;
        border: 1px solid #0f2b5c !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button:hover {
        background-color: #1e3a8a !important;
        border-color: #1e3a8a !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(15, 43, 92, 0.2) !important;
    }

    @media (max-width: 768px) {
        .hero-main-title { font-size: 2rem; }
        .features-ribbon { flex-direction: column; gap: 10px; }
    }
</style>
""", unsafe_allow_html=True)

# אתחול Session States
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "תלמיד"
if "teacher_authenticated" not in st.session_state:
    st.session_state.teacher_authenticated = False
if "current_room" not in st.session_state:
    st.session_state.current_room = "דף הבית"
if "zoom_chat_history" not in st.session_state:
    st.session_state.zoom_chat_history = []
if "last_voice_reply" not in st.session_state:
    st.session_state.last_voice_reply = None
if "mock_exam_data" not in st.session_state:
    st.session_state.mock_exam_data = None
if "exam_submitted" not in st.session_state:
    st.session_state.exam_submitted = False
if "ai_cache" not in st.session_state:
    st.session_state.ai_cache = {}
if "slides_data" not in st.session_state:
    st.session_state.slides_data = None
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "שליף החירום סגר לי את החומר לפני המבחן בהיסטוריה, הציל לי 20 נקודות."},
        {"name": "נועה ל.", "grade": "כיתה י\"א (ביולוגיה)", "rating": 5, "text": "האתר נראה יוקרתי, נקי מכל השטויות ובאמת מדבר בגובה העיניים."},
        {"name": "מאיה ר.", "grade": "כיתה י\"א (5 יח')", "rating": 5, "text": "מפרק המתמטיקה ומכתב הערעור זה גאונות. המורה קיבלה את הערעור והחזירה נקודות!"}
    ]

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ מפתח GEMINI_API_KEY אינו מוגדר ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

def generate_ai(contents, use_cache=False):
    if use_cache and isinstance(contents, str) and contents in st.session_state.ai_cache:
        return st.session_state.ai_cache[contents]

    models = ["gemini-2.5-flash", "gemini-2.5-pro"]
    last_err = None
    for m in models:
        for _ in range(2):
            try:
                res = client.models.generate_content(model=m, contents=contents)
                if use_cache and isinstance(contents, str):
                    st.session_state.ai_cache[contents] = res
                return res
            except Exception as e:
                last_err = e
                time.sleep(1)
    raise last_err

def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    text = text.strip("`").strip()
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if match:
        text = match.group(1)
    try:
        return json.loads(text)
    except Exception:
        clean_str = re.sub(r"[\r\n\t]+", " ", text)
        return json.loads(clean_str)

def get_tts_audio_url(text):
    clean_text = re.sub(r"[*#_`>\[\]\(\)]", "", text)
    clean_text = clean_text[:200]
    encoded = urllib.parse.quote(clean_text)
    return f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl=iw&client=tw-ob"

def get_whatsapp_share_link(text):
    encoded = urllib.parse.quote(f"היי, מצאתי את זה ב-The Dan Method:\n\n{text[:450]}")
    return f"https://api.whatsapp.com/send?text={encoded}"

# --- סרגל צד נקי ומסודר ---
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="font-size: 26px;">🎓</span>
            <span style="font-size: 1.3rem; font-weight: 800; color: #0f2b5c;">The Dan Method</span>
        </div>
        <div style="font-size: 0.85rem; color: #2563eb; font-weight: 700; margin-bottom: 12px;">בס״ד | לומדים. מתקדמים.</div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("👤 הפרופיל שלך")
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
    no_yap = st.toggle("מצב תכל'ס (מענה ממוקד ולעניין)", value=True)

    if st.session_state.app_mode == "מורה" and st.session_state.teacher_authenticated:
        st.markdown("---")
        if st.button("🔒 נעילת מצב מורה (התנתקות)", use_container_width=True):
            st.session_state.teacher_authenticated = False
            st.session_state.app_mode = "תלמיד"
            st.session_state.current_room = "דף הבית"
            st.rerun()

anti_yap_rule = "השב ישירות לתכל'ס, ללא פסקאות פתיחה או סיום מיותרות." if no_yap else ""
student_context = f"שכבת לימוד: {chosen_grade}, מתמטיקה: {math_units}, אנגלית: {eng_units}, מגמה: {chosen_major}."

# --- סרגל ניווט עליון ---
col_nav_logo, col_nav_mode, col_nav_btn = st.columns([2.5, 1.5, 1])
with col_nav_logo:
    st.markdown("""
        <div class="learnit-navbar">
            <div class="brand-logo-container">
                <div style="width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #0f2b5c, #2563eb); display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 20px;">⚡</span>
                </div>
                <div style="display: flex; flex-direction: column; text-align: left; line-height: 1.1;">
                    <span class="brand-main-name">THE DAN METHOD</span>
                    <span class="brand-sub-badge">STUDY AI • לומדים. מתקדמים.</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_nav_mode:
    mode_selection = st.radio(
        "מצב מערכת:",
        ["תלמיד 🎓", "מורה וצוות 🧑‍🏫"],
        index=0 if st.session_state.app_mode == "תלמיד" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    new_mode = "תלמיד" if "תלמיד" in mode_selection else "מורה"
    if new_mode != st.session_state.app_mode:
        st.session_state.app_mode = new_mode
        st.session_state.current_room = "דף הבית"
        st.rerun()

with col_nav_btn:
    if st.button("🏠 עמוד הבית", key="nav_home_main", use_container_width=True):
        st.session_state.current_room = "דף הבית"
        st.rerun()

# --- בדיקת אבטחה למצב מורה ---
if st.session_state.app_mode == "מורה" and not st.session_state.teacher_authenticated:
    st.markdown("""
        <div class="room-card-dan" style="text-align: center; max-width: 550px; margin: 40px auto; border-right: none; border-top: 5px solid #0f2b5c;">
            <div style="font-size: 48px; margin-bottom: 10px;">🔒</div>
            <h2 style="color: #0f2b5c; margin: 0 0 8px 0; font-weight: 800;">אזור מוגן לצוות הוראה והנהלה</h2>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 20px;">
                כלי המורים כוללים מחווני בחינה ומערכי שיעור.<br>
                כדי למנוע דליפת פתרונות, הגישה מותרת באמצעות קוד מורה בלבד.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_lock1, col_lock2, col_lock3 = st.columns([1, 1.2, 1])
    with col_lock2:
        code_input = st.text_input("הזן קוד מורה:", type="password", placeholder="הזן קוד גישה...")
        if st.button("🔓 כניסה לחדר מורים", use_container_width=True):
            if code_input.strip() == TEACHER_ACCESS_CODE:
                st.session_state.teacher_authenticated = True
                st.success("קוד גישה אומת בהצלחה!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("קוד הגישה אינו תקין.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅️ חזרה למצב תלמיד", use_container_width=True):
            st.session_state.app_mode = "תלמיד"
            st.rerun()
    st.stop()

# ----------------- דף הבית -----------------
if st.session_state.current_room == "דף הבית":
    mode_title = "הדרך שלך להצלחה מתחילה כאן." if st.session_state.app_mode == "תלמיד" else "מרחב הפדגוגיה וההוראה החכמה."
    mode_sub = "לימודים קלים יותר, בכל מקום ובכל זמן." if st.session_state.app_mode == "תלמיד" else "הכנת מערכי שיעור, בחנים ומחוונים בתוך שניות."
    
    st.markdown(f"""
        <div class="hero-banner">
            <h1 class="hero-main-title">{mode_title}</h1>
            <p class="hero-desc">{mode_sub}<br>שאל את ה-AI שאלה, או בחר כלי עבודה:</p>
        </div>
    """, unsafe_allow_html=True)

    query_search = st.text_input("🔍 שאל שאלה או חפש כלי:", placeholder="למשל: 'איך גוזרים פונקציה?', 'מצגת', 'מבחן'...", label_visibility="collapsed")

    if query_search.strip():
        q_lower = query_search.lower()
        if any(w in q_lower for w in ["מצגת", "שקופיות", "slides"]):
            if st.button("📊 כניסה ישירה למחולל המצגות", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()
        elif any(w in q_lower for w in ["זום", "מורה מיה", "שיעור פרטי"]):
            if st.button("🚀 כניסה ישירה לחדר זום עם המורה מיה", use_container_width=True):
                st.session_state.current_room = "חדר זום"
                st.rerun()
        elif any(w in q_lower for w in ["מערך", "שיעור", "מורה"]):
            if st.button("⏱️ כניסה למחולל מערכי שיעור", use_container_width=True):
                st.session_state.current_room = "מערכי שיעור"
                st.rerun()
        elif any(w in q_lower for w in ["חילוץ", "לילה", "בהול"]):
            if st.button("🚨 כניסה ישירה למצב חילוץ ב-3 בלילה", use_container_width=True):
                st.session_state.current_room = "חילוץ לילה"
                st.rerun()
        else:
            with st.spinner("דן AI מנסח תשובה ממוקדת..."):
                try:
                    res_bot = generate_ai(f"אתה עוזר לימודי אישי חכם ({'לתלמיד' if st.session_state.app_mode == 'תלמיד' else 'למורה'}). בהקשר: {student_context}. ענה על השאלה ישירות, ברור וקצר: {query_search}. {anti_yap_rule}", use_cache=True)
                    st.markdown("""
                        <div class="room-card-dan" style="border-right-color: #2563eb;">
                            <div class="room-header-badge">💡 מענה מהיר של דן AI</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(res_bot.text)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_bot.text)}" target="_blank">📲 שתף מענה בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.warning("נסה לשאול שוב.")

    st.markdown("""
        <div class="features-ribbon">
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #e0f2fe; color: #0284c7;">📖</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">תוכן איכותי ומדויק</div>
                    <div style="color:#64748b; font-size:0.8rem;">מכויל לבגרויות ולחטיבה</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #e0f2fe; color: #0284c7;">⏱️</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">חוסך שעות עבודה</div>
                    <div style="color:#64748b; font-size:0.8rem;">הכנה ותרגול ב-60 שניות</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #e0f2fe; color: #0284c7;">👥</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">מותאם לצוות ולתלמידים</div>
                    <div style="color:#64748b; font-size:0.8rem;">התאמה מלאה לרמות ולמגמות</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #fef3c7; color: #d97706;">⭐</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">למידה עצמאית מנצחת</div>
                    <div style="color:#64748b; font-size:0.8rem;">הישגים גבוהים בפחות זמן</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="story-card">
            <div class="story-title">⚡ על השיטה של The Dan Method</div>
            <p class="story-p">
                נמאס לשבת שעות מול סיכומים ארוכים, מורים שמדברים מסביב ואתרי לימוד שנראים כמו שנת 2005.<br>
                <b>The Dan Method</b> נבנה במטרה אחת: לתת לתלמידי ומורי ישראל את הדרך הקצרה, המדויקת והחדה ביותר להצלחה במבחנים ובבגרויות.<br>
                במקום ללמוד 4 שעות ולזכור חצי – מפרקים כל נושא לשלבי ברזל, מסננים חפירות מיותרות, ומלמדים בדיוק לפי מה שהבוחן מחפש בטופס הבדיקה.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="compare-container">
            <h3 style="margin-top: 0; color: #0f2b5c; font-size: 1.3rem; font-weight: 800;">למה The Dan Method ולא סתם בינה מלאכותית רגילה?</h3>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 20px;">ChatGPT ודגמי AI רגילים לא מכירים את בתי הספר בישראל ומבזבזים זמן:</p>
            <table class="compare-table">
                <thead>
                    <tr>
                        <th style="width: 32%;">תכונה</th>
                        <th style="width: 34%; color: #0f2b5c; font-weight: 800;">The Dan Method 🎓</th>
                        <th style="width: 34%;">ChatGPT / מודל רגיל</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="font-weight: 600;">התאמה למערכת החינוך</td>
                        <td style="color: #2563eb; font-weight: 700;">מכויל בול לפי מחווני בגרות, הקבצות וכיתות ז'-י"ב בישראל</td>
                        <td style="color: #64748b;">תשובות גנריות באנגלית שתורגמו לעברית, לא מכיר מחוונים</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">אורך המענה והיעילות</td>
                        <td style="color: #2563eb; font-weight: 700;">מצב תכל'ס (No Yap) – פירוק ממוקד ב-3 שורות בדיוק למה שצריך</td>
                        <td style="color: #64748b;">פסקאות פתיחה וסיום ארוכות ומריחת זמן</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">בדיקת מבחנים וציונים</td>
                        <td style="color: #2563eb; font-weight: 700;">חישוב ציון אמיתי מתוך 100 עם הורדת נקודות לפי נימוקים חסרים</td>
                        <td style="color: #64748b;">סתם מחמיא לתשובה ולא יודע לתת ציון בגרות אמיתי</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">חילוץ רגע לפני מבחן</td>
                        <td style="color: #2563eb; font-weight: 700;">שליף 60 שניות, מצב חילוץ בלילה ורנטגן שגיאות</td>
                        <td style="color: #64748b;">מייצר טקסטים ענקיים שבלתי אפשרי לקרוא תחת לחץ</td>
                    </tr>
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.app_mode == "תלמיד":
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h2 style="font-size: 1.5rem; font-weight: 800; color: #0f2b5c; margin: 0;">מרכז הלמידה של התלמיד</h2>
                <span style="color: #64748b; font-weight: 600; font-size: 0.95rem;">בחר כלי כדי להתחיל</span>
            </div>
        """, unsafe_allow_html=True)

        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">📊</div><h4 style="margin:4px 0; color:#0f2b5c;">מחולל מצגות</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">שקופיות והערות להצגה</p></div>', unsafe_allow_html=True)
            if st.button("בנה מצגת", key="btn_slides_t", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()

        with col_t2:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">📹</div><h4 style="margin:4px 0; color:#0f2b5c;">חדר זום חי</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">שיעור קולי 1-על-1</p></div>', unsafe_allow_html=True)
            if st.button("היכנס לזום", key="btn_zoom_t", use_container_width=True):
                st.session_state.current_room = "חדר זום"
                st.rerun()

        with col_t3:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">📸</div><h4 style="margin:4px 0; color:#0f2b5c;">סורק תרגילים</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פיענוח מתמונה ודף</p></div>', unsafe_allow_html=True)
            if st.button("פתח סורק", key="btn_scanner_t", use_container_width=True):
                st.session_state.current_room = "סורק תמונות"
                st.rerun()

        with col_t4:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">📝</div><h4 style="margin:4px 0; color:#0f2b5c;">מבחני דמה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">סימולציה עם מחוון</p></div>', unsafe_allow_html=True)
            if st.button("בנה מבחן", key="btn_exam_t", use_container_width=True):
                st.session_state.current_room = "מבחני דמה"
                st.rerun()

        col_t5, col_t6, col_t7, col_t8 = st.columns(4)
        with col_t5:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🆘</div><h4 style="margin:4px 0; color:#0f2b5c;">חילוץ ב-3 בלילה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">תוכנית הצלה לפני מבחן</p></div>', unsafe_allow_html=True)
            if st.button("פתח חילוץ לילה", key="btn_panic_t", use_container_width=True):
                st.session_state.current_room = "חילוץ לילה"
                st.rerun()

        with col_t6:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🚨</div><h4 style="margin:4px 0; color:#0f2b5c;">שליף חירום</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">60 שניות לפני מבחן</p></div>', unsafe_allow_html=True)
            if st.button("הצג שליף", key="btn_cheat_t", use_container_width=True):
                st.session_state.current_room = "שליף חירום"
                st.rerun()

        with col_t7:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🩻</div><h4 style="margin:4px 0; color:#0f2b5c;">רנטגן שגיאות</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">מלכודות הבוחנים</p></div>', unsafe_allow_html=True)
            if st.button("גלה מוקשים", key="btn_xray_t", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()

        with col_t8:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">⚖️</div><h4 style="margin:4px 0; color:#0f2b5c;">מכתב ערעור</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">החזרת נקודות ממורים</p></div>', unsafe_allow_html=True)
            if st.button("נסח ערעור", key="btn_appeal_t", use_container_width=True):
                st.session_state.current_room = "ערעור"
                st.rerun()

        col_t9, col_t10, col_t11, col_t12 = st.columns(4)
        with col_t9:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">📐</div><h4 style="margin:4px 0; color:#0f2b5c;">מעבדת מתמטיקה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פירוק שלב-אחר-שלב</p></div>', unsafe_allow_html=True)
            if st.button("פרק תרגיל", key="btn_math_t", use_container_width=True):
                st.session_state.current_room = "מעבדת מתמטיקה"
                st.rerun()

        with col_t10:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🎴</div><h4 style="margin:4px 0; color:#0f2b5c;">כרטיסיות חזרה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">שינון מושגים מהיר</p></div>', unsafe_allow_html=True)
            if st.button("פתח כרטיסיות", key="btn_flash_t", use_container_width=True):
                st.session_state.current_room = "כרטיסיות"
                st.rerun()

        with col_t11:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🧘</div><h4 style="margin:4px 0; color:#0f2b5c;">רווחה והפחתת לחץ</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">נשימות 30 שנ\' ופוקוס</p></div>', unsafe_allow_html=True)
            if st.button("מרחב רווחה", key="btn_well_t", use_container_width=True):
                st.session_state.current_room = "רווחה"
                st.rerun()

        with col_t12:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🎯</div><h4 style="margin:4px 0; color:#0f2b5c;">מחשבון בגרות</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">חיזוי הציון הסופי</p></div>', unsafe_allow_html=True)
            if st.button("חשב ציון יעד", key="btn_calc_t", use_container_width=True):
                st.session_state.current_room = "מחשבון"
                st.rerun()

    else:
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h2 style="font-size: 1.5rem; font-weight: 800; color: #0f2b5c; margin: 0;">מרכז הפדגוגיה והכלים למורים 🔒</h2>
                <span style="color: #2563eb; font-weight: 700; font-size: 0.95rem;">● מחובר כאנשי צוות מאומתים</span>
            </div>
        """, unsafe_allow_html=True)

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">📊</div><h4 style="margin:4px 0; color:#0f2b5c;">מחולל מצגות לשיעור</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">מבנה שקופיות והערות מורה</p></div>', unsafe_allow_html=True)
            if st.button("בנה מצגת לשיעור", key="btn_slides_m", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()

        with col_m2:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">⏱️</div><h4 style="margin:4px 0; color:#0f2b5c;">מערך שיעור (45 דק\')</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פתיחה, גוף ותרגול מדורג</p></div>', unsafe_allow_html=True)
            if st.button("בנה מערך שיעור", key="btn_lesson_m", use_container_width=True):
                st.session_state.current_room = "מערכי שיעור"
                st.rerun()

        with col_m3:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">📝</div><h4 style="margin:4px 0; color:#0f2b5c;">בוחן פתע + מחוון</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">טופס כיתתי ומחוון בדיקה</p></div>', unsafe_allow_html=True)
            if st.button("ייצר בוחן ומחוון", key="btn_quiz_m", use_container_width=True):
                st.session_state.current_room = "בחנים ומחוונים"
                st.rerun()

        with col_m4:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🏛️</div><h4 style="margin:4px 0; color:#0f2b5c;">מכתב רשמי להנהלה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פדגוגיה והצגת פיילוט ליועצת</p></div>', unsafe_allow_html=True)
            if st.button("הצג מכתב להנהלה", key="btn_letter_m", use_container_width=True):
                st.session_state.current_room = "הנהלה"
                st.rerun()

        col_m5, col_m6, col_m7, col_m8 = st.columns(4)
        with col_m5:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🖨️</div><h4 style="margin:4px 0; color:#0f2b5c;">דפי עבודה להדפסה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">דפי תרגול מדורגים לכיתה</p></div>', unsafe_allow_html=True)
            if st.button("הפק דף עבודה", key="btn_print_m", use_container_width=True):
                st.session_state.current_room = "דפי הדפסה"
                st.rerun()

        with col_m6:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🩻</div><h4 style="margin:4px 0; color:#0f2b5c;">איתור מוקשי למידה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">הטעויות הנפוצות בנושא</p></div>', unsafe_allow_html=True)
            if st.button("בדוק מלכודות", key="btn_xray_m", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()

        with col_m7:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🧘</div><h4 style="margin:4px 0; color:#0f2b5c;">ארגז כלים ליועצת</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">הפחתת חרדת בחינות</p></div>', unsafe_allow_html=True)
            if st.button("ארגז כלים ליועצת", key="btn_well_m", use_container_width=True):
                st.session_state.current_room = "רווחה"
                st.rerun()

        with col_m8:
            st.markdown('<div class="room-tile"><div style="font-size:30px;">🗣️</div><h4 style="margin:4px 0; color:#0f2b5c;">מפשט שאלות</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">התאמת ניסוח לתלמידים</p></div>', unsafe_allow_html=True)
            if st.button("פשט שאלה", key="btn_street_m", use_container_width=True):
                st.session_state.current_room = "מתרגם"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⭐ מה שאומרים על The Dan Method")
    col_rev1, col_rev2 = st.columns([1.8, 1.2])
    with col_rev1:
        for r in st.session_state.reviews:
            stars = "⭐" * r["rating"]
            st.markdown(f"""
                <div class="room-card-dan" style="padding: 16px; margin-bottom: 12px; border-right-width: 4px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b>{r['name']}</b> ({r['grade']})
                        <span style="font-size:0.9rem;">{stars}</span>
                    </div>
                    <p style="color: #475569; margin: 6px 0 0 0; font-size: 0.95rem;">{r['text']}</p>
                </div>
            """, unsafe_allow_html=True)
            
    with col_rev2:
        st.markdown('<div class="room-card-dan" style="border-right-width: 4px;"><h4 style="margin-top:0; color:#0f2b5c;">✍️ הוסף חוות דעת:</h4>', unsafe_allow_html=True)
        with st.form("feedback_form_home", clear_on_submit=True):
            fb_name = st.text_input("שם או כינוי:")
            fb_grade = st.selectbox("תפקיד / כיתה:", ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב", "מורה מקצועי", "מחנך / יועצת"], index=2)
            fb_rating = st.slider("דירוג (כוכבים):", 1, 5, 5)
            fb_text = st.text_area("איך הפלטפורמה עזרה לך?")
            submitted_fb = st.form_submit_button("שלח חוות דעת 🚀")
            if submitted_fb:
                if not fb_text.strip():
                    st.warning("נא לכתוב כמה מילים.")
                else:
                    st.session_state.reviews.insert(0, {
                        "name": fb_name.strip() if fb_name.strip() else "אנונימי",
                        "grade": fb_grade,
                        "rating": fb_rating,
                        "text": fb_text.strip()
                    })
                    st.success("תודה! חוות הדעת נוספה בהצלחה.")
                    st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- חדר: מחולל מצגות -----------------
elif st.session_state.current_room == "מצגות":
    st.markdown('<div class="room-header-badge">📊 The Dan Method Deck</div>', unsafe_allow_html=True)
    st.title("מחולל מצגות מקצועי")
    st.caption("בונה שלד שקופיות שלם: כותרות מנצחות, נקודות תכל'ס והערות לדובר.")
    
    col_sl1, col_sl2 = st.columns(2)
    with col_sl1:
        slide_topic = st.text_input("נושא המצגת:", placeholder="למשל: תהליך הפוטוסינתזה, מלחמת העולם הראשונה...")
        slide_subject = st.selectbox("מקצוע:", ["היסטוריה", "ביולוגיה", "אזרחות", "ספרות", "אנגלית", "מדעים", "גיאוגרפיה", chosen_major])
    with col_sl2:
        slide_count = st.slider("מספר שקופיות:", 3, 8, 5)
        slide_goal = st.selectbox("מטרת המצגת:", [
            "הצגה פרונטלית של תלמיד מול הכיתה (5 דקות)",
            "מצגת שיעור של מורה להקניה ותרגול",
            "סיכום פרויקט עבודת חקר / בגרות"
        ])

    if st.button("🔨 צור לי שלד מצגת מושלם!", use_container_width=True):
        if not slide_topic.strip():
            st.warning("נא להזין נושא למצגת.")
        else:
            prompt_slides = (
                f"אתה מומחה להכנת מצגות לימודיות מעולות עבור מערכת החינוך בישראל ({student_context}).\n"
                f"נושא המצגת: {slide_topic}, מקצוע: {slide_subject}, מספר שקופיות: {slide_count}, מטרה: {slide_goal}.\n\n"
                "החזר אך ורק מערך JSON תקין שבו כל איבר מייצג שקופית:\n"
                "[\n"
                "  {\n"
                '    "slide_num": 1,\n'
                '    "title": "כותרת קצרה לשקופית",\n'
                '    "bullets": ["נקודה 1", "נקודה 2", "נקודה 3"],\n'
                '    "visual_idea": "תיאור קצר לתמונה",\n'
                '    "speaker_notes": "הסבר בעל פה לדובר (עד 3 משפטים)"\n'
                "  }\n"
                "]\n"
                "אל תוסיף שום טקסט מחוץ ל-JSON. שמור על תחביר JSON תקין."
            )
            with st.spinner("בונה שקופיות והערות דובר..."):
                try:
                    res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt_slides,
                        config={"response_mime_type": "application/json"}
                    )
                    st.session_state.slides_data = json.loads(res.text)
                    st.success("המצגת מוכנה! השקופיות מופיעות למטה.")
                    st.rerun()
                except Exception:
                    try:
                        res = generate_ai(prompt_slides)
                        st.session_state.slides_data = extract_json(res.text)
                        st.success("המצגת מוכנה! השקופיות מופיעות למטה.")
                        st.rerun()
                    except Exception as err:
                        st.error(f"שגיאה בבניית המצגת: {err}")

    if st.session_state.slides_data:
        st.markdown("---")
        full_text_for_share = f"מצגת בנושא: {slide_topic}\n\n"
        for s in st.session_state.slides_data:
            bullets_formatted = "\n".join([f"• {b}" for b in s.get("bullets", [])])
            st.markdown(f"""
                <div class="slide-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#0f2b5c;">שקופית {s['slide_num']}: {s['title']}</h3>
                        <span style="background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:8px; font-weight:700; font-size:0.85rem;">🖼️ רעיון ויזואלי: {s.get('visual_idea', '')}</span>
                    </div>
                    <div style="margin-top:12px; font-size:1.05rem; line-height:1.7;">
                        <b>מה מקרינים על הלוח:</b><br>
                        {bullets_formatted}
                    </div>
                    <div class="slide-speaker-notes">
                        <b>🗣️ הערות דובר (מה לומר בכיתה):</b><br>
                        {s.get('speaker_notes', '')}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            full_text_for_share += f"שקופית {s['slide_num']}: {s['title']}\n{bullets_formatted}\n\n"

        st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(full_text_for_share)}" target="_blank">📲 שתף את שלד המצגת בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: מערכי שיעור -----------------
elif st.session_state.current_room == "מערכי שיעור":
    st.markdown('<div class="room-header-badge">⏱️ Lesson Builder</div>', unsafe_allow_html=True)
    st.title("מחולל מערך שיעור ממוקד (45 דקות)")
    st.caption("כלי עבודה פדגוגי למורים: בניית שיעור מובנה עם זמנים מדויקים.")
    
    l_sub = st.text_input("מקצוע השיעור:")
    l_top = st.text_input("נושא השיעור:")
    if st.button("בנה מערך שיעור 📚", use_container_width=True):
        if l_sub and l_top:
            with st.spinner("בונה מערך שיעור..."):
                prompt_plan = f"בנה מערך שיעור של 45 דק' לכיתה {chosen_grade}. מקצוע: {l_sub}, נושא: {l_top}. חלק לזמנים מדויקים: פתיחה (7 דק'), גוף (23 דק'), תרגול מדורג (10 דק'), סיכום (5 דק')."
                res_plan = generate_ai(prompt_plan)
                st.markdown(f'<div class="room-card-dan">{res_plan.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_plan.text)}" target="_blank">📲 שתף מערך שיעור בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: בחנים ומחוונים -----------------
elif st.session_state.current_room == "בחנים ומחוונים":
    st.markdown('<div class="room-header-badge">📝 Assessment & Rubric</div>', unsafe_allow_html=True)
    st.title("מחולל בוחן כיתתי + מחוון משרד החינוך")
    st.caption("הפקת בוחן קצר של 15 דקות לצד מחוון בדיקה מלא עם חלוקת נקודות.")
    
    q_sub = st.text_input("מקצוע הבוחן:")
    q_top = st.text_input("נושא הבוחן המדויק:")
    if st.button("ייצר בוחן ומחוון 📄", use_container_width=True):
        if q_sub and q_top:
            with st.spinner("מכין שאלות ומחוון..."):
                prompt_quiz = f"צור בוחן של 15 דקות ומחוון בדיקה לכיתה {chosen_grade}. מקצוע: {q_sub}, נושא: {q_top}. טופס לתלמיד בנפרד ומחוון מלא למורה בנפרד."
                res_quiz = generate_ai(prompt_quiz)
                st.markdown(f'<div class="room-card-dan">{res_quiz.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_quiz.text)}" target="_blank">📲 שתף בוחן ומחוון בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: הנהלה -----------------
elif st.session_state.current_room == "הנהלה":
    st.markdown('<div class="room-header-badge">🏛️ School Leadership</div>', unsafe_allow_html=True)
    st.title("מכתב רשמי להנהלת בית הספר ולצוות הייעוץ")
    st.markdown("""
        <div class="room-card-dan" style="border-right-color: #0f2b5c;">
            <h3 style="margin-top:0; color:#0f2b5c;">לכבוד: מנהלת בית הספר והיועצת החינוכית</h3>
            <b>הנדון: שילוב פלטפורמת 'The Dan Method' ככלי פדגוגי מסייע ללמידה עצמאית והפחתת חרדת בחינות</b>
            <p style="margin-top: 10px; line-height: 1.7; color: #334155;">
                מערכת <b>The Dan Method</b> פותחה מתוך הבנת האתגרים הייחודיים של תלמידי חטיבת הביניים והחטיבה העליונה בישראל, ומכוילת על פי תוכניות הלימודים ומחווני הבגרות של משרד החינוך.<br><br>
                המערכת מעודדת למידה עצמאית, סוגרת פערים לימודיים, מסייעת בהפחתת חרדת בחינות באמצעות מרחב רווחה ותרגול מודרך, וחוסכת שעות יקרות של הכנת חומרים לצוות ההוראה.
            </p>
            <div class="room-highlight-box">
                <b>הצעה לפיילוט:</b> קיום התנסות מבוקרת בכיתה אחת לקראת מבחן קרוב למדידת שביעות הרצון וההישגים.
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link("מכתב רשמי על The Dan Method להנהלה ולייעוץ החינוכי.")}" target="_blank">📲 שתף מכתב להנהלה בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: רווחה והפחתת לחץ -----------------
elif st.session_state.current_room == "רווחה":
    st.markdown('<div class="room-header-badge">🧘 Wellbeing & Focus</div>', unsafe_allow_html=True)
    st.title("מרחב רווחה, ויסות והפחתת לחץ")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("""
            <div class="room-card-dan">
                <h4 style="margin-top:0; color:#0f2b5c;">תרגיל נשימה להורדת דופק (Box Breathing)</h4>
                <p>1. שאיפה (4 שנ') 🌬️ | 2. החזקה (4 שנ') ⏸️ | 3. נשיפה (4 שנ') 💨 | 4. המתנה (4 שנ') 🧘</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("הפעל טיימר נשימה של 30 שניות ⏱️"):
            prog = st.progress(0)
            status_text = st.empty()
            phases = ["שאף מהאף... 🌬️", "החזק... ⏸️", "נשוף לאט... 💨", "המתן ברוגע... 🧘"]
            for i in range(30):
                time.sleep(1)
                prog.progress((i + 1) / 30)
                status_text.text(phases[i % 4])
            st.success("מעולה! עכשיו המוח רגוע ומוכן לקלוט חומר בצורה חדה.")

    with col_w2:
        st.markdown("""
            <div class="room-card-dan">
                <h4 style="margin-top:0; color:#0f2b5c;">טיימר פוקוס עמוק (Deep Focus)</h4>
                <p style="color:#64748b;">למידה ממוקדת של 25 דקות ללא הסחות דעת:</p>
                <div style="font-size:2.8rem; font-weight:900; color:#0f2b5c; text-align:center;">25:00</div>
            </div>
        """, unsafe_allow_html=True)

# ----------------- חדר: חילוץ ב-3 בלילה -----------------
elif st.session_state.current_room == "חילוץ לילה":
    st.markdown('<div class="room-header-badge">🆘 Panic Rescue</div>', unsafe_allow_html=True)
    st.title("מצב חילוץ ב-3 בלילה")
    st.caption("יש לך מבחן מחר בבוקר? תוכנית הצלה קריטית לציון עובר ומעלה.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        panic_sub = st.text_input("מקצוע המבחן:")
        panic_top = st.text_area("חומר המבחן:")
    with col_p2:
        hours_left = st.slider("שעות עד היציאה מהבית:", 1, 8, 3)
    
    if st.button("🚨 הצל אותי עכשיו!", use_container_width=True):
        if panic_sub and panic_top:
            with st.spinner("מחלץ תוכנית הצלה..."):
                prompt = f"תוכנית חירום לתלמיד ב-{student_context}. מקצוע: {panic_sub}, חומר: {panic_top}, שעות: {hours_left}. 3 מושגי חובה, טריק הבחינה ומשפט פתיחה למאיות."
                res = generate_ai(prompt)
                st.markdown(f"""
                    <div class="room-card-dan" style="border-right-color: #ef4444; background: #fffaf0;">
                        <h4 style="color:#0f2b5c; margin-top:0;">תוכנית הצלה ממוקדת:</h4>
                        {res.text}
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף תוכנית הצלה בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: רנטגן שגיאות -----------------
elif st.session_state.current_room == "רנטגן":
    st.markdown('<div class="room-header-badge">🩻 Mistake X-Ray</div>', unsafe_allow_html=True)
    st.title("רנטגן שגיאות ומלכודות בוחנים")
    st.caption("חשיפת המוקשים שהבוחנים אוהבים להפיל בהם תלמידים.")
    
    xray_topic = st.text_input("איזה נושא או תרגיל לבדוק?")
    if st.button("חשוף מלכודות ⚡", use_container_width=True):
        if xray_topic:
            with st.spinner("מבצע צילום רנטגן..."):
                prompt = f"חשוף מלכודות בוחנים בנושא: {xray_topic} עבור {student_context}."
                res = generate_ai(prompt)
                st.markdown(f'<div class="room-card-dan">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף מוקשים בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: מכתב ערעור -----------------
elif st.session_state.current_room == "ערעור":
    st.markdown('<div class="room-header-badge">⚖️ Grade Appeal</div>', unsafe_allow_html=True)
    st.title("מחולל מכתב ערעור על ציון")
    st.caption("ניסוח רשמי ומנומק לפי מחוון משרד החינוך להחזרת נקודות.")
    
    c_sub = st.text_input("מקצוע המבחן:")
    c_q = st.text_area("השאלה:")
    c_ans = st.text_area("תשובתך:")
    c_lost = st.text_input("הערת המורה ונקודות שירדו:")
    if st.button("נסח מכתב ערעור 🚀", use_container_width=True):
        if c_sub and c_ans:
            with st.spinner("מנסח מכתב ערעור..."):
                prompt = f"נסח ערעור רשמי ומנומק למורה עבור {student_context}. מקצוע: {c_sub}, שאלה: {c_q}, תשובה: {c_ans}, הערה: {c_lost}."
                res = generate_ai(prompt)
                st.markdown(f'<div class="room-card-dan">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף נוסח ערעור בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: כרטיסיות חזרה -----------------
elif st.session_state.current_room == "כרטיסיות":
    st.markdown('<div class="room-header-badge">🎴 Flashcards</div>', unsafe_allow_html=True)
    st.title("כרטיסיות חזרה מהירות")
    st.caption("שינון מושגי מפתח ונוסחאות תוך כדי תנועה.")
    
    f_topic = st.text_input("נושא הכרטיסיות:")
    if st.button("ייצר כרטיסיות ⚡", use_container_width=True):
        if f_topic:
            with st.spinner("מכין כרטיסיות..."):
                prompt = f"צור 4 כרטיסיות בפורמט JSON בלבד בנושא {f_topic}: [{{\"front\":\"שאלה\",\"back\":\"תשובה\"}}]"
                res = generate_ai(prompt)
                st.session_state["flashcards_data"] = extract_json(res.text)
    if "flashcards_data" in st.session_state:
        for i, card in enumerate(st.session_state["flashcards_data"]):
            with st.expander(f"🎴 כרטיסייה {i+1}: {card.get('front', '')}"):
                st.markdown(f'<div class="room-highlight-box">{card.get("back", "")}</div>', unsafe_allow_html=True)

# ----------------- חדר: מחשבון בגרות -----------------
elif st.session_state.current_room == "מחשבון":
    st.markdown('<div class="room-header-badge">🎯 Score Calculator</div>', unsafe_allow_html=True)
    st.title("מחשבון ציון יעד לבגרות ומגן")
    st.caption("חישוב הציון הנדרש בבגרות להשגת הציון הסופי המבוקש.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        magen_score = st.number_input("ציון מגן:", 0, 100, 85)
        magen_weight = st.selectbox("משקל המגן באחוזים:", [30, 50, 40, 20], index=0)
    with col_c2:
        target_final = st.number_input("ציון סופי מבוקש:", 60, 100, 90)
    
    bagrut_weight = 100 - magen_weight
    needed_bagrut = (target_final * 100 - (magen_score * magen_weight)) / bagrut_weight
    st.markdown("---")
    if needed_bagrut > 100:
        st.error(f"תצטרך מעל 100 בבגרות ({needed_bagrut:.1f}) כדי להגיע ליעד זה.")
    elif needed_bagrut <= 0:
        st.success("המגן שלך מספיק גבוה כדי להגיע ליעד בקלות!")
    else:
        st.markdown(f"""
            <div class="room-card-dan">
                <h3 style="color:#0f2b5c; margin:0;">🎯 עליך להוציא לפחות {round(needed_bagrut)} בבחינת הבגרות</h3>
                <p style="color:#64748b; margin:6px 0 0 0;">לפי משקל מגן של {magen_weight}% ומשקל בגרות של {bagrut_weight}%.</p>
            </div>
        """, unsafe_allow_html=True)

# ----------------- חדר: מתרגם סלנג -----------------
elif st.session_state.current_room == "מתרגם":
    st.markdown('<div class="room-header-badge">🗣️ Street Translator</div>', unsafe_allow_html=True)
    st.title("מתרגם סלנג לימודי לתכל'ס")
    st.caption("פירוק שאלות יבשות ומסורבלות לשפת תלמידים פשוטה.")
    
    dry_question = st.text_area("הדבק את השאלה המסורבלת:")
    if st.button("תרגם לתכל'ס 🧠", use_container_width=True):
        if dry_question:
            with st.spinner("מתרגם..."):
                prompt = f"תרגם את השאלה לתכל'ס פשוט לתלמיד ב-{student_context}:\n{dry_question}"
                res = generate_ai(prompt)
                st.markdown(f'<div class="room-card-dan">{res.text}</div>', unsafe_allow_html=True)

# ----------------- חדר: זום חי -----------------
elif st.session_state.current_room == "חדר זום":
    st.markdown('<div class="room-header-badge">📹 Live Zoom Tutor</div>', unsafe_allow_html=True)
    st.title("שיעור פרטי בזום עם המורה מיה")
    
    col_z1, col_z2 = st.columns([1, 2])
    with col_z1:
        st.markdown("""
            <div class="zoom-learnit-card">
                <div class="teacher-circle-box">
                    <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80" alt="המורה מיה">
                </div>
                <h4 style="margin:0; color:#0f2b5c;">המורה מיה</h4>
                <p style="color:#64748b; font-size:0.85rem; margin-top:4px;">מחוברת לשיחה חיה</p>
            </div>
        """, unsafe_allow_html=True)
        z_subject = st.selectbox("בחר מקצוע:", ["מתמטיקה", "אנגלית", "היסטוריה", "לשון"])

    with col_z2:
        chat_box = st.container(height=300)
        with chat_box:
            for m in st.session_state.zoom_chat_history:
                with st.chat_message(m["role"]):
                    st.write(m["content"])
        text_spoken = st.chat_input("כתוב כאן למורה מיה...")
        if text_spoken:
            st.session_state.zoom_chat_history.append({"role": "user", "content": text_spoken})
            res_zoom = generate_ai(f"את המורה מיה בשיעור קצר בגובה העיניים על {z_subject} עבור {student_context}. עני עד 2 משפטים ושאלי שאלה: {text_spoken}")
            st.session_state.zoom_chat_history.append({"role": "assistant", "content": res_zoom.text})
            st.rerun()

# ----------------- חדר: סורק תמונות -----------------
elif st.session_state.current_room == "סורק תמונות":
    st.markdown('<div class="room-header-badge">📸 Exercise Scanner</div>', unsafe_allow_html=True)
    st.title("סורק תמונות ושיעורי בית")
    photo_topic = st.text_input("מה החומר או המקצוע?")
    file = st.file_uploader("בחר קובץ תמונה:", type=["png", "jpg", "jpeg"])
    if st.button("פענח ופתור ⚡", use_container_width=True):
        if file and photo_topic:
            img = Image.open(file)
            with st.spinner("מפענח..."):
                res = generate_ai([f"פתור והסבר שלב אחרי שלב עבור {student_context}. נושא: {photo_topic}", img])
                st.markdown(f'<div class="room-card-dan">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף פתרון בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: מבחני דמה -----------------
elif st.session_state.current_room == "מבחני דמה":
    st.markdown('<div class="room-header-badge">📝 Mock Exam</div>', unsafe_allow_html=True)
    st.title("מחולל מבחני דמה מלאים")
    exam_subject = st.selectbox("מקצוע המבחן:", ["מתמטיקה", "היסטוריה", "אזרחות", "אנגלית"])
    exam_topic = st.text_input("הנושא:")
    if st.button("צור מבחן דמה 🔨", use_container_width=True):
        if exam_topic:
            with st.spinner("בונה מבחן..."):
                prompt = f"צור מבחן דמה ב-JSON עבור {student_context}. מקצוע: {exam_subject}, נושא: {exam_topic}."
                res = generate_ai(prompt)
                st.session_state.mock_exam_data = extract_json(res.text)
    if st.session_state.mock_exam_data:
        st.markdown(f'<div class="room-card-dan">{json.dumps(st.session_state.mock_exam_data, ensure_ascii=False, indent=2)}</div>', unsafe_allow_html=True)

# ----------------- חדר: מעבדת מתמטיקה -----------------
elif st.session_state.current_room == "מעבדת מתמטיקה":
    st.markdown('<div class="room-header-badge">📐 Math Lab</div>', unsafe_allow_html=True)
    st.title("מעבדת פירוק מתמטיקה ומדעים")
    m_topic = st.text_input("נושא:")
    m_input = st.text_area("תרגיל:")
    if st.button("פרק תרגיל שלב-אחר-שלב 🧠", use_container_width=True):
        if m_topic and m_input:
            with st.spinner("פותר..."):
                res = generate_ai(f"פתור שלב אחרי שלב עבור {student_context}. נושא: {m_topic}, תרגיל: {m_input}")
                st.markdown(f'<div class="room-card-dan">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף פתרון בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: שליף חירום -----------------
elif st.session_state.current_room == "שליף חירום":
    st.markdown('<div class="room-header-badge">🚨 Cheat Sheet</div>', unsafe_allow_html=True)
    st.title("שליף חירום: 60 שניות לפני מבחן")
    p_topic = st.text_input("נושא המבחן:")
    if st.button("הצל אותי עכשיו ⚡", use_container_width=True):
        if p_topic:
            with st.spinner("מחלץ שליף..."):
                res = generate_ai(f"שליף קצר של 60 שניות לפני מבחן על {p_topic} עבור {student_context}.")
                st.markdown(f'<div class="room-card-dan" style="border-right-color:#f59e0b; background:#fffdf5;">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף שליף בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: דפי הדפסה -----------------
elif st.session_state.current_room == "דפי הדפסה":
    st.markdown('<div class="room-header-badge">🖨️ Printable Worksheets</div>', unsafe_allow_html=True)
    st.title("מחולל דפי תרגול להדפסה")
    pr_top = st.text_input("נושא הדף:")
    if st.button("ייצר דף עבודה 📄", use_container_width=True):
        if pr_top:
            with st.spinner("מייצר דף..."):
                res = generate_ai(f"צור דף תרגול ומבחן מעוצב בעברית בנושא {pr_top} עבור {student_context}.")
                st.markdown(f'<div class="room-card-dan">{res.text}</div>', unsafe_allow_html=True)
                st.markdown("""<button onclick="window.print()" style="padding: 10px 20px; background: #0f2b5c; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🖨️ הדפס דף זה</button>""", unsafe_allow_html=True)
