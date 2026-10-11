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

# עיצוב מותאם לכל המכשירים + ביטול סיידבר מוחלט + כפתורים קריאים וברורים
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* ביטול סיידבר סורר */
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
        padding-top: 10px !important;
        direction: rtl;
        text-align: right;
        background-color: #f8fafc;
        color: #0f172a;
    }

    .main .block-container {
        padding: 1rem 1.5rem 3rem 1.5rem !important;
        max-width: 1100px;
        margin: 0 auto;
    }

    /* כותרת מרכז הלמידה */
    .dashboard-header-container {
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 25px 0 15px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
    .dashboard-header-title {
        font-size: 1.6rem;
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
        padding: 26px 20px 18px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
        text-align: center;
    }
    .hero-main-title {
        font-size: 2.2rem;
        font-weight: 900;
        color: #0f2b5c;
        line-height: 1.25;
        margin-bottom: 6px;
    }
    .hero-desc {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 12px;
        font-weight: 500;
    }

    /* כרטיסיות חדרים - קופסאות יפות ומיושרות */
    .room-tile {
        border-radius: 14px 14px 0 0;
        padding: 16px 10px;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.08);
        border-bottom: none;
        height: 115px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .room-tile h4 {
        margin: 6px 0 2px 0;
        font-size: 1.1rem;
        font-weight: 800;
        color: #0f2b5c;
    }
    .room-tile p {
        font-size: 0.82rem;
        color: #64748b;
        margin: 0;
    }

    .cat-purple { background: #f5edff; }
    .cat-blue   { background: #e8f5fe; }
    .cat-green  { background: #eafaf1; }
    .cat-orange { background: #fff3e6; }
    .cat-yellow { background: #fefce8; }
    .cat-red    { background: #feebeb; }
    .cat-teal   { background: #e6faf7; }
    .cat-indigo { background: #eef2ff; }
    .cat-pink   { background: #fdf2f8; }
    .cat-slate  { background: #f8fafc; }

    /* תיקון הכפתורים השחורים - כפתור כחול/נייבי ברור, קריא ומחובר לכרטיסייה */
    .stButton button {
        background-color: #0f2b5c !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border-radius: 0 0 14px 14px !important;
        border: 1px solid #0f2b5c !important;
        border-top: none !important;
        padding: 8px 12px !important;
        margin-top: 0px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 2px 6px rgba(15, 43, 92, 0.15) !important;
        transition: all 0.2s ease !important;
    }
    .stButton button:hover {
        background-color: #1e40af !important;
        color: #ffffff !important;
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
        .hero-main-title { font-size: 1.75rem !important; }
        .dashboard-header-container { flex-direction: column; align-items: flex-start; gap: 4px; }
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
if "chosen_grade" not in st.session_state:
    st.session_state.chosen_grade = "כיתה ט'"
if "math_units" not in st.session_state:
    st.session_state.math_units = "הקבצה א' / מצוינות"
if "no_yap" not in st.session_state:
    st.session_state.no_yap = True

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

anti_yap_rule = "השב ישירות לתכל'ס, ללא חפירות." if st.session_state.no_yap else ""
student_context = f"שכבת לימוד: {st.session_state.chosen_grade}, מתמטיקה: {st.session_state.math_units}."

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

# --- הגדרת פרופיל נקייה ---
with st.expander(f"👤 הפרופיל שלך: {st.session_state.chosen_grade} | {st.session_state.math_units} (לחץ לשינוי)"):
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

    # כותרת מרכז הלמידה - ברורה, עליונה ומיושרת
    header_text = "מרכז הלמידה של התלמיד" if st.session_state.app_mode == "תלמיד" else "מרכז הכלים למורים וצוות"
    st.markdown(f"""
        <div class="dashboard-header-container">
            <h2 class="dashboard-header-title">{header_text}</h2>
            <span class="dashboard-header-subtitle">בחר כלי כדי להתחיל</span>
        </div>
    """, unsafe_allow_html=True)

    # פריסה של 3 עמודות רחבות - לא נחתכות בשום מסך (3x3 במקום 4 שנמחץ)
    if st.session_state.app_mode == "תלמיד":
        # שורה 1
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="room-tile cat-pink"><div style="font-size:28px;">📊</div><h4>מחולל מצגות</h4><p>שקופיות והערות להצגה</p></div>', unsafe_allow_html=True)
            if st.button("כניסה למחולל מצגות", key="btn_slides_t", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()
        with c2:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:28px;">📹</div><h4>חדר זום חי</h4><p>שיעור קולי 1-על-1</p></div>', unsafe_allow_html=True)
            if st.button("כניסה לחדר זום", key="btn_zoom_t", use_container_width=True):
                st.session_state.current_room = "חדר זום"
                st.rerun()
        with c3:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:28px;">📸</div><h4>סורק תרגילים</h4><p>פיענוח מתמונה ודף</p></div>', unsafe_allow_html=True)
            if st.button("פתיחת סורק תרגילים", key="btn_scanner_t", use_container_width=True):
                st.session_state.current_room = "סורק תמונות"
                st.rerun()

        # שורה 2
        c4, c5, c6 = st.columns(3)
        with c4:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:28px;">📝</div><h4>מבחני דמה</h4><p>סימולציה עם מחוון מלא</p></div>', unsafe_allow_html=True)
            if st.button("בניית מבחן דמה", key="btn_exam_t", use_container_width=True):
                st.session_state.current_room = "מבחני דמה"
                st.rerun()
        with c5:
            st.markdown('<div class="room-tile cat-red"><div style="font-size:28px;">🆘</div><h4>חילוץ ב-3 בלילה</h4><p>תוכנית הצלה דחופה לפני מבחן</p></div>', unsafe_allow_html=True)
            if st.button("הפעלת חילוץ לילה", key="btn_panic_t", use_container_width=True):
                st.session_state.current_room = "חילוץ לילה"
                st.rerun()
        with c6:
            st.markdown('<div class="room-tile cat-yellow"><div style="font-size:28px;">🚨</div><h4>שליף חירום</h4><p>60 שניות לפני הכניסה לכיתה</p></div>', unsafe_allow_html=True)
            if st.button("הצגת שליף חירום", key="btn_cheat_t", use_container_width=True):
                st.session_state.current_room = "שליף חירום"
                st.rerun()

        # שורה 3
        c7, c8, c9 = st.columns(3)
        with c7:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:28px;">🩻</div><h4>רנטגן שגיאות</h4><p>חשיפת מלכודות הבוחנים</p></div>', unsafe_allow_html=True)
            if st.button("גילוי מלכודות", key="btn_xray_t", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()
        with c8:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:28px;">⚖️</div><h4>מכתב ערעור</h4><p>החזרת נקודות בצדק ממורים</p></div>', unsafe_allow_html=True)
            if st.button("ניסוח מכתב ערעור", key="btn_appeal_t", use_container_width=True):
                st.session_state.current_room = "ערעור"
                st.rerun()
        with c9:
            st.markdown('<div class="room-tile cat-orange"><div style="font-size:28px;">📐</div><h4>מעבדת מתמטיקה</h4><p>פירוק שלב-אחר-שלב של תרגילים</p></div>', unsafe_allow_html=True)
            if st.button("פירוק תרגיל מתמטי", key="btn_math_t", use_container_width=True):
                st.session_state.current_room = "מעבדת מתמטיקה"
                st.rerun()

    else:
        # מצב מורה ב-3 עמודות
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown('<div class="room-tile cat-pink"><div style="font-size:28px;">📊</div><h4>מחולל מצגות</h4><p>שקופיות והערות מורה</p></div>', unsafe_allow_html=True)
            if st.button("בניית מצגת לשיעור", key="btn_slides_m", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()
        with m2:
            st.markdown('<div class="room-tile cat-indigo"><div style="font-size:28px;">⏱️</div><h4>מערך שיעור</h4><p>45 דקות מובנות ומדורגות</p></div>', unsafe_allow_html=True)
            if st.button("בניית מערך שיעור", key="btn_lesson_m", use_container_width=True):
                st.session_state.current_room = "מערכי שיעור"
                st.rerun()
        with m3:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:28px;">📝</div><h4>בוחן פתע + מחוון</h4><p>שאלות ומחוון בדיקה כיתתי</p></div>', unsafe_allow_html=True)
            if st.button("יצירת בוחן ומחוון", key="btn_quiz_m", use_container_width=True):
                st.session_state.current_room = "בחנים ומחוונים"
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
