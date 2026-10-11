import streamlit as st
from google import genai
from PIL import Image
import requests
from io import BytesIO
import json
import re
import time
import urllib.parse
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# קוד גישה סודי לחדר מורים והנהלה
TEACHER_ACCESS_CODE = "DAN100"

st.set_page_config(
    page_title="The Dan Method | לומדים. מתקדמים.",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# שפת עיצוב LearnIt וטיפוגרפיה
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700;800;900&display=swap');

    * {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

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
        background-color: #fbfcfd;
        color: #1e293b;
    }

    .main .block-container {
        padding-top: 1.2rem !important;
        max-width: 1180px;
        margin: 0 auto;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-left: 1px solid #f1f5f9;
        min-width: 290px !important;
        max-width: 330px !important;
        white-space: normal !important;
    }

    [data-testid="stSidebar"] * {
        word-break: normal !important;
        white-space: normal !important;
    }

    div[data-testid="stSlider"] > div {
        direction: ltr !important;
    }
    div[data-testid="stSlider"] label {
        direction: rtl !important;
        text-align: right !important;
    }

    .learnit-navbar {
        background-color: #ffffff;
        border: 1px solid #eef2f6;
        border-radius: 18px;
        padding: 12px 24px;
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
    }
    .brand-logo-container {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        direction: ltr;
    }
    .brand-main-name {
        font-size: 1.35rem;
        font-weight: 900;
        letter-spacing: -0.3px;
        color: #0f2b5c;
    }
    .brand-sub-badge {
        font-size: 0.65rem;
        font-weight: 800;
        color: #2563eb;
        letter-spacing: 1.2px;
    }

    .hero-banner {
        background: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.92)), 
                    url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80') center/cover no-repeat;
        border: 1px solid #e2e8f0;
        border-radius: 28px;
        padding: 44px 30px 30px 30px;
        box-shadow: 0 6px 24px rgba(15, 23, 42, 0.03);
        margin-bottom: 22px;
        text-align: center;
    }
    .hero-main-title {
        font-size: 2.9rem;
        font-weight: 900;
        color: #0f2b5c;
        line-height: 1.25;
        margin-bottom: 10px;
    }
    .hero-desc {
        font-size: 1.15rem;
        color: #64748b;
        margin-bottom: 16px;
        font-weight: 500;
    }

    .features-ribbon {
        display: flex;
        justify-content: space-around;
        background: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 20px;
        padding: 16px 20px;
        margin-bottom: 24px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.02);
    }
    .ribbon-item {
        display: flex;
        align-items: center;
        gap: 12px;
        text-align: right;
    }
    .ribbon-icon-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }

    .method-card-learnit {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-right: 5px solid #2563eb;
        border-radius: 22px;
        padding: 26px 30px;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.03);
    }
    .method-title-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #eff6ff;
        color: #1d4ed8;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.95rem;
        margin-bottom: 12px;
    }

    .compare-card-learnit {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 22px;
        padding: 26px 30px;
        margin-bottom: 28px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.03);
    }
    .compare-table-learnit {
        width: 100%;
        border-collapse: collapse;
        margin-top: 14px;
        text-align: right;
    }
    .compare-table-learnit th {
        padding: 14px;
        border-bottom: 2px solid #f1f5f9;
        font-weight: 800;
        font-size: 0.95rem;
        color: #475569;
    }
    .compare-table-learnit td {
        padding: 16px 14px;
        border-bottom: 1px solid #f8fafc;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .cat-grid-title {
        font-size: 1.55rem;
        font-weight: 800;
        color: #0f2b5c;
        margin-bottom: 4px;
    }
    .cat-grid-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 18px;
    }

    .pastel-tile {
        border-radius: 18px;
        padding: 24px 16px;
        text-align: center;
        margin-bottom: 14px;
        border: 1px solid transparent;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .pastel-tile:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    }
    .pastel-tile-icon {
        font-size: 32px;
        margin-bottom: 8px;
    }
    .pastel-tile-title {
        font-size: 1.1rem;
        font-weight: 800;
        margin-bottom: 3px;
    }
    .pastel-tile-count {
        font-size: 0.82rem;
        font-weight: 600;
        opacity: 0.8;
    }

    .tile-purple { background-color: #f3e8ff; border-color: #e9d5ff; color: #6b21a8; }
    .tile-blue   { background-color: #e0f2fe; border-color: #bae6fd; color: #0369a1; }
    .tile-mint   { background-color: #dcfce7; border-color: #bbf7d0; color: #15803d; }
    .tile-peach  { background-color: #ffedd5; border-color: #fed7aa; color: #c2410c; }
    .tile-yellow { background-color: #fef9c3; border-color: #fef08a; color: #a16207; }
    .tile-slate  { background-color: #f1f5f9; border-color: #e2e8f0; color: #334155; }
    .tile-pink   { background-color: #fce7f3; border-color: #fbcfe8; color: #be185d; }
    .tile-indigo { background-color: #e0e7ff; border-color: #c7d2fe; color: #4338ca; }

    .room-content-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 3px 14px rgba(15, 23, 42, 0.03);
        margin-bottom: 20px;
        line-height: 1.7;
    }
    .room-badge-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .slide-card-learnit {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-right: 4px solid #2563eb;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.02);
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

    /* חלון שיחת זום אינטראקטיבי */
    .zoom-video-container {
        background: #0f172a;
        border-radius: 24px;
        overflow: hidden;
        border: 3px solid #1e3a8a;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.2);
        position: relative;
        height: 310px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .zoom-video-container video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .zoom-live-pill {
        position: absolute;
        top: 14px;
        right: 14px;
        background: rgba(15, 23, 42, 0.85);
        color: #22c55e;
        border: 1px solid #22c55e;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 800;
        backdrop-filter: blur(6px);
        z-index: 10;
    }
    .zoom-teacher-tag {
        position: absolute;
        bottom: 14px;
        right: 14px;
        background: rgba(15, 23, 42, 0.85);
        color: #ffffff;
        padding: 6px 16px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.9rem;
        backdrop-filter: blur(6px);
        z-index: 10;
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

    div.stButton > button {
        background-color: #0f2b5c !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 8px 18px !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button:hover {
        background-color: #1e3a8a !important;
        box-shadow: 0 4px 12px rgba(15, 43, 92, 0.2) !important;
    }

    @media (max-width: 768px) {
        .hero-main-title { font-size: 2.1rem; }
        .features-ribbon { flex-direction: column; gap: 12px; }
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
if "zoom_homework" not in st.session_state:
    st.session_state.zoom_homework = None
if "mock_exam_data" not in st.session_state:
    st.session_state.mock_exam_data = None
if "ai_cache" not in st.session_state:
    st.session_state.ai_cache = {}
if "slides_data" not in st.session_state:
    st.session_state.slides_data = None
if "pptx_bytes" not in st.session_state:
    st.session_state.pptx_bytes = None
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

# שימוש במודלים זמינים תמיד ב-v1beta ללא שגיאת 404
AVAILABLE_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]

def generate_ai(contents, use_cache=False):
    if use_cache and isinstance(contents, str) and contents in st.session_state.ai_cache:
        return st.session_state.ai_cache[contents]

    last_err = None
    for m in AVAILABLE_MODELS:
        try:
            res = client.models.generate_content(model=m, contents=contents)
            if use_cache and isinstance(contents, str):
                st.session_state.ai_cache[contents] = res
            return res
        except Exception as e:
            last_err = e
            time.sleep(0.5)
            continue
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

# דיבור חי בדפדפן בחינם דרך Web Speech API
def speak_in_browser(text):
    clean = re.sub(r"[*#_`>\[\]\(\)\n]", " ", text)
    clean = clean.replace('"', '\\"').strip()
    js_code = f"""
    <script>
        (function() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{clean}");
                msg.lang = 'he-IL';
                msg.rate = 1.0;
                window.speechSynthesis.speak(msg);
            }}
        }})();
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

def get_whatsapp_share_link(text):
    encoded = urllib.parse.quote(f"היי, מצאתי את זה ב-The Dan Method:\n\n{text[:450]}")
    return f"https://api.whatsapp.com/send?text={encoded}"

def create_pptx_file(slides_info, topic_name):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    for s in slides_info:
        slide = prs.slides.add_slide(blank_layout)
        
        title_box = slide.shapes.add_textbox(Inches(1), Inches(0.8), Inches(11.333), Inches(1.2))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = s.get("title", f"שקופית {s.get('slide_num', 1)}")
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = RGBColor(15, 43, 92)

        body_box = slide.shapes.add_textbox(Inches(1), Inches(2.2), Inches(11.333), Inches(4.5))
        btf = body_box.text_frame
        btf.word_wrap = True
        for bullet in s.get("bullets", []):
            bp = btf.add_paragraph()
            bp.text = f"• {bullet}"
            bp.font.size = Pt(22)
            bp.font.color.rgb = RGBColor(30, 41, 59)
            bp.space_after = Pt(14)
            
        if "speaker_notes" in s and s["speaker_notes"]:
            notes_slide = slide.notes_slide
            text_frame = notes_slide.notes_text_frame
            text_frame.text = s["speaker_notes"]

    bio = BytesIO()
    prs.save(bio)
    bio.seek(0)
    return bio

# --- סרגל צד עם רשימת המגמות המלאה ---
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
        math_units = st.selectbox("מתמטיקה:", [
            "הקבצה א' / מופת ומצוינות", 
            "הקבצה א' רגילה", 
            "הקבצה ב'", 
            "רמה רגילה / תמיכה לימודית"
        ])
        eng_units = st.selectbox("אנגלית:", [
            "דוברי אנגלית (Native Speakers)", 
            "הקבצה א' / מואצת", 
            "הקבצה ב'", 
            "רמה רגילה"
        ])
        chosen_major = st.selectbox("מסלול / עתודה בחטיבה:", [
            "ללא מסלול (מקצועות ליבה בלבד)",
            "עתודה מדעית טכנולוגית (עמ\"ט)",
            "מדעי המחשב / סייבר ורובוטיקה",
            "מדעים, רפואה וביולוגיה",
            "תקשורת, עיתונות ורדיו",
            "אמנות חזותית ועיצוב גרפי",
            "קולנוע ומולטימדיה",
            "מוזיקה וסאונד",
            "תיאטרון ומשחק",
            "מנהיגות, יזמות ומשפטים"
        ])
    else:
        math_units = st.selectbox("מתמטיקה לבגרות:", [
            "5 יחידות לימוד (רמת מדעים והנדסה)", 
            "4 יחידות לימוד", 
            "3 יחידות לימוד"
        ])
        eng_units = st.selectbox("אנגלית לבגרות:", [
            "5 יחידות לימוד / דוברי אנגלית", 
            "4 יחידות לימוד (Modules C, D, E)", 
            "3 יחידות לימוד (Modules A, B, C)"
        ])
        chosen_major = st.selectbox("מגמה בתיכון (מקצוע בחירה מוגבר):", [
            "ללא מגמה (מקצועות ליבה בלבד)",
            "מדעי המחשב / הנדסת תוכנה (10 יח')",
            "סייבר והגנת מרחב הסייבר",
            "פיזיקה (5 יח')",
            "ביולוגיה / ביוטכנולוגיה",
            "כימיה (5 יח')",
            "מערכות רפואיות / מדעי הבריאות",
            "ניהול עסקי / יזמות וכלכלה",
            "מדעי החברה: פסיכולוגיה וסוציולוגיה",
            "משפטים ומדע המדינה",
            "קולנוע, טלוויזיה והפקה",
            "תקשורת ומדיה דיגיטלית",
            "אמנות פלסטית ועיצוב",
            "ערבית ואסלאם מוגבר",
            "גיאוגרפיה ופיתוח סביבתי",
            "היסטוריה מוגברת (5 יח')",
            "ספרות מוגברת (5 יח')",
            "תנ\"ך מוגבר (5 יח')"
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
student_context = f"שכבת לימוד: {chosen_grade}, מתמטיקה: {math_units}, אנגלית: {eng_units}, מגמה/מסלול: {chosen_major}."

# --- סרגל ניווט עליון בסגנון LearnIt ---
col_nav_logo, col_nav_mode, col_nav_btn = st.columns([2.5, 1.5, 1])
with col_nav_logo:
    st.markdown("""
        <div class="learnit-navbar">
            <div class="brand-logo-container">
                <div style="width: 38px; height: 38px; border-radius: 12px; background: linear-gradient(135deg, #0f2b5c, #2563eb); display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 20px;">🎓</span>
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
    if st.button("🏠 דף הבית", key="nav_home_main", use_container_width=True):
        st.session_state.current_room = "דף הבית"
        st.rerun()

# --- בדיקת אבטחה למצב מורה ---
if st.session_state.app_mode == "מורה" and not st.session_state.teacher_authenticated:
    st.markdown("""
        <div class="room-content-card" style="text-align: center; max-width: 520px; margin: 40px auto; border-top: 5px solid #0f2b5c;">
            <div style="font-size: 44px; margin-bottom: 8px;">🔒</div>
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
        if st.button("🔓 כניסה למרחב ההוראה", use_container_width=True):
            if code_input.strip() == TEACHER_ACCESS_CODE:
                st.session_state.teacher_authenticated = True
                st.success("קוד גישה אומת בהצלחה!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("קוד הגישה אינו תקין. הגישה מותרת לצוות מורשה בלבד.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅️ חזרה למצב תלמיד", use_container_width=True):
            st.session_state.app_mode = "תלמיד"
            st.rerun()
    st.stop()

# ----------------- דף הבית -----------------
if st.session_state.current_room == "דף הבית":
    mode_title = "הדרך שלך להצלחה מתחילה כאן." if st.session_state.app_mode == "תלמיד" else "מרחב הפדגוגיה וההוראה החכמה."
    mode_sub = "לימודים קלים יותר, בכל מקום ובכל זמן. כל מה שצריך כדי להצליח – במקום אחד." if st.session_state.app_mode == "תלמיד" else "הכנת מערכי שיעור, בחני פתע ומחוונים רשמיים בתוך שניות."
    
    st.markdown(f"""
        <div class="hero-banner">
            <h1 class="hero-main-title">{mode_title}</h1>
            <p class="hero-desc">{mode_sub}</p>
        </div>
    """, unsafe_allow_html=True)

    query_search = st.text_input("🔍 מה תרצה ללמוד היום?", placeholder="מה תרצה ללמוד היום? (למשל: 'איך גוזרים פונקציה?', 'מצגת', 'שליף חירום'...)")

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
            with st.spinner("מעבד תשובה ממוקדת..."):
                try:
                    res_bot = generate_ai(f"אתה עוזר לימודי אישי חכם ({'לתלמיד' if st.session_state.app_mode == 'תלמיד' else 'למורה'}). בהקשר: {student_context}. ענה על השאלה ישירות, ברור וקצר לתכל'ס בלי חפירות: {query_search}. {anti_yap_rule}", use_cache=True)
                    st.markdown(f"""
                        <div class="room-content-card" style="border-right: 4px solid #2563eb;">
                            <span class="room-badge-pill" style="background:#e0f2fe; color:#0369a1;">💡 מענה מהיר של דן AI</span>
                            <div style="font-size:1.05rem; line-height:1.7;">{res_bot.text}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_bot.text)}" target="_blank">📲 שתף מענה בוואטסאפ</a>', unsafe_allow_html=True)
                except Exception as err:
                    st.error(f"שגיאה בעיבוד השאלה: {err}")

    st.markdown("""
        <div class="features-ribbon">
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #f3e8ff; color: #7e22ce;">📖</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">תוכן איכותי ומדויק</div>
                    <div style="color:#64748b; font-size:0.8rem;">הסברים בהירים וממוקדים</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #e0f2fe; color: #0284c7;">⏱️</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">לומדים בקצב שלך</div>
                    <div style="color:#64748b; font-size:0.8rem;">גישה חופשית 24/7</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #dcfce7; color: #15803d;">👥</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">מותאם לצוות ולתלמידים</div>
                    <div style="color:#64748b; font-size:0.8rem;">התאמה מלאה לרמות ולמגמות</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #fef9c3; color: #a16207;">⭐</div>
                <div>
                    <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">מתאים לכל תלמיד</div>
                    <div style="color:#64748b; font-size:0.8rem;">מהיסודי ועד הבגרות</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="method-card-learnit">
            <div class="method-title-badge">⚡ על השיטה של The Dan Method</div>
            <p style="font-size: 1.05rem; color: #334155; line-height: 1.75; margin: 0;">
                נמאס לשבת שעות מול סיכומים ארוכים, מורים שמדברים מסביב ואתרי לימוד שנראים כמו שנת 2005.<br>
                <b>The Dan Method</b> נבנה במטרה אחת ברורה: לתת לתלמידי ומורי ישראל את הדרך הקצרה, המדויקת והחדה ביותר להצלחה במבחנים ובבגרויות.<br>
                במקום ללמוד 4 שעות ולזכור חצי – אנחנו מפרקים כל נושא לשלבי ברזל, מסננים חפירות מיותרות (מצב תכל'ס), ומלמדים אותך בדיוק לפי מה שהבוחן מחפש בעין בטופס הבדיקה.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="compare-card-learnit">
            <h3 style="margin-top: 0; color: #0f2b5c; font-size: 1.35rem; font-weight: 800;">למה The Dan Method ולא סתם בינה מלאכותית רגילה?</h3>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 12px;">ChatGPT ודגמי AI רגילים לא מכירים את בתי הספר בישראל ומבזבזים לך זמן. הנה ההבדל:</p>
            <table class="compare-table-learnit">
                <thead>
                    <tr>
                        <th style="width: 28%;">תכונה</th>
                        <th style="width: 36%; color: #2563eb;">🎓 The Dan Method</th>
                        <th style="width: 36%; color: #64748b;">🤖 ChatGPT / מודל רגיל</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="font-weight: 700; color: #0f172a;">התאמה למערכת החינוך</td>
                        <td style="color: #16a34a; font-weight: 700;">✔️ מכויל בול לפי מחווני בגרות, הקבצות וכיתות ז'-י"ב בישראל</td>
                        <td style="color: #64748b;">❌ תשובות גנריות באנגלית שתורגמו, לא מכיר מחווני בדיקה</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 700; color: #0f172a;">אורך המענה והיעילות</td>
                        <td style="color: #16a34a; font-weight: 700;">✔️ מצב תכל'ס (No Yap) – פירוק ממוקד ב-3 שורות בדיוק למה שצריך</td>
                        <td style="color: #64748b;">❌ פסקאות פתיחה וסיום ארוכות, חפירות ומריחת זמן מיותרת</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 700; color: #0f172a;">בדיקת מבחנים וציונים</td>
                        <td style="color: #16a34a; font-weight: 700;">✔️ חישוב ציון אמיתי מתוך 100 עם הורדת נקודות לפי נימוקים חסרים</td>
                        <td style="color: #64748b;">❌ סתם מחמיא לתשובה ולא יודע לתת ציון בגרות אמיתי ומדויק</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 700; color: #0f172a;">חילוץ רגע לפני מבחן</td>
                        <td style="color: #16a34a; font-weight: 700;">✔️ שליף 60 שניות, מצב חילוץ בלילה ורנטגן שגיאות בוחנים</td>
                        <td style="color: #64748b;">❌ מייצר טקסטים ענקיים שבלתי אפשרי לקרוא תחת לחץ זמן</td>
                    </tr>
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="margin-top: 10px; margin-bottom: 12px;">
            <div class="cat-grid-title">קטגוריות לימוד וכלים</div>
            <div class="cat-grid-subtitle">בחר את התחום שמעניין אותך והתחל ללמוד</div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.app_mode == "תלמיד":
        col_c1, col_c2, col_c3, col_c4, col_c5, col_c6 = st.columns(6)
        with col_c1:
            st.markdown('<div class="pastel-tile tile-purple"><div class="pastel-tile-icon">🧮</div><div class="pastel-tile-title">מתמטיקה</div><div class="pastel-tile-count">פירוק שלב-אחר-שלב</div></div>', unsafe_allow_html=True)
            if st.button("מעבדה", key="p_math", use_container_width=True):
                st.session_state.current_room = "מעבדת מתמטיקה"
                st.rerun()

        with col_c2:
            st.markdown('<div class="pastel-tile tile-blue"><div class="pastel-tile-icon">📊</div><div class="pastel-tile-title">מצגות</div><div class="pastel-tile-count">בנייה והורדת PPTX</div></div>', unsafe_allow_html=True)
            if st.button("מחולל", key="p_slides", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()

        with col_c3:
            st.markdown('<div class="pastel-tile tile-mint"><div class="pastel-tile-icon">📹</div><div class="pastel-tile-title">חדר זום</div><div class="pastel-tile-count">וידאו, קול ותרגול</div></div>', unsafe_allow_html=True)
            if st.button("זום חי", key="p_zoom", use_container_width=True):
                st.session_state.current_room = "חדר זום"
                st.rerun()

        with col_c4:
            st.markdown('<div class="pastel-tile tile-peach"><div class="pastel-tile-icon">📸</div><div class="pastel-tile-title">סורק תמונות</div><div class="pastel-tile-count">פיענוח מדף/תרגיל</div></div>', unsafe_allow_html=True)
            if st.button("סורק", key="p_scan", use_container_width=True):
                st.session_state.current_room = "סורק תמונות"
                st.rerun()

        with col_c5:
            st.markdown('<div class="pastel-tile tile-yellow"><div class="pastel-tile-icon">🚨</div><div class="pastel-tile-title">שליף חירום</div><div class="pastel-tile-count">60 שניות לפני מבחן</div></div>', unsafe_allow_html=True)
            if st.button("שליף", key="p_cheat", use_container_width=True):
                st.session_state.current_room = "שליף חירום"
                st.rerun()

        with col_c6:
            st.markdown('<div class="pastel-tile tile-pink"><div class="pastel-tile-icon">🆘</div><div class="pastel-tile-title">חילוץ לילה</div><div class="pastel-tile-count">תוכנית 3 בלילה</div></div>', unsafe_allow_html=True)
            if st.button("חילוץ", key="p_panic", use_container_width=True):
                st.session_state.current_room = "חילוץ לילה"
                st.rerun()

        col_c7, col_c8, col_c9, col_c10, col_c11, col_c12 = st.columns(6)
        with col_c7:
            st.markdown('<div class="pastel-tile tile-slate"><div class="pastel-tile-icon">📝</div><div class="pastel-tile-title">מבחני דמה</div><div class="pastel-tile-count">סימולציה עם מחוון</div></div>', unsafe_allow_html=True)
            if st.button("מבחן", key="p_exam", use_container_width=True):
                st.session_state.current_room = "מבחני דמה"
                st.rerun()

        with col_c8:
            st.markdown('<div class="pastel-tile tile-indigo"><div class="pastel-tile-icon">🩻</div><div class="pastel-tile-title">רנטגן שגיאות</div><div class="pastel-tile-count">מלכודות בוחנים</div></div>', unsafe_allow_html=True)
            if st.button("רנטגן", key="p_xray", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()

        with col_c9:
            st.markdown('<div class="pastel-tile tile-blue"><div class="pastel-tile-icon">⚖️</div><div class="pastel-tile-title">מכתב ערעור</div><div class="pastel-tile-count">החזרת נקודות</div></div>', unsafe_allow_html=True)
            if st.button("ערעור", key="p_appeal", use_container_width=True):
                st.session_state.current_room = "ערעור"
                st.rerun()

        with col_c10:
            st.markdown('<div class="pastel-tile tile-mint"><div class="pastel-tile-icon">🎴</div><div class="pastel-tile-title">כרטיסיות</div><div class="pastel-tile-count">שינון מהיר</div></div>', unsafe_allow_html=True)
            if st.button("כרטיסיות", key="p_flash", use_container_width=True):
                st.session_state.current_room = "כרטיסיות"
                st.rerun()

        with col_c11:
            st.markdown('<div class="pastel-tile tile-peach"><div class="pastel-tile-icon">🧘</div><div class="pastel-tile-title">מרחב רווחה</div><div class="pastel-tile-count">ויסות ופוקוס</div></div>', unsafe_allow_html=True)
            if st.button("רווחה", key="p_well", use_container_width=True):
                st.session_state.current_room = "רווחה"
                st.rerun()

        with col_c12:
            st.markdown('<div class="pastel-tile tile-yellow"><div class="pastel-tile-icon">🎯</div><div class="pastel-tile-title">מחשבון בגרות</div><div class="pastel-tile-count">חיזוי ציון סופי</div></div>', unsafe_allow_html=True)
            if st.button("מחשבון", key="p_calc", use_container_width=True):
                st.session_state.current_room = "מחשבון"
                st.rerun()

    else:
        col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
        with col_m1:
            st.markdown('<div class="pastel-tile tile-blue"><div class="pastel-tile-icon">📊</div><div class="pastel-tile-title">מצגת לשיעור</div><div class="pastel-tile-count">הורדת מצגת PPTX</div></div>', unsafe_allow_html=True)
            if st.button("מצגת מורה", key="pm_slides", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()

        with col_m2:
            st.markdown('<div class="pastel-tile tile-indigo"><div class="pastel-tile-icon">⏱️</div><div class="pastel-tile-title">מערך שיעור</div><div class="pastel-tile-count">45 דקות מדורגות</div></div>', unsafe_allow_html=True)
            if st.button("מערך", key="pm_lesson", use_container_width=True):
                st.session_state.current_room = "מערכי שיעור"
                st.rerun()

        with col_m3:
            st.markdown('<div class="pastel-tile tile-mint"><div class="pastel-tile-icon">📝</div><div class="pastel-tile-title">בוחן + מחוון</div><div class="pastel-tile-count">15 דק\' עם ניקוד</div></div>', unsafe_allow_html=True)
            if st.button("בוחן", key="pm_quiz", use_container_width=True):
                st.session_state.current_room = "בחנים ומחוונים"
                st.rerun()

        with col_m4:
            st.markdown('<div class="pastel-tile tile-slate"><div class="pastel-tile-icon">🏛️</div><div class="pastel-tile-title">מכתב להנהלה</div><div class="pastel-tile-count">פיילוט וייעוץ</div></div>', unsafe_allow_html=True)
            if st.button("מכתב", key="pm_lead", use_container_width=True):
                st.session_state.current_room = "הנהלה"
                st.rerun()

        with col_m5:
            st.markdown('<div class="pastel-tile tile-peach"><div class="pastel-tile-icon">🖨️</div><div class="pastel-tile-title">דפי הדפסה</div><div class="pastel-tile-count">תרגול לכיתה</div></div>', unsafe_allow_html=True)
            if st.button("דפי עבודה", key="pm_print", use_container_width=True):
                st.session_state.current_room = "דפי הדפסה"
                st.rerun()

        with col_m6:
            st.markdown('<div class="pastel-tile tile-purple"><div class="pastel-tile-icon">🩻</div><div class="pastel-tile-title">מוקשי למידה</div><div class="pastel-tile-count">טעויות נפוצות</div></div>', unsafe_allow_html=True)
            if st.button("מלכודות", key="pm_xray", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="margin-bottom: 12px;">
            <div class="cat-grid-title" style="font-size:1.35rem;">⭐ חוות דעת של תלמידים ומורים</div>
            <div class="cat-grid-subtitle">משובים אמיתיים מרחבי הארץ</div>
        </div>
    """, unsafe_allow_html=True)
    
    col_rev1, col_rev2 = st.columns([1.8, 1.2])
    with col_rev1:
        for r in st.session_state.reviews:
            stars = "⭐" * r["rating"]
            st.markdown(f"""
                <div class="room-content-card" style="padding: 16px 20px; margin-bottom: 12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b>{r['name']}</b> <span style="color:#64748b; font-size:0.9rem;">({r['grade']})</span>
                        <span style="font-size:0.9rem;">{stars}</span>
                    </div>
                    <p style="color: #475569; margin: 6px 0 0 0; font-size: 0.95rem;">{r['text']}</p>
                </div>
            """, unsafe_allow_html=True)
            
    with col_rev2:
        st.markdown('<div class="room-content-card"><h4 style="margin-top:0; color:#0f2b5c;">✍️ הוסף חוות דעת:</h4>', unsafe_allow_html=True)
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
    st.markdown('<span class="room-badge-pill" style="background:#e0f2fe; color:#0369a1;">📊 LearnIt Deck Builder & Exporter</span>', unsafe_allow_html=True)
    st.title("מחולל מצגות PowerPoint אמיתי")
    st.caption("ה-AI בונה עבורך שקופיות מעוצבות, ומייצר קובץ PowerPoint (.pptx) מוכן להורדה!")
    
    col_sl1, col_sl2 = st.columns(2)
    with col_sl1:
        slide_topic = st.text_input("נושא המצגת:", placeholder="למשל: תהליך הפוטוסינתזה, מלחמת העולם הראשונה, המהפכה המדעית...")
        slide_subject = st.selectbox("מקצוע:", ["היסטוריה", "ביולוגיה", "אזרחות", "ספרות", "אנגלית", "מדעים", "גיאוגרפיה", chosen_major])
    with col_sl2:
        slide_count = st.slider("מספר שקופיות:", 3, 8, 5)
        slide_goal = st.selectbox("מטרת המצגת:", [
            "הצגה פרונטלית של תלמיד מול הכיתה (5 דקות)",
            "מצגת שיעור של מורה להקניה ותרגול",
            "סיכום פרויקט עבודת חקר / בגרות"
        ])

    if st.button("🔨 צור קובץ מצגת מושלם!", use_container_width=True):
        if not slide_topic.strip():
            st.warning("נא להזין נושא למצגת.")
        else:
            prompt_slides = (
                f"אתה מומחה להכנת מצגות לימודיות עבור מערכת החינוך בישראל ({student_context}).\n"
                f"נושא: {slide_topic}, מקצוע: {slide_subject}, שקופיות: {slide_count}, מטרה: {slide_goal}.\n\n"
                "החזר אך ורק מערך JSON תקין שבו כל איבר מייצג שקופית:\n"
                "[\n"
                "  {\n"
                '    "slide_num": 1,\n'
                '    "title": "כותרת קצרה לשקופית",\n'
                '    "bullets": ["נקודה 1", "נקודה 2", "נקודה 3"],\n'
                '    "visual_idea": "תיאור קצר לתמונה",\n'
                '    "speaker_notes": "הסבר בעל פה לדובר (עד 3 משפטים)"\n'
                "  }\n"
                "]"
            )
            with st.spinner("בונה שקופיות ומייצר קובץ מצגת להורדה..."):
                try:
                    res = generate_ai(prompt_slides)
                    st.session_state.slides_data = extract_json(res.text)
                    st.session_state.pptx_bytes = create_pptx_file(st.session_state.slides_data, slide_topic)
                    st.success("המצגת נוצרה בהצלחה! ניתן להוריד את הקובץ ישירות.")
                    st.rerun()
                except Exception as err:
                    st.error(f"שגיאה בבניית המצגת: {err}")

    if st.session_state.slides_data:
        st.markdown("---")
        if st.session_state.pptx_bytes:
            st.download_button(
                label="📥 הורד קובץ מצגת PowerPoint מוכן (.pptx)",
                data=st.session_state.pptx_bytes,
                file_name=f"מצגת_{slide_topic.replace(' ', '_')}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        full_text_for_share = f"מצגת בנושא: {slide_topic}\n\n"
        for s in st.session_state.slides_data:
            bullets_formatted = "\n".join([f"• {b}" for b in s.get("bullets", [])])
            st.markdown(f"""
                <div class="slide-card-learnit">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#0f2b5c;">שקופית {s['slide_num']}: {s['title']}</h3>
                        <span style="background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:8px; font-weight:700; font-size:0.85rem;">🖼️ {s.get('visual_idea', '')}</span>
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

# ----------------- חדר: שיעור זום חי עם המורה מיה (חינם לגמרי עם Web Speech API) -----------------
elif st.session_state.current_room == "חדר זום":
    st.markdown('<span class="room-badge-pill" style="background:#dcfce7; color:#15803d;">📹 Live Interactive Zoom Class</span>', unsafe_allow_html=True)
    st.title("שיעור פרטי בזום עם המורה מיה")
    st.caption("שיחת וידאו חיה, מענה קולי אוטומטי בדפדפן ותרגול שיעורי בית מותאם אישית!")
    
    col_z1, col_z2 = st.columns([1.1, 1.9])
    with col_z1:
        # וידאו חי של מורה
        st.markdown("""
            <div class="zoom-video-container">
                <div class="zoom-live-pill">● שידור חי פועל</div>
                <video autoplay loop muted playsinline>
                    <source src="https://assets.mixkit.co/videos/preview/mixkit-young-woman-talking-on-video-call-40013-large.mp4" type="video/mp4">
                </video>
                <div class="zoom-teacher-tag">המורה מיה (מחוברת)</div>
            </div>
        """, unsafe_allow_html=True)
        
        # הפעלת קול הדפדפן (Web Speech API) ללא עלות
        if st.session_state.last_voice_reply:
            speak_in_browser(st.session_state.last_voice_reply)
            st.markdown("<div style='margin-top:10px; color:#16a34a; font-weight:700;'>🔊 המורה מיה מדברת אליך בקול...</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        z_subject = st.selectbox("מקצוע השיעור:", ["מתמטיקה", "אנגלית", "היסטוריה", "לשון והבעה", "ביולוגיה", "אזרחות"])
        
        if st.button("📚 תני לי משימת תרגול / שיעורי בית לשיעור", use_container_width=True):
            with st.spinner("המורה מיה מכינה תרגילי אתגר לשיעור..."):
                try:
                    hw_prompt = (
                        f"את המורה מיה. תני לתלמיד ב-{student_context} משימת תרגול קצרה ומאתגרת (שיעורי בית) ב{z_subject}.\n"
                        "המשימה צריכה לכלול:\n"
                        "1. תרגיל/שאלה 1 ברמה בסיסית.\n"
                        "2. תרגיל/שאלה 2 ברמת בגרות/מבחן כיתתי.\n"
                        "3. הנחיה מה לכתוב לך בחזרה בצ'אט כדי שתבדקי ותתני ציון."
                    )
                    res_hw = generate_ai(hw_prompt)
                    st.session_state.zoom_homework = res_hw.text
                    st.session_state.last_voice_reply = "הכנתי לך שתי שאלות תרגול מעולות. תפתור אותן ותכתוב לי כאן את התשובות ואבדוק לך מיד!"
                    st.rerun()
                except Exception as err:
                    st.error(f"שגיאה בהכנת המשימה: {err}")

        if st.button("🧹 איפוס שיחה", use_container_width=True):
            st.session_state.zoom_chat_history = []
            st.session_state.last_voice_reply = None
            st.session_state.zoom_homework = None
            st.rerun()

    with col_z2:
        if st.session_state.zoom_homework:
            st.markdown(f"""
                <div class="room-content-card" style="border-right: 4px solid #16a34a; background:#f0fdf4;">
                    <span class="room-badge-pill" style="background:#dcfce7; color:#15803d;">📝 משימת תרגול מותאמת מהמורה מיה</span>
                    <div style="font-size:1rem; line-height:1.7;">{st.session_state.zoom_homework}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<b>💬 שיחה חיה עם המורה מיה:</b>", unsafe_allow_html=True)
        chat_box = st.container(height=300)
        with chat_box:
            if not st.session_state.zoom_chat_history:
                st.info(f"👋 **המורה מיה:** היי! שמחה לפגוש אותך לשיעור ב{z_subject}. תגיד לי איזה נושא או תרגיל מציק לך, ונתחיל לפרק אותו ביחד!")
            else:
                for m in st.session_state.zoom_chat_history:
                    with st.chat_message(m["role"]):
                        st.write(m["content"])

        text_spoken = st.chat_input("הקלד תשובה או שאלה למורה מיה...")
        if text_spoken:
            st.session_state.zoom_chat_history.append({"role": "user", "content": text_spoken})
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.zoom_chat_history[-6:]])
            zoom_prompt = (
                f"את המורה מיה בשיעור פרטי אישי חי עם תלמיד ב-{student_context}.\n"
                f"מקצוע השיעור: {z_subject}.\n"
                "הנחיות קריטיות:\n"
                "1. דברי בלשון נקבה על עצמך ('אני כאן איתך', 'בדקתי את התשובה').\n"
                "2. עני בגובה העיניים, מעודד וממוקד מאוד (עד 3 משפטים).\n"
                "3. אם התלמיד פותר תרגיל או שיעורי בית – בדקי אותו, תני לו משוב וציון!\n"
                "4. בסוף התשובה שאלי שאלה קצרה כדי לוודא שהוא הבין.\n\n"
                f"היסטוריה:\n{history_text}\n\nהודעת התלמיד: {text_spoken}"
            )
            with st.spinner("המורה מיה מקשיבה ומכינה מענה..."):
                try:
                    res_zoom = generate_ai(zoom_prompt)
                    st.session_state.zoom_chat_history.append({"role": "assistant", "content": res_zoom.text})
                    st.session_state.last_voice_reply = res_zoom.text
                    st.rerun()
                except Exception as err:
                    st.error(f"שגיאה בתקשורת עם המורה: {err}")

# ----------------- שאר החדרים -----------------
elif st.session_state.current_room == "מערכי שיעור":
    st.markdown('<span class="room-badge-pill" style="background:#e0e7ff; color:#4338ca;">⏱️ 45 Min Lesson Plan</span>', unsafe_allow_html=True)
    st.title("מחולל מערך שיעור ממוקד")
    l_sub = st.text_input("מקצוע השיעור:")
    l_top = st.text_input("נושא השיעור:")
    if st.button("בנה מערך שיעור 📚", use_container_width=True):
        if l_sub and l_top:
            with st.spinner("בונה מערך שיעור..."):
                prompt_plan = f"בנה מערך שיעור של 45 דק' לכיתה {chosen_grade}. מקצוע: {l_sub}, נושא: {l_top}. חלק לזמנים מדויקים: פתיחה (7 דק'), גוף (23 דק'), תרגול מדורג (10 דק'), סיכום (5 דק')."
                res_plan = generate_ai(prompt_plan)
                st.markdown(f'<div class="room-content-card">{res_plan.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_plan.text)}" target="_blank">📲 שתף מערך שיעור בוואטסאפ</a>', unsafe_allow_html=True)

elif st.session_state.current_room == "בחנים ומחוונים":
    st.markdown('<span class="room-badge-pill" style="background:#dcfce7; color:#15803d;">📝 Assessment & Rubric</span>', unsafe_allow_html=True)
    st.title("מחולל בוחן כיתתי + מחוון משרד החינוך")
    q_sub = st.text_input("מקצוע הבוחן:")
    q_top = st.text_input("נושא הבוחן המדויק:")
    if st.button("ייצר בוחן ומחוון 📄", use_container_width=True):
        if q_sub and q_top:
            with st.spinner("מכין שאלות ומחוון..."):
                prompt_quiz = f"צור בוחן של 15 דקות ומחוון בדיקה לכיתה {chosen_grade}. מקצוע: {q_sub}, נושא: {q_top}. חלק 1: טופס כיתתי. חלק 2: מחוון מפורט למורה."
                res_quiz = generate_ai(prompt_quiz)
                st.markdown(f'<div class="room-content-card">{res_quiz.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_quiz.text)}" target="_blank">📲 שתף בוחן ומחוון בוואטסאפ</a>', unsafe_allow_html=True)

elif st.session_state.current_room == "הנהלה":
    st.markdown('<span class="room-badge-pill" style="background:#f1f5f9; color:#334155;">🏛️ Leadership Proposal</span>', unsafe_allow_html=True)
    st.title("מכתב רשמי להנהלת בית הספר ולצוות הייעוץ")
    st.markdown("""
        <div class="room-content-card">
            <h3 style="margin-top:0; color:#0f2b5c;">לכבוד: מנהלת בית הספר והיועצת החינוכית</h3>
            <b>הנדון: שילוב פלטפורמת 'The Dan Method' ככלי פדגוגי מסייע ללמידה עצמאית והפחתת חרדת בחינות</b>
            <p style="margin-top: 10px; line-height: 1.7; color: #334155;">
                מערכת <b>The Dan Method</b> פותחה מתוך הבנת האתגרים הייחודיים של תלמידי חטיבת הביניים והחטיבה העליונה בישראל, ומכוילת על פי תוכניות הלימודים ומחווני הבגרות של משרד החינוך.<br><br>
                המערכת מעודדת למידה עצמאית, סוגרת פערים לימודיים, מסייעת בהפחתת חרדת בחינות באמצעות מרחב רווחה ותרגול מודרך, וחוסכת שעות יקרות של הכנת חומרים לצוות ההוראה.
            </p>
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:16px; margin-top:14px;">
                <b>הצעה לפיילוט:</b> קיום התנסות מבוקרת בכיתה אחת לקראת מבחן קרוב למדידת שביעות הרצון וההישגים.
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link("מכתב רשמי על The Dan Method להנהלה ולייעוץ החינוכי.")}" target="_blank">📲 שתף מכתב להנהלה בוואטסאפ</a>', unsafe_allow_html=True)

elif st.session_state.current_room == "רווחה":
    st.markdown('<span class="room-badge-pill" style="background:#ffedd5; color:#c2410c;">🧘 Wellbeing & Calm</span>', unsafe_allow_html=True)
    st.title("מרחב רווחה, ויסות והפחתת לחץ")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("""
            <div class="room-content-card">
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
            <div class="room-content-card">
                <h4 style="margin-top:0; color:#0f2b5c;">טיימר פוקוס עמוק (Deep Focus)</h4>
                <p style="color:#64748b;">למידה ממוקדת של 25 דקות ללא הסחות דעת:</p>
                <div style="font-size:2.8rem; font-weight:900; color:#0f2b5c; text-align:center;">25:00</div>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_room == "חילוץ לילה":
    st.markdown('<span class="room-badge-pill" style="background:#fce7f3; color:#be185d;">🆘 Night Shift Rescue</span>', unsafe_allow_html=True)
    st.title("מצב חילוץ ב-3 בלילה")
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
                st.markdown(f'<div class="room-content-card" style="border-right: 4px solid #be185d;">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף תוכנית הצלה בוואטסאפ</a>', unsafe_allow_html=True)

elif st.session_state.current_room == "רנטגן":
    st.markdown('<span class="room-badge-pill" style="background:#e0e7ff; color:#4338ca;">🩻 Mistake X-Ray</span>', unsafe_allow_html=True)
    st.title("רנטגן שגיאות ומלכודות בוחנים")
    xray_topic = st.text_input("איזה נושא או תרגיל לבדוק?")
    if st.button("חשוף מלכודות ⚡", use_container_width=True):
        if xray_topic:
            with st.spinner("מבצע צילום רנטגן..."):
                prompt = f"חשוף מלכודות בוחנים בנושא: {xray_topic} עבור {student_context}."
                res = generate_ai(prompt)
                st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף מוקשים בוואטסאפ</a>', unsafe_allow_html=True)

elif st.session_state.current_room == "ערעור":
    st.markdown('<span class="room-badge-pill" style="background:#e0f2fe; color:#0369a1;">⚖️ Appeal Generator</span>', unsafe_allow_html=True)
    st.title("מחולל מכתב ערעור על ציון")
    c_sub = st.text_input("מקצוע המבחן:")
    c_q = st.text_area("השאלה:")
    c_ans = st.text_area("תשובתך:")
    c_lost = st.text_input("הערת המורה ונקודות שירדו:")
    if st.button("נסח מכתב ערעור 🚀", use_container_width=True):
        if c_sub and c_ans:
            with st.spinner("מנסח מכתב ערעור..."):
                prompt = f"נסח ערעור רשמי ומנומק למורה עבור {student_context}. מקצוע: {c_sub}, שאלה: {c_q}, תשובה: {c_ans}, הערה: {c_lost}."
                res = generate_ai(prompt)
                st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף נוסח ערעור בוואטסאפ</a>', unsafe_allow_html=True)

elif st.session_state.current_room == "כרטיסיות":
    st.markdown('<span class="room-badge-pill" style="background:#dcfce7; color:#15803d;">🎴 Flashcards</span>', unsafe_allow_html=True)
    st.title("כרטיסיות חזרה מהירות")
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
                st.markdown(f'<div style="background:#f8fafc; padding:14px; border-radius:10px;">{card.get("back", "")}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "מחשבון":
    st.markdown('<span class="room-badge-pill" style="background:#fef9c3; color:#a16207;">🎯 Target Calculator</span>', unsafe_allow_html=True)
    st.title("מחשבון ציון יעד לבגרות ומגן")
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
            <div class="room-content-card">
                <h3 style="color:#0f2b5c; margin:0;">🎯 עליך להוציא לפחות {round(needed_bagrut)} בבחינת הבגרות</h3>
                <p style="color:#64748b; margin:6px 0 0 0;">לפי משקל מגן של {magen_weight}% ומשקל בגרות של {bagrut_weight}%.</p>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_room == "סורק תמונות":
    st.markdown('<span class="room-badge-pill" style="background:#ffedd5; color:#c2410c;">📸 Homework Scanner</span>', unsafe_allow_html=True)
    st.title("סורק תמונות ושיעורי בית")
    photo_topic = st.text_input("מה החומר או המקצוע?")
    file = st.file_uploader("בחר קובץ תמונה:", type=["png", "jpg", "jpeg"])
    if st.button("פענח ופתור ⚡", use_container_width=True):
        if file and photo_topic:
            img = Image.open(file)
            with st.spinner("מפענח..."):
                res = generate_ai([f"פתור והסבר שלב אחרי שלב עבור {student_context}. נושא: {photo_topic}", img])
                st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף פתרון בוואטסאפ</a>', unsafe_allow_html=True)

elif st.session_state.current_room == "מבחני דמה":
    st.markdown('<span class="room-badge-pill" style="background:#f1f5f9; color:#334155;">📝 Mock Exam Builder</span>', unsafe_allow_html=True)
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
        st.markdown(f'<div class="room-content-card">{json.dumps(st.session_state.mock_exam_data, ensure_ascii=False, indent=2)}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "מעבדת מתמטיקה":
    st.markdown('<span class="room-badge-pill" style="background:#f3e8ff; color:#6b21a8;">🧮 Step-by-Step Lab</span>', unsafe_allow_html=True)
    st.title("מעבדת פירוק מתמטיקה ומדעים")
    m_topic = st.text_input("נושא:")
    m_input = st.text_area("תרגיל:")
    if st.button("פרק תרגיל שלב-אחר-שלב 🧠", use_container_width=True):
        if m_topic and m_input:
            with st.spinner("פותר..."):
                res = generate_ai(f"פתור שלב אחרי שלב עבור {student_context}. נושא: {m_topic}, תרגיל: {m_input}")
                st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף פתרון בוואטסאפ</a>', unsafe_allow_html=True)

elif st.session_state.current_room == "שליף חירום":
    st.markdown('<span class="room-badge-pill" style="background:#fef9c3; color:#a16207;">🚨 60 Sec Cheat Sheet</span>', unsafe_allow_html=True)
    st.title("שליף חירום: 60 שניות לפני מבחן")
    p_topic = st.text_input("נושא המבחן:")
    if st.button("הצל אותי עכשיו ⚡", use_container_width=True):
        if p_topic:
            with st.spinner("מחלץ שליף..."):
                res = generate_ai(f"שליף קצר של 60 שניות לפני מבחן על {p_topic} עבור {student_context}.")
                st.markdown(f'<div class="room-content-card" style="border-right: 4px solid #f59e0b; background:#fffdfa;">{res.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res.text)}" target="_blank">📲 שתף שליף בוואטסאפ</a>', unsafe_allow_html=True)

elif st.session_state.current_room == "דפי הדפסה":
    st.markdown('<span class="room-badge-pill" style="background:#ffedd5; color:#c2410c;">🖨️ Printable Worksheets</span>', unsafe_allow_html=True)
    st.title("מחולל דפי תרגול להדפסה")
    pr_top = st.text_input("נושא הדף:")
    if st.button("ייצר דף עבודה 📄", use_container_width=True):
        if pr_top:
            with st.spinner("מייצר דף..."):
                res = generate_ai(f"צור דף תרגול ומבחן מעוצב בעברית בנושא {pr_top} עבור {student_context}.")
                st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)
                st.markdown("""<button onclick="window.print()" style="padding: 10px 20px; background: #0f2b5c; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🖨️ הדפס דף זה</button>""", unsafe_allow_html=True)
