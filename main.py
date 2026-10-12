import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import requests
from io import BytesIO
import json
import re
import time
import urllib.parse
import hashlib
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from gtts import gTTS

DEFAULT_TEACHER_CODE = "DAN100"

ALLOWED_SCHOOL_DOMAINS = [
    "tichonoz.org.il",
    "school.org.il",
    "msh.org.il",
    "k12.gov.il"
]

st.set_page_config(
    page_title="The Dan Method | לומדים. מתקדמים.",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700;800;900&display=swap');

    * {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        box-sizing: border-box;
    }

    #MainMenu, footer, div[data-testid="stDecoration"] {
        display: none !important;
    }

    .stApp {
        direction: rtl;
        text-align: right;
        background-color: #fbfcfd;
        color: #1e293b;
    }

    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1180px;
        margin: 0 auto;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-left: 1px solid #f1f5f9;
        min-width: 280px !important;
        max-width: 320px !important;
    }

    .learnit-navbar {
        background-color: #ffffff;
        border: 1px solid #eef2f6;
        border-radius: 18px;
        padding: 12px 20px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
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
        background: linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.94)), 
                    url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80') center/cover no-repeat;
        border: 1px solid #e2e8f0;
        border-radius: 24px;
        padding: 36px 20px 24px 20px;
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.03);
        margin-bottom: 22px;
        text-align: center;
    }
    .hero-main-title {
        font-size: 2.6rem;
        font-weight: 900;
        color: #0f2b5c;
        line-height: 1.25;
        margin-bottom: 10px;
    }
    .hero-desc {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 16px;
        font-weight: 500;
    }

    .features-ribbon {
        display: flex;
        justify-content: space-around;
        background: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 18px;
        padding: 14px 18px;
        margin-bottom: 22px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.02);
    }
    .ribbon-item {
        display: flex;
        align-items: center;
        gap: 10px;
        text-align: right;
    }
    .ribbon-icon-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }

    .compare-card-learnit {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 24px 26px;
        margin-bottom: 22px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03);
        overflow-x: auto;
    }
    .compare-table-learnit {
        width: 100%;
        border-collapse: collapse;
        margin-top: 12px;
        text-align: right;
        min-width: 500px;
    }
    .compare-table-learnit th {
        padding: 12px;
        border-bottom: 2px solid #f1f5f9;
        font-weight: 800;
        font-size: 0.95rem;
        color: #475569;
    }
    .compare-table-learnit td {
        padding: 14px 12px;
        border-bottom: 1px solid #f8fafc;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .method-card-learnit {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-right: 5px solid #2563eb;
        border-radius: 20px;
        padding: 24px 26px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03);
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

    .cat-grid-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f2b5c;
        margin-bottom: 4px;
    }
    .cat-grid-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 16px;
    }

    .pastel-tile {
        border-radius: 16px;
        padding: 18px 10px;
        text-align: center;
        margin-bottom: 12px;
        border: 1px solid transparent;
        transition: transform 0.15s ease;
    }
    .pastel-tile-icon { font-size: 28px; margin-bottom: 4px; }
    .pastel-tile-title { font-size: 1rem; font-weight: 800; margin-bottom: 2px; }
    .pastel-tile-count { font-size: 0.8rem; font-weight: 600; opacity: 0.8; }

    .tile-purple { background-color: #f3e8ff; border-color: #e9d5ff; color: #6b21a8; }
    .tile-blue   { background-color: #e0f2fe; border-color: #bae6fd; color: #0369a1; }
    .tile-mint   { background-color: #dcfce7; border-color: #bbf7d0; color: #15803d; }
    .tile-peach  { background-color: #ffedd5; border-color: #fed7aa; color: #c2410c; }
    .tile-yellow { background-color: #fef9c3; border-color: #fef08a; color: #a16207; }
    .tile-slate  { background-color: #f1f5f9; border-color: #e2e8f0; color: #334155; }
    .tile-pink   { background-color: #fce7f3; border-color: #fbcfe8; color: #be185d; }
    .tile-indigo { background-color: #e0e7ff; border-color: #c7d2fe; color: #4338ca; }
    .tile-teal   { background-color: #ccfbf1; border-color: #99f6e4; color: #0f766e; }

    .room-content-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.03);
        margin-bottom: 18px;
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
        padding: 20px;
        margin-bottom: 14px;
    }

    .zoom-video-stage {
        position: relative;
        border-radius: 22px;
        overflow: hidden;
        border: 3px solid #1e3a8a;
        background: #0f172a;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.3);
        height: 290px;
    }
    .zoom-video-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center top;
    }
    .zoom-live-pill {
        position: absolute;
        top: 12px;
        right: 12px;
        background: rgba(15, 23, 42, 0.85);
        color: #22c55e;
        border: 1px solid #22c55e;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .live-dot {
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
        display: inline-block;
    }
    .zoom-teacher-tag {
        position: absolute;
        bottom: 12px;
        right: 12px;
        background: rgba(15, 23, 42, 0.85);
        color: #ffffff;
        padding: 5px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.85rem;
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

    div.stButton > button {
        background-color: #0f2b5c !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 8px 16px !important;
    }
    div.stButton > button:hover {
        background-color: #1e3a8a !important;
    }

    .stat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
    }
    .stat-val { font-size: 1.8rem; font-weight: 900; color: #0f2b5c; }
    .stat-lbl { color: #64748b; font-size: 0.85rem; font-weight: 600; }

    @media (max-width: 768px) {
        .hero-main-title { font-size: 2rem; }
        .features-ribbon { flex-direction: column; gap: 10px; }
        .main .block-container { padding-left: 12px !important; padding-right: 12px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ----------------- ניהול מצבי משתמש וסיסמאות -----------------
if "teacher_current_code" not in st.session_state:
    st.session_state.teacher_current_code = DEFAULT_TEACHER_CODE
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "תלמיד"
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_avatar" not in st.session_state:
    st.session_state.user_avatar = "🎓"
if "current_room" not in st.session_state:
    st.session_state.current_room = "דף הבית"
if "zoom_chat_history" not in st.session_state:
    st.session_state.zoom_chat_history = []
if "last_voice_audio_bytes" not in st.session_state:
    st.session_state.last_voice_audio_bytes = None
if "last_processed_audio_hash" not in st.session_state:
    st.session_state.last_processed_audio_hash = None
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
if "oral_chat_history" not in st.session_state:
    st.session_state.oral_chat_history = []
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "שליף החירום סגר לי את החומר לפני המבחן בהיסטוריה, הציל לי 20 נקודות."},
        {"name": "נועה ל.", "grade": "כיתה י\"א (ביולוגיה)", "rating": 5, "text": "האתר נראה יוקרתי, נקי מכל השטויות ובאמת מדבר בגובה העיניים."},
        {"name": "מאיה ר.", "grade": "כיתה י\"א (5 יח')", "rating": 5, "text": "מפרק המתמטיקה ומכתב הערעור זה גאונות. המורה קיבלה את הערעור והחזירה נקודות!"}
    ]

# ----------------- מסך כניסה חכם ומבודד -----------------
if not st.session_state.user_authenticated:
    st.markdown("""
        <div class="room-content-card" style="text-align: center; max-width: 520px; margin: 30px auto; border-top: 5px solid #0f2b5c;">
            <div style="font-size: 46px; margin-bottom: 6px;">🎓</div>
            <h2 style="color: #0f2b5c; margin: 0 0 6px 0; font-weight: 800;">ברוך הבא ל-The Dan Method</h2>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 18px;">
                בחר את סוג המשתמש לכניסה:
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.4, 1])
    with col_l2:
        chosen_type = st.radio("סוג משתמש:", ["תלמיד/ה 🎓", "מורה / איש צוות 🧑‍🏫"], horizontal=True)[cite: 9]
        is_teacher = "מורה" in chosen_type

        with st.form("unified_login_form"):
            in_email = st.text_input("אימייל בית-ספרי:", placeholder="name@tichonoz.org.il")[cite: 9]
            allow_guest = st.checkbox("אני מבית ספר אחר (פיילוט)")[cite: 9]
            in_name = st.text_input("כינוי / שם לתצוגה:", placeholder="למשל: דן כהן")[cite: 9]
            
            st.markdown("<div style='font-size:0.9rem; font-weight:700; color:#0f2b5c; margin-top:6px;'>בחר אווטאר:</div>", unsafe_allow_html=True)
            avatar_list = ["👨‍🎓 תלמיד", "👩‍🎓 תלמידה", "🚀 יזם", "🧠 גאון", "⚡ מהיר", "🦉 חכם", "🧑‍🏫 מורה", "🔬 חוקר"]
            in_avatar = st.selectbox("אווטאר:", avatar_list, index=6 if is_teacher else 0, label_visibility="collapsed")[cite: 9]
            
            teacher_pass_input = ""
            if is_teacher:
                st.markdown("---")
                teacher_pass_input = st.text_input("קוד גישה למורה (ראשוני: DAN100):", type="password", placeholder="הזן סיסמת מורה...")

            btn_submit_login = st.form_submit_button("כניסה למערכת 🚀", use_container_width=True)[cite: 9]
            if btn_submit_login:
                email_clean = in_email.strip().lower()
                domain_part = email_clean.split("@")[-1] if "@" in email_clean else ""
                
                if not email_clean or "@" not in email_clean:
                    st.error("נא להזין כתובת אימייל תקינה.")
                elif not allow_guest and not any(domain_part == d or domain_part.endswith("." + d) for d in ALLOWED_SCHOOL_DOMAINS):
                    st.error("האימייל אינו שייך לבית ספר מאושר. יש להשתמש בחשבון בית ספרי (למשל: @tichonoz.org.il) או לסמן פיילוט.")
                elif not in_name.strip():
                    st.error("נא להזין שם או כינוי לתצוגה.")
                elif is_teacher and teacher_pass_input.strip() != st.session_state.teacher_current_code:
                    st.error("קוד גישה למורה שגוי.")
                else:
                    st.session_state.user_email = email_clean
                    st.session_state.user_name = in_name.strip()
                    st.session_state.user_avatar = in_avatar.split()[0]
                    st.session_state.user_role = "מורה" if is_teacher else "תלמיד"
                    st.session_state.user_authenticated = True
                    st.session_state.current_room = "דף הבית"
                    st.success(f"שלום {st.session_state.user_name}! נכנסים למערכת...")
                    time.sleep(0.5)
                    st.rerun()
    st.stop()

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ מפתח GEMINI_API_KEY אינו מוגדר ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)
AVAILABLE_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]

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

def create_audio_bytes(text, lang='iw'):
    clean = re.sub(r"[*#_`>\[\]\(\)\n]", " ", text)
    clean = clean[:250].strip()
    tts = gTTS(text=clean, lang=lang)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

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

# ----------------- סרגל צד -----------------
with st.sidebar:
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; background: #f8fafc; padding: 10px 14px; border-radius: 14px; border: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 26px;">{st.session_state.user_avatar}</span>
                <div>
                    <div style="font-weight: 800; color: #0f2b5c; font-size: 0.95rem;">{st.session_state.user_name}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">סוג משתמש: <b>{st.session_state.user_role}</b></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 התנתק / החלף משתמש", use_container_width=True):
        st.session_state.user_authenticated = False
        st.session_state.user_role = "תלמיד"
        st.session_state.current_room = "דף הבית"
        st.rerun()

    # שינוי סיסמה אך ורק למורה
    if st.session_state.user_role == "מורה":
        with st.expander("🔑 שינוי סיסמת מורה"):
            with st.form("change_pass_form"):
                old_pass = st.text_input("סיסמה נוכחית:", type="password")
                new_pass = st.text_input("סיסמה חדשה:", type="password")
                confirm_pass = st.text_input("אימות סיסמה חדשה:", type="password")
                btn_change = st.form_submit_button("עדכן סיסמה")
                if btn_change:
                    if old_pass.strip() != st.session_state.teacher_current_code:
                        st.error("הסיסמה הנוכחית שגויה.")
                    elif len(new_pass.strip()) < 4:
                        st.error("הסיסמה חייבת לכלול לפחות 4 תווים.")
                    elif new_pass.strip() != confirm_pass.strip():
                        st.error("הסיסמה החדשה אינה תואמת לאימות.")
                    else:
                        st.session_state.teacher_current_code = new_pass.strip()
                        st.success("הסיסמה עודכנה בהצלחה!")

    st.markdown("---")
    st.subheader("👤 הפרופיל הלימודי")
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
        chosen_major = st.selectbox("מגמה בתיכון:", [
            "ללא מגמה (מקצועות ליבה בלבד)",
            "מדעי המחשב / הנדסת תוכנה (10 יח')",
            "פיזיקה (5 יח')",
            "ביולוגיה / כימיה",
            "ניהול עסקי / יזמות",
            "מדעי החברה / משפטים"
        ])
    
    st.markdown("---")
    no_yap = st.toggle("מצב תכל'ס (מענה ממוקד ולעניין)", value=True)

anti_yap_rule = "השב ישירות לתכל'ס, ללא פסקאות פתיחה או סיום מיותרות." if no_yap else ""
student_context = f"משתמש: {st.session_state.user_name} ({st.session_state.user_role}), שכבת לימוד: {chosen_grade}, מתמטיקה: {math_units}, אנגלית: {eng_units}, מגמה: {chosen_major}."

# ----------------- סרגל עליון (ללא כפתור מעבר בין תלמיד למורה) -----------------
col_nav_logo, col_nav_role_badge, col_nav_btn = st.columns([2.5, 1.5, 1])
with col_nav_logo:
    st.markdown(f"""
        <div class="learnit-navbar">
            <div class="brand-logo-container">
                <div style="width: 38px; height: 38px; border-radius: 12px; background: linear-gradient(135deg, #0f2b5c, #2563eb); display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 20px;">{st.session_state.user_avatar}</span>
                </div>
                <div style="display: flex; flex-direction: column; text-align: left; line-height: 1.1;">
                    <span class="brand-main-name">THE DAN METHOD</span>
                    <span class="brand-sub-badge">שלום {st.session_state.user_name} • לומדים. מתקדמים.</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_nav_role_badge:
    role_color = "#16a34a" if st.session_state.user_role == "תלמיד" else "#2563eb"
    st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:10px 14px; text-align:center; font-weight:800; color:{role_color}; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
            מרחב: {st.session_state.user_role} 🔒
        </div>
    """, unsafe_allow_html=True)

with col_nav_btn:
    if st.button("🏠 דף הבית", key="nav_home_main", use_container_width=True):
        st.session_state.current_room = "דף הבית"
        st.rerun()

# ----------------- דף הבית -----------------
if st.session_state.current_room == "דף הבית":
    mode_title = f"שלום {st.session_state.user_name}, הדרך שלך להצלחה מתחילה כאן." if st.session_state.user_role == "תלמיד" else f"שלום {st.session_state.user_name}, מרחב הפדגוגיה וההוראה החכמה."
    mode_sub = "לימודים קלים יותר, בכל מקום ובכל זמן. כל מה שצריך כדי להצליח – במקום אחד." if st.session_state.user_role == "תלמיד" else "הכנת מערכי שיעור, בחני פתע, לוח בקרה בית ספרי ומחוונים רשמיים בתוך שניות."
    
    st.markdown(f"""
        <div class="hero-banner">
            <h1 class="hero-main-title">{mode_title}</h1>
            <p class="hero-desc">{mode_sub}</p>
        </div>
    """, unsafe_allow_html=True)

    query_search = st.text_input("🔍 מה תרצה ללמוד היום?", placeholder="מה תרצה ללמוד היום? (למשל: 'איך גוזרים פונקציה?', 'מצגת', 'בגרות בעל פה'...)")

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
        elif any(w in q_lower for w in ["אנגלית", "בעל פה", "cobe", "oral"]):
            if st.button("🎙️ כניסה ישירה לסימולטור בגרות בעל פה באנגלית", use_container_width=True):
                st.session_state.current_room = "בגרות בעל פה"
                st.rerun()
        elif any(w in q_lower for w in ["מערך", "שיעור", "מורה"]) and st.session_state.user_role == "מורה":
            if st.button("⏱️ כניסה למחולל מערכי שיעור", use_container_width=True):
                st.session_state.current_room = "מערכי שיעור"
                st.rerun()
        else:
            with st.spinner("מעבד תשובה ממוקדת..."):
                try:
                    res_bot = generate_ai(f"אתה עוזר לימודי אישי חכם עבור {st.session_state.user_role}. פנה אל המשתמש בשם {st.session_state.user_name}. בהקשר: {student_context}. ענה על השאלה ישירות, ברור וקצר לתכל'ס בלי חפירות: {query_search}. {anti_yap_rule}", use_cache=True)
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

    # טבלת השוואה מעל הסיפור הקצר
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

    # הסיפור הקצר על השיטה
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
        <div style="margin-top: 10px; margin-bottom: 12px;">
            <div class="cat-grid-title">קטגוריות לימוד וכלים</div>
            <div class="cat-grid-subtitle">בחר את התחום שמעניין אותך והתחל ללמוד</div>
        </div>
    """, unsafe_allow_html=True)

    # אם המשתמש תלמיד - מציג אך ורק כלי תלמידים
    if st.session_state.user_role == "תלמיד":
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
            st.markdown('<div class="pastel-tile tile-indigo"><div class="pastel-tile-icon">🇬🇧</div><div class="pastel-tile-title">בגרות בעל פה</div><div class="pastel-tile-count">English Oral COBE</div></div>', unsafe_allow_html=True)
            if st.button("אנגלית בע\"פ", key="p_oral", use_container_width=True):
                st.session_state.current_room = "בגרות בעל פה"
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
            st.markdown('<div class="pastel-tile tile-teal"><div class="pastel-tile-icon">📸</div><div class="pastel-tile-title">סורק תמונות</div><div class="pastel-tile-count">פיענוח מדף/מחברת</div></div>', unsafe_allow_html=True)
            if st.button("סורק", key="p_scan", use_container_width=True):
                st.session_state.current_room = "סורק תמונות"
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

    # אם המשתמש מורה - מציג אך ורק כלי הוראה והנהלה
    else:
        col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
        with col_m1:
            st.markdown('<div class="pastel-tile tile-indigo"><div class="pastel-tile-icon">📊</div><div class="pastel-tile-title">לוח בקרה</div><div class="pastel-tile-count">מדדי בית ספר</div></div>', unsafe_allow_html=True)
            if st.button("אנליטיקס", key="pm_dash", use_container_width=True):
                st.session_state.current_room = "לוח בקרה"
                st.rerun()

        with col_m2:
            st.markdown('<div class="pastel-tile tile-blue"><div class="pastel-tile-icon">📑</div><div class="pastel-tile-title">מצגת שיעור</div><div class="pastel-tile-count">הורדת PPTX</div></div>', unsafe_allow_html=True)
            if st.button("מצגת מורה", key="pm_slides", use_container_width=True):
                st.session_state.current_room = "מצגות"
                st.rerun()

        with col_m3:
            st.markdown('<div class="pastel-tile tile-mint"><div class="pastel-tile-icon">⏱️</div><div class="pastel-tile-title">מערך שיעור</div><div class="pastel-tile-count">45 דק\' מדורגות</div></div>', unsafe_allow_html=True)
            if st.button("מערך", key="pm_lesson", use_container_width=True):
                st.session_state.current_room = "מערכי שיעור"
                st.rerun()

        with col_m4:
            st.markdown('<div class="pastel-tile tile-yellow"><div class="pastel-tile-icon">📝</div><div class="pastel-tile-title">בוחן + מחוון</div><div class="pastel-tile-count">15 דק\' עם ניקוד</div></div>', unsafe_allow_html=True)
            if st.button("בוחן", key="pm_quiz", use_container_width=True):
                st.session_state.current_room = "בחנים ומחוונים"
                st.rerun()

        with col_m5:
            st.markdown('<div class="pastel-tile tile-teal"><div class="pastel-tile-icon">🔬</div><div class="pastel-tile-title">מטלת חקר (30%)</div><div class="pastel-tile-count">הערכה חלופית</div></div>', unsafe_allow_html=True)
            if st.button("הערכה חלופית", key="pm_pbl", use_container_width=True):
                st.session_state.current_room = "הערכה חלופית"
                st.rerun()

        with col_m6:
            st.markdown('<div class="pastel-tile tile-slate"><div class="pastel-tile-icon">🏛️</div><div class="pastel-tile-title">מכתב להנהלה</div><div class="pastel-tile-count">פיילוט וייעוץ</div></div>', unsafe_allow_html=True)
            if st.button("מכתב", key="pm_lead", use_container_width=True):
                st.session_state.current_room = "הנהלה"
                st.rerun()

        col_m7, col_m8, col_m9, col_m10, col_m11, col_m12 = st.columns(6)
        with col_m7:
            st.markdown('<div class="pastel-tile tile-peach"><div class="pastel-tile-icon">✍️</div><div class="pastel-tile-title">בנק הערכות</div><div class="pastel-tile-count">משובים לתעודות</div></div>', unsafe_allow_html=True)
            if st.button("הערכות", key="pm_feedback", use_container_width=True):
                st.session_state.current_room = "בנק הערכות"
                st.rerun()

        with col_m8:
            st.markdown('<div class="pastel-tile tile-mint"><div class="pastel-tile-icon">📱</div><div class="pastel-tile-title">הודעה להורים</div><div class="pastel-tile-count">וואטסאפ כיתתי</div></div>', unsafe_allow_html=True)
            if st.button("הורים", key="pm_parents", use_container_width=True):
                st.session_state.current_room = "הודעות הורים"
                st.rerun()

        with col_m9:
            st.markdown('<div class="pastel-tile tile-purple"><div class="pastel-tile-icon">🪜</div><div class="pastel-tile-title">דיפרנציאלי</div><div class="pastel-tile-count">3 רמות קושי</div></div>', unsafe_allow_html=True)
            if st.button("דיפרנציאלי", key="pm_diff", use_container_width=True):
                st.session_state.current_room = "מבדק דיפרנציאלי"
                st.rerun()

        with col_m10:
            st.markdown('<div class="pastel-tile tile-yellow"><div class="pastel-tile-icon">💡</div><div class="pastel-tile-title">פתיחת שיעור</div><div class="pastel-tile-count">Hook של 5 דקות</div></div>', unsafe_allow_html=True)
            if st.button("פתיחה", key="pm_hook", use_container_width=True):
                st.session_state.current_room = "פתיחת שיעור"
                st.rerun()

        with col_m11:
            st.markdown('<div class="pastel-tile tile-pink"><div class="pastel-tile-icon">🩻</div><div class="pastel-tile-title">מוקשי למידה</div><div class="pastel-tile-count">טעויות נפוצות</div></div>', unsafe_allow_html=True)
            if st.button("מלכודות", key="pm_xray", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()

        with col_m12:
            st.markdown('<div class="pastel-tile tile-blue"><div class="pastel-tile-icon">🖨️</div><div class="pastel-tile-title">דפי הדפסה</div><div class="pastel-tile-count">תרגול לכיתה</div></div>', unsafe_allow_html=True)
            if st.button("דפי עבודה", key="pm_print", use_container_width=True):
                st.session_state.current_room = "דפי הדפסה"
                st.rerun()

    # אזור חוות דעת של תלמידים ומורים
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
            fb_name = st.text_input("שם או כינוי:", value=st.session_state.user_name)
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

# ----------------- חדר: לוח בקרה ומדדי למידה להנהלה -----------------
elif st.session_state.current_room == "לוח בקרה":
    st.markdown('<span class="room-badge-pill" style="background:#e0e7ff; color:#4338ca;">📊 School Leadership Analytics</span>', unsafe_allow_html=True)
    st.title("לוח בקרה ומדדי למידה בית-ספריים")
    st.caption("תמונת מצב חיה להנהלת בית הספר ולרכזי המקצועות על היקפי הלמידה, מוקדי הקושי וחיסכון בשעות הוראה.")

    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.markdown('<div class="stat-card"><div class="stat-val">2,480</div><div class="stat-lbl">תרגילים ושאלות שנפתרו החודש</div></div>', unsafe_allow_html=True)
    with col_stat2:
        st.markdown('<div class="stat-card"><div class="stat-val">142 שעות</div><div class="stat-lbl">שעות הכנת חומרים שנחסכו לצוות</div></div>', unsafe_allow_html=True)
    with col_stat3:
        st.markdown('<div class="stat-card"><div class="stat-val">87%</div><div class="stat-lbl">מדד שביעות רצון והבנת החומר</div></div>', unsafe_allow_html=True)
    with col_stat4:
        st.markdown('<div class="stat-card"><div class="stat-val">340</div><div class="stat-lbl">שיעורי זום ותרגולים קוליים עם מיה</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_d_left, col_d_right = st.columns([1.2, 1.8])
    with col_d_left:
        st.markdown("""
            <div class="room-content-card">
                <h4 style="margin-top:0; color:#0f2b5c;">📌 התפלגות פניות לפי מקצוע</h4>
                <div style="margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; font-weight:700;"><span>מתמטיקה (4-5 יח')</span><span>42%</span></div>
                    <div style="background:#e2e8f0; border-radius:8px; height:8px; overflow:hidden;"><div style="background:#2563eb; width:42%; height:100%;"></div></div>
                </div>
                <div style="margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; font-weight:700;"><span>אנגלית (דקדוק ובעל פה)</span><span>24%</span></div>
                    <div style="background:#e2e8f0; border-radius:8px; height:8px; overflow:hidden;"><div style="background:#16a34a; width:24%; height:100%;"></div></div>
                </div>
                <div style="margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; font-weight:700;"><span>לשון והבעה עברית</span><span>18%</span></div>
                    <div style="background:#e2e8f0; border-radius:8px; height:8px; overflow:hidden;"><div style="background:#f59e0b; width:18%; height:100%;"></div></div>
                </div>
                <div>
                    <div style="display:flex; justify-content:space-between; font-weight:700;"><span>מדעי החברה / היסטוריה</span><span>16%</span></div>
                    <div style="background:#e2e8f0; border-radius:8px; height:8px; overflow:hidden;"><div style="background:#8b5cf6; width:16%; height:100%;"></div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_d_right:
        st.markdown("""
            <div class="room-content-card">
                <h4 style="margin-top:0; color:#0f2b5c;">🚨 מוקדי קושי שזוהו בזמן אמת (דורשים תגבור כיתתי):</h4>
                <ul style="color:#334155; line-height:1.8; margin-bottom:14px;">
                    <li><b>שכבת ט' – מתמטיקה:</b> שגיאות חוזרות בפירוק לגורמים ומשוואות ריבועיות עם מקדם שלילי.</li>
                    <li><b>שכבת י"א – אנגלית:</b> קושי ברציפות דיבור ותשובות קצרות מדי בשאלות הפרויקט של הבגרות בעל פה.</li>
                    <li><b>שכבת י' – לשון:</b> בלבול שכיח בין בניין נפעל לבניין קל בגזרת השלמים.</li>
                </ul>
                <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:12px; font-size:0.9rem; color:#15803d;">
                    💡 <b>המלצה פדגוגית להנהלה:</b> שילוב תרגול ממוקד של 10 דקות בתחילת השיעורים הקרובים סוגר 75% מפערים אלו.
                </div>
            </div>
        """, unsafe_allow_html=True)

# ----------------- חדר: בגרות בעל פה באנגלית -----------------
elif st.session_state.current_room == "בגרות בעל פה":
    st.markdown('<span class="room-badge-pill" style="background:#e0e7ff; color:#4338ca;">🇬🇧 English Oral Bagrut (COBE Simulator)</span>', unsafe_allow_html=True)
    st.title("סימולטור בגרות בעל פה באנגלית")
    st.caption("אימון אישי לקראת הבחינה בעל פה: מענה קולי לשאלות אישיות, פרויקט החקר וסרטוני הבחינה עם משוב מיידי.")

    col_or1, col_or2 = st.columns([1.2, 1.8])
    with col_or1:
        st.markdown("""
            <div class="room-content-card">
                <h4 style="margin-top:0; color:#0f2b5c;">🎯 חלק הבחינה לתרגול:</h4>
        """, unsafe_allow_html=True)
        part_oral = st.selectbox("Exam Part:", [
            "Part A: Personal Interview (Hobby, School, Future)",
            "Part B: Project Presentation (Topic, Findings, Reflection)",
            "Part C: Clip / Video Response & Dilemma"
        ])
        level_oral = st.selectbox("English Level:", ["4 Points (Good & Clear)", "5 Points (Rich Vocabulary & Idioms)"])
        
        if st.button("🚀 Start / New Oral Question", use_container_width=True):
            prompt_or = f"You are the official English Bagrut Oral Examiner (COBE) in Israel for high school students. Level: {level_oral}. Part: {part_oral}. The student's name is {st.session_state.user_name}. Give the student ONE authentic, clear exam question. Speak politely and clearly."
            with st.spinner("Examiner is preparing a question..."):
                try:
                    res_or = generate_ai(prompt_or)
                    st.session_state.oral_chat_history = [{"role": "assistant", "content": res_or.text}]
                    st.session_state.last_voice_audio_bytes = create_audio_bytes(res_or.text, lang='en')
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.button("🧹 Reset English Simulation", use_container_width=True):
            st.session_state.oral_chat_history = []
            st.session_state.last_voice_audio_bytes = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_or2:
        st.markdown("<b>🎙️ Oral Exam Dialogue:</b>", unsafe_allow_html=True)
        box_or = st.container(height=260)
        with box_or:
            if not st.session_state.oral_chat_history:
                st.info("Click 'Start / New Oral Question' on the left to begin your spoken English practice!")
            else:
                for msg in st.session_state.oral_chat_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

        if st.session_state.last_voice_audio_bytes:
            st.audio(st.session_state.last_voice_audio_bytes, format="audio/mp3", autoplay=True)

        user_oral_voice = st.audio_input("Record your spoken answer in English:")
        if user_oral_voice is not None:
            v_data = user_oral_voice.read()
            v_hash = hashlib.md5(v_data).hexdigest()
            if v_hash != st.session_state.last_processed_audio_hash:
                st.session_state.last_processed_audio_hash = v_hash
                with st.spinner("Examiner is evaluating your answer..."):
                    try:
                        audio_part = types.Part.from_bytes(data=v_data, mime_type="audio/wav")
                        prompt_eval = [
                            f"You are the official Bagrut oral examiner in Israel. Listen to the student ({st.session_state.user_name}). 1. Praise what they did well. 2. Give 1 vocabulary or grammar correction. 3. Rate their fluency out of 100. 4. Ask the next brief follow-up question. Keep it concise (under 4 sentences).",
                            audio_part
                        ]
                        res_eval_or = generate_ai(prompt_eval)
                        st.session_state.oral_chat_history.append({"role": "user", "content": "🎙️ [Recorded Spoken Answer]"})
                        st.session_state.oral_chat_history.append({"role": "assistant", "content": res_eval_or.text})
                        st.session_state.last_voice_audio_bytes = create_audio_bytes(res_eval_or.text, lang='en')
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# ----------------- חדר: מטלת חקר והערכה חלופית 30% -----------------
elif st.session_state.current_room == "הערכה חלופית":
    st.markdown('<span class="room-badge-pill" style="background:#ccfbf1; color:#0f766e;">🔬 30% Alternative Assessment & PBL</span>', unsafe_allow_html=True)
    st.title("מחולל מטלות חקר והערכה חלופית (30% בגרות)")
    st.caption("בניית משימות ביצוע (PBL), שאלות חקר פתוחות ומחוון הערכה משרד החינוך בלחיצת כפתור.")

    col_pbl1, col_pbl2 = st.columns(2)
    with col_pbl1:
        pbl_sub = st.text_input("מקצוע הלימוד:", placeholder="היסטוריה, אזרחות, ביולוגיה, ספרות, מדעי החברה...")
        pbl_top = st.text_input("נושא עבודת החקר:", placeholder="למשל: השפעת הרשתות החברתיות על דימוי עצמי, מנהיגות בעת משבר...")
    with col_pbl2:
        pbl_format = st.selectbox("פורמט ההגשה הנדרש:", [
            "עבודת חקר מודפסת כוללת שאלת מחקר וביבליוגרפיה",
            "פודקאסט מוקלט או ראיון מצולם",
            "תערוכה דיגיטלית / פוסטר מדעי",
            "נייר עמדה מנומק לדילמה אקטואלית"
        ])

    if st.button("🔬 בנה תוכנית הערכה חלופית מלאה", use_container_width=True):
        if pbl_sub and pbl_top:
            with st.spinner("בונה משימת הערכה חלופית ומחוון..."):
                p_pbl = (
                    f"אתה מומחה להערכה חלופית (30% בגרות) במשרד החינוך בישראל עבור כיתה {chosen_grade}.\n"
                    f"מקצוע: {pbl_sub}, נושא: {pbl_top}, פורמט: {pbl_format}.\n"
                    "בנה דף הנחיות רשמי ומלא למורה ולתלמידים הכולל:\n"
                    "1. מטרת המטלה והקשר שלה לתוכנית הלימודים.\n"
                    "2. שלבי הביצוע צעד-אחר-צעד (ניסוח שאלת חקר, איסוף מקורות, עיבוד ורפלקציה).\n"
                    "3. תוצר ההגשה הנדרש.\n"
                    "4. מחוון הערכה מדויק מתוך 100 נקודות (תוכן, עומק, מקוריות, רפלקציה)."
                )
                res_pbl = generate_ai(p_pbl)
                st.markdown(f'<div class="room-content-card" style="border-right: 4px solid #0f766e;">{res_pbl.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_pbl.text)}" target="_blank">📲 שתף מטלת חקר בוואטסאפ</a>', unsafe_allow_html=True)
        else:
            st.warning("נא להזין מקצוע ונושא.")

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

# ----------------- חדר: שיעור זום חי עם המורה מיה -----------------
elif st.session_state.current_room == "חדר זום":
    st.markdown('<span class="room-badge-pill" style="background:#dcfce7; color:#15803d;">📹 Live Interactive Zoom Class</span>', unsafe_allow_html=True)
    st.title("שיעור פרטי בזום עם המורה מיה")
    st.caption("שיחת קול חיה, מענה מותאם אישית ותרגול שיעורי בית לבגרות ולמבחנים!")
    
    col_z1, col_z2 = st.columns([1.1, 1.9])
    with col_z1:
        zoom_ui_html = """
        <div class="zoom-video-stage">
            <div class="zoom-live-pill"><span class="live-dot"></span> שידור חי פועל</div>
            <img class="zoom-video-img" src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=800&q=80" alt="המורה מיה">
            <div class="zoom-teacher-tag">המורה מיה (בשיחה חיה)</div>
        </div>
        """
        st.markdown(zoom_ui_html, unsafe_allow_html=True)
        
        if st.session_state.last_voice_audio_bytes:
            st.markdown("<div style='margin-top: 12px; margin-bottom: 4px; font-weight: 700; color: #0f2b5c;'>🔊 השמעת תשובת המורה מיה:</div>", unsafe_allow_html=True)
            st.audio(st.session_state.last_voice_audio_bytes, format="audio/mp3", autoplay=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        z_subject = st.selectbox("מקצוע השיעור:", ["מתמטיקה", "אנגלית", "היסטוריה", "לשון והבעה", "ביולוגיה", "אזרחות"])
        
        if st.button("📚 תני לי משימת תרגול / שיעורי בית לשיעור", use_container_width=True):
            with st.spinner("המורה מיה מכינה תרגילי אתגר לשיעור..."):
                try:
                    hw_prompt = (
                        f"את המורה מיה. תני לתלמיד {st.session_state.user_name} ב-{student_context} משימת תרגול קצרה ומאתגרת (שיעורי בית) ב{z_subject}.\n"
                        "המשימה צריכה לכלול:\n"
                        "1. תרגיל/שאלה 1 ברמה בסיסית.\n"
                        "2. תרגיל/שאלה 2 ברמת בגרות/מבחן כיתתי.\n"
                        "3. הנחיה מה לכתוב או להקליט לך בחזרה כדי שתבדקי ותתני ציון."
                    )
                    res_hw = generate_ai(hw_prompt)
                    reply_text = f"היי {st.session_state.user_name}, הכנתי לך שתי שאלות תרגול מעולות. תפתור אותן ותקליט לי או תכתוב לי כאן את התשובות ואבדוק לך מיד!"
                    st.session_state.zoom_homework = res_hw.text
                    st.session_state.last_voice_audio_bytes = create_audio_bytes(reply_text)
                    st.rerun()
                except Exception as err:
                    st.error(f"שגיאה בהכנת המשימה: {err}")

        if st.button("🧹 איפוס שיחה", use_container_width=True):
            st.session_state.zoom_chat_history = []
            st.session_state.last_voice_audio_bytes = None
            st.session_state.last_processed_audio_hash = None
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
        chat_box = st.container(height=260)
        with chat_box:
            if not st.session_state.zoom_chat_history:
                st.info(f"👋 **המורה מיה:** היי {st.session_state.user_name}! שמחה לפגוש אותך לשיעור ב{z_subject}. אתה יכול לכתוב לי, להשתמש בשאלות ההדגמה למטה, או פשוט להקליט לי הודעה קולית ישירות!")
            else:
                for m in st.session_state.zoom_chat_history:
                    with st.chat_message(m["role"]):
                        st.write(m["content"])

        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #64748b; margin-top: 6px;'>⚡ שאלות מהירות לדמו (לחיצה אחת):</div>", unsafe_allow_html=True)
        col_demo1, col_demo2, col_demo3 = st.columns(3)
        trigger_demo_text = None
        with col_demo1:
            if st.button("🧮 תרגיל במתמטיקה", use_container_width=True):
                trigger_demo_text = "איך פותרים משוואה ריבועית בעזרת נוסחת השורשים? תני לי דוגמה פשוטה."
        with col_demo2:
            if st.button("📖 הסבר מהיר לבגרות", use_container_width=True):
                trigger_demo_text = f"תסבירי לי ב-3 שורות בדיוק מושג מרכזי ב{z_subject} שאסור לי לפספס במבחן."
        with col_demo3:
            if st.button("🎯 טיפ למאיות", use_container_width=True):
                trigger_demo_text = "איזה טיפ זהב יבטיח לי 100 במבחן הקרוב?"

        st.markdown("<div style='font-weight:700; font-size:0.9rem; color:#0f2b5c; margin-top:8px;'>🎙️ הקלט הודעה קולית למורה מיה:</div>", unsafe_allow_html=True)
        voice_rec = st.audio_input("הקלט הודעה קולית למיה", label_visibility="collapsed")
        
        if voice_rec is not None:
            audio_bytes_data = voice_rec.read()
            current_hash = hashlib.md5(audio_bytes_data).hexdigest()
            
            if current_hash != st.session_state.last_processed_audio_hash:
                st.session_state.last_processed_audio_hash = current_hash
                with st.spinner("המורה מיה מקשיבה להקלטה ומכינה מענה..."):
                    try:
                        audio_part = types.Part.from_bytes(
                            data=audio_bytes_data,
                            mime_type="audio/wav"
                        )
                        prompt_audio = [
                            (
                                f"את המורה מיה בשיעור פרטי אישי חי עם התלמיד {st.session_state.user_name} ב-{student_context}.\n"
                                f"מקצוע השיעור: {z_subject}.\n"
                                "התלמיד שלח לך הקלטה קולית זו. הקשיבי לה ועני לו ישירות בעברית.\n"
                                "הנחיות: פני אליו בשמו, דברי בלשון נקבה על עצמך, עני בגובה העיניים, מעודד וממוקד (עד 3 משפטים).\n"
                                "אם הוא פתר תרגיל, בדקי אותו ותני ציון. בסוף שאלי שאלה קצרה."
                            ),
                            audio_part
                        ]
                        res_zoom = generate_ai(prompt_audio)
                        st.session_state.zoom_chat_history.append({"role": "user", "content": "🎙️ [שלח הודעה קולית]"})
                        st.session_state.zoom_chat_history.append({"role": "assistant", "content": res_zoom.text})
                        st.session_state.last_voice_audio_bytes = create_audio_bytes(res_zoom.text)
                        st.rerun()
                    except Exception as err:
                        st.error(f"שגיאה בעיבוד ההקלטה: {err}")

        text_spoken = st.chat_input("או הקלד כאן הודעה בטקסט...")
        final_input_to_send = trigger_demo_text if trigger_demo_text else text_spoken

        if final_input_to_send:
            st.session_state.zoom_chat_history.append({"role": "user", "content": final_input_to_send})
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.zoom_chat_history[-6:]])
            zoom_prompt = (
                f"את המורה מיה בשיעור פרטי אישי חי עם התלמיד {st.session_state.user_name} ב-{student_context}.\n"
                f"מקצוע השיעור: {z_subject}.\n"
                "הנחיות קריטיות:\n"
                "1. פני אליו בשמו.\n"
                "2. דברי בלשון נקבה על עצמך ('אני כאן איתך', 'בדקתי את התשובה').\n"
                "3. עני בגובה העיניים, מעודד וממוקד מאוד (עד 3 משפטים).\n"
                "4. אם התלמיד פותר תרגיל או שיעורי בית – בדקי אותו, תני לו משוב וציון!\n"
                "5. בסוף התשובה שאלי שאלה קצרה כדי לוודא שהוא הבין.\n\n"
                f"היסטוריה:\n{history_text}\n\nהודעת התלמיד: {final_input_to_send}"
            )
            with st.spinner("המורה מיה מקשיבה ומכינה מענה..."):
                try:
                    res_zoom = generate_ai(zoom_prompt)
                    st.session_state.zoom_chat_history.append({"role": "assistant", "content": res_zoom.text})
                    st.session_state.last_voice_audio_bytes = create_audio_bytes(res_zoom.text)
                    st.rerun()
                except Exception as err:
                    st.error(f"שגיאה בתקשורת עם המורה: {err}")

# ----------------- חדר: בנק הערכות ומשובים לתעודות (רק למורה) -----------------
elif st.session_state.current_room == "בנק הערכות" and st.session_state.user_role == "מורה":
    st.markdown('<span class="room-badge-pill" style="background:#fef9c3; color:#a16207;">✍️ Report Cards & Evaluations</span>', unsafe_allow_html=True)
    st.title("מחולל הערכות ומשובים לתעודות ולימי הורים")
    st.caption("ניסוח משובים פדגוגיים, מכבדים ומעצימים המוכנים להעתקה ישירה למשו״ב / סמארטסקול.")
    
    col_fb1, col_fb2 = st.columns(2)
    with col_fb1:
        st_name = st.text_input("שם התלמיד/ה:", placeholder="למשל: דניאל, יובל, מאיה...")
        st_gender = st.radio("מגדר:", ["תלמיד (זכר)", "תלמידה (נקבה)"], horizontal=True)
        st_sub = st.text_input("מקצוע הלימוד:", placeholder="מתמטיקה, היסטוריה, אנגלית...")
    with col_fb2:
        st_level = st.selectbox("הישגים לימודיים:", ["מצטיין / גבוה מאוד (90-100)", "טוב מאוד / שולט בחומר (80-89)", "הישגים בינוניים / דרוש תרגול (65-79)", "מתקשה / פערים לימודיים (מתחת ל-65)"])
        st_effort = st.selectbox("השקעה והתנהגות:", ["השקעה גבוהה, פעיל ותורם לשיעור", "משקיע ומכין מטלות אך שקט", "פוטנציאל גבוה שאינו ממומש", "קושי בהתמדה ואיחורים/חיסורים"])
        fb_length = st.radio("📏 אורך המשוב המבוקש:", [
            "קצר וממוקד (משפט-שניים למשו״ב)",
            "בינוני ומאוזן (פסקה סטנדרטית)",
            "מפורט ומעמיק (ליום הורים / סיכום שנה)"
        ], index=1, horizontal=True)

    if st.button("✨ נסח משוב אישי ומעצים", use_container_width=True):
        if st_name and st_sub:
            with st.spinner("מנסח משוב אישי פדגוגי..."):
                p_gender = "זכר" if "זכר" in st_gender else "נקבה"
                fb_prompt = (
                    f"אתה יועץ חינוכי ומורה מומחה במערכת החינוך בישראל.\n"
                    f"נסח משוב לתעודה/יום הורים עבור התלמיד/ה {st_name} (מגדר: {p_gender}) במקצוע {st_sub}.\n"
                    f"שכבת גיל: {chosen_grade}.\n"
                    f"הישגים: {st_level}, השקעה: {st_effort}.\n"
                    f"הנחיית אורך קריטית: {fb_length}.\n"
                    "דרישות:\n"
                    "1. משוב מעצים ומכבד שמתמקד בחוזקות לצד יעד ברור לשיפור.\n"
                    "2. הקפד בדיוק על האורך שנבחר.\n"
                    "3. ניסוח רשמי, חם ומותאם לשדות הערכה בית-ספריים."
                )
                res_eval = generate_ai(fb_prompt)
                st.markdown(f'<div class="room-content-card" style="border-right: 4px solid #f59e0b;">{res_eval.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_eval.text)}" target="_blank">📲 שתף משוב בוואטסאפ</a>', unsafe_allow_html=True)
        else:
            st.warning("נא להזין שם תלמיד ומקצוע לימוד.")

# ----------------- חדר: הודעות וואטסאפ להורים (רק למורה) -----------------
elif st.session_state.current_room == "הודעות הורים" and st.session_state.user_role == "מורה":
    st.markdown('<span class="room-badge-pill" style="background:#dcfce7; color:#15803d;">📱 Classroom WhatsApp Broadcast</span>', unsafe_allow_html=True)
    st.title("מחולל הודעות וואטסאפ רשמיות להורים")
    st.caption("ניסוח הודעות ברורות, חמות ומאורגנות לקבוצת ההורים או להורה ספציפי.")
    
    col_pmsg1, col_pmsg2 = st.columns(2)
    with col_pmsg1:
        pmsg_type = st.selectbox("סוג ההודעה:", [
            "עדכון לקראת מבחן קרוב וטיפים ללמידה בבית",
            "סיכום שבועי של הלמידה והישגי הכיתה",
            "תזכורת חמה לגבי הגשת מטלה / שיעורי בית",
            "הודעה אישית להורה על התקדמות יפה של תלמיד",
            "הודעה על התנהגות או פערים לימודיים הדורשים שיתוף פעולה"
        ])
        pmsg_subject = st.text_input("מקצוע או נושא:", placeholder="מתמטיקה, היסטוריה, אנגלית...")
        pmsg_length = st.radio("📏 אורך ההודעה:", [
            "קצר ולעניין (מבזק וואטסאפ של 2-3 שורות)",
            "בינוני (נוסח סטנדרטי עם נקודות)",
            "מפורט (הסבר מלא עם רקע, הנחיות וטיפים)"
        ], index=1, horizontal=True)
    with col_pmsg2:
        pmsg_details = st.text_area("פרטים נוספים שכדאי להכניס להודעה:", placeholder="למשל: המבחן יתקיים ביום רביעי, החומר כולל עמודים 30-50, חשוב להביא סרגל ומחשבון...")

    if st.button("📲 צור נוסח הודעה מוכן לשליחה", use_container_width=True):
        if pmsg_subject:
            with st.spinner("מנסח הודעה ייצוגית..."):
                prompt_parent = (
                    f"אתה מורה/מחנך בישראל עבור כיתה {chosen_grade}.\n"
                    f"נסח הודעת וואטסאפ רשמית, חמה ומסודרת להורים.\n"
                    f"סוג ההודעה: {pmsg_type}, נושא: {pmsg_subject}, פרטים נוספים: {pmsg_details}.\n"
                    f"הנחיית אורך קריטית: {pmsg_length}.\n"
                    "דרישות:\n"
                    "1. ניסוח נעים ומכבד בגובה העיניים עם אימוג'ים מתאימים.\n"
                    "2. אם נבחר קצר: 2-3 משפטים חדים ומדויקים בלבד. אם בינוני/ארוך: חלוקה לנקודות מסודרות.\n"
                    "3. סיום בהזמנה ליצירת קשר וברכת שבוע טוב / בהצלחה."
                )
                res_pmsg = generate_ai(prompt_parent)
                st.markdown(f'<div class="room-content-card" style="border-right: 4px solid #22c55e;">{res_pmsg.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_pmsg.text)}" target="_blank">📲 שלח ישירות בוואטסאפ</a>', unsafe_allow_html=True)
        else:
            st.warning("נא להזין מקצוע או נושא.")

# ----------------- חדר: מבדק דיפרנציאלי (רק למורה) -----------------
elif st.session_state.current_room == "מבדק דיפרנציאלי" and st.session_state.user_role == "מורה":
    st.markdown('<span class="room-badge-pill" style="background:#f3e8ff; color:#6b21a8;">🪜 Differentiated Assessment</span>', unsafe_allow_html=True)
    st.title("מחולל מבדק דיפרנציאלי ב-3 רמות")
    st.caption("יצירת תרגול המותאם לכיתה הטרוגנית: רמת בסיס, רמת ליבה ורמת אתגר ומצוינות.")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        diff_sub = st.text_input("מקצוע:", placeholder="מתמטיקה, מדעים, לשון, אנגלית...")
        diff_topic = st.text_input("הנושא הנלמד:", placeholder="למשל: משוואות מעריכיות, שמות תואר, מערכת העיכול...")
    with col_d2:
        diff_type = st.selectbox("מבנה המטלה:", [
            "שאלות פתוחות עם שלבי פתרון",
            "שאלות אמריקאיות (רב-ברירה) עם נימוק",
            "משימת חקר / ניתוח קטע קצר"
        ])

    if st.button("🪜 בנה מבדק ב-3 רמות", use_container_width=True):
        if diff_sub and diff_topic:
            with st.spinner("בונה מבדק מדורג..."):
                prompt_diff = (
                    f"בנה דף תרגול ומבדק דיפרנציאלי מותאם לכיתה {chosen_grade}.\n"
                    f"מקצוע: {diff_sub}, נושא: {diff_topic}, מבנה: {diff_type}.\n"
                    "חלק את הדף ל-3 חלקים ברורים:\n"
                    "1. רמת מדרגה ראשונה (בסיס וחיזוק) - שאלות מונחות עם רמזים לתלמידים מתקשים.\n"
                    "2. רמת ליבה (מבחן סטנדרטי) - שאלות ברמת תוכנית הלימודים הרגילה.\n"
                    "3. רמת אתגר ומצוינות (למתקדמים) - שאלת חשיבה גבוהה/יישום שמאתגרת את התלמידים החזקים.\n"
                    "הוסף בסוף מחוון פתרונות קצר למורה."
                )
                res_diff = generate_ai(prompt_diff)
                st.markdown(f'<div class="room-content-card" style="border-right: 4px solid #8b5cf6;">{res_diff.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_diff.text)}" target="_blank">📲 שתף מבדק דיפרנציאלי בוואטסאפ</a>', unsafe_allow_html=True)
        else:
            st.warning("נא להזין מקצוע ונושא.")

# ----------------- חדר: פתיחת שיעור מסקרנת (רק למורה) -----------------
elif st.session_state.current_room == "פתיחת שיעור" and st.session_state.user_role == "מורה":
    st.markdown('<span class="room-badge-pill" style="background:#ccfbf1; color:#0f766e;">💡 5-Minute Class Hook</span>', unsafe_allow_html=True)
    st.title("מחולל פתיחת שיעור מסקרנת (Hook)")
    st.caption("רעיונות להפעלות של 5 דקות בתחילת השיעור שמעוררות עניין וסקרנות בקרב התלמידים.")
    
    col_hk1, col_hk2 = st.columns(2)
    with col_hk1:
        hk_sub = st.text_input("מקצוע:", placeholder="אזרחות, היסטוריה, מדעים, ספרות...")
        hk_topic = st.text_input("נושא השיעור:", placeholder="למשל: דמוקרטיה וזכויות אדם, חוקי ניוטון, שירת ימי הביניים...")
    with col_hk2:
        hk_style = st.selectbox("סגנון הפתיחה המבוקש:", [
            "דילמה מוסרית או משפטית מעוררת ויכוח",
            "חידה / פרדוקס שקשור לנושא",
            "שאלה שמחברת את החומר לחיים האמיתיים של הנוער",
            "משחקון קצר או הצבעה כיתתית אינטראקטיבית"
        ])

    if st.button("💡 צור 3 רעיונות לפתיחת שיעור", use_container_width=True):
        if hk_sub and hk_topic:
            with st.spinner("מייצר רעיונות סוחפים לפתיחת השיעור..."):
                prompt_hook = (
                    f"אתה מומחה להוראה פעילה ופדגוגיה חדשנית בישראל עבור כיתה {chosen_grade}.\n"
                    f"מקצוע: {hk_sub}, נושא: {hk_topic}, סגנון: {hk_style}.\n"
                    "הצע 3 אפשרויות שונות לפתיחת שיעור מסקרנת של 5 דקות:\n"
                    "עבור כל אפשרות פרט:\n"
                    "- מה המורה אומר/מציג על הלוח (הטריגר)\n"
                    "- שאלת הפעלה לתלמידים\n"
                    "- איך לחבר את התשובות שלהם לנושא המרכזי של השיעור"
                )
                res_hk = generate_ai(prompt_hook)
                st.markdown(f'<div class="room-content-card" style="border-right: 4px solid #0d9488;">{res_hk.text}</div>', unsafe_allow_html=True)
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_hk.text)}" target="_blank">📲 שתף פתיחת שיעור בוואטסאפ</a>', unsafe_allow_html=True)
        else:
            st.warning("נא להזין מקצוע ונושא.")

# ----------------- חדר: מכתב להנהלה (רק למורה) -----------------
elif st.session_state.current_room == "הנהלה" and st.session_state.user_role == "מורה":
    st.markdown('<span class="room-badge-pill" style="background:#f1f5f9; color:#334155;">🏛️ Leadership Proposal</span>', unsafe_allow_html=True)
    st.title("מכתב רשמי להנהלת בית הספר ולצוות הייעוץ")
    
    col_lead1, col_lead2 = st.columns(2)
    with col_lead1:
        lead_focus = st.selectbox("מוקד המכתב:", [
            "הצעה לפיילוט כיתתי ללמידה עצמאית והפחתת עומס ממורים",
            "תוכנית תמיכה לתלמידים מתקשים והפחתת חרדת בחינות",
            "שילוב כלי בינה מלאכותית מבוקרים בהוראה השוטפת"
        ])
    with col_lead2:
        lead_length = st.radio("📏 אורך המכתב:", [
            "תקציר מנהלים ממוקד (עמוד קצר / 2 פסקאות)",
            "מכתב רשמי סטנדרטי (מבנה פדגוגי מלא)",
            "הצעת פרויקט מפורטת (כולל יעדים ושלבי פיילוט)"
        ], index=1, horizontal=True)

    if st.button("📄 נסח מכתב מותאם להנהלה", use_container_width=True):
        with st.spinner("מנסח מכתב רשמי..."):
            prompt_lead = (
                f"נסח מכתב פנייה רשמי ומקצועי למנהלת בית הספר ויועצת השכבה עבור שכבת {chosen_grade}.\n"
                f"הפונה: {st.session_state.user_name} ({st.session_state.user_email}).\n"
                f"נושא הפנייה: פלטפורמת 'The Dan Method'.\n"
                f"מוקד: {lead_focus}.\n"
                f"אורך מבוקש: {lead_length}.\n"
                "הדגש את היתרונות של התאמה למשרד החינוך, הפחתת חרדת בחינות, חיסכון בזמן למורים, והצעת פיילוט התנסותי מדוד."
            )
            res_lead = generate_ai(prompt_lead)
            st.session_state["custom_lead_letter"] = res_lead.text

    letter_display = st.session_state.get("custom_lead_letter", f"""לכבוד: מנהלת בית הספר והיועצת החינוכית
מאת: {st.session_state.user_name}
הנדון: שילוב פלטפורמת 'The Dan Method' ככלי פדגוגי מסייע ללמידה עצמאית והפחתת חרדת בחינות

מערכת The Dan Method פותחה מתוך הבנת האתגרים הייחודיים של תלמידי חטיבת הביניים והחטיבה העליונה בישראל, ומכוילת על פי תוכניות הלימודים ומחווני הבגרות של משרד החינוך.

המערכת מעודדת למידה עצמאית, סוגרת פערים לימודיים, מסייעת בהפחתת חרדת בחינות באמצעות מרחב רווחה ותרגול מודרך, וחוסכת שעות יקרות של הכנת חומרים לצוות ההוראה.

הצעה לפיילוט: קיום התנסות מבוקרת בכיתה אחת לקראת מבחן קרוב למדידת שביעות הרצון וההישגים.""")

    st.markdown(f"""
        <div class="room-content-card">
            <div style="font-size:1.05rem; line-height:1.75; white-space: pre-wrap;">{letter_display}</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(letter_display)}" target="_blank">📲 שתף מכתב להנהלה בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- חדר: רווחה -----------------
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
                <h4 style="margin-top:0; color:#0f2b5c;">טיימר פוקוס עמוק (Deep Focus - Pomodoro)</h4>
                <p style="color:#64748b;">למידה ממוקדת של 25 דקות ללא הסחות דעת:</p>
            </div>
        """, unsafe_allow_html=True)
        
        timer_placeholder = st.empty()
        timer_prog = st.empty()
        
        col_btn_t1, col_btn_t2 = st.columns(2)
        with col_btn_t1:
            start_focus = st.button("▶️ הפעל טיימר פוקוס (25 דקות)", use_container_width=True)
        with col_btn_t2:
            demo_focus = st.button("⚡ דמו מהיר (10 שניות לבדיקה)", use_container_width=True)

        if start_focus:
            total_sec = 25 * 60
            for sec in range(total_sec, 0, -1):
                mins = sec // 60
                secs = sec % 60
                timer_placeholder.markdown(f'<div style="font-size:2.8rem; font-weight:900; color:#0f2b5c; text-align:center; margin-bottom:8px;">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
                timer_prog.progress((total_sec - sec) / total_sec)
                time.sleep(1)
            st.balloons()
            st.success("כל הכבוד! סיימת 25 דקות של פוקוס מושלם.")
        elif demo_focus:
            total_sec = 10
            for sec in range(total_sec, 0, -1):
                mins = sec // 60
                secs = sec % 60
                timer_placeholder.markdown(f'<div style="font-size:2.8rem; font-weight:900; color:#0f2b5c; text-align:center; margin-bottom:8px;">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
                timer_prog.progress((total_sec - sec) / total_sec)
                time.sleep(1)
            st.balloons()
            st.success("בדיקת טיימר הושלמה בהצלחה!")
        else:
            timer_placeholder.markdown('<div style="font-size:2.8rem; font-weight:900; color:#0f2b5c; text-align:center; margin-bottom:8px;">25:00</div>', unsafe_allow_html=True)

# ----------------- שאר החדרים -----------------
elif st.session_state.current_room == "מערכי שיעור" and st.session_state.user_role == "מורה":
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

elif st.session_state.current_room == "בחנים ומחוונים" and st.session_state.user_role == "מורה":
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
                prompt = f"תוכנית חירום לתלמיד {st.session_state.user_name} ב-{student_context}. מקצוע: {panic_sub}, חומר: {panic_top}, שעות: {hours_left}. 3 מושגי חובה, טריק הבחינה ומשפט פתיחה למאיות."
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
