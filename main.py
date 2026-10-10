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
    page_title="The Dan Method | לומדים. מתקדמים.",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# שפת עיצוב LearnIt נקייה, מודרנית והסרת סרגלי Streamlit
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700;800;900&display=swap');

    * {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* הסתרת סרגלי הניהול המובנים של Streamlit */
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
        padding: 42px 26px 26px 26px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
        margin-bottom: 22px;
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
        margin-bottom: 28px;
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
    .cat-slate  { background: #f1f5f9; border-color: #e2e8f0; }

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
    .cheat-learnit {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 16px;
        padding: 24px;
        color: #92400e;
        margin-top: 14px;
        line-height: 1.7;
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
    .portal-tag-learnit {
        display: inline-block;
        padding: 8px 16px;
        background: #f8fafc;
        color: #1e3a8a !important;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 700;
        margin-left: 8px;
        margin-bottom: 8px;
    }

    /* כפתור שיתוף לוואטסאפ */
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
    .whatsapp-btn:hover {
        background-color: #1ebe57;
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

# אתחול Session States וזיכרון מטמון
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
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "השליף חירום סגר לי את החומר לפני המבחן בהיסטוריה."},
        {"name": "נועה ל.", "grade": "כיתה י\"א (ביולוגיה)", "rating": 5, "text": "עיצוב נוח, נקי ובלי סרבול."},
        {"name": "מאיה ר.", "grade": "כיתה י\"א (5 יח')", "rating": 5, "text": "מפרק המתמטיקה מסביר לפי מחוון בגרות בדיוק כמו שצריך."}
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
    text = re.sub(r"^```json\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text.strip(), flags=re.MULTILINE)
    return json.loads(text.strip("`").strip())

def get_tts_audio_url(text):
    clean_text = re.sub(r"[*#_`>\[\]\(\)]", "", text)
    clean_text = clean_text[:200]
    encoded = urllib.parse.quote(clean_text)
    return f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl=iw&client=tw-ob"

def get_whatsapp_share_link(text):
    encoded = urllib.parse.quote(f"היי, הנה משהו שימושי מ-The Dan Method:\n\n{text[:450]}")
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

anti_yap_rule = "השב ישירות לתכל'ס, ללא פסקאות פתיחה או סיום מיותרות." if no_yap else ""
student_context = f"שכבת לימוד: {chosen_grade}, מתמטיקה: {math_units}, אנגלית: {eng_units}, מגמה: {chosen_major}."

# --- סרגל ניווט עליון עצמאי עם לוגו מעוצב וכפתור בית ---
col_nav_logo, col_nav_btn = st.columns([3.8, 1.2])
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
            <div style="color: #64748b; font-size: 0.95rem; font-weight: 600;">
                מחובר: <b>""" + chosen_grade + """ (""" + math_units + """)</b>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col_nav_btn:
    if st.button("🏠 עמוד הבית", key="nav_home_main", use_container_width=True):
        st.session_state.current_room = "דף הבית"
        st.rerun()

# --- עוזר AI צף לסגירת פינות מהירה (זמין בכל מסך) ---
with st.expander("💡 דן AI – שאלת הבהרה מהירה (זמין מכל מסך)", expanded=False):
    col_f1, col_f2 = st.columns([3.5, 1])
    with col_f1:
        quick_ai_q = st.text_input("שאל שאלה קצרה:", placeholder="למשל: מה הנוסחה לשטח משולש? למה מורידים נקודות על סעיף כזה?", label_visibility="collapsed")
    with col_f2:
        btn_quick_ask = st.button("שאל עכשיו", key="btn_quick_ai", use_container_width=True)
    if btn_quick_ask and quick_ai_q.strip():
        with st.spinner("דן AI עונה..."):
            try:
                res_fast = generate_ai(f"אתה עוזר לימודי אישי חכם לתלמיד ב-{student_context}. ענה ישירות, קצר וממוקד ב-2 שורות בלבד: {quick_ai_q}. {anti_yap_rule}")
                st.info(res_fast.text)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_fast.text)}" target="_blank">📲 שתף בוואטסאפ</a>', unsafe_allow_html=True)
            except Exception:
                st.warning("הייתה תקלה קלה, נסה לשאול שוב.")

# ----------------- דף הבית (המרכז הראשי) -----------------
if st.session_state.current_room == "דף הבית":
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-main-title">הדרך שלך להצלחה<br>מתחילה כאן.</h1>
            <p class="hero-desc">
                לומדים בקלות, בכל מקום ובכל זמן.<br>
                שאל את ה-AI שאלה, או בחר כלי ומקצוע:
            </p>
        </div>
    """, unsafe_allow_html=True)

    query_search = st.text_input("🔍 מה תרצה ללמוד או לשאול היום?", placeholder="שאל שאלה לימודית, או חפש כלי (למשל: 'איך גוזרים פונקציה?', 'זום', 'מבחן', 'חילוץ')...")

    if query_search.strip():
        q_lower = query_search.lower()
        if any(w in q_lower for w in ["זום", "מורה", "שיעור פרטי"]):
            if st.button("🚀 כניסה ישירה לחדר זום עם המורה מיה", use_container_width=True):
                st.session_state.current_room = "חדר זום"
                st.rerun()
        elif any(w in q_lower for w in ["חילוץ", "לילה", "בהול", "חירום 3"]):
            if st.button("🚨 כניסה ישירה למצב חילוץ ב-3 בלילה", use_container_width=True):
                st.session_state.current_room = "חילוץ לילה"
                st.rerun()
        elif any(w in q_lower for w in ["מבחן", "דמה", "סימולציה"]):
            if st.button("🚀 כניסה ישירה למחולל מבחני דמה", use_container_width=True):
                st.session_state.current_room = "מבחני דמה"
                st.rerun()
        elif any(w in q_lower for w in ["ערעור", "ציון", "מכתב"]):
            if st.button("📝 כניסה ישירה למחולל מכתבי ערעור", use_container_width=True):
                st.session_state.current_room = "ערעור"
                st.rerun()
        elif any(w in q_lower for w in ["שליף", "חירום", "60"]):
            if st.button("🚀 כניסה ישירה לשליף חירום", use_container_width=True):
                st.session_state.current_room = "שליף חירום"
                st.rerun()
        elif any(w in q_lower for w in ["סורק", "תמונה", "שיעורי בית"]):
            if st.button("🚀 כניסה ישירה לסורק התמונות", use_container_width=True):
                st.session_state.current_room = "סורק תמונות"
                st.rerun()
        else:
            with st.spinner("דן AI מנסח תשובה ממוקדת..."):
                try:
                    res_bot = generate_ai(f"אתה עוזר לימודי אישי חכם לתלמיד ב-{student_context}. ענה על השאלה ישירות, ברור וקצר לתכל'ס בלי חפירות: {query_search}. {anti_yap_rule}", use_cache=True)
                    st.markdown("""
                        <div class="clean-box" style="border-right: 4px solid #3b82f6;">
                            <h4 style="margin: 0; color: #1e3a8a;">💡 מענה מהיר של דן AI:</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(res_bot.text)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_bot.text)}" target="_blank">📲 שתף פתרון בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.warning("לא הצלחנו לפענח כרגע, נסה לשאול שוב.")

    st.markdown("""
        <div class="features-ribbon">
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #f3e8ff; color: #9333ea;">📖</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">תוכן איכותי ומדויק</div>
                    <div style="color:#64748b; font-size:0.8rem;">הסברים ממוקדים לבגרות</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #e0f2fe; color: #0284c7;">⏱️</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">לומדים בקצב שלך</div>
                    <div style="color:#64748b; font-size:0.8rem;">גישה חופשית ומיידית 24/7</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #dcfce7; color: #16a34a;">👥</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">כל המגמות וההקבצות</div>
                    <div style="color:#64748b; font-size:0.8rem;">התאמה מלאה לרמתך</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #fef9c3; color: #ca8a04;">⭐</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">מתאים לכל תלמיד</div>
                    <div style="color:#64748b; font-size:0.8rem;">מחטיבה ועד בגרות</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h2 style="font-size: 1.5rem; font-weight: 800; color: #0f2b5c; margin: 0;">מרכז הלמידה והכלים המתקדמים</h2>
            <span style="color: #64748b; font-weight: 600; font-size: 0.95rem;">בחר כלי כדי להתחיל לתרגל</span>
        </div>
    """, unsafe_allow_html=True)

    # שורה 1: כלי בסיס
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.markdown('<div class="room-tile cat-blue"><div style="font-size:30px;">📹</div><h4 style="margin:4px 0;">חדר זום חי</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">שיעור קולי 1-על-1</p></div>', unsafe_allow_html=True)
        if st.button("היכנס לזום", key="btn_zoom", use_container_width=True):
            st.session_state.current_room = "חדר זום"
            st.rerun()

    with g2:
        st.markdown('<div class="room-tile cat-purple"><div style="font-size:30px;">📸</div><h4 style="margin:4px 0;">סורק תרגילים</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פיענוח מתמונה ודף</p></div>', unsafe_allow_html=True)
        if st.button("פתח סורק", key="btn_scanner", use_container_width=True):
            st.session_state.current_room = "סורק תמונות"
            st.rerun()

    with g3:
        st.markdown('<div class="room-tile cat-green"><div style="font-size:30px;">📝</div><h4 style="margin:4px 0;">מבחני דמה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">סימולציה עם מחוון</p></div>', unsafe_allow_html=True)
        if st.button("בנה מבחן", key="btn_exam", use_container_width=True):
            st.session_state.current_room = "מבחני דמה"
            st.rerun()

    with g4:
        st.markdown('<div class="room-tile cat-orange"><div style="font-size:30px;">📐</div><h4 style="margin:4px 0;">מעבדת מתמטיקה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פירוק שלב-אחר-שלב</p></div>', unsafe_allow_html=True)
        if st.button("פרק תרגיל", key="btn_math", use_container_width=True):
            st.session_state.current_room = "מעבדת מתמטיקה"
            st.rerun()

    # שורה 2: כלי מהירות וחירום
    g5, g6, g7, g8 = st.columns(4)
    with g5:
        st.markdown('<div class="room-tile cat-red"><div style="font-size:30px;">🆘</div><h4 style="margin:4px 0;">חילוץ ב-3 בלילה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">תוכנית הצלה לפני מבחן</p></div>', unsafe_allow_html=True)
        if st.button("פתח חילוץ לילה", key="btn_panic", use_container_width=True):
            st.session_state.current_room = "חילוץ לילה"
            st.rerun()

    with g6:
        st.markdown('<div class="room-tile cat-yellow"><div style="font-size:30px;">🚨</div><h4 style="margin:4px 0;">שליף חירום</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">60 שניות לפני מבחן</p></div>', unsafe_allow_html=True)
        if st.button("הצג שליף", key="btn_cheat", use_container_width=True):
            st.session_state.current_room = "שליף חירום"
            st.rerun()

    with g7:
        st.markdown('<div class="room-tile cat-slate"><div style="font-size:30px;">💯</div><h4 style="margin:4px 0;">מלטשת תשובות</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">שדרוג למחוון 100</p></div>', unsafe_allow_html=True)
        if st.button("לטש תשובה", key="btn_polish", use_container_width=True):
            st.session_state.current_room = "מלטשת תשובות"
            st.rerun()

    with g8:
        st.markdown('<div class="room-tile cat-purple"><div style="font-size:30px;">🩻</div><h4 style="margin:4px 0;">רנטגן שגיאות</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">מלכודות הבוחנים</p></div>', unsafe_allow_html=True)
        if st.button("גלה מוקשים", key="btn_xray", use_container_width=True):
            st.session_state.current_room = "רנטגן"
            st.rerun()

    # שורה 3: כלים חדשים שוברי שוק
    g9, g10, g11, g12 = st.columns(4)
    with g9:
        st.markdown('<div class="room-tile cat-blue"><div style="font-size:30px;">⚖️</div><h4 style="margin:4px 0;">מכתב ערעור על ציון</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">החזרת נקודות ממורים</p></div>', unsafe_allow_html=True)
        if st.button("נסח ערעור", key="btn_appeal", use_container_width=True):
            st.session_state.current_room = "ערעור"
            st.rerun()

    with g10:
        st.markdown('<div class="room-tile cat-green"><div style="font-size:30px;">🎴</div><h4 style="margin:4px 0;">כרטיסיות חזרה</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">שינון מושגים מהיר</p></div>', unsafe_allow_html=True)
        if st.button("פתח כרטיסיות", key="btn_flash", use_container_width=True):
            st.session_state.current_room = "כרטיסיות"
            st.rerun()

    with g11:
        st.markdown('<div class="room-tile cat-orange"><div style="font-size:30px;">🎯</div><h4 style="margin:4px 0;">מחשבון בגרות ומגן</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">חיזוי הציון הסופי</p></div>', unsafe_allow_html=True)
        if st.button("חשב ציון יעד", key="btn_calc", use_container_width=True):
            st.session_state.current_room = "מחשבון"
            st.rerun()

    with g12:
        st.markdown('<div class="room-tile cat-slate"><div style="font-size:30px;">🗣️</div><h4 style="margin:4px 0;">מתרגם סלנג לימודי</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">תרגום שאלות לתכל\'ס</p></div>', unsafe_allow_html=True)
        if st.button("תרגם שאלה", key="btn_street", use_container_width=True):
            st.session_state.current_room = "מתרגם"
            st.rerun()

    # שורה 4: כלי עזר
    g13, g14, g15, g16 = st.columns(4)
    with g13:
        st.markdown('<div class="room-tile cat-blue"><div style="font-size:30px;">🎬</div><h4 style="margin:4px 0;">ספריית וידאו</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">שיעורים ממוקדים</p></div>', unsafe_allow_html=True)
        if st.button("צפה בשיעורים", key="btn_video", use_container_width=True):
            st.session_state.current_room = "ספריית וידאו"
            st.rerun()

    with g14:
        st.markdown('<div class="room-tile cat-purple"><div style="font-size:30px;">🖨️</div><h4 style="margin:4px 0;">דפי תרגול</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">הדפסה נקייה במדפסת</p></div>', unsafe_allow_html=True)
        if st.button("הפק דף עבודה", key="btn_print", use_container_width=True):
            st.session_state.current_room = "דפי הדפסה"
            st.rerun()

    with g15:
        st.markdown('<div class="room-tile cat-green"><div style="font-size:30px;">🏫</div><h4 style="margin:4px 0;">Classroom וספרים</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">פורטלים ושיעורי בית</p></div>', unsafe_allow_html=True)
        if st.button("פתח פורטל", key="btn_classroom", use_container_width=True):
            st.session_state.current_room = "קלאסרום"
            st.rerun()

    with g16:
        st.markdown('<div class="room-tile cat-orange"><div style="font-size:30px;">📅</div><h4 style="margin:4px 0;">מתכנן לו״ז</h4><p style="font-size:0.85rem; color:#64748b; margin:0;">תוכנית עבודה למבחן</p></div>', unsafe_allow_html=True)
        if st.button("תכנן לו״ז", key="btn_sched", use_container_width=True):
            st.session_state.current_room = "לוז"
            st.rerun()

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
                f"התלמיד ב-{student_context} רוצה לדעת איפה בוחנים מכשילים תלמידים בנושא: {xray_topic}.\n"
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

# ----------------- חדר: מחולל מכתב ערעור על ציון -----------------
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

# ----------------- חדר: כרטיסיות חזרה מהירות -----------------
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

# ----------------- חדר: מחשבון בגרות ומגן -----------------
elif st.session_state.current_room == "מחשבון":
    st.title("🎯 מחשבון ציון יעד לבגרות ומגן")
    st.caption("בדוק בדיוק כמה אתה חייב להוציא בבגרות כדי לסיים עם הציון שאתה רוצה.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        magen_score = st.number_input("ציון המגן השנתי שלך (הערכה בית-ספרית):", 0, 100, 85)
        magen_weight = st.slider("אחוז משקל המגן (לרוב 30% או 50%):", 10, 50, 30, step=10)
    with col_c2:
        target_final = st.number_input("מה הציון הסופי שאתה מכוון אליו?", 60, 100, 90)
    
    bagrut_weight = 100 - magen_weight
    # חישוב: target = (magen * weight + bagrut * weight) / 100
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

# ----------------- חדר: מלטשת תשובות -----------------
elif st.session_state.current_room == "מלטשת תשובות":
    st.title("💯 מלטשת תשובות לציון 100")
    a_top = st.text_input("מקצוע ונושא השאלה:")
    a_q = st.text_input("מה השאלה?")
    a_ans = st.text_area("התשובה שכתבת:", height=100)
    if st.button("שדרג תשובה ל-100 🚀", use_container_width=True):
        if a_top and a_ans:
            with st.spinner("מלטש לפי מחוון..."):
                try:
                    res = generate_ai(f"מעריך בחינות קפדן לתלמיד ב-{student_context}.\nחומר: {a_top}\nשאלה: {a_q}\nתשובה: {a_ans}\nהחזר: 1. ציון מוערך 2. מה חסר 3. תשובה מושלמת סופית שסוגרת 100 נקודות. {anti_yap_rule}")
                    st.markdown(res.text)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף תשובת מחוון בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception:
                    st.error("שגיאה בליטוש התשובה.")

# ----------------- חדר: ספריית וידאו -----------------
elif st.session_state.current_room == "ספריית וידאו":
    st.title("🎬 ספריית שיעורי וידאו ממוקדים")
    v_links = {
        "משפט פיתגורס": "https://www.youtube.com/watch?v=xAgLlIAum3c",
        "משוואה ריבועית": "https://www.youtube.com/watch?v=fghk_W4x_eM",
        "Present Simple vs Progressive": "https://www.youtube.com/watch?v=L9AWrJnhsRI",
        "שלושת חוקי ניוטון": "https://www.youtube.com/watch?v=kKKM8Y-u7ds"
    }
    chosen_v = st.selectbox("בחר שיעור:", list(v_links.keys()))
    st.video(v_links[chosen_v])

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

# ----------------- חדר: קלאסרום וספרים -----------------
elif st.session_state.current_room == "קלאסרום":
    st.title("🏫 Classroom וספרי לימוד")
    st.markdown("""
        <div>
            <a class="portal-tag-learnit" href="https://classroom.google.com" target="_blank">🌐 Google Classroom</a>
            <a class="portal-tag-learnit" href="https://www.classoos.com" target="_blank">📖 Classoos</a>
            <a class="portal-tag-learnit" href="https://my.education.gov.il" target="_blank">🏛️ פורטל משרד החינוך</a>
        </div>
    """, unsafe_allow_html=True)
    c_text = st.text_area("הדבק הודעת מטלה מהמורה:", height=100)
    if st.button("פרק מטלה למשימות וזמנים 📋", use_container_width=True):
        if c_text:
            with st.spinner("מנתח מטלה..."):
                try:
                    res = generate_ai(f"פרק מטלה עבור {student_context}:\n{c_text}\nמה נדרש, דד-ליין, ושלבי ביצוע מהירים. {anti_yap_rule}")
                    st.markdown(res.text)
                except Exception:
                    st.error("שגיאה בניתוח המטלה.")

# ----------------- חדר: מתכנן לו״ז -----------------
elif st.session_state.current_room == "לוז":
    st.title("📅 מתכנן לוח זמנים למבחן")
    l_top = st.text_area("החומר שצריך להספיק:")
    l_days = st.number_input("כמה ימים נשארו?", 1, 30, 3)
    if st.button("בנה לו״ז לימודים 🗓️", use_container_width=True):
        if l_top:
            with st.spinner("בונה לו״ז..."):
                try:
                    res = generate_ai(f"בנה לוח זמנים פרקטי ללימוד למבחן עבור {student_context}.\nימים: {l_days}, חומר: {l_top}. חלק בצורה מאוזנת לפי ימים עם זמני מנוחה.")
                    st.markdown(res.text)
                except Exception:
                    st.error("שגיאה בבניית לוח הזמנים.")
