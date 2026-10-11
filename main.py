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

# עיצוב מותאם לכל המכשירים + ביטול סיידבר מוחלט למניעת מריחות
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* חיסול מוחלט של הסיידבר כדי שלא יצוף מאחורי הכרטיסים בספארי ומק */
    [data-testid="stSidebar"], 
    section[data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
        height: 0px !important;
        pointer-events: none !important;
        position: absolute !important;
        left: -9999px !important;
    }

    /* הסרת בר ניהול עליון ותחתון */
    header, [data-testid="stHeader"], footer, [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    .stApp {
        padding-top: 15px !important;
        direction: rtl;
        text-align: right;
        background-color: #f8fafc;
        color: #0f172a;
    }

    .main .block-container {
        padding: 1.5rem 1rem 3rem 1rem !important;
        max-width: 1140px;
        margin: 0 auto;
    }

    /* כותרת מרכז הלמידה - מיושרת, ברורה ולא נחתכת */
    .dashboard-header-container {
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 35px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #e2e8f0;
    }
    .dashboard-header-title {
        font-size: 1.7rem;
        font-weight: 900;
        color: #0f2b5c;
        margin: 0;
    }
    .dashboard-header-subtitle {
        color: #64748b;
        font-weight: 700;
        font-size: 0.95rem;
    }

    /* Navbar */
    .learnit-navbar {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 10px 18px;
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
        color: #0f2b5c;
        line-height: 1.1;
    }
    .brand-sub-badge {
        font-size: 0.7rem;
        font-weight: 800;
        color: #2563eb;
        line-height: 1.1;
    }

    /* Hero */
    .hero-banner {
        background: linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.96)), 
                    url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80') center/cover no-repeat;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 30px 20px 20px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
        text-align: center;
    }
    .hero-main-title {
        font-size: 2.3rem;
        font-weight: 900;
        color: #0f2b5c;
        line-height: 1.25;
        margin-bottom: 6px;
    }
    .hero-desc {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 12px;
        font-weight: 500;
    }

    /* כרטיסיות חדרים - יציבות ללא עיוות */
    .room-tile {
        border-radius: 14px;
        padding: 14px 10px;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.06);
        margin-bottom: 6px;
        height: 110px;
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
    }
    .room-tile p {
        font-size: 0.8rem;
        color: #64748b;
        margin: 0;
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

    /* כפתורי מערכת Streamlit אחידים */
    .stButton button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        margin-bottom: 12px !important;
    }

    .clean-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 16px;
    }
    .panic-box {
        background: #fef2f2;
        border: 2px solid #ef4444;
        border-radius: 16px;
        padding: 22px;
        color: #991b1b;
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
    }

    @media (max-width: 768px) {
        .hero-main-title { font-size: 1.8rem !important; }
        .dashboard-header-container { flex-direction: column; align-items: flex-start; gap: 4px; }
        .dashboard-header-title { font-size: 1.4rem !important; }
        .room-tile { height: 100px; }
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
if "slides_data" not in st.session_state:
    st.session_state.slides_data = None
if "chosen_grade" not in st.session_state:
    st.session_state.chosen_grade = "כיתה ט'"
if "chosen_major" not in st.session_state:
    st.session_state.chosen_major = "ללא מגמה (מקצועות ליבה)"
if "math_units" not in st.session_state:
    st.session_state.math_units = "הקבצה א' / מצוינות"
if "eng_units" not in st.session_state:
    st.session_state.eng_units = "הקבצה א' / דוברי אנגלית"
if "no_yap" not in st.session_state:
    st.session_state.no_yap = True
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

def generate_ai(contents):
    models = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
    last_err = None
    for m in models:
        for _ in range(2):
            try:
                return client.models.generate_content(model=m, contents=contents)
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
    return json.loads(text)

def get_whatsapp_share_link(text):
    encoded = urllib.parse.quote(f"היי, מצאתי את זה ב-The Dan Method:\n\n{text[:450]}")
    return f"https://api.whatsapp.com/send?text={encoded}"

# --- סרגל ניווט עליון יציב ---
col_nav_logo, col_nav_mode, col_nav_btn = st.columns([2.4, 1.4, 1.2])
with col_nav_logo:
    st.markdown("""
        <div class="learnit-navbar">
            <div class="brand-logo-container">
                <div style="width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #0f2b5c, #2563eb); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
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
        "מצב:",
        ["תלמיד 🎓", "מורה 🧑‍🏫"],
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
    if st.button("🏠 דף הבית", key="nav_home_main", use_container_width=True):
        st.session_state.current_room = "דף הבית"
        st.rerun()

# --- הגדרת פרופיל (ישירות בדף, ללא Sidebar שובר) ---
with st.expander(f"👤 הפרופיל שלך: {st.session_state.chosen_grade} | {st.session_state.math_units} (לחץ לעריכה)"):
    cp1, cp2, cp3 = st.columns(3)
    with cp1:
        st.session_state.chosen_grade = st.selectbox(
            "שכבת לימוד:",
            ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב (בגרות)"],
            index=["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב (בגרות)"].index(st.session_state.chosen_grade)
        )
    with cp2:
        st.session_state.math_units = st.selectbox("מתמטיקה:", ["הקבצה א' / 5 יח'", "הקבצה ב' / 4 יח'", "רמה רגילה / 3 יח'"])
    with cp3:
        st.session_state.no_yap = st.toggle("מצב תכל'ס (קצר וממוקד)", value=st.session_state.no_yap)

anti_yap_rule = "השב ישירות לתכל'ס, ללא חפירות." if st.session_state.no_yap else ""
student_context = f"שכבת לימוד: {st.session_state.chosen_grade}, מתמטיקה: {st.session_state.math_units}."

# בדיקת אבטחה למצב מורה
if st.session_state.app_mode == "מורה" and not st.session_state.teacher_authenticated:
    st.markdown("""
        <div class="clean-box" style="text-align: center; max-width: 500px; margin: 30px auto;">
            <div style="font-size: 40px; margin-bottom: 8px;">🔒</div>
            <h3 style="color: #0f2b5c; margin: 0 0 8px 0;">כניסה למרחב מורים</h3>
            <p style="color: #64748b; font-size: 0.9rem;">הזן קוד מורה כדי לפתוח את כלי ההוראה.</p>
        </div>
    """, unsafe_allow_html=True)
    c_l1, c_l2, c_l3 = st.columns([1, 1.2, 1])
    with c_l2:
        code_input = st.text_input("קוד גישה:", type="password", placeholder="הזן קוד...")
        if st.button("🔓 כניסה לחדר מורים", use_container_width=True):
            if code_input.strip() == TEACHER_ACCESS_CODE:
                st.session_state.teacher_authenticated = True
                st.rerun()
            else:
                st.error("קוד שגוי.")
    st.stop()

# ----------------- 0. דף הבית (המרכז הראשי) -----------------
if st.session_state.current_room == "דף הבית":
    mode_title = "הדרך שלך להצלחה מתחילה כאן." if st.session_state.app_mode == "תלמיד" else "מרחב הפדגוגיה וההוראה החכמה."
    mode_sub = "לימודים קלים יותר, בכל מקום ובכל זמן." if st.session_state.app_mode == "תלמיד" else "הכנת מערכי שיעור, בחנים, מצגות ומחוונים בתוך שניות."
    
    st.markdown(f"""
        <div class="hero-banner">
            <h1 class="hero-main-title">{mode_title}</h1>
            <p class="hero-desc">{mode_sub}</p>
        </div>
    """, unsafe_allow_html=True)

    # שורת שאילתה חכמה
    query_search = st.text_input("🔍 שאל שאלה מהירה את דן AI:", placeholder="למשל: 'איך גוזרים פונקציה?', 'משפט חוצה זווית'...")
    if query_search.strip():
        with st.spinner("דן AI מנסח תשובה..."):
            res_bot = generate_ai(f"אתה עוזר לימודי אישי חכם. הקשר: {student_context}. ענה ישירות, קצר ולעניין: {query_search}. {anti_yap_rule}")
            st.markdown(f"""
                <div class="clean-box" style="border-right: 4px solid #3b82f6;">
                    <h4 style="margin: 0; color: #1e3a8a;">💡 מענה מהיר של דן AI:</h4>
                    <p style="margin-top: 8px;">{res_bot.text}</p>
                </div>
            """, unsafe_allow_html=True)

    # כותרת מרכז הלמידה - נקייה ובטוחה
    header_text = "מרכז הלמידה של התלמיד" if st.session_state.app_mode == "תלמיד" else "מרכז הכלים למורים וצוות"
    st.markdown(f"""
        <div class="dashboard-header-container">
            <h2 class="dashboard-header-title">{header_text}</h2>
            <span class="dashboard-header-subtitle">בחר כלי כדי להתחיל</span>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.app_mode == "תלמיד":
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
            st.markdown('<div class="room-tile cat-teal"><div style="font-size:26px;">🧘</div><h4>רווחה ופוקוס</h4><p>נשימות ורגיעה</p></div>', unsafe_allow_html=True)
            if st.button("מרחב רווחה", key="btn_well_t", use_container_width=True):
                st.session_state.current_room = "רווחה"
                st.rerun()

        with col_t12:
            st.markdown('<div class="room-tile cat-orange"><div style="font-size:26px;">🎯</div><h4>מחשבון בגרות</h4><p>חיזוי הציון הסופי</p></div>', unsafe_allow_html=True)
            if st.button("חשב יעד", key="btn_calc_t", use_container_width=True):
                st.session_state.current_room = "מחשבון"
                st.rerun()

    else:
        # מצב מורה
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown('<div class="room-tile cat-pink"><div style="font-size:26px;">📊</div><h4>מחולל מצגות לשיעור</h4><p>שקופיות והערות מורה</p></div>', unsafe_allow_html=True)
            if st.button("בנה מצגת", key="btn_slides_m", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()

        with col_m2:
            st.markdown('<div class="room-tile cat-indigo"><div style="font-size:26px;">⏱️</div><h4>מערך שיעור (45 דק\')</h4><p>פתיחה, גוף ותרגול</p></div>', unsafe_allow_html=True)
            if st.button("בנה מערך", key="btn_lesson_m", use_container_width=True):
                st.session_state.current_room = "מערכי שיעור"
                st.rerun()

        with col_m3:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:26px;">📝</div><h4>בוחן פתע + מחוון</h4><p>שאלות ומחוון בדיקה</p></div>', unsafe_allow_html=True)
            if st.button("ייצר בוחן", key="btn_quiz_m", use_container_width=True):
                st.session_state.current_room = "בחנים ומחוונים"
                st.rerun()

        with col_m4:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:26px;">🏛️</div><h4>מכתב רשמי להנהלה</h4><p>הצגת פיילוט ליועצת</p></div>', unsafe_allow_html=True)
            if st.button("הצג מכתב", key="btn_letter_m", use_container_width=True):
                st.session_state.current_room = "הנהלה"
                st.rerun()

# ----------------- החדרים הנוספים -----------------
elif st.session_state.current_room == "מצגות":
    st.title("📊 מחולל מצגות מקצועי")
    topic = st.text_input("נושא המצגת:")
    if st.button("בנה שלד מצגת", use_container_width=True) and topic:
        with st.spinner("בונה מצגת..."):
            res = generate_ai(f"בנה שלד מצגת של 5 שקופיות בנושא {topic} עבור {student_context}. לכל שקופית כותרת, נקודות והערות דובר.")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "חדר זום":
    st.title("📹 שיעור פרטי בזום עם המורה מיה")
    chat_box = st.container(height=320)
    with chat_box:
        if not st.session_state.zoom_chat_history:
            st.info("👋 המורה מיה: היי! מה נלמד עכשיו?")
        else:
            for m in st.session_state.zoom_chat_history:
                with st.chat_message(m["role"]):
                    st.write(m["content"])
    text_input = st.chat_input("כתוב כאן למורה מיה...")
    if text_input:
        st.session_state.zoom_chat_history.append({"role": "user", "content": text_input})
        res = generate_ai(f"את המורה מיה. תלמיד: {student_context}. עני בקצרה ובגובה העיניים על: {text_input}")
        st.session_state.zoom_chat_history.append({"role": "assistant", "content": res.text})
        st.rerun()

elif st.session_state.current_room == "סורק תמונות":
    st.title("📸 סורק תמונות ושיעורי בית")
    file = st.file_uploader("העלה תמונת תרגיל:", type=["png", "jpg", "jpeg"])
    if file and st.button("פתור תרגיל", use_container_width=True):
        img = Image.open(file)
        with st.spinner("מפענח..."):
            res = generate_ai([f"פתור את התרגיל שבתמונה צעד אחרי צעד עבור {student_context}", img])
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "מבחני דמה":
    st.title("📝 מחולל מבחני דמה")
    top = st.text_input("נושא למבחן:")
    if top and st.button("צור מבחן", use_container_width=True):
        with st.spinner("יוצר שאלות..."):
            res = generate_ai(f"צור מבחן קצר של 3 שאלות ומחוון בדיקה בנושא: {top} עבור {student_context}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "חילוץ לילה":
    st.title("🆘 מצב חילוץ ב-3 בלילה")
    top = st.text_input("חומר למבחן מחר:")
    if top and st.button("הצל אותי עכשיו", use_container_width=True):
        with st.spinner("מחלץ..."):
            res = generate_ai(f"תוכנית חילוץ לפני מבחן: {top}. 3 מושגי חובה, טעויות קלאסיות ומשפטי מפתח.")
            st.markdown(f'<div class="panic-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "שליף חירום":
    st.title("🚨 שליף חירום: 60 שניות לפני מבחן")
    top = st.text_input("נושא המבחן:")
    if top and st.button("הצג שליף", use_container_width=True):
        with st.spinner("מכין..."):
            res = generate_ai(f"שליף של 60 שניות בנושא: {top}. תכל'ס בלבד.")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "רנטגן":
    st.title("🩻 רנטגן שגיאות ומלכודות בוחנים")
    top = st.text_input("נושא:")
    if top and st.button("חשוף מלכודות", use_container_width=True):
        with st.spinner("מאתר מוקשים..."):
            res = generate_ai(f"איפה בוחנים מכשילים בנושא {top} ואיך להימנע?")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "ערעור":
    st.title("⚖️ מחולל מכתב ערעור על ציון")
    q = st.text_input("על מה ירדו נקודות?")
    if q and st.button("נסח ערעור", use_container_width=True):
        with st.spinner("מנסח..."):
            res = generate_ai(f"נסח מכתב ערעור מנומק למורה על: {q}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "מעבדת מתמטיקה":
    st.title("📐 מעבדת מתמטיקה")
    q = st.text_area("הזן תרגיל:")
    if q and st.button("פתור שלב-אחר-שלב", use_container_width=True):
        with st.spinner("פותר..."):
            res = generate_ai(f"פתור צעד אחרי צעד: {q}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "כרטיסיות":
    st.title("🎴 כרטיסיות חזרה")
    top = st.text_input("נושא:")
    if top and st.button("ייצר כרטיסיות", use_container_width=True):
        with st.spinner("מייצר..."):
            res = generate_ai(f"4 כרטיסיות שינון קצרות בנושא: {top}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "רווחה":
    st.title("🧘 מרחב רווחה ופוקוס")
    st.write("תרגיל נשימה 4-4-4 להורדת מתח לפני למידה.")
    if st.button("הפעל טיימר 30 שניות"):
        prog = st.progress(0)
        for i in range(30):
            time.sleep(1)
            prog.progress((i+1)/30)
        st.success("מעולה! הגוף רגוע וכעת הלמידה תהיה אפקטיבית.")

elif st.session_state.current_room == "מחשבון":
    st.title("🎯 מחשבון ציון יעד לבגרות")
    magen = st.number_input("ציון מגן:", 0, 100, 85)
    target = st.number_input("יעד סופי:", 60, 100, 90)
    needed = (target * 100 - (magen * 30)) / 70
    st.info(f"ציון דרוש בבגרות: {round(needed)}")

elif st.session_state.current_room == "מערכי שיעור":
    st.title("⏱️ מחולל מערך שיעור (45 דק')")
    top = st.text_input("נושא:")
    if top and st.button("בנה מערך", use_container_width=True):
        with st.spinner("מכין..."):
            res = generate_ai(f"מערך שיעור 45 דק' בנושא {top}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "בחנים ומחוונים":
    st.title("📝 בוחן פתע ומחוון")
    top = st.text_input("נושא:")
    if top and st.button("ייצר בוחן ומחוון", use_container_width=True):
        with st.spinner("מכין..."):
            res = generate_ai(f"בוחן 15 דק' ומחוון בנושא {top}")
            st.markdown(f'<div class="clean-box">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "הנהלה":
    st.title("🏛️ מכתב רשמי להנהלה")
    st.markdown("""
        <div class="clean-box">
            <h3>לכבוד הנהלת בית הספר</h3>
            <p>הנדון: שילוב פלטפורמת 'The Dan Method' לשיפור הישגים ולמידה עצמאית.</p>
        </div>
    """, unsafe_allow_html=True)
