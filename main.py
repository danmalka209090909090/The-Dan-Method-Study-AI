import streamlit as st
from google import genai
from PIL import Image
import requests
from io import BytesIO
import json
import re
import time
import datetime
import urllib.parse

# הגנה מפני קריסה אם python-pptx לא מותקן בענן
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    PPTX_READY = True
except ImportError:
    PPTX_READY = False

TEACHER_ACCESS_CODE = "DAN100"

st.set_page_config(
    page_title="The Dan Method | לומדים. מתקדמים.",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# שפת עיצוב עמידה ללא סיידבר
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    * { box-sizing: border-box; }

    /* העלמת הסיידבר לחלוטין כדי למנוע טקסט שקוף צף */
    [data-testid="stSidebar"], 
    section[data-testid="stSidebar"],
    div[data-testid="stSidebarCollapsedControl"],
    .stSidebar {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
        position: absolute !important;
        left: -99999px !important;
    }

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
        max-width: 1120px;
        margin: 0 auto;
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
        white-space: nowrap;
    }
    .brand-main-name {
        font-size: 1.3rem;
        font-weight: 900;
        color: #0f2b5c;
        line-height: 1.1;
    }
    .brand-sub-badge {
        font-size: 0.72rem;
        font-weight: 800;
        color: #2563eb;
        line-height: 1.1;
    }

    /* Hero Banner */
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

    /* כרטיסיית חדר מורים ייעודי */
    .teacher-profile-card {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 14px;
    }
    .teacher-avatar-circle {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        margin: 0 auto 10px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
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

    /* סיפור השיטה */
    .story-card {
        background: linear-gradient(135deg, #0f2b5c 0%, #1e3a8a 100%);
        color: #ffffff;
        border-radius: 20px;
        padding: 24px 26px;
        margin-bottom: 22px;
        box-shadow: 0 8px 25px rgba(15, 43, 92, 0.12);
        width: 100%;
        display: block;
    }
    .story-title {
        font-size: 1.45rem;
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
        margin-bottom: 26px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
        overflow-x: auto;
        width: 100%;
    }
    .compare-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 14px;
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
        padding: 13px 12px;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.95rem;
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

    /* כרטיסיות חדרים */
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
        font-size: 1.02rem;
        font-weight: 800;
        color: #0f2b5c;
    }
    .room-tile p {
        font-size: 0.8rem;
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

    /* כפתורי מערכת מחוברים וקריאים */
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
if "subject_teacher_chat" not in st.session_state:
    st.session_state.subject_teacher_chat = []
if "mock_exam_data" not in st.session_state:
    st.session_state.mock_exam_data = None
if "slides_data" not in st.session_state:
    st.session_state.slides_data = None
if "saved_vault" not in st.session_state:
    st.session_state.saved_vault = []
if "streak_count" not in st.session_state:
    st.session_state.streak_count = 3
if "exam_scores_history" not in st.session_state:
    st.session_state.exam_scores_history = [78, 85, 92]
if "exam_start_time" not in st.session_state:
    st.session_state.exam_start_time = None
if "chosen_grade" not in st.session_state:
    st.session_state.chosen_grade = "כיתה ט'"
if "math_units" not in st.session_state:
    st.session_state.math_units = "הקבצה א' / מצוינות"
if "chosen_major" not in st.session_state:
    st.session_state.chosen_major = "ללא מגמה (מקצועות ליבה)"
if "no_yap" not in st.session_state:
    st.session_state.no_yap = True
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "השליף חירום סגר לי את החומר לפני המבחן בהיסטוריה, הציל לי 20 נקודות."},
        {"name": "נועה ל.", "grade": "כיתה י\"א (ביולוגיה)", "rating": 5, "text": "האתר נראה יוקרתי, נקי מכל השטויות ובאמת מדבר בגובה העיניים."},
        {"name": "מאיה ר.", "grade": "כיתה י\"א (5 יח')", "rating": 5, "text": "מפרק המתמטיקה ומכתב הערעור זה גאונות. המורה החזירה לי 9 נקודות!"}
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
        try:
            res = client.models.generate_content(model=m, contents=contents)
            return res.text
        except Exception as e:
            last_err = e
            time.sleep(0.5)
            continue
    return f"שגיאה בתקשורת עם ה-AI: {last_err}"

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

def build_pptx_file(slides_data, topic_name):
    if not PPTX_READY:
        return None
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)
    blank_layout = prs.slide_layouts[6]

    for s in slides_data:
        slide = prs.slides.add_slide(blank_layout)
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(8.4), Inches(1))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"{s.get('slide_num', '')}. {s.get('title', '')}"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = RGBColor(15, 43, 92)

        body_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(8.4), Inches(3.2))
        bf = body_box.text_frame
        bf.word_wrap = True
        for bullet in s.get("bullets", []):
            bp = bf.add_paragraph()
            bp.text = f"• {bullet}"
            bp.font.size = Pt(18)
            bp.font.color.rgb = RGBColor(51, 65, 85)

        if "speaker_notes" in s and s["speaker_notes"]:
            notes_slide = slide.notes_slide
            tf_notes = notes_slide.notes_text_frame
            tf_notes.text = s["speaker_notes"]

    bio = BytesIO()
    prs.save(bio)
    bio.seek(0)
    return bio

anti_yap_rule = "השב ישירות לתכל'ס, ללא חפירות." if st.session_state.no_yap else ""
student_context = f"שכבת לימוד: {st.session_state.chosen_grade}, מתמטיקה: {st.session_state.math_units}, מגמה: {st.session_state.chosen_major}."

# סרגל ניווט עליון
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

# הגדרת פרופיל נקייה
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

# הגנת חדר מורים
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

    query_search = st.text_input("🔍 שאל שאלה מהירה את דן AI:", placeholder="למשל: 'איך גוזרים פונקציה?', 'משפט חוצה זווית'...")
    if query_search.strip():
        with st.spinner("דן AI מנסח תשובה..."):
            ans_text = generate_ai(f"אתה עוזר לימודי אישי חכם. הקשר: {student_context}. ענה ישירות, קצר ולעניין: {query_search}. {anti_yap_rule}")
            st.markdown(f"""
                <div class="clean-box" style="border-right: 4px solid #3b82f6;">
                    <h4 style="margin: 0; color: #1e3a8a;">💡 מענה מהיר של דן AI:</h4>
                    <p style="margin-top: 8px;">{ans_text}</p>
                </div>
            """, unsafe_allow_html=True)
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(ans_text)}" target="_blank">📲 שתף בוואטסאפ</a>', unsafe_allow_html=True)
            with col_act2:
                if st.button("💾 שמור לכספת שלי", key="save_fast_ans"):
                    st.session_state.saved_vault.append({"title": f"מענה: {query_search}", "content": ans_text})
                    st.success("נשמר בכספת בהצלחה!")

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

    # סיפור השיטה
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

    # טבלת השוואה
    st.markdown("""
        <div class="compare-container">
            <h3 style="margin-top: 0; color: #0f2b5c; font-size: 1.3rem; font-weight: 800;">למה The Dan Method ולא סתם בינה מלאכותית רגילה?</h3>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 20px;">מודלים רגילים לא מכירים את בתי הספר בישראל ומבזבזים לך זמן. הנה ההבדל:</p>
            <table class="compare-table">
                <thead>
                    <tr>
                        <th style="width: 32%;">תכונה</th>
                        <th style="width: 34%; color: #1e3a8a;">The Dan Method 🎓</th>
                        <th style="width: 34%;">כלי בינה מלאכותית רגיל</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="font-weight: 600;">התאמה למערכת החינוך</td>
                        <td style="color: #16a34a; font-weight: 700;">מכויל בול לפי מחווני בגרות, הקבצות וכיתות ז'-י"ב בישראל</td>
                        <td style="color: #64748b;">תשובות גנריות באנגלית שתורגמו, לא מכיר מחווני בדיקה</td>
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

    # מרכז החדרים
    header_text = "מרכז הלמידה של התלמיד" if st.session_state.app_mode == "תלמיד" else "מרכז הכלים למורים וצוות"
    st.markdown(f"""
        <div class="dashboard-header-container">
            <h2 class="dashboard-header-title">{header_text}</h2>
            <span class="dashboard-header-subtitle">בחר כלי כדי להתחיל</span>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.app_mode == "תלמיד":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="room-tile cat-pink"><div style="font-size:28px;">📊</div><h4>מחולל מצגות</h4><p>שקופיות והורדת PPTX</p></div>', unsafe_allow_html=True)
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

        c4, c5, c6 = st.columns(3)
        with c4:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:28px;">📝</div><h4>סימולטור מבחן</h4><p>טיימר וציון עם מחוון</p></div>', unsafe_allow_html=True)
            if st.button("בניית מבחן עם טיימר", key="btn_exam_t", use_container_width=True):
                st.session_state.current_room = "מבחני דמה"
                st.rerun()
        with c5:
            st.markdown('<div class="room-tile cat-red"><div style="font-size:28px;">🆘</div><h4>חילוץ ב-3 בלילה</h4><p>תוכנית הצלה דחופה למחר</p></div>', unsafe_allow_html=True)
            if st.button("הפעלת חילוץ לילה", key="btn_panic_t", use_container_width=True):
                st.session_state.current_room = "חילוץ לילה"
                st.rerun()
        with c6:
            st.markdown('<div class="room-tile cat-yellow"><div style="font-size:28px;">🚨</div><h4>שליף חירום</h4><p>60 שניות לפני הכיתה</p></div>', unsafe_allow_html=True)
            if st.button("הצגת שליף חירום", key="btn_cheat_t", use_container_width=True):
                st.session_state.current_room = "שליף חירום"
                st.rerun()

        c7, c8, c9 = st.columns(3)
        with c7:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:28px;">🩻</div><h4>רנטגן שגיאות</h4><p>חשיפת מלכודות הבוחנים</p></div>', unsafe_allow_html=True)
            if st.button("גילוי מלכודות", key="btn_xray_t", use_container_width=True):
                st.session_state.current_room = "רנטגן"
                st.rerun()
        with c8:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:28px;">⚖️</div><h4>מכתב ערעור</h4><p>החזרת נקודות ממורים</p></div>', unsafe_allow_html=True)
            if st.button("ניסוח מכתב ערעור", key="btn_appeal_t", use_container_width=True):
                st.session_state.current_room = "ערעור"
                st.rerun()
        with c9:
            st.markdown('<div class="room-tile cat-orange"><div style="font-size:28px;">📐</div><h4>מעבדת מתמטיקה LaTeX</h4><p>פירוק שלב-אחר-שלב ונוסחאות</p></div>', unsafe_allow_html=True)
            if st.button("פירוק תרגיל מתמטי", key="btn_math_t", use_container_width=True):
                st.session_state.current_room = "מעבדת מתמטיקה"
                st.rerun()

        c10, c11, c12 = st.columns(3)
        with c10:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:28px;">🎴</div><h4>כרטיסיות חזרה</h4><p>שינון מושגים מהיר</p></div>', unsafe_allow_html=True)
            if st.button("פתיחת כרטיסיות", key="btn_flash_t", use_container_width=True):
                st.session_state.current_room = "כרטיסיות"
                st.rerun()
        with c11:
            st.markdown('<div class="room-tile cat-teal"><div style="font-size:28px;">🧘</div><h4>רווחה והפחתת לחץ</h4><p>נשימות ופוקוס עמוק</p></div>', unsafe_allow_html=True)
            if st.button("מרחב רווחה", key="btn_well_t", use_container_width=True):
                st.session_state.current_room = "רווחה"
                st.rerun()
        with c12:
            st.markdown('<div class="room-tile cat-orange"><div style="font-size:28px;">🎯</div><h4>מחשבון בגרות</h4><p>חיזוי הציון הסופי והמגן</p></div>', unsafe_allow_html=True)
            if st.button("חישוב ציון יעד", key="btn_calc_t", use_container_width=True):
                st.session_state.current_room = "מחשבון"
                st.rerun()

        # שורות הפיצ'רים החדשים
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("⚡ כלי למידה ותרגול מתקדמים (חדש!)")

        n1, n2, n3 = st.columns(3)
        with n1:
            st.markdown('<div class="room-tile cat-red"><div style="font-size:28px;">⚔️</div><h4>דו-קרב ידע 1-על-1</h4><p>תחרות שאלות מהירה מול חבר</p></div>', unsafe_allow_html=True)
            if st.button("פתח דו-קרב", key="btn_battle", use_container_width=True):
                st.session_state.current_room = "דו קרב"
                st.rerun()
        with n2:
            st.markdown(f'<div class="room-tile cat-yellow"><div style="font-size:28px;">🔥</div><h4>אתגר בוקר ורצף ({st.session_state.streak_count} ימים)</h4><p>שאלת חידוד יומית קצרה</p></div>', unsafe_allow_html=True)
            if st.button("פתור אתגר יומי", key="btn_streak", use_container_width=True):
                st.session_state.current_room = "רצף יומי"
                st.rerun()
        with n3:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:28px;">🗣️</div><h4>בגרות בעל פה COBE</h4><p>סימולציית ראיון באנגלית</p></div>', unsafe_allow_html=True)
            if st.button("התחל ראיון באנגלית", key="btn_cobe", use_container_width=True):
                st.session_state.current_room = "בגרות בעל פה"
                st.rerun()

        n4, n5, n6 = st.columns(3)
        with n4:
            st.markdown('<div class="room-tile cat-green"><div style="font-size:28px;">📈</div><h4>אוצר מילים Band 3</h4><p>מילות מפתח לבגרות באנגלית</p></div>', unsafe_allow_html=True)
            if st.button("תרגל אוצר מילים", key="btn_band3", use_container_width=True):
                st.session_state.current_room = "אוצר מילים"
                st.rerun()
        with n5:
            st.markdown('<div class="room-tile cat-indigo"><div style="font-size:28px;">🔍</div><h4>רדאר מקורות וציטוטים</h4><p>ביבליוגרפיה תקנית לעבודות</p></div>', unsafe_allow_html=True)
            if st.button("בנה ביבליוגרפיה", key="btn_sources", use_container_width=True):
                st.session_state.current_room = "ביבליוגרפיה"
                st.rerun()
        with n6:
            st.markdown('<div class="room-tile cat-pink"><div style="font-size:28px;">✍️</div><h4>בודק פסקאות טיעון</h4><p>בדיקה לפי מחוון לשון</p></div>', unsafe_allow_html=True)
            if st.button("בדוק פסקת טיעון", key="btn_arg", use_container_width=True):
                st.session_state.current_room = "פסקת טיעון"
                st.rerun()

        n7, n8, n9 = st.columns(3)
        with n7:
            st.markdown('<div class="room-tile cat-teal"><div style="font-size:28px;">⏱️</div><h4>פומודורו מודרך</h4><p>טיימר עם הגדרת מטרת פוקוס</p></div>', unsafe_allow_html=True)
            if st.button("הפעל פומודורו", key="btn_pomo", use_container_width=True):
                st.session_state.current_room = "פומודורו"
                st.rerun()
        with n8:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:28px;">🎥</div><h4>חילוץ מ-YouTube</h4><p>שאלות תרגול מסרטון הסבר</p></div>', unsafe_allow_html=True)
            if st.button("חלץ שאלות מסרטון", key="btn_yt", use_container_width=True):
                st.session_state.current_room = "יוטיוב"
                st.rerun()
        with n9:
            st.markdown('<div class="room-tile cat-orange"><div style="font-size:28px;">📑</div><h4>שאלות בגרות דומות</h4><p>איתור שאלה מקבילה מבגרות</p></div>', unsafe_allow_html=True)
            if st.button("אתר שאלת בגרות", key="btn_past_exam", use_container_width=True):
                st.session_state.current_room = "בגרות מקבילה"
                st.rerun()

        n10, n11, n12 = st.columns(3)
        with n10:
            st.markdown('<div class="room-tile cat-slate"><div style="font-size:28px;">🎧</div><h4>פודקאסט 3 דקות</h4><p>הסבר מוקלט קליל לכל נושא</p></div>', unsafe_allow_html=True)
            if st.button("צור פודקאסט קצר", key="btn_pod", use_container_width=True):
                st.session_state.current_room = "פודקאסט"
                st.rerun()
        with n11:
            st.markdown('<div class="room-tile cat-red"><div style="font-size:28px;">🗺️</div><h4>מפת חולשות אישית</h4><p>איפה אתה מאבד נקודות</p></div>', unsafe_allow_html=True)
            if st.button("צפה במפת חולשות", key="btn_heatmap", use_container_width=True):
                st.session_state.current_room = "מפת חולשות"
                st.rerun()
        with n12:
            st.markdown('<div class="room-tile cat-blue"><div style="font-size:28px;">🖨️</div><h4>כרטיסי כיס מודפסים</h4><p>עמוד לגזירה בבוקר המבחן</p></div>', unsafe_allow_html=True)
            if st.button("הדפס כרטיסי כיס", key="btn_pocket", use_container_width=True):
                st.session_state.current_room = "כרטיסי כיס"
                st.rerun()

    # מצב מורה וצוות
    else:
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

        tm1, tm2, tm3 = st.columns(3)
        with tm1:
            st.markdown('<div class="room-tile cat-yellow"><div style="font-size:28px;">🎲</div><h4>מחולל Kahoot & Quizizz</h4><p>שאלות ומסיחים להעתקה ישירה</p></div>', unsafe_allow_html=True)
            if st.button("ייצר משחק Kahoot", key="btn_kahoot", use_container_width=True):
                st.session_state.current_room = "קהוט"
                st.rerun()
        with tm2:
            st.markdown('<div class="room-tile cat-teal"><div style="font-size:28px;">💬</div><h4>הודעות להורים ולווטסאפ</h4><p>ניסוח מנומס ומדויק לכיתה</p></div>', unsafe_allow_html=True)
            if st.button("נסח הודעה להורים", key="btn_parents", use_container_width=True):
                st.session_state.current_room = "הודעות הורים"
                st.rerun()
        with tm3:
            st.markdown('<div class="room-tile cat-purple"><div style="font-size:28px;">📝</div><h4>הערכות לתעודה</h4><p>ניסוח אישי, חם ומנומק</p></div>', unsafe_allow_html=True)
            if st.button("נסח הערכה לתעודה", key="btn_report", use_container_width=True):
                st.session_state.current_room = "הערכות תעודה"
                st.rerun()

    # הכספת האישית
    if st.session_state.saved_vault:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📦 הכספת האישית שלך (חומרים שמורים)")
        for idx, item in enumerate(st.session_state.saved_vault):
            with st.expander(f"📌 {item['title']}"):
                st.write(item["content"])
                st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(item["content"])}" target="_blank">📲 שתף חומר שמור</a>', unsafe_allow_html=True)

    # ביקורות
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
            fb_grade = st.selectbox("תפקיד / כיתה:", ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב", "מורה מקצועי"], index=2)
            fb_rating = st.slider("דירוג (כוכבים):", 1, 5, 5)
            fb_text = st.text_area("איך הפלטפורמה עזרה לך?")
            if st.form_submit_button("שלח חוות דעת 🚀"):
                if fb_text.strip():
                    st.session_state.reviews.insert(0, {
                        "name": fb_name.strip() if fb_name.strip() else "אנונימי",
                        "grade": fb_grade,
                        "rating": fb_rating,
                        "text": fb_text.strip()
                    })
                    st.success("תודה! חוות הדעת נוספה בהצלחה.")
                    st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- 1. דו-קרב 1-על-1 -----------------
elif st.session_state.current_room == "דו קרב":
    st.title("⚔️ זירת דו-קרב ידע 1-על-1")
    st.caption("תחרות שאלות מהירה מול חבר או מול ה-AI על חומר המבחן.")
    b_topic = st.text_input("נושא הקרב:", placeholder="למשל: חוקי ניוטון, מושגים באזרחות, נוסחאות גזירה")
    if st.button("התחל דו-קרב עכשיו 🥊", use_container_width=True) and b_topic:
        with st.spinner("מכין שאלות קרב..."):
            prompt_battle = f"צור 3 שאלות רב-ברירה מהירות ברמת תחרות בנושא {b_topic} עבור {student_context}. לכל שאלה 4 אפשרויות ותשובה נכונה מודגשת."
            res_battle = generate_ai(prompt_battle)
            st.markdown(f'<div class="clean-box">{res_battle}</div>', unsafe_allow_html=True)

# ----------------- 2. אתגר בוקר ורצף -----------------
elif st.session_state.current_room == "רצף יומי":
    st.title("🔥 אתגר בוקר יומי (חידוד מוח של 60 שניות)")
    st.info(f"הרצף הנוכחי שלך: {st.session_state.streak_count} ימי למידה ברצף! שמור עליו פעיל.")
    if st.button("שלוף שאלת אתגר יומית ⚡", use_container_width=True):
        with st.spinner("שולף שאלה..."):
            prompt_streak = f"צור שאלת אתגר יומית אחת ממוקדת ברמת מבחן/בגרות עבור {student_context} עם 4 מסיחים ותשובה נכונה מנומקת."
            res_streak = generate_ai(prompt_streak)
            st.markdown(f'<div class="clean-box">{res_streak}</div>', unsafe_allow_html=True)

# ----------------- 3. בגרות בעל פה באנגלית COBE -----------------
elif st.session_state.current_room == "בגרות בעל פה":
    st.title("🗣️ סימולטור בגרות בעל פה באנגלית (COBE)")
    st.caption("תרגול שיחה ומענה לבוחן בגרות על הפרויקט ונושאים אישיים.")
    proj_topic = st.text_input("What is your Bagrut Project about?", placeholder="e.g., Artificial Intelligence, Climate Change, Volunteer work")
    if st.button("Start COBE Simulation 🎙️", use_container_width=True) and proj_topic:
        with st.spinner("Examiner is preparing questions..."):
            prompt_cobe = f"You are an official Israeli Bagrut COBE examiner. Give 3 structured questions to the student about their project: '{proj_topic}', along with tips on key vocabulary and transition words they should use."
            res_cobe = generate_ai(prompt_cobe)
            st.markdown(f'<div class="clean-box">{res_cobe}</div>', unsafe_allow_html=True)

# ----------------- 4. אוצר מילים Band 3 -----------------
elif st.session_state.current_room == "אוצר מילים":
    st.title("📈 מאמן אוצר מילים לבגרות (Band 2 & Band 3)")
    st.caption("5 מילות חובה של משרד החינוך בכל אימון עם משפטי השלמה.")
    if st.button("הפק 5 מילות מפתח יומיות 🇬🇧", use_container_width=True):
        with st.spinner("מחלץ מילים ממאגר משרד החינוך..."):
            prompt_voc = f"Give 5 essential vocabulary words from the Israeli Ministry of Education Band 3 list for high-school students ({student_context}). Include: Hebrew translation, example sentence, and a short fill-in-the-blank test."
            res_voc = generate_ai(prompt_voc)
            st.markdown(f'<div class="clean-box">{res_voc}</div>', unsafe_allow_html=True)

# ----------------- 5. רדאר מקורות וציטוטים -----------------
elif st.session_state.current_room == "ביבליוגרפיה":
    st.title("🔍 רדאר מקורות וביבליוגרפיה תקנית")
    st.caption("הזן נושא לעבודת חקר וקבל מקורות מהימנים וציטוטים לפי כללי משרד החינוך.")
    paper_topic = st.text_input("נושא עבודת החקר:", placeholder="למשל: השפעת הרשתות החברתיות על בני נוער, מלחמת העצמאות")
    if st.button("בנה ביבליוגרפיה וראשי פרקים 📚", use_container_width=True) and paper_topic:
        with st.spinner("מאתר מקורות ומנסח ציטוטים..."):
            prompt_src = f"הצע 3 מקורות מידע מהימנים בעברית (ספר, מאמר, אתר מוסמך) ונסח עבורם ציטוט ביבליוגרפי תקני (APA/משרד החינוך) בנושא: {paper_topic}. בנוסף, הצע 3 ראשי פרקים לעבודה."
            res_src = generate_ai(prompt_src)
            st.markdown(f'<div class="clean-box">{res_src}</div>', unsafe_allow_html=True)

# ----------------- 6. בודק פסקאות טיעון -----------------
elif st.session_state.current_room == "פסקת טיעון":
    st.title("✍️ בודק פסקאות טיעון בלשון והבעה")
    st.caption("בדיקת טקסט לפי מחוון לשון: טענה, נימוק, דוגמה, מילות קישור תקינות וסיום.")
    arg_text = st.text_area("הדבק כאן את פסקת הטיעון שלך:", height=150)
    if st.button("בדוק פסקת טיעון 📝", use_container_width=True) and arg_text:
        with st.spinner("בודק לפי מחוון משרד החינוך..."):
            prompt_arg = f"בדוק את פסקת הטיעון הבאה לפי מחוון הבגרות בלשון והבעה: טענה, נימוק, הרחבה/דוגמה, מילות קישור, פיסוק וסיום. תן ציון מתוך 100 והצע נוסח מתוקן של 100:\n\n{arg_text}"
            res_arg = generate_ai(prompt_arg)
            st.markdown(f'<div class="clean-box">{res_arg}</div>', unsafe_allow_html=True)

# ----------------- 7. פומודורו מודרך -----------------
elif st.session_state.current_room == "פומודורו":
    st.title("⏱️ טיימר פומודורו מודרך עם שאלת פוקוס")
    pomo_goal = st.text_input("מה המטרה היחידה שלך ל-25 הדקות הקרובות?", placeholder="למשל: לפתור 3 תרגילים בהסתברות")
    st.markdown('<div class="clean-box" style="text-align:center;"><h1 style="font-size:3.5rem; color:#0f2b5c;">25:00</h1><p>שים את הטלפון על מצב טיסה והתחל במטרה.</p></div>', unsafe_allow_html=True)
    if st.button("סיימתי סבב פומודורו! בדוק אותי 🎯", use_container_width=True) and pomo_goal:
        prompt_pomo = f"התלמיד הגדיר מטרה: '{pomo_goal}' וסיים סבב פומודורו. שאל אותו שאלת ביקורת מהירה אחת לבדוק שהוא באמת שולט במה שלמד, ותן טיפ להמשך."
        res_pomo = generate_ai(prompt_pomo)
        st.markdown(f'<div class="clean-box">{res_pomo}</div>', unsafe_allow_html=True)

# ----------------- 8. חילוץ מ-YouTube -----------------
elif st.session_state.current_room == "יוטיוב":
    st.title("🎥 מחלץ שאלות ותרגול מסרטון YouTube")
    yt_topic = st.text_input("נושא הסרטון או מושג שנלמד בו:", placeholder="למשל: משפט פיתגורס, אימפריאליזם, חוק שני של ניוטון")
    if st.button("חלץ שאלות מפתח ותרגול ⚡", use_container_width=True) and yt_topic:
        with st.spinner("מחלץ שאלות מפתח..."):
            prompt_yt = f"בהתבסס על נושא השיעור/הסרטון '{yt_topic}' עבור {student_context}, חלץ: 3 שאלות הבנה מרכזיות, 1 שאלת אתגר למבחן ותשובות קצרות לתכל'ס."
            res_yt = generate_ai(prompt_yt)
            st.markdown(f'<div class="clean-box">{res_yt}</div>', unsafe_allow_html=True)

# ----------------- 9. שאלות בגרות מקבילות -----------------
elif st.session_state.current_room == "בגרות מקבילה":
    st.title("📑 רדאר שאלות בגרות מקבילות")
    st.caption("הזן תרגיל משיעורי הבית וקבל שאלה במבנה זהה מתוך מבחני בגרות רשמיים.")
    hw_q = st.text_area("הזן שאלה או תרגיל משיעורי הבית:", height=100)
    if st.button("אתר שאלת בגרות מקבילה 🎯", use_container_width=True) and hw_q:
        with st.spinner("מאתר שאלה מקבילה..."):
            prompt_past = f"בהתבסס על התרגיל הבא: '{hw_q}' עבור {student_context}, הצג שאלה במבנה זהה לחלוטין כפי שהיא מופיעה בבחינות בגרות אמיתיות, והסבר את העיקרון שמאחוריה."
            res_past = generate_ai(prompt_past)
            st.markdown(f'<div class="clean-box">{res_past}</div>', unsafe_allow_html=True)

# ----------------- 10. פודקאסט 3 דקות -----------------
elif st.session_state.current_room == "פודקאסט":
    st.title("🎧 פודקאסט לימודי קצר (3 דקות)")
    st.caption("הסבר מבואר בגובה העיניים להאזנה בדרך לבית הספר.")
    pod_topic = st.text_input("נושא הפודקאסט:", placeholder="למשל: הסכם ריבנטרופ-מולוטוב, פונקציות טריגונומטריות")
    if st.button("הפק תסריט פודקאסט קליל 🎙️", use_container_width=True) and pod_topic:
        with st.spinner("יוצר תסריט פודקאסט..."):
            prompt_pod = f"כתוב תסריט פודקאסט קליל של 3 דקות בין שני מנחים (דן ומיה) שמסבירים בגובה העיניים, בשפה זורמת וברורה ללא חפירות, את הנושא: {pod_topic} עבור {student_context}."
            res_pod = generate_ai(prompt_pod)
            st.markdown(f'<div class="clean-box">{res_pod}</div>', unsafe_allow_html=True)

# ----------------- 11. מפת חולשות -----------------
elif st.session_state.current_room == "מפת חולשות":
    st.title("🗺️ מפת חולשות ומוקדי שיפור אישיים")
    st.caption("ניתוח התחומים בהם יש נטייה לאבד נקודות והמלצה לחיזוק.")
    sub_for_map = st.selectbox("בחר מקצוע לבדיקה:", ["מתמטיקה", "אנגלית", "היסטוריה", "אזרחות", "לשון והבעה"])
    if st.button("חשב מפת חולשות והמלצות ⚡", use_container_width=True):
        with st.spinner("מנתח מוקדי כשל..."):
            prompt_map = f"הצג לתלמיד ב-{student_context} ב{sub_for_map} פירוט של 3 הנושאים שבהם רוב התלמידים מאבדים הכי הרבה נקודות (מוקדי חולשה), יחד עם תרגיל חיזוק קצר וממוקד לכל אחד."
            res_map = generate_ai(prompt_map)
            st.markdown(f'<div class="clean-box">{res_map}</div>', unsafe_allow_html=True)

# ----------------- 12. כרטיסי כיס מודפסים -----------------
elif st.session_state.current_room == "כרטיסי כיס":
    st.title("🖨️ מחולל כרטיסי כיס מודפסים לבוקר המבחן")
    st.caption("עמוד A4 המחולק ל-4 כרטיסים קטנים שגוזרים ושומרים בקלמר בבוקר המבחן.")
    p_topic = st.text_input("נושא המבחן:", placeholder="למשל: נוסחאות פיזיקה מכניקה, מושגי יסוד באזרחות")
    if st.button("ייצר 4 כרטיסי כיס לגזירה 📄", use_container_width=True) and p_topic:
        with st.spinner("מייצר כרטיסים מעוצבים..."):
            prompt_pkt = f"צור 4 כרטיסי כיס קצרים, מדויקים וחדים (כרטיס 1, 2, 3, 4) בנושא: {p_topic} עבור {student_context}. כל כרטיס יכלול רק נוסחאות ברזל ומשפטי חובה שחייבים לזכור בבוקר המבחן."
            res_pkt = generate_ai(prompt_pkt)
            st.markdown(f'<div class="clean-box">{res_pkt}</div>', unsafe_allow_html=True)

# ----------------- 13. מחולל Kahoot & Quizizz (מורה) -----------------
elif st.session_state.current_room == "קהוט":
    st.title("🎲 מחולל חידונים ל-Kahoot ו-Quizizz")
    st.caption("כלי למורים: הפקת שאלות ומסיחים מוכנים להעתקה מהירה למשחקי כיתה.")
    k_topic = st.text_input("נושא החידון:", placeholder="למשל: מהפכה תעשייתית, אוצר מילים באנגלית, גיאומטריה")
    k_q_count = st.slider("מספר שאלות:", 3, 10, 5)
    if st.button("ייצר שאלות ל-Kahoot 🎮", use_container_width=True) and k_topic:
        with st.spinner("מכין שאלות ומסיחים..."):
            prompt_kahoot = f"צור חידון של {k_q_count} שאלות עבור משחק Kahoot בנושא: {k_topic} עבור כיתה {chosen_grade}. הצג בפורמט: שאלה, 4 תשובות (סמן את הנכונה), והסבר קצר של שורה אחת."
            res_kahoot = generate_ai(prompt_kahoot)
            st.markdown(f'<div class="clean-box">{res_kahoot}</div>', unsafe_allow_html=True)

# ----------------- 14. הודעות להורים ולווטסאפ (מורה) -----------------
elif st.session_state.current_room == "הודעות הורים":
    st.title("💬 מנסח הודעות להורים ולווטסאפ הכיתתי")
    st.caption("כלי למורים: ניסוח הודעות מנומסות, בהירות ומכובדות.")
    msg_type = st.selectbox("סוג ההודעה:", ["תזכורת למבחן וטיפים ללמידה בבית", "הודעת עידוד על שיפור והשקעה", "עדכון על חוסר ציוד או משימות"])
    msg_details = st.text_input("פרטים להודעה:", placeholder="למשל: מבחן בהיסטוריה ביום שלישי, חומר פרקים 2-4")
    if st.button("נסח הודעה רשמית להורים 📲", use_container_width=True):
        prompt_msg = f"נסח הודעת וואטסאפ מנומסת, ברורה ומכבדת ממורה להורי כיתה {chosen_grade}. סוג ההודעה: {msg_type}. פרטים: {msg_details}."
        res_msg = generate_ai(prompt_msg)
        st.markdown(f'<div class="clean-box">{res_msg}</div>', unsafe_allow_html=True)
        st.markdown(f'<a class="whatsapp-btn" href="{get_whatsapp_share_link(res_msg)}" target="_blank">📲 העתק ושתף בוואטסאפ</a>', unsafe_allow_html=True)

# ----------------- 15. הערכות אישיות לתעודה (מורה) -----------------
elif st.session_state.current_room == "הערכות תעודה":
    st.title("📝 מחולל הערכות אישיות לתעודה")
    st.caption("כלי למורים: ניסוח הערכה פדגוגית חמה, מנומקת ומעצימה לתעודה.")
    st_name = st.text_input("שם התלמיד/ה:", placeholder="למשל: דן, מאיה")
    st_traits = st.multiselect("מאפיינים בולטים:", ["השתתפות פעילה", "שיפור ניכר בציונים", "עזרה לחברים", "התמדה והשקעה", "חשיבה יצירתית", "זקוק/ה לחיזוק בהכנת שיעורים"], default=["התמדה והשקעה", "שיפור ניכר בציונים"])
    st_subject = st.text_input("מקצוע:", value="מתמטיקה")
    if st.button("נסח הערכה מעצימה לתעודה 🎓", use_container_width=True) and st_name:
        prompt_rep = f"נסח הערכה אישית, פדגוגית ומעצימה לתעודת סוף מחצית/שנה עבור התלמיד/ה {st_name} במקצוע {st_subject} (כיתה {chosen_grade}). מאפיינים: {', '.join(st_traits)}. כתוב בגובה העיניים, בצורה מפרגנת שמצביעה על החוזקות ומעודדת להמשך הצלחה."
        res_rep = generate_ai(prompt_rep)
        st.markdown(f'<div class="clean-box">{res_rep}</div>', unsafe_allow_html=True)

# ----------------- החדרים הקודמים שנותרו -----------------
elif st.session_state.current_room == "מצגות":
    st.title("📊 מחולל מצגות מקצועי")
    topic = st.text_input("נושא המצגת:")
    if st.button("בנה מצגת", use_container_width=True) and topic:
        with st.spinner("בונה מצגת..."):
            res = generate_ai(f"שלד מצגת 5 שקופיות בנושא {topic} עבור {student_context}")
            st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "חדר זום":
    st.title("📹 שיעור פרטי בזום")
    txt = st.chat_input("שאל את המורה...")
    if txt:
        res = generate_ai(f"אתה מורה פרטי. תלמיד: {student_context}. ענה על: {txt}")
        st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "סורק תמונות":
    st.title("📸 סורק תרגילים")
    f = st.file_uploader("תמונה:", type=["png", "jpg", "jpeg"])
    if f and st.button("פתור"):
        res = generate_ai([f"פתור צעד אחרי צעד עבור {student_context}", Image.open(f)])
        st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "מבחני דמה":
    st.title("📝 סימולטור מבחן")
    top = st.text_input("נושא:")
    if top and st.button("ייצר מבחן"):
        res = generate_ai(f"צור מבחן קצר של 3 שאלות ומחוון בדיקה בנושא {top} עבור {student_context}")
        st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "חילוץ לילה":
    st.title("🆘 חילוץ ב-3 בלילה")
    top = st.text_input("נושא:")
    if top and st.button("הצל אותי"):
        res = generate_ai(f"תוכנית הצלה דחופה לפני מבחן בנושא {top} עבור {student_context}")
        st.markdown(f'<div class="panic-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "שליף חירום":
    st.title("🚨 שליף חירום")
    top = st.text_input("נושא:")
    if top and st.button("הצג שליף"):
        res = generate_ai(f"שליף של 60 שניות בנושא {top} עבור {student_context}")
        st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "רנטגן":
    st.title("🩻 רנטגן שגיאות")
    top = st.text_input("נושא:")
    if top and st.button("חשוף מלכודות"):
        res = generate_ai(f"מלכודות בוחנים בנושא {top} עבור {student_context}")
        st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "ערעור":
    st.title("⚖️ מכתב ערעור")
    q = st.text_input("על מה ירדו נקודות?")
    if q and st.button("נסח ערעור"):
        res = generate_ai(f"מכתב ערעור מנומק למורה על: {q} עבור {student_context}")
        st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "מעבדת מתמטיקה":
    st.title("📐 מעבדת מתמטיקה LaTeX")
    q = st.text_area("משוואה:")
    if q and st.button("פתור"):
        res = generate_ai(f"פתור עם נוסחאות LaTeX תקניות עבור {student_context}: {q}")
        st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "כרטיסיות":
    st.title("🎴 כרטיסיות חזרה")
    top = st.text_input("נושא:")
    if top and st.button("ייצר כרטיסיות"):
        res = generate_ai(f"4 כרטיסיות מושגים בנושא {top} עבור {student_context}")
        st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "רווחה":
    st.title("🧘 מרחב רווחה")
    if st.button("הפעל 30 שניות נשימה"):
        prog = st.progress(0)
        for i in range(30):
            time.sleep(1)
            prog.progress((i+1)/30)
        st.success("מעולה! הגוף רגוע.")

elif st.session_state.current_room == "מחשבון":
    st.title("🎯 מחשבון ציון יעד")
    magen = st.number_input("מגן:", 0, 100, 85)
    target = st.number_input("יעד:", 60, 100, 90)
    needed = (target * 100 - (magen * 30)) / 70
    st.info(f"דרוש בבגרות: {round(needed)}")

elif st.session_state.current_room == "מערכי שיעור":
    st.title("⏱️ מחולל מערך שיעור")
    top = st.text_input("נושא:")
    if top and st.button("בנה מערך"):
        res = generate_ai(f"מערך שיעור 45 דק' בנושא {top} עבור {student_context}")
        st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "בחנים ומחוונים":
    st.title("📝 בוחן ומחוון")
    top = st.text_input("נושא:")
    if top and st.button("ייצר בוחן"):
        res = generate_ai(f"בוחן 15 דק' ומחוון בנושא {top} עבור {student_context}")
        st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)
        
