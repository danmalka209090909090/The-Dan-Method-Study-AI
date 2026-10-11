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
    initial_sidebar_state="collapsed"
)

# הגדרות עיצוב עמידות למק, ווינדוס ומובייל
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    * {
        box-sizing: border-box;
    }

    /* העלמת מעטפת Streamlit ומניעת זליגת אלמנטים ברקע */
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
    }

    /* מניעת שקיפות של הסיידבר שמלכלכת את הדף הראשי */
    [data-testid="stSidebarCollapsedControl"] {
        z-index: 100 !important;
    }

    .stApp {
        padding-top: 10px !important;
        direction: rtl;
        text-align: right;
        background-color: #f8fafc;
        color: #0f172a;
        overflow-x: hidden;
    }

    .main .block-container {
        padding: 1.5rem 1rem 3rem 1rem !important;
        max-width: 1180px;
        margin: 0 auto;
        position: relative;
        z-index: 1;
    }

    /* כותרות סדורות וקבועות */
    .section-header-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 28px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
    .section-header-title {
        font-size: 1.6rem;
        font-weight: 900;
        color: #0f2b5c;
        margin: 0;
        white-space: nowrap;
    }
    .section-header-sub {
        color: #64748b;
        font-weight: 600;
        font-size: 0.95rem;
    }

    /* סרגל עליון */
    .learnit-navbar {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 12px 20px;
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
        flex-shrink: 0;
    }
    
    .brand-main-name {
        font-size: 1.3rem;
        font-weight: 900;
        letter-spacing: -0.4px;
        color: #0f2b5c;
        line-height: 1.1;
        white-space: nowrap;
    }
    
    .brand-sub-badge {
        font-size: 0.72rem;
        font-weight: 800;
        color: #2563eb;
        letter-spacing: 0.5px;
        line-height: 1.1;
        white-space: nowrap;
        display: block;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.96)), 
                    url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80') center/cover no-repeat;
        border: 1px solid #e2e8f0;
        border-radius: 24px;
        padding: 34px 20px 22px 20px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
        text-align: center;
    }
    .hero-main-title {
        font-size: 2.5rem;
        font-weight: 900;
        color: #0f2b5c;
        line-height: 1.25;
        margin-bottom: 8px;
    }
    .hero-desc {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 12px;
        font-weight: 500;
    }

    /* שורת יתרונות */
    .features-ribbon {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 12px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 14px 18px;
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
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
    }

    /* כרטיסיות חדרים - אחידות גובה והגנה מספארי */
    .room-tile {
        border-radius: 16px;
        padding: 16px 12px;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.06);
        margin-bottom: 6px;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background-color: #ffffff;
    }
    .room-tile h4 {
        margin: 4px 0 2px 0;
        font-size: 1.05rem;
        font-weight: 800;
        color: #0f2b5c;
        white-space: nowrap;
    }
    .room-tile p {
        font-size: 0.82rem;
        color: #64748b;
        margin: 0;
        white-space: nowrap;
    }

    .cat-purple { background: #f5edff; border-color: #e9d5ff; }
    .cat-blue   { background: #e8f5fe; border-color: #bae6fd; }
    .cat-green  { background: #eafaf1; border-color: #bbf7d0; }
    .cat-orange { background: #fff3e6; border-color: #fed7aa; }
    .cat-yellow { background: #fefce8; border-color: #fef08a; }
    .cat-red    { background: #feebeb; border-color: #fca5a5; }
    .cat-teal   { background: #e6faf7; border-color: #99f6e4; }
    .cat-indigo { background: #eef2ff; border-color: #c7d2fe; }
    .cat-pink   { background: #fdf2f8; border-color: #fbcfe8; }
    .cat-slate  { background: #f8fafc; border-color: #e2e8f0; }

    /* תיבות מידע כלליות */
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
        box-shadow: 0 2px 8px rgba(37, 211, 102, 0.25);
    }

    /* כפתורי מערכת של Streamlit - התאמה מדויקת */
    .stButton button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        margin-bottom: 12px !important;
    }

    /* התאמה לסלולר (Mobile) */
    @media (max-width: 768px) {
        .hero-main-title { font-size: 1.85rem !important; }
        .hero-banner { padding: 22px 14px 18px 14px !important; }
        .section-header-box { flex-direction: column; align-items: flex-start; gap: 4px; }
        .section-header-title { font-size: 1.35rem !important; }
        .features-ribbon { grid-template-columns: 1fr; }
        .room-tile { height: 110px; }
        .room-tile h4 { font-size: 0.95rem; }
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

# --- סרגל צד (בתוך בלוק מסודר) ---
with st.sidebar:
    st.markdown("### 🎓 The Dan Method")
    st.caption("בס״ד | לומדים. מתקדמים.")
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

# --- סרגל ניווט עליון יציב ---
col_nav_logo, col_nav_mode, col_nav_btn = st.columns([2.4, 1.4, 1.2])
with col_nav_logo:
    st.markdown("""
        <div class="learnit-navbar">
            <div class="brand-logo-container">
                <div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #0f2b5c, #2563eb); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
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
        <div class="clean-box" style="text-align: center; max-width: 550px; margin: 40px auto; border-top: 5px solid #1e3a8a;">
            <div style="font-size: 48px; margin-bottom: 10px;">🔒</div>
            <h2 style="color: #0f2b5c; margin: 0 0 8px 0; font-weight: 800;">אזור מוגן לצוות הוראה והנהלה</h2>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 20px;">
                כלי המורים כוללים מחווני בחינה, מערכי שיעור וטפסי הערכה רשמיים.<br>
                הגישה מותרת באמצעות קוד מורה בלבד.
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

# ----------------- 0. דף הבית (המרכז הראשי) -----------------
if st.session_state.current_room == "דף הבית":
    mode_title = "הדרך שלך להצלחה מתחילה כאן." if st.session_state.app_mode == "תלמיד" else "מרחב הפדגוגיה וההוראה החכמה."
    mode_sub = "לימודים קלים יותר, בכל מקום ובכל זמן." if st.session_state.app_mode == "תלמיד" else "הכנת מערכי שיעור, בחנים, מצגות ומחוונים בתוך שניות."
    
    st.markdown(f"""
        <div class="hero-banner">
            <h1 class="hero-main-title">{mode_title}</h1>
            <p class="hero-desc">{mode_sub}<br>שאל את ה-AI שאלה, או בחר כלי עבודה למטה:</p>
        </div>
    """, unsafe_allow_html=True)

    # שורת חיפוש חכמה
    query_search = st.text_input("🔍 שאל שאלה או חפש כלי:", placeholder="למשל: 'איך גוזרים פונקציה?', 'מצגת', 'מבחן'...", label_visibility="collapsed")

    if query_search.strip():
        q_lower = query_search.lower()
        if any(w in q_lower for w in ["מצגת", "שקופיות"]):
            if st.button("📊 מעבר למחולל המצגות", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()
        elif any(w in q_lower for w in ["זום", "מורה מיה"]):
            if st.button("🚀 כניסה לחדר זום עם המורה מיה", use_container_width=True):
                st.session_state.current_room = "חדר זום"
                st.rerun()
        else:
            with st.spinner("דן AI מנסח תשובה..."):
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

    # ----------------- כותרת ומרכז הכרטיסים (התאמה מלאה) -----------------
    if st.session_state.app_mode == "תלמיד":
        st.markdown("""
            <div class="section-header-box">
                <h2 class="section-header-title">מרכז הלמידה של התלמיד</h2>
                <span class="section-header-sub">בחר כלי כדי להתחיל</span>
            </div>
        """, unsafe_allow_html=True)

        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.markdown('<div class="room-tile cat-pink"><div style="font-size:26px;">📊</div><h4>מחולל מצגות</h4><p>שקופיות והערות להצגה</p></div>', unsafe_allow_html=True)
            if st.button("בנה מצגת", key="btn_slides_t", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()

        with col_t2:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:26px;">📹</div><h4>חדר זום חי</h4><p>שיעור קולי 1-על-1</p></div>', unsafe_allow_html=True)
            if st.button("היכנס לזום", key="btn_zoom_t", use_container_width=True):
                st.session_state.current_room = "חדר זום"
                st.rerun()

        with col_t3:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:26px;">📸</div><h4>סורק תרגילים</h4><p>פיענוח מתמונה ודף</p></div>', unsafe_allow_html=True)
            if st.button("פתח סורק", key="btn_scanner_t", use_container_width=True):
                st.session_state.current_room = "סורק תמונות"
                st.rerun()

        with col_t4:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:26px;">📝</div><h4>מבחני דמה</h4><p>סימולציה עם מחוון</p></div>', unsafe_allow_html=True)
            if st.button("בנה מבחן", key="btn_exam_t", use_container_width=True):
                st.session_state.current_room = "מבחני דמה"
                st.rerun()

        col_t5, col_t6, col_t7, col_t8 = st.columns(4)
        with col_t5:
            st.markdown('<div class="room-tile cat-red"><div style="font-size:26px;">🆘</div><h4>חילוץ ב-3 בלילה</h4><p>תוכנית הצלה לפני מבחן</p></div>', unsafe_allow_html=True)
            if st.button("חילוץ לילה", key="btn_panic_t", use_container_width=True):
                st.session_state.current_room = "חילוץ לילה"
                st.rerun()

        with col_t6:
            st.markdown('<div class="room-tile cat-yellow"><div style="font-size:26px;">🚨</div><h4>שליף חירום</h4><p>60 שניות לפני מבחן</p></div>', unsafe_allow_html=True)
            if st.button("הצג שליף", key="btn_cheat_t", use_container_width=True):
                st.session_state.current_room = "שליף חירום"
                st.rerun()

        with col_t7:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:26px;">🩻</div><h4>רנטגן שגיאות</h4><p>מלכודות הבוחנים</p></div>', unsafe_allow_html=True)
            if st.button("גלה מוקשים", key="btn_xray_t", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()

        with col_t8:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:26px;">⚖️</div><h4>מכתב ערעור</h4><p>החזרת נקודות ממורים</p></div>', unsafe_allow_html=True)
            if st.button("נסח ערעור", key="btn_appeal_t", use_container_width=True):
                st.session_state.current_room = "ערעור"
                st.rerun()

        col_t9, col_t10, col_t11, col_t12 = st.columns(4)
        with col_t9:
            st.markdown('<div class="room-tile cat-orange"><div style="font-size:26px;">📐</div><h4>מעבדת מתמטיקה</h4><p>פירוק שלב-אחר-שלב</p></div>', unsafe_allow_html=True)
            if st.button("פרק תרגיל", key="btn_math_t", use_container_width=True):
                st.session_state.current_room = "מעבדת מתמטיקה"
                st.rerun()

        with col_t10:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:26px;">🎴</div><h4>כרטיסיות חזרה</h4><p>שינון מושגים מהיר</p></div>', unsafe_allow_html=True)
            if st.button("פתח כרטיסיות", key="btn_flash_t", use_container_width=True):
                st.session_state.current_room = "כרטיסיות"
                st.rerun()

        with col_t11:
            st.markdown('<div class="room-tile cat-teal"><div style="font-size:26px;">🧘</div><h4>רווחה ופוקוס</h4><p>נשימות 30 שנ\' ורגיעה</p></div>', unsafe_allow_html=True)
            if st.button("מרחב רווחה", key="btn_well_t", use_container_width=True):
                st.session_state.current_room = "רווחה"
                st.rerun()

        with col_t12:
            st.markdown('<div class="room-tile cat-orange"><div style="font-size:26px;">🎯</div><h4>מחשבון בגרות</h4><p>חיזוי הציון הסופי</p></div>', unsafe_allow_html=True)
            if st.button("חשב יעד", key="btn_calc_t", use_container_width=True):
                st.session_state.current_room = "מחשבון"
                st.rerun()

    else:
        # מצב מורה וצוות חינוכי
        st.markdown("""
            <div class="section-header-box">
                <h2 class="section-header-title">מרכז הפדגוגיה והכלים למורים 🔒</h2>
                <span class="section-header-sub" style="color: #16a34a; font-weight: 700;">● מחובר כצוות מאומת</span>
            </div>
        """, unsafe_allow_html=True)

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown('<div class="room-tile cat-pink"><div style="font-size:26px;">📊</div><h4>מחולל מצגות לשיעור</h4><p>מבנה שקופיות והערות מורה</p></div>', unsafe_allow_html=True)
            if st.button("בנה מצגת", key="btn_slides_m", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()

        with col_m2:
            st.markdown('<div class="room-tile cat-indigo"><div style="font-size:26px;">⏱️</div><h4>מערך שיעור (45 דק\')</h4><p>פתיחה, גוף ותרגול מדורג</p></div>', unsafe_allow_html=True)
            if st.button("בנה מערך", key="btn_lesson_m", use_container_width=True):
                st.session_state.current_room = "מערכי שיעור"
                st.rerun()

        with col_m3:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:26px;">📝</div><h4>בוחן פתע + מחוון</h4><p>טופס כיתתי ומחוון בדיקה</p></div>', unsafe_allow_html=True)
            if st.button("ייצר בוחן", key="btn_quiz_m", use_container_width=True):
                st.session_state.current_room = "בחנים ומחוונים"
                st.rerun()

        with col_m4:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:26px;">🏛️</div><h4>מכתב רשמי להנהלה</h4><p>פדגוגיה והצגת פיילוט</p></div>', unsafe_allow_html=True)
            if st.button("הצג מכתב", key="btn_letter_m", use_container_width=True):
                st.session_state.current_room = "הנהלה"
                st.rerun()

        col_m5, col_m6, col_m7, col_m8 = st.columns(4)
        with col_m5:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:26px;">🖨️</div><h4>דפי עבודה להדפסה</h4><p>דפי תרגול מדורגים לכיתה</p></div>', unsafe_allow_html=True)
            if st.button("הפק דף עבודה", key="btn_print_m", use_container_width=True):
                st.session_state.current_room = "דפי הדפסה"
                st.rerun()

        with col_m6:
            st.markdown('<div class="room-tile cat-yellow"><div style="font-size:26px;">🩻</div><h4>איתור מוקשי למידה</h4><p>טעויות נפוצות בנושא</p></div>', unsafe_allow_html=True)
            if st.button("בדוק מלכודות", key="btn_xray_m", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()

        with col_m7:
            st.markdown('<div class="room-tile cat-teal"><div style="font-size:26px;">🧘</div><h4>ארגז כלים ליועצת</h4><p>הפחתת חרדת בחינות</p></div>', unsafe_allow_html=True)
            if st.button("כלים ליועצת", key="btn_well_m", use_container_width=True):
                st.session_state.current_room = "רווחה"
                st.rerun()

        with col_m8:
            st.markdown('<div class="room-tile cat-slate"><div style="font-size:26px;">🗣️</div><h4>מפשט שאלות</h4><p>התאמת ניסוח לתלמידים</p></div>', unsafe_allow_html=True)
            if st.button("פשט שאלה", key="btn_street_m", use_container_width=True):
                st.session_state.current_room = "מתרגם"
                st.rerun()

    # חוות דעת והמלצות
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⭐ מה שאומרים על The Dan Method")
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

# ----------------- שאר החדרים -----------------
elif st.session_state.current_room == "מצגות":
    st.title("📊 מחולל מצגות מקצועי")
    col_sl1, col_sl2 = st.columns(2)
    with col_sl1:
        slide_topic = st.text_input("נושא המצגת:")
        slide_subject = st.selectbox("מקצוע:", ["היסטוריה", "ביולוגיה", "אזרחות", "ספרות", "אנגלית", "מדעים", "גיאוגרפיה", chosen_major])
    with col_sl2:
        slide_count = st.slider("מספר שקופיות:", 3, 8, 5)
        slide_goal = st.selectbox("מטרת המצגת:", ["הצגה פרונטלית (5 דק')", "מצגת שיעור להקניה", "עבודת חקר"])

    if st.button("🔨 צור מצגת", use_container_width=True):
        if slide_topic.strip():
            with st.spinner("בונה מצגת..."):
                res = generate_ai(f"צור שלד מצגת עם {slide_count} שקופיות בנושא {slide_topic} עבור {student_context}. לכל שקופית כותרת, נקודות והערות דובר.")
                st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף בוואטסאפ</a>', unsafe_allow_html=True)

elif st.session_state.current_room == "חדר זום":
    st.title("📹 שיעור פרטי בזום עם המורה מיה")
    z_subject = st.selectbox("מקצוע לשיעור:", ["מתמטיקה", "אנגלית", chosen_major, "היסטוריה", "אזרחות", "לשון והבעה"])
    chat_box = st.container(height=320)
    with chat_box:
        if not st.session_state.zoom_chat_history:
            st.info("👋 המורה מיה: היי! איזה נושא נפרק עכשיו?")
        else:
            for m in st.session_state.zoom_chat_history:
                with st.chat_message(m["role"]):
                    st.write(m["content"])
    text_spoken = st.chat_input("כתוב כאן למורה מיה...")
    if text_spoken:
        st.session_state.zoom_chat_history.append({"role": "user", "content": text_spoken})
        res = generate_ai(f"את המורה מיה בשיעור עם תלמיד ב-{student_context}. עני בקצרה ובגובה העיניים על: {text_spoken}. סיימי בשאלה קצרה לבדיקת הבנה.")
        st.session_state.zoom_chat_history.append({"role": "assistant", "content": res.text})
        st.rerun()

elif st.session_state.current_room == "סורק תמונות":
    st.title("📸 סורק תמונות ושיעורי בית")
    file = st.file_uploader("בחר תמונה:", type=["png", "jpg", "jpeg"])
    if file and st.button("פענח ופתור", use_container_width=True):
        img = Image.open(file)
        with st.spinner("מפענח..."):
            res = generate_ai([f"פתור את התרגיל שבתמונה צעד אחרי צעד עבור {student_context}", img])
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "מבחני דמה":
    st.title("📝 מחולל מבחני דמה")
    top = st.text_input("נושא למבחן:")
    if top and st.button("צור מבחן", use_container_width=True):
        with st.spinner("מייצר שאלות ומחוון..."):
            res = generate_ai(f"צור מבחן קצר של 3 שאלות ומחוון בדיקה עם ניקוד מלא בנושא: {top} עבור {student_context}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "חילוץ לילה":
    st.title("🆘 מצב חילוץ ב-3 בלילה")
    top = st.text_input("מקצוע וחומר למבחן מחר בבוקר:")
    if top and st.button("הצל אותי עכשיו", use_container_width=True):
        with st.spinner("מחלץ..."):
            res = generate_ai(f"תוכנית הצלה קריטית לפני מבחן בנושא: {top} עבור {student_context}. החזר 3 מושגי חובה, הטעות הכי נפוצה, ואיך לפתוח תשובה כדי לקבל נקודות.")
            st.markdown(f'<div class="panic-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "שליף חירום":
    st.title("🚨 שליף חירום: 60 שניות לפני מבחן")
    top = st.text_input("נושא המבחן:")
    if top and st.button("הצג שליף", use_container_width=True):
        with st.spinner("מכין שליף..."):
            res = generate_ai(f"שליף של דקה אחת לפני מבחן בנושא {top}. 3 משפטי זהב וטעות שאסור לעשות.")
            st.markdown(f'<div class="cheat-learnit">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "רנטגן":
    st.title("🩻 רנטגן שגיאות ומלכודות בוחנים")
    top = st.text_input("נושא לבדיקה:")
    if top and st.button("חשוף מלכודות", use_container_width=True):
        with st.spinner("מאתר מוקשים..."):
            res = generate_ai(f"איפה בוחנים מכשילים תלמידים בנושא: {top}? הצג את הטעות הקלאסית ואיך להימנע ממנה.")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "ערעור":
    st.title("⚖️ מחולל מכתב ערעור על ציון")
    q = st.text_input("נושא השאלה:")
    lost = st.text_input("כמה נקודות ירדו ומדוע?")
    if q and lost and st.button("נסח ערעור", use_container_width=True):
        with st.spinner("מנסח..."):
            res = generate_ai(f"נסח מכתב ערעור מנומק ומכבד למורה על שאלה בנושא {q} שבה ירדו {lost} נקודות.")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "מעבדת מתמטיקה":
    st.title("📐 מעבדת פירוק מתמטיקה")
    math_q = st.text_area("הזן תרגיל:")
    if math_q and st.button("פרק תרגיל", use_container_width=True):
        with st.spinner("פותר..."):
            res = generate_ai(f"פתור שלב אחרי שלב בצורה ברורה: {math_q}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "כרטיסיות":
    st.title("🎴 כרטיסיות חזרה")
    top = st.text_input("נושא לשינון:")
    if top and st.button("ייצר כרטיסיות", use_container_width=True):
        with st.spinner("מכין..."):
            res = generate_ai(f"החזר 4 הגדרות מפתח לתכל'ס בנושא: {top}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "רווחה":
    st.title("🧘 מרחב רווחה ופוקוס")
    st.write("תרגיל נשימה להורדת דופק: 4 שניות שאיפה, 4 עצירה, 4 נשיפה.")
    if st.button("הפעל 30 שניות נשימה"):
        prog = st.progress(0)
        for i in range(30):
            time.sleep(1)
            prog.progress((i+1)/30)
        st.success("מעולה! הגוף רגוע והמוח מוכן לקלוט.")

elif st.session_state.current_room == "מחשבון":
    st.title("🎯 מחשבון ציון יעד לבגרות")
    magen = st.number_input("ציון המגן:", 0, 100, 85)
    target = st.number_input("יעד סופי:", 60, 100, 90)
    needed = (target * 100 - (magen * 30)) / 70
    st.info(f"ציון דרוש בבגרות (במשקל 70/30): {round(needed)}")

elif st.session_state.current_room == "מערכי שיעור":
    st.title("⏱️ מחולל מערך שיעור (45 דק')")
    top = st.text_input("נושא השיעור:")
    if top and st.button("בנה מערך", use_container_width=True):
        with st.spinner("מכין מערך..."):
            res = generate_ai(f"מערך שיעור של 45 דקות בנושא {top} עם פתיחה, הקניה ותרגול.")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "בחנים ומחוונים":
    st.title("📝 בוחן פתע + מחוון")
    top = st.text_input("נושא הבוחן:")
    if top and st.button("ייצר בוחן ומחוון", use_container_width=True):
        with st.spinner("מכין..."):
            res = generate_ai(f"בוחן של 15 דקות ומחוון בדיקה למורה בנושא: {top}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "הנהלה":
    st.title("🏛️ מכתב רשמי להנהלה")
    st.markdown("""
        <div class="clean-box">
            <h3>לכבוד הנהלת בית הספר והיועצת החינוכית</h3>
            <p>הנדון: שילוב פלטפורמת 'The Dan Method' לתגבור למידה עצמאית והורדת חרדת בחינות.</p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_room == "דפי הדפסה":
    st.title("🖨️ דפי עבודה להדפסה")
    top = st.text_input("נושא:")
    if top and st.button("הפק דף עבודה", use_container_width=True):
        with st.spinner("מייצר..."):
            res = generate_ai(f"דף עבודה ותרגול מעוצב בנושא {top}")
            st.markdown(res.text)

elif st.session_state.current_room == "מתרגם":
    st.title("🗣️ מפשט שאלות")
    dry = st.text_area("הדבק שאלה מסורבלת:")
    if dry and st.button("פשט שאלה", use_container_width=True):
        with st.spinner("מפשט..."):
            res = generate_ai(f"הסבר בשורה אחת מה מבקשים כאן ואיך מתחילים לענות: {dry}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)
