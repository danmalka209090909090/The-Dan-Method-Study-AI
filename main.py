import streamlit as st
from google import genai
from PIL import Image
import requests
from io import BytesIO
import json
import re
import time
import urllib.parse

# קוד גישה סודי לחדר מורים והנהלה (ניתן לשינוי כאן)
TEACHER_ACCESS_CODE = "DAN100"

st.set_page_config(
    page_title="The Dan Method | לומדים. מתקדמים.",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# שפת עיצוב LearnIt, פונט Assistant, תיקון כיוון סליידרים והסרת מעטפת Streamlit
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700;800;900&display=swap');

    * {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* הסתרת כל מעטפת הניהול והאייקונים המובנים של Streamlit */
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

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-left: 1px solid #e2e8f0;
    }

    /* תיקון סליידרים שלא יתהפכו ב-RTL */
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
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
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
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
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

    /* שורת יתרונות */
    .features-ribbon {
        display: flex;
        justify-content: space-around;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 14px 20px;
        margin-bottom: 24px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
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

    /* תיבת הסבר על השיטה */
    .story-card {
        background: linear-gradient(135deg, #0f2b5c 0%, #1e3a8a 100%);
        color: #ffffff;
        border-radius: 20px;
        padding: 28px 30px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(15, 43, 92, 0.12);
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

    /* טבלת השוואה */
    .compare-container {
        margin-bottom: 30px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 26px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
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

    /* כרטיסיות חדרים פסטליות */
    .room-tile {
        border-radius: 16px;
        padding: 18px 14px;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 12px;
        transition: transform 0.15s ease;
    }
    .room-tile:hover {
        transform: translateY(-2px);
    }
    .cat-purple { background: #f3e8ff; border-color: #e9d5ff; }
    .cat-blue   { background: #e0f2fe; border-color: #bae6fd; }
    .cat-green  { background: #dcfce7; border-color: #bbf7d0; }
    .cat-orange { background: #ffedd5; border-color: #fed7aa; }
    .cat-yellow { background: #fef9c3; border-color: #fef08a; }
    .cat-red    { background: #fee2e2; border-color: #fca5a5; }
    .cat-teal   { background: #ccfbf1; border-color: #99f6e4; }
    .cat-indigo { background: #e0e7ff; border-color: #c7d2fe; }
    .cat-pink   { background: #fce7f3; border-color: #fbcfe8; }
    .cat-slate  { background: #f1f5f9; border-color: #e2e8f0; }

    /* כרטיסיית שקופית מעוצבת למצגות */
    .slide-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        border-right: 5px solid #2563eb;
    }
    .slide-speaker-notes {
        background: #f8fafc;
        border: 1px dashed #cbd5e1;
        border-radius: 12px;
        padding: 14px;
        margin-top: 12px;
        color: #334155;
        font-size: 0.95rem;
    }

    /* כרטיסיית חדר זום ומורה */
    .zoom-learnit-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        text-align: center;
    }
    .teacher-circle-box {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        margin: 0 auto 12px auto;
        overflow: hidden;
        border: 3px solid #3b82f6;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.25);
    }
    .teacher-circle-box img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .clean-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 16px;
    }
    .panic-box {
        background: #fef2f2;
        border: 2px solid #ef4444;
        border-radius: 16px;
        padding: 24px;
        color: #991b1b;
        margin-top: 14px;
        line-height: 1.7;
    }
    .badge-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
        border: 2px solid #3b82f6;
        color: white;
        border-radius: 20px;
        padding: 26px;
        text-align: center;
        box-shadow: 0 8px 30px rgba(30, 58, 138, 0.2);
    }
    .cheat-learnit {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 16px;
        padding: 24px;
        color: #92400e;
        margin-top: 14px;
        line-height: 1.7;
    }
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

    @media (max-width: 768px) {
        .hero-main-title { font-size: 2rem; }
        .features-ribbon { flex-direction: column; gap: 10px; }
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
if "solved_count" not in st.session_state:
    st.session_state.solved_count = 7
if "slides_data" not in st.session_state:
    st.session_state.slides_data = None
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "השליף חירום סגר לי את החומר לפני המבחן בהיסטוריה, הציל לי 20 נקודות."},
        {"name": "נועה ל.", "grade": "כיתה י\"א (ביולוגיה)", "rating": 5, "text": "האתר נראה יוקרתי, נקי מכל השטויות ובאמת מדבר בגובה העיניים."},
        {"name": "מאיה ר.", "grade": "כיתה י\"א (5 יח')", "rating": 5, "text": "מפרק המתמטיקה ומכתב הערעור זה גאונות. המורה קיבלה את הערעור והחזירה לי 9 נקודות!"}
    ]

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ מפתח GEMINI_API_KEY אינו מוגדר ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

def generate_ai(contents, use_cache=False):
    if use_cache and isinstance(contents, str) and contents in st.session_state.ai_cache:
        return st.session_state.ai_cache[contents]

    models = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
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
    text = re.sub(r"^
```json\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"^
```\s*", "", text.strip(), flags=re.MULTILINE)
    return json.loads(text.strip("`").strip())

def get_tts_audio_url(text):
    clean_text = re.sub(r"[*#_`>\[\]\(\)]", "", text)
    clean_text = clean_text[:200]
    encoded = urllib.parse.quote(clean_text)
    return f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl=iw&client=tw-ob"

def get_whatsapp_share_link(text):
    encoded = urllib.parse.quote(f"היי, מצאתי את זה ב-The Dan Method:\n\n{text[:450]}")
    return f"https://api.whatsapp.com/send?text={encoded}"

# --- סרגל צד נקי (פרופיל בלבד) ---
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="font-size: 26px;">🎓</span>
            <span style="font-size: 1.3rem; font-weight: 800; color: #1e3a8a;">The Dan Method</span>
        </div>
        <div style="font-size: 0.85rem; color: #64748b; font-weight: 600; margin-bottom: 12px;">בס״ד | לומדים. מתקדמים.</div>
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

# --- סרגל ניווט עליון עצמאי עם בחירת מצב תלמיד/מורה ---
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

# --- בדיקת אבטחה: אם נבחר מצב מורה והוא טרם אומת, הצג מסך נעילה ---
if st.session_state.app_mode == "מורה" and not st.session_state.teacher_authenticated:
    st.markdown("""
        <div class="clean-box" style="text-align: center; max-width: 550px; margin: 40px auto; border-top: 5px solid #1e3a8a;">
            <div style="font-size: 48px; margin-bottom: 10px;">🔒</div>
            <h2 style="color: #0f2b5c; margin: 0 0 8px 0; font-weight: 800;">אזור מוגן לצוות הוראה והנהלה</h2>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 20px;">
                כלי המורים כוללים מחווני בחינה, מערכי שיעור וטפסי הערכה רשמיים.<br>
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
                st.success("קוד גישה אומת בהצלחה! ברוך הבא למרחב ההוראה.")
                time.sleep(0.6)
                st.rerun()
            else:
                st.error("קוד הגישה אינו תקין. הגישה מותרת לצוות מורשה בלבד.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅️ חזרה למצב תלמיד", use_container_width=True):
            st.session_state.app_mode = "תלמיד"
            st.rerun()
    st.stop()

# ----------------- 0. דף הבית (המרכז הראשי) -----------------
if st.session_state.current_room == "דף הבית":
    mode_title = "הדרך שלך להצלחה מתחילה כאן." if st.session_state.app_mode == "תלמיד" else "מרחב הפדגוגיה וההוראה החכמה."
    mode_sub = "לימודים קלים יותר, בכל מקום ובכל זמן." if st.session_state.app_mode == "תלמיד" else "הכנת מערכי שיעור, בחנים, מצגות ומחוונים בתוך שניות."
    
    st.markdown(f"""
        <div class="hero-banner">
            <h1 class="hero-main-title">{mode_title}</h1>
            <p class="hero-desc">{mode_sub}<br>שאל את ה-AI שאלה, או בחר כלי עבודה:</p>
        </div>
    """, unsafe_allow_html=True)

    # שורת חיפוש חכמה
    query_search = st.text_input("🔍 שאל שאלה או חפש כלי:", placeholder="למשל: 'איך גוזרים פונקציה?', 'מצגת', 'מבחן', 'חילוץ לילה'...", label_visibility="collapsed")

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
                    res_bot = generate_ai(f"אתה עוזר לימודי אישי חכם ({'לתלמיד' if st.session_state.app_mode == 'תלמיד' else 'למורה'}). בהקשר: {student_context}. ענה על השאלה ישירות, ברור וקצר לתכל'ס בלי חפירות: {query_search}. {anti_yap_rule}", use_cache=True)
                    st.markdown("""
                        <div class="clean-box" style="border-right: 4px solid #3b82f6;">
                            <h4 style="margin: 0; color: #1e3a8a;">💡 מענה מהיר של דן AI:</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(res_bot.text)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_bot.text)}" target="_blank">📲 שתף מענה בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.warning("לא הצלחנו לפענח כרגע, נסה לשאול שוב.")

    st.markdown("""
        <div class="features-ribbon">
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #f3e8ff; color: #9333ea;">📖</div>
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
                <div class="ribbon-icon-circle" style="background: #dcfce7; color: #16a34a;">👥</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">מותאם לצוות ולתלמידים</div>
                    <div style="color:#64748b; font-size:0.8rem;">התאמה מלאה לרמות ולמגמות</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #fef9c3; color: #ca8a04;">⭐</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">למידה עצמאית מנצחת</div>
                    <div style="color:#64748b; font-size:0.8rem;">הישגים גבוהים בפחות זמן</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. על השיטה (הדבר הראשון שרואים)
    st.markdown("""
        <div class="story-card">
            <div class="story-title">⚡ על השיטה של The Dan Method</div>
            <p class="story-p">
                נמאס לשבת שעות מול סיכומים ארוכים, מורים שמדברים מסביב ואתרי לימוד שנראים כמו שנת 2005.<br>
                <b>The Dan Method</b> נבנה במטרה אחת ברורה: לתת לתלמידי ומורי ישראל את הדרך הקצרה, המדויקת והחדה ביותר להצלחה במבחנים ובבגרויות.<br>
                במקום ללמוד 4 שעות ולזכור חצי – אנחנו מפרקים כל נושא לשלבי ברזל, מסננים חפירות מיותרות (מצב תכל'ס), ומלמדים אותך בדיוק לפי מה שהבוחן מחפש בעין בטופס הבדיקה.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. טבלת ההשוואה (צמוד לעל השיטה)
    st.markdown("""
        <div class="compare-container">
            <h3 style="margin-top: 0; color: #0f2b5c; font-size: 1.3rem; font-weight: 800;">למה The Dan Method ולא סתם בינה מלאכותית רגילה?</h3>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 20px;">ChatGPT ודגמי AI רגילים לא מכירים את בתי הספר בישראל ומבזבזים לך זמן. הנה ההבדל:</p>
            <table class="compare-table">
                <thead>
                    <tr>
                        <th style="width: 32%;">תכונה</th>
                        <th style="width: 34%; color: #1e3a8a;">The Dan Method 🎓</th>
                        <th style="width: 34%;">ChatGPT / מודל רגיל</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="font-weight: 600;">התאמה למערכת החינוך</td>
                        <td style="color: #16a34a; font-weight: 700;">מכויל בול לפי מחווני בגרות, הקבצות וכיתות ז'-י"ב בישראל</td>
                        <td style="color: #64748b;">תשובות גנריות באנגלית שתורגמו לעברית, לא מכיר מחוונים</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">אורך המענה והיעילות</td>
                        <td style="color: #16a34a; font-weight: 700;">מצב תכל'ס (No Yap) – פירוק ממוקד ב-3 שורות בדיוק למה שצריך</td>
                        <td style="color: #64748b;">פסקאות פתיחה וסיום ארוכות, חפירות ומריחת זמן</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">בדיקת מבחנים וציונים</td>
                        <td style="color: #16a34a; font-weight: 700;">חישוב ציון אמיתי מתוך 100 עם הורדת נקודות לפי נימוקים חסרים</td>
                        <td style="color: #64748b;">סתם מחמיא לתשובה ולא יודע לתת ציון בגרות אמיתי</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">חילוץ רגע לפני מבחן</td>
                        <td style="color: #16a34a; font-weight: 700;">שליף 60 שניות, מצב חילוץ בלילה ורנטגן שגיאות</td>
                        <td style="color: #64748b;">מייצר טקסטים ענקיים שבלתי אפשרי לקרוא תחת לחץ</td>
                    </tr>
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)

    # ----------------- חלוקת החדרים לפי מצב תלמיד / מצב מורה -----------------
    if st.session_state.app_mode == "תלמיד":
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h2 style="font-size: 1.5rem; font-weight: 800; color: #0f2b5c; margin: 0;">מרכז הלמידה של התלמיד</h2>
                <span style="color: #64748b; font-weight: 600; font-size: 0.95rem;">בחר כלי כדי להתחיל</span>
            </div>
        """, unsafe_allow_html=True)

        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.markdown('<div class="room-tile cat-pink"><div style="font-size:30px;">📊</div><h4 style="margin:4px 0;">מחולל מצגות</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">שקופיות והערות להצגה</p></div>', unsafe_allow_html=True)
            if st.button("בנה מצגת", key="btn_slides_t", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()

        with col_t2:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:30px;">📹</div><h4 style="margin:4px 0;">חדר זום חי</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">שיעור קולי 1-על-1</p></div>', unsafe_allow_html=True)
            if st.button("היכנס לזום", key="btn_zoom_t", use_container_width=True):
                st.session_state.current_room = "חדר זום"
                st.rerun()

        with col_t3:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:30px;">📸</div><h4 style="margin:4px 0;">סורק תרגילים</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פיענוח מתמונה ודף</p></div>', unsafe_allow_html=True)
            if st.button("פתח סורק", key="btn_scanner_t", use_container_width=True):
                st.session_state.current_room = "סורק תמונות"
                st.rerun()

        with col_t4:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:30px;">📝</div><h4 style="margin:4px 0;">מבחני דמה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">סימולציה עם מחוון</p></div>', unsafe_allow_html=True)
            if st.button("בנה מבחן", key="btn_exam_t", use_container_width=True):
                st.session_state.current_room = "מבחני דמה"
                st.rerun()

        col_t5, col_t6, col_t7, col_t8 = st.columns(4)
        with col_t5:
            st.markdown('<div class="room-tile cat-red"><div style="font-size:30px;">🆘</div><h4 style="margin:4px 0;">חילוץ ב-3 בלילה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">תוכנית הצלה לפני מבחן</p></div>', unsafe_allow_html=True)
            if st.button("פתח חילוץ לילה", key="btn_panic_t", use_container_width=True):
                st.session_state.current_room = "חילוץ לילה"
                st.rerun()

        with col_t6:
            st.markdown('<div class="room-tile cat-yellow"><div style="font-size:30px;">🚨</div><h4 style="margin:4px 0;">שליף חירום</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">60 שניות לפני מבחן</p></div>', unsafe_allow_html=True)
            if st.button("הצג שליף", key="btn_cheat_t", use_container_width=True):
                st.session_state.current_room = "שליף חירום"
                st.rerun()

        with col_t7:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:30px;">🩻</div><h4 style="margin:4px 0;">רנטגן שגיאות</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">מלכודות הבוחנים</p></div>', unsafe_allow_html=True)
            if st.button("גלה מוקשים", key="btn_xray_t", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()

        with col_t8:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:30px;">⚖️</div><h4 style="margin:4px 0;">מכתב ערעור</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">החזרת נקודות ממורים</p></div>', unsafe_allow_html=True)
            if st.button("נסח ערעור", key="btn_appeal_t", use_container_width=True):
                st.session_state.current_room = "ערעור"
                st.rerun()

        col_t9, col_t10, col_t11, col_t12 = st.columns(4)
        with col_t9:
            st.markdown('<div class="room-tile cat-orange"><div style="font-size:30px;">📐</div><h4 style="margin:4px 0;">מעבדת מתמטיקה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פירוק שלב-אחר-שלב</p></div>', unsafe_allow_html=True)
            if st.button("פרק תרגיל", key="btn_math_t", use_container_width=True):
                st.session_state.current_room = "מעבדת מתמטיקה"
                st.rerun()

        with col_t10:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:30px;">🎴</div><h4 style="margin:4px 0;">כרטיסיות חזרה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">שינון מושגים מהיר</p></div>', unsafe_allow_html=True)
            if st.button("פתח כרטיסיות", key="btn_flash_t", use_container_width=True):
                st.session_state.current_room = "כרטיסיות"
                st.rerun()

        with col_t11:
            st.markdown('<div class="room-tile cat-teal"><div style="font-size:30px;">🧘</div><h4 style="margin:4px 0;">רווחה והפחתת לחץ</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">נשימות 30 שנ\' ופוקוס</p></div>', unsafe_allow_html=True)
            if st.button("מרחב רווחה", key="btn_well_t", use_container_width=True):
                st.session_state.current_room = "רווחה"
                st.rerun()

        with col_t12:
            st.markdown('<div class="room-tile cat-orange"><div style="font-size:30px;">🎯</div><h4 style="margin:4px 0;">מחשבון בגרות</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">חיזוי הציון הסופי</p></div>', unsafe_allow_html=True)
            if st.button("חשב ציון יעד", key="btn_calc_t", use_container_width=True):
                st.session_state.current_room = "מחשבון"
                st.rerun()

    else:
        # מצב מורה וצוות חינוכי (נגיש רק לאחר אימות מוצלח)
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h2 style="font-size: 1.5rem; font-weight: 800; color: #0f2b5c; margin: 0;">מרכז הפדגוגיה והכלים למורים 🔒</h2>
                <span style="color: #16a34a; font-weight: 700; font-size: 0.95rem;">● מחובר כאנשי צוות מאומתים</span>
            </div>
        """, unsafe_allow_html=True)

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown('<div class="room-tile cat-pink"><div style="font-size:30px;">📊</div><h4 style="margin:4px 0;">מחולל מצגות לשיעור</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">מבנה שקופיות והערות מורה</p></div>', unsafe_allow_html=True)
            if st.button("בנה מצגת לשיעור", key="btn_slides_m", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()

        with col_m2:
            st.markdown('<div class="room-tile cat-indigo"><div style="font-size:30px;">⏱️</div><h4 style="margin:4px 0;">מערך שיעור (45 דק\')</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פתיחה, גוף ותרגול מדורג</p></div>', unsafe_allow_html=True)
            if st.button("בנה מערך שיעור", key="btn_lesson_m", use_container_width=True):
                st.session_state.current_room = "מערכי שיעור"
                st.rerun()

        with col_m3:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:30px;">📝</div><h4 style="margin:4px 0;">בוחן פתע + מחוון</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">טופס כיתתי ומחוון בדיקה</p></div>', unsafe_allow_html=True)
            if st.button("ייצר בוחן ומחוון", key="btn_quiz_m", use_container_width=True):
                st.session_state.current_room = "בחנים ומחוונים"
                st.rerun()

        with col_m4:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:30px;">🏛️</div><h4 style="margin:4px 0;">מכתב רשמי להנהלה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פדגוגיה והצגת פיילוט ליועצת</p></div>', unsafe_allow_html=True)
            if st.button("הצג מכתב להנהלה", key="btn_letter_m", use_container_width=True):
                st.session_state.current_room = "הנהלה"
                st.rerun()

        col_m5, col_m6, col_m7, col_m8 = st.columns(4)
        with col_m5:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:30px;">🖨️</div><h4 style="margin:4px 0;">דפי עבודה להדפסה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">דפי תרגול מדורגים לכיתה</p></div>', unsafe_allow_html=True)
            if st.button("הפק דף עבודה", key="btn_print_m", use_container_width=True):
                st.session_state.current_room = "דפי הדפסה"
                st.rerun()

        with col_m6:
            st.markdown('<div class="room-tile cat-yellow"><div style="font-size:30px;">🩻</div><h4 style="margin:4px 0;">איתור מוקשי למידה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">הטעויות הנפוצות בנושא</p></div>', unsafe_allow_html=True)
            if st.button("בדוק מלכודות", key="btn_xray_m", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()

        with col_m7:
            st.markdown('<div class="room-tile cat-teal"><div style="font-size:30px;">🧘</div><h4 style="margin:4px 0;">ארגז כלים ליועצת</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">הפחתת חרדת בחינות</p></div>', unsafe_allow_html=True)
            if st.button("ארגז כלים ליועצת", key="btn_well_m", use_container_width=True):
                st.session_state.current_room = "רווחה"
                st.rerun()

        with col_m8:
            st.markdown('<div class="room-tile cat-slate"><div style="font-size:30px;">🗣️</div><h4 style="margin:4px 0;">מפשט שאלות</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">התאמת ניסוח לתלמידים</p></div>', unsafe_allow_html=True)
            if st.button("פשט שאלה", key="btn_street_m", use_container_width=True):
                st.session_state.current_room = "מתרגם"
                st.rerun()

    # חוות דעת והמלצות
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⭐ מה שאומרים על The Dan Method")
    st.caption("משובים אמיתיים מתלמידים ומורים מכל הארץ:")
    
    col_rev1, col_rev2 = st.columns([1.8, 1.2])
    with col_rev1:
        for r in st.session_state.reviews:
            stars = "⭐" * r["rating"]
            st.markdown(f"""
                <div class="clean-box">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b>{r['name']}</b> ({r['grade']})
                        <span style="font-size:0.9rem;">{stars}</span>
                    </div>
                    <p style="color: #475569; margin: 6px 0 0 0; font-size: 0.95rem;">{r['text']}</p>
                </div>
            """, unsafe_allow_html=True)
            
    with col_rev2:
        st.markdown('<div class="clean-box"><h4 style="margin-top:0;">✍️ הוסף חוות דעת:</h4>', unsafe_allow_html=True)
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

# ----------------- חדר: מחולל מצגות (פעיל גם לתלמיד וגם למורה) -----------------
elif st.session_state.current_room == "מצגות":
    st.title("📊 מחולל מצגות מקצועי (Slide Deck Generator)")
    st.caption("בונה שלד שקופיות שלם: כותרות מנצחות, נקודות תכל'ס להקרנה, והערות מפורטות לדובר מה להגיד בכיתה.")
    
    col_sl1, col_sl2 = st.columns(2)
    with col_sl1:
        slide_topic = st.text_input("נושא המצגת:", placeholder="למשל: תהליך הפוטוסינתזה, מלחמת העצמאות, המהפכה המדעית...")
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
                f"נושא המצגת: {slide_topic}, מקצוע: {slide_subject}, מספר שקופיות: {slide_count}, מטרה: {slide_goal}.\n"
                "החזר אך ורק מערך JSON תקין (ללא שום טקסט או הערות מסביב):\n"
                "[\n"
                "  {\n"
                '    "slide_num": 1,\n'
                '    "title": "כותרת שקופית קולעת",\n'
                '    "bullets": ["נקודה 1 קצרה להקרנה", "נקודה 2 קצרה להקרנה", "נקודה 3 קצרה להקרנה"],\n'
                '    "visual_idea": "רעיון לתמונה או גרף שכדאי לשים בשקופית",\n'
                '    "speaker_notes": "מה הדובר/המורה אומר בפועל בכיתה כשהשקופית הזו מוצגת (3-4 משפטים ברורים ומעניינים)"\n'
                "  }\n"
                "]"
            )
            with st.spinner("בונה שקופיות והערות דובר..."):
                try:
                    res = generate_ai(prompt_slides)
                    st.session_state.slides_data = extract_json(res.text)
                    st.success("המצגת מוכנה! השקופיות מופיעות למטה.")
                except Exception as e:
                    st.error(f"שגיאה בבניית המצגת: {e}")

    if st.session_state.slides_data:
        st.markdown("---")
        full_text_for_share = f"מצגת בנושא: {slide_topic}\n\n"
        for s in st.session_state.slides_data:
            bullets_formatted = "\n".join([f"• {b}" for b in s.get("bullets", [])])
            st.markdown(f"""
                <div class="slide-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#1e3a8a;">שקופית {s['slide_num']}: {s['title']}</h3>
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

# ----------------- חדר: מחולל מערכי שיעור למורים -----------------
elif st.session_state.current_room == "מערכי שיעור":
    st.title("⏱️ מחולל מערך שיעור ממוקד (45 דקות)")
    st.caption("כלי עבודה פדגוגי למורים: בניית שיעור מובנה עם זמנים מדויקים, פתיחה, הקניה ותרגול מדורג.")
    
    l_sub = st.text_input("מקצוע השיעור:", placeholder="למשל: היסטוריה, ביולוגיה, מתמטיקה, אזרחות...")
    l_top = st.text_input("נושא השיעור:", placeholder="למשל: תהליך הפוטוסינתזה, העלייה השנייה, משפט תאלס...")
    if st.button("בנה מערך שיעור 45 דק' 📚", use_container_width=True):
        if l_sub and l_top:
            with st.spinner("בונה מערך שיעור פדגוגי..."):
                prompt_plan = (
                    f"אתה רכז פדגוגי בכיר במשרד החינוך. בנה מערך שיעור מובנה של 45 דקות עבור כיתה {chosen_grade}.\n"
                    f"מקצוע: {l_sub}, נושא: {l_top}.\n"
                    "חלק לזמנים מדויקים:\n"
                    "- פתיחה וגירוי חשיבה (5-7 דק')\n"
                    "- גוף השיעור והקניית מושגים (20 דק')\n"
                    "- תרגול כיתתי מדורג: בסיסי ואתגר (12 דק')\n"
                    "- סיכום ומשימת יציאה לבדיקת הבנה (5 דק')\n"
                    "הקפד על ניסוח בהיר, מובנה ומקצועי למורה."
                )
                res_plan = generate_ai(prompt_plan)
                st.markdown("""<div class="clean-box"><h4>מערך שיעור מוכן למורה:</h4></div>""", unsafe_allow_html=True)
                st.markdown(res_plan.text)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_plan.text)}" target="_blank">📲 שתף מערך שיעור בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: בחנים ומחוונים למורים -----------------
elif st.session_state.current_room == "בחנים ומחוונים":
    st.title("📝 מחולל בוחן כיתתי + מחוון משרד החינוך")
    st.caption("הפקת בוחן קצר של 15 דקות לכיתה לצד מחוון בדיקה מלא למורה עם פירוט חלוקת נקודות.")
    
    q_sub = st.text_input("מקצוע הבוחן:", placeholder="אנגלית, מתמטיקה, תנ\"ך, היסטוריה...")
    q_top = st.text_input("נושא הבוחן המדויק:", placeholder="למשל: פעלים יוצאי דופן, חוקי ניוטון, שיווי משקל...")
    if st.button("ייצר בוחן ומחוון בדיקה 📄", use_container_width=True):
        if q_sub and q_top:
            with st.spinner("מכין שאלות ומחוון..."):
                prompt_quiz = (
                    f"צור בוחן כיתתי קצר של 15 דקות (3 שאלות ברמת קושי עולה) ומחוון בדיקה מלא למורה.\n"
                    f"כיתה: {chosen_grade}, מקצוע: {q_sub}, נושא: {q_top}.\n"
                    "חלק 1: טופס הבוחן לתלמיד (עם שורות לכתיבה וניקוד ליד כל שאלה).\n"
                    "חלק 2: מחוון בדיקה מפורט למורה (תשובות נכונות, פירוט ניקוד וטעויות נפוצות שמונעות נקודות)."
                )
                res_quiz = generate_ai(prompt_quiz)
                st.markdown("""<div class="clean-box"><h4>טופס הבוחן והמחוון למורה:</h4></div>""", unsafe_allow_html=True)
                st.markdown(res_quiz.text)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_quiz.text)}" target="_blank">📲 שתף בוחן ומחוון בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: מכתב רשמי להנהלה ולמורים -----------------
elif st.session_state.current_room == "הנהלה":
    st.title("🏛️ מכתב רשמי להנהלת בית הספר ולצוות הייעוץ")
    st.caption("הסבר פדגוגי מנומק המוכן להצגה ישירה בפני המנהלת והיועצת לפתיחת פיילוט כיתתי.")
    
    st.markdown("""
        <div class="clean-box" style="border-right: 4px solid #1e3a8a;">
            <h3 style="margin-top:0; color:#0f2b5c;">לכבוד: מנהלת בית הספר והיועצת החינוכית</h3>
            <b>הנדון: שילוב פלטפורמת 'The Dan Method' ככלי פדגוגי מסייע ללמידה עצמאית והפחתת חרדת בחינות</b>
            <p style="margin-top: 10px; line-height: 1.7; color: #334155;">
                מערכת <b>The Dan Method</b> פותחה מתוך הבנת האתגרים הייחודיים של תלמידי חטיבת הביניים והחטיבה העליונה בישראל. 
                בניגוד לכלי AI גנריים, המערכת מכוילת באופן מדויק על פי תוכניות הלימודים ומחווני הבגרות של משרד החינוך.<br><br>
                <b>תרומת הפלטפורמה לתלמידים ולצוות בית הספר:</b><br>
                1. <b>עידוד למידה עצמאית וסגירת פערים:</b> מענה מותאם אישית לתלמידים מתקשים הזקוקים לפירוק שלבי למידה בקצב שלהם.<br>
                2. <b>הפחתת חרדת בחינות:</b> מרחב רווחה מובנה עם תרגילי ויסות ונשימה, לצד מתכנן לו"ז מאוזן למניעת דחיינות ועומס.<br>
                3. <b>חיסכון בזמן למורים:</b> הפקת בחני פתע מדורגים, מערכי שיעור ומצגות בלחיצת כפתור אחת.<br><br>
                אנו מציעים לקיים <b>פיילוט לימודי מבוקר</b> בכיתה אחת לקראת הבחינות הקרובות, למדידת שביעות הרצון וההישגים.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link("שלום, מצורף מכתב ההסבר הפדגוגי של The Dan Method לצוות ההנהלה והיועצת.")}" target="_blank">📲 שתף מכתב זה להנהלה</a>', unsafe_allow_html=True)

# ----------------- חדר: רווחה והפחתת לחץ -----------------
elif st.session_state.current_room == "רווחה":
    st.title("🧘 מרחב רווחה, ויסות והפחתת חרדת בחינות")
    st.caption("פיתוח בשיתוף עקרונות ייעוץ חינוכי: למידה אפקטיבית מתחילה ברוגע ובפוקוס.")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.subheader("מד עומס ומתח לימודי")
        stress_lvl = st.select_slider("איך אתה מרגיש לקראת הלמידה עכשיו?", ["רגוע וממוקד 🟢", "קצת לחוץ 🟡", "עומס בינוני 🟠", "לחץ גבוה לפני מבחן 🔴"], value="קצת לחוץ 🟡")
        
        if "לחץ גבוה" in stress_lvl or "עומס בינוני" in stress_lvl:
            st.info("💡 מומלץ לקחת 2 דקות נשימה מודרכת לפני שפותחים ספרים. זה מעלה את הזיכרון בעד 30%.")
            
        st.markdown("---")
        st.subheader("תרגיל נשימה להורדת דופק (Box Breathing)")
        st.markdown("""
            1. **שאיפה עמוקה מהאף** – 4 שניות 🌬️  
            2. **עצירת אוויר בריאות** – 4 שניות ⏸️  
            3. **נשיפה איטית מהפה** – 4 שניות 💨  
            4. **המתנה רגועה** – 4 שניות 🧘
        """)
        if st.button("הפעל טיימר נשימה של 30 שניות ⏱️"):
            prog = st.progress(0)
            status_text = st.empty()
            phases = ["שאף מהאף... 🌬️", "החזק... ⏸️", "נשוף לאט... 💨", "המתן ברוגע... 🧘"]
            for i in range(30):
                time.sleep(1)
                prog.progress((i + 1) / 30)
                status_text.text(phases[i % 4])
            st.success("מעולה! הגוף נרגע, עכשיו המוח מוכן לקלוט חומר בצורה חדה.")

    with col_w2:
        st.subheader("טיימר פוקוס עמוק (Deep Focus)")
        st.caption("25 דקות ריכוז נטו ללא התראות טלפון:")
        focus_mins = st.slider("זמן סבב למידה (דקות):", 15, 45, 25)
        st.markdown(f"""
            <div class="clean-box" style="text-align:center;">
                <h1 style="font-size:3.5rem; color:#1e3a8a; margin:0;">{focus_mins}:00</h1>
                <p style="color:#64748b; margin-top:4px;">שים את הטלפון על מצב טיסה והתחל תרגיל אחד.</p>
            </div>
        """, unsafe_allow_html=True)
        st.success("טיפ של יועצת: הפרד בין שולחן הלמידה למיטה כדי לשמור על רמת ערנות גבוהה.")

# ----------------- חדר: חילוץ ב-3 בלילה -----------------
elif st.session_state.current_room == "חילוץ לילה":
    st.title("🆘 מצב חילוץ ב-3 בלילה")
    st.caption("יש לך מבחן מחר בבוקר ולא הספקת ללמוד? נחלץ אותך עכשיו עם המינימום שמבטיח ציון עובר וגבוה.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        panic_sub = st.text_input("מקצוע המבחן מחר:", placeholder="למשל: היסטוריה, תנ\"ך, ביולוגיה...")
        panic_top = st.text_area("מה החומר או הפרקים שצריך?", placeholder="פרקים 2-5, חוקי הגנטיקה, המהפכה התעשייתית...")
    with col_p2:
        hours_left = st.slider("כמה שעות נשאר לך עד שאתה יוצא מהבית?", 1, 8, 3)
        target_score = st.select_slider("איזה ציון אתה חייב להוציא?", ["רק לעבור (65-70)", "ציון טוב (80-85)", "ציון פצצה (90+)"])

    if st.button("🚨 הצל אותי עכשיו!", use_container_width=True):
        if not panic_sub.strip() or not panic_top.strip():
            st.warning("נא לציין מקצוע וחומר למבחן.")
        else:
            prompt = (
                f"התלמיד ב-{student_context} תקוע בשעה מאוחרת לפני מבחן מחר בבוקר.\n"
                f"מקצוע: {panic_sub}, חומר: {panic_top}, שעות פנויות: {hours_left}, יעד: {target_score}.\n"
                "החזר תוכנית הצלה קריטית בעברית:\n"
                "1. **3 מושגים/נוסחאות שחייבים לדעת בעל פה** כי הם בטוח מופיעים במבחן.\n"
                "2. **הטריק של הבחינה**: איפה רוב הנקודות מחולקות ואיך לענות כדי שהבוחן ייתן נקודות גם בלי לדעת הכל מושלם.\n"
                "3. **משפט פתיחה של מאיות**: איך לפתוח תשובה פתוחה כדי לעשות רושם מושלם על הבודק.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מחלץ תוכנית הצלה דחופה..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(f'<div class="panic-box">{res.text}</div>', unsafe_allow_html=True)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף תוכנית הצלה בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.error("שגיאה בחילוץ.")

# ----------------- חדר: רנטגן שגיאות -----------------
elif st.session_state.current_room == "רנטגן":
    st.title("🩻 רנטגן שגיאות ומלכודות בוחנים")
    st.caption("גלה איפה 80% מהתלמידים נופלים במבחן ואיך לא ליפול במלכודות של הבוחנים.")
    
    xray_topic = st.text_input("איזה נושא או תרגיל תרצה לבדוק?", placeholder="למשל: סדרות חשבוניות, משפט תאלס, שיווי משקל שוק, גנטיקה...")
    if st.button("חשוף מלכודות במבחן ⚡", use_container_width=True):
        if not xray_topic.strip():
            st.warning("נא לציין נושא.")
        else:
            prompt = (
                f"התלמיד/המורה ב-{student_context} רוצה לדעת איפה בוחנים מכשילים תלמידים בנושא: {xray_topic}.\n"
                "החזר:\n"
                "1. **המלכודת הנפוצה ביותר**: הטעות הקלאסית שכולם נופלים בה.\n"
                "2. **איך הבוחן מנסח את השאלה המכשילה**: ציטוט או דוגמה לאיך זה נראה בטופס.\n"
                "3. **הפתרון שמציל נקודות**: הנימוק או הבדיקה שמונעים את הטעות.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מבצע צילום רנטגן לבחינה..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown("""<div class="clean-box" style="border-right: 4px solid #ef4444;"><h3>דוח מלכודות בוחנים:</h3></div>""", unsafe_allow_html=True)
                    st.markdown(res.text)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף מוקשים בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.error("שגיאה ברנטגן.")

# ----------------- חדר: מחולל מכתב ערעור -----------------
elif st.session_state.current_room == "ערעור":
    st.title("⚖️ מחולל מכתב ערעור על ציון")
    st.caption("הורידו לך נקודות לא בצדק? נסח מכתב ערעור רשמי ומנומק לפי מחוון משרד החינוך שהמורה יתקשה לדחות.")
    
    c_sub = st.text_input("מקצוע המבחן:", placeholder="מתמטיקה, אזרחות, היסטוריה, ביולוגיה...")
    c_q = st.text_area("מה הייתה השאלה במבחן?", height=70)
    c_ans = st.text_area("מה התשובה שכתבת במחברת?", height=80)
    c_lost = st.text_input("כמה נקודות ירדו ומה המורה כתב/ה בהערה?", placeholder="למשל: ירדו 8 נקודות, המורה כתבה 'חסר נימוק'")
    
    if st.button("נסח מכתב ערעור מנוצח 🚀", use_container_width=True):
        if not c_sub.strip() or not c_ans.strip():
            st.warning("נא למלא את פרטי השאלה והתשובה.")
        else:
            prompt = (
                f"נסח מכתב ערעור רשמי, מנומס אך בלתי ניתן לעירעור ממלכתי עבור תלמיד ב-{student_context}.\n"
                f"מקצוע: {c_sub}\nשאלה: {c_q}\nתשובת התלמיד: {c_ans}\nהערת המורה ונקודות: {c_lost}\n\n"
                "הנחיות לכתיבת הערעור:\n"
                "1. פנייה מכבדת למורה.\n"
                "2. ציטוט מדויק של מה שהתלמיד כתב והסבר למה לפי מחוון הבחינה התשובה עונה על הדרישות ומצדיקה קבלת הנקודות.\n"
                "3. בקשה עניינית לבדיקה חוזרת והעלאת הציון.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנסח מכתב ערעור אקדמי..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown("""<div class="clean-box"><h3>נוסח מכתב הערעור (העתק ושלח למורה):</h3></div>""", unsafe_allow_html=True)
                    st.markdown(res.text)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף נוסח ערעור בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.error("שגיאה בניסוח הערעור.")

# ----------------- חדר: כרטיסיות חזרה -----------------
elif st.session_state.current_room == "כרטיסיות":
    st.title("🎴 כרטיסיות חזרה מהירות (Interactive Flashcards)")
    st.caption("שינון מושגי מפתח ונוסחאות בקלות בהסעה או בהפסקה.")
    
    f_topic = st.text_input("איזה נושא תרצה לשנן?", placeholder="למשל: מושגים באזרחות, זמנים באנגלית, נוסחאות טריגו...")
    if st.button("ייצר לי כרטיסיות שינון ⚡", use_container_width=True):
        if not f_topic.strip():
            st.warning("נא לציין נושא.")
        else:
            prompt = (
                f"צור 4 כרטיסיות שינון מעולות עבור תלמיד ב-{student_context} בנושא: {f_topic}.\n"
                "החזר אך ורק מערך JSON תקין (ללא הערות מסביב):\n"
                "[\n"
                "  {\"front\": \"המושג או השאלה\", \"back\": \"ההגדרה הקצרה לתכל'ס או הנוסחה\"}\n"
                "]"
            )
            with st.spinner("מכין כרטיסיות..."):
                try:
                    res = generate_ai(prompt)
                    st.session_state["flashcards_data"] = extract_json(res.text)
                except Exception:
                    st.error("שגיאה ביצירת כרטיסיות.")

    if "flashcards_data" in st.session_state:
        st.markdown("---")
        for i, card in enumerate(st.session_state["flashcards_data"]):
            with st.expander(f"🎴 כרטיסייה {i+1}: {card['front']}"):
                st.markdown(f"**תשובה והסבר תכל'ס:**\n\n{card['back']}")

# ----------------- חדר: מחשבון בגרות ומגן (מד מתוקן) -----------------
elif st.session_state.current_room == "מחשבון":
    st.title("🎯 מחשבון ציון יעד לבגרות ומגן")
    st.caption("בדוק בדיוק כמה אתה חייב להוציא בבגרות כדי לסיים עם הציון שאתה רוצה.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        magen_score = st.number_input("ציון המגן השנתי שלך (הערכה בית-ספרית):", 0, 100, 85)
        magen_weight = st.slider("אחוז משקל המגן (לרוב 30% או 50%):", min_value=10, max_value=50, value=30, step=10)
    with col_c2:
        target_final = st.number_input("מה הציון הסופי שאתה מכוון אליו?", 60, 100, 90)
    
    bagrut_weight = 100 - magen_weight
    needed_bagrut = (target_final * 100 - (magen_score * magen_weight)) / bagrut_weight
    
    st.markdown("---")
    if needed_bagrut > 100:
        st.error(f"⚠️ עם מגן של {magen_score}, תצטרך מעל 100 בבגרות ({needed_bagrut:.1f}) כדי להגיע ל-{target_final}. כדאי לשפר את המגן או לכוון ליעד ריאלי יותר.")
    elif needed_bagrut <= 0:
        st.success(f"🎉 המגן שלך ({magen_score}) כל כך גבוה שגם עם ציון בסיסי בבגרות אתה עובר את יעד ה-{target_final}!")
    else:
        st.success(f"🎯 **עליך להוציא לפחות {round(needed_bagrut)} בבחינת הבגרות** כדי לסיים עם ציון סופי של {target_final}.")

# ----------------- חדר: מתרגם סלנג לימודי -----------------
elif st.session_state.current_room == "מתרגם":
    st.title("🗣️ מתרגם סלנג לימודי (Street Translator)")
    st.caption("ספר הלימוד או המורה ניסחו שאלה מסובכת ויבשה? נתרגם לך אותה לשפת תכל'ס פשוטה.")
    
    dry_question = st.text_area("הדבק כאן את השאלה או המשפט המסורבל:", height=100)
    if st.button("תרגם לי לתכל'ס 🧠", use_container_width=True):
        if not dry_question.strip():
            st.warning("הדבק קודם שאלה.")
        else:
            prompt = (
                f"התלמיד ב-{student_context} לא מבין מה השאלה המסורבלת הבאה רוצה ממנו:\n{dry_question}\n\n"
                "החזר:\n"
                "1. **מה באמת שואלים כאן בשפה פשוטה של תלמידים** (שורה אחת).\n"
                "2. **איזו פעולה צריך לעשות בפועל** (לחשב, להשוות, להסביר סיבה).\n"
                "3. **משפט התשובה הראשון** שאיתו פותחים את הפתרון.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מתרגם שאלות לסלנג פשוט..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown("""<div class="clean-box"><h3>תרגום תכל'ס:</h3></div>""", unsafe_allow_html=True)
                    st.markdown(res.text)
                except Exception:
                    st.error("שגיאה בתרגום.")

# ----------------- חדר: חדר זום עם מורה פרטית -----------------
elif st.session_state.current_room == "חדר זום":
    st.title("📹 שיעור פרטי בזום עם המורה מיה")
    st.caption(f"מותאם עבור {chosen_grade} | {math_units} | {chosen_major}")
    
    col_z_cam, col_z_chat = st.columns([1.15, 1.85])
    with col_z_cam:
        st.markdown("""
            <div class="zoom-learnit-card">
                <div style="display: inline-block; background: #ecfdf5; border: 1px solid #a7f3d0; color: #059669; font-size: 0.85rem; font-weight: 700; padding: 4px 14px; border-radius: 20px; margin-bottom: 12px;">
                    ● מחוברת לשיחה חיה
                </div>
                <div class="teacher-circle-box">
                    <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80" alt="המורה מיה">
                </div>
                <h3 style="margin: 0; color: #1e3a8a; font-weight: 800; font-size: 1.3rem;">המורה מיה</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin: 4px 0 0 0;">מורה פרטית אישית לבגרויות ולחטיבה</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.last_voice_reply:
            st.markdown("<br><b>🔊 השמעת קול המורה מיה:</b>", unsafe_allow_html=True)
            audio_url = get_tts_audio_url(st.session_state.last_voice_reply)
            st.audio(audio_url, format="audio/mp3", autoplay=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        z_subject = st.selectbox("בחר מקצוע לשיעור:", [
            "מתמטיקה", "אנגלית", chosen_major, "היסטוריה", "אזרחות", "תנ\"ך", "לשון והבעה", "ביולוגיה", "פיזיקה", "מדעי המחשב"
        ])
        z_goal = st.radio("מה מטרת השיעור עכשיו?", [
            "הסבר מאפס על נושא חדש שלא הבנתי בכיתה",
            "לפתור ביחד תרגיל או שיעורי בית שלב אחרי שלב",
            "הכנה דחופה לקראת מבחן או בוחן פתע"
        ])
        
        if st.button("🧹 איפוס שיחה", use_container_width=True):
            st.session_state.zoom_chat_history = []
            st.session_state.last_voice_reply = None
            st.rerun()

    with col_z_chat:
        st.subheader(f"💬 מהלך השיעור: {z_subject}")
        chat_box = st.container(height=360)
        with chat_box:
            if not st.session_state.zoom_chat_history:
                st.info(f"👋 **המורה מיה:** היי! שמחה לפגוש אותך לשיעור ב{z_subject}. תגיד לי איזה נושא או תרגיל אנחנו מפרקים עכשיו, ונתקדם ביחד בכיף!")
            else:
                for m in st.session_state.zoom_chat_history:
                    with st.chat_message(m["role"]):
                        st.write(m["content"])

        st.caption("🎙️ דיבור במיקרופון ישירות למורה:")
        audio_prompt = st.audio_input("הקלט שאלה קולית:")

        if audio_prompt is not None:
            with st.spinner("המורה מיה מקשיבה ומכינה מענה..."):
                try:
                    audio_bytes = audio_prompt.read()
                    prompt_audio = (
                        f"את המורה מיה, מורה פרטית ישראלית מקצועית וסבלנית בשיעור עם תלמיד ב-{student_context}.\n"
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
                except Exception:
                    st.error("הייתה תקלה בהקלטה, נסה לדבר שוב.")

        text_spoken = st.chat_input("או כתוב כאן למורה מיה...")
        if text_spoken:
            st.session_state.zoom_chat_history.append({"role": "user", "content": text_spoken})
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.zoom_chat_history[-6:]])
            zoom_prompt = (
                f"את המורה מיה בשיעור עם תלמיד ב-{student_context}.\n"
                f"מקצוע: {z_subject}. מטרה: {z_goal}.\n"
                "1. דברי בלשון נקבה על עצמך ('אני איתך', 'בוא נראה', 'הסברתי').\n"
                "2. עני בגובה העיניים, מעודד וקצר (2-3 משפטים ממוקדים בכל פעם).\n"
                "3. בסוף כל תשובה שאלי שאלה קצרה לבדיקת הבנה.\n"
                f"{anti_yap_rule}\n\n"
                f"היסטוריית השיחה:\n{history_text}\n\nשאלה: {text_spoken}"
            )
            with st.spinner("המורה מיה מכינה מענה..."):
                try:
                    res_zoom = generate_ai(zoom_prompt)
                    st.session_state.zoom_chat_history.append({"role": "assistant", "content": res_zoom.text})
                    st.session_state.last_voice_reply = res_zoom.text
                    st.rerun()
                except Exception:
                    st.error("הייתה תקלה בתקשורת, נסה לשלוח שוב.")

# ----------------- חדר: סורק תמונות -----------------
elif st.session_state.current_room == "סורק תמונות":
    st.title("📸 סורק תמונות ושיעורי בית")
    photo_topic = st.text_input("מה החומר או המקצוע?", placeholder="תרגיל בפיזיקה, אלגברה, שאלות בתנ\"ך...")
    input_method = st.radio("מקור התמונה:", ["📁 העלאת קובץ מהמכשיר", "🔗 קישור ישיר (URL)"], horizontal=True)
    
    img_to_solve = None
    if input_method == "📁 העלאת קובץ מהמכשיר":
        file = st.file_uploader("בחר קובץ תמונה (JPG/PNG):", type=["png", "jpg", "jpeg"])
        if file:
            img_to_solve = Image.open(file)
            st.image(img_to_solve, caption="התמונה שהועלתה", width=340)
    else:
        url_input = st.text_input("הדבק כתובת URL לתמונה:", placeholder="https://example.com/homework.jpg")
        if url_input.strip():
            try:
                response = requests.get(url_input.strip(), timeout=10)
                img_to_solve = Image.open(BytesIO(response.content))
                st.image(img_to_solve, caption="תמונה מקישור", width=340)
            except Exception:
                st.error("לא הצלחנו לפתוח את הקישור לתמונה.")

    action = st.text_input("הנחיה לפיתרון:", value="פתור והסבר שלב אחרי שלב בצורה ברורה ומדויקת")
    if st.button("פענח ופתור ⚡", use_container_width=True):
        if not photo_topic.strip() or img_to_solve is None:
            st.warning("נא לציין נושא ולהעלות תמונה ברורה.")
        else:
            with st.spinner("מפענח את התמונה ומחשב פתרון..."):
                try:
                    res = generate_ai([f"התלמיד ב-{student_context}. החומר: {photo_topic}. הנחיה: {action}. {anti_yap_rule}", img_to_solve])
                    st.markdown("""<div class="clean-box"><h3>פתרון מפורט:</h3></div>""", unsafe_allow_html=True)
                    st.markdown(res.text)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף פתרון בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.error("התמונה לא פוענחה בהצלחה. ודא שהתמונה מוארת וברורה.")

# ----------------- חדר: מבחני דמה -----------------
elif st.session_state.current_room == "מבחני דמה":
    st.title("📝 מחולל מבחני דמה מלאים (Mock Exam)")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        exam_subject = st.selectbox("מקצוע המבחן:", ["מתמטיקה", "היסטוריה", "אזרחות", "אנגלית", "תנ\"ך", "לשון והבעה", "ביולוגיה", "פיזיקה", chosen_major])
        exam_topic = st.text_input("הנושא המדויק למבחן:", placeholder="למשל: סדרות חשבוניות, העלייה השנייה...")
    with col_m2:
        q_count = st.slider("מספר שאלות:", 2, 5, 3)
        exam_level = st.select_slider("רמת קושי:", ["בסיסית", "רמת מבחן כיתתי", "רמת בגרות מלאה"], value="רמת מבחן כיתתי")

    if st.button("🔨 צור לי מבחן דמה עכשיו!", use_container_width=True):
        if not exam_topic.strip():
            st.warning("נא להזין נושא למבחן.")
        else:
            prompt_gen = (
                f"אתה מורה שבונה מבחן דמה לתלמיד ב-{student_context}.\n"
                f"מקצוע: {exam_subject}, נושא: {exam_topic}, רמה: {exam_level}, מספר שאלות: {q_count}.\n"
                "החזר אך ורק מערך JSON תקין (ללא הערות מסביב):\n"
                "[\n"
                "  {\n"
                '    "id": 1,\n'
                '    "type": "multiple_choice",\n'
                '    "question": "ניסוח שאלה",\n'
                '    "points": 30,\n'
                '    "options": ["אפשרות א", "אפשרות ב", "אפשרות ג", "אפשרות ד"],\n'
                '    "correct_answer": "אפשרות א",\n'
                '    "explanation": "הסבר"\n'
                "  },\n"
                "  {\n"
                '    "id": 2,\n'
                '    "type": "open",\n'
                '    "question": "ניסוח שאלה פתוחה",\n'
                '    "points": 35,\n'
                '    "ideal_answer": "תשובה מלאה"\n'
                "  }\n"
                "]"
            )
            with st.spinner("בונה מבחן..."):
                try:
                    res = generate_ai(prompt_gen)
                    st.session_state.mock_exam_data = extract_json(res.text)
                    st.session_state.exam_submitted = False
                    st.success("המבחן מוכן לעבודה למטה.")
                except Exception:
                    st.error("שגיאה בבניית השאלות, נסה שוב.")

    if st.session_state.mock_exam_data:
        st.markdown("---")
        user_answers = {}
        for q in st.session_state.mock_exam_data:
            st.markdown(f"""<div class="clean-box"><h4 style="margin:0; color:#1e3a8a;">שאלה {q['id']} ({q.get('points', 25)} נקודות)</h4><p style="margin:6px 0 0 0;">{q['question']}</p></div>""", unsafe_allow_html=True)
            if q["type"] == "multiple_choice":
                user_answers[q["id"]] = st.radio(f"תשובה לשאלה {q['id']}:", q["options"], key=f"mcq_{q['id']}", index=None)
            else:
                user_answers[q["id"]] = st.text_area(f"תשובתך לשאלה {q['id']}:", key=f"open_{q['id']}", height=80)

        if st.button("🏁 הגש לבדיקה וקבלת ציון", use_container_width=True):
            st.session_state.exam_submitted = True
            with st.spinner("הבוחן מעריך את המבחן ומחשב ציון..."):
                try:
                    prompt_grade = f"אתה בוחן משרד החינוך. תלמיד: {student_context}.\nמבחן:\n{json.dumps(st.session_state.mock_exam_data, ensure_ascii=False)}\nתשובות:\n{json.dumps(user_answers, ensure_ascii=False)}\nהחזר ציון מתוך 100, פירוט נקודות ונוסח מלא של 100."
                    res_feedback = generate_ai(prompt_grade)
                    st.markdown("""<div class="clean-box" style="border-right: 4px solid #10b981;"><h2 style="color: #059669; margin: 0;">🎉 תוצאות מבחן הדמה:</h2></div>""", unsafe_allow_html=True)
                    st.markdown(res_feedback.text)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_feedback.text)}" target="_blank">📲 שתף תוצאות בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.error("הייתה שגיאה בבדיקת המבחן, נסה להגיש שוב.")

# ----------------- חדר: מעבדת מתמטיקה -----------------
elif st.session_state.current_room == "מעבדת מתמטיקה":
    st.title("📐 מעבדת פירוק מתמטיקה ומדעים")
    m_topic = st.text_input("מה הנושא הנלמד?", placeholder="חקירת פונקציה, טריגו, קינמטיקה...")
    m_input = st.text_area("הזן תרגיל או משוואה:", height=100)
    if st.button("פרק תרגיל שלב-אחר-שלב 🧠", use_container_width=True):
        if m_topic and m_input:
            with st.spinner("פותר ומפרק..."):
                try:
                    res = generate_ai(f"פתור עבור תלמיד ב-{student_context}.\nנושא: {m_topic}\nתרגיל: {m_input}\nפתור שלב אחרי שלב בבירור עם נימוק קצר ליד כל שלב, וסמן תוצאה סופית מודגשת. {anti_yap_rule}", use_cache=True)
                    st.markdown(res.text)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף פתרון בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.error("שגיאה בפיתרון התרגיל, נסה שוב.")

# ----------------- חדר: שליף חירום -----------------
elif st.session_state.current_room == "שליף חירום":
    st.title("🚨 שליף חירום: 60 שניות לפני מבחן")
    p_topic = st.text_input("נושא המבחן:", placeholder="משפט חוצה זווית, מרד בר כוכבא...")
    if st.button("הצל אותי עכשיו ⚡", use_container_width=True):
        if p_topic:
            with st.spinner("מחלץ שליף ממוקד..."):
                try:
                    res = generate_ai(f"התלמיד ב-{student_context} נכנס בעוד דקה למבחן על החומר: {p_topic}.\nהחזר אך ורק:\n1. 3 משפטי זהב שחייבים לרשום במבחן.\n2. הטעות הנפוצה ביותר.\n3. מושג חובה שהבוחן מחפש. {anti_yap_rule}", use_cache=True)
                    st.markdown(f'<div class="cheat-learnit">{res.text}</div>', unsafe_allow_html=True)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף שליף בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.error("לא הצלחנו לייצר שליף כרגע.")

# ----------------- חדר: דפי הדפסה -----------------
elif st.session_state.current_room == "דפי הדפסה":
    st.title("🖨️ מחולל דפי תרגול להדפסה")
    pr_top = st.text_input("נושא דף התרגול:", placeholder="למשל: משוואות ריבועיות, גנטיקה...")
    pr_sub = st.selectbox("מקצוע:", ["מתמטיקה", "אנגלית", "מדעי המחשב", "ביולוגיה", "היסטוריה"])
    if st.button("ייצר דף עבודה 📄", use_container_width=True):
        if pr_top:
            with st.spinner("מייצר דף נקי להדפסה..."):
                try:
                    res = generate_ai(f"צור דף תרגול ומבחן מעוצב בעברית לתלמיד ב-{student_context}.\nמקצוע: {pr_sub}, נושא: {pr_top}.\nכותרת עליונה, שאלות ברמת קושי עולה, ובסוף דף מחוון תשובות מלא.")
                    st.session_state["printable_sheet"] = res.text
                except Exception:
                    st.error("שגיאה בהפקת דף התרגול.")
    if "printable_sheet" in st.session_state:
        st.markdown(st.session_state["printable_sheet"])
        st.markdown("""<div style="text-align: center; margin-top: 15px;"><button onclick="window.print()" style="padding: 10px 20px; font-size: 15px; background: #1e3a8a; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🖨️ הדפס דף זה</button></div>""", unsafe_allow_html=True)
