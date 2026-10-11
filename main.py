import streamlit as st
from google import genai
from PIL import Image
import requests
from io import BytesIO
import json
import re
import time
import urllib.parse

# הגנה מקריסה אם הספרייה לא מותקנת
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

# שפת עיצוב עמידה ללא סיידבר כלל
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    * { box-sizing: border-box; }

    /* העלמת כל זכר לסיידבר כדי שלא יצוף בשום דפדפן */
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
        max-width: 1100px;
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
if "mock_exam_data" not in st.session_state:
    st.session_state.mock_exam_data = None
if "slides_data" not in st.session_state:
    st.session_state.slides_data = None
if "saved_vault" not in st.session_state:
    st.session_state.saved_vault = []
if "exam_start_time" not in st.session_state:
    st.session_state.exam_start_time = None
if "chosen_grade" not in st.session_state:
    st.session_state.chosen_grade = "כיתה ט'"
if "math_units" not in st.session_state:
    st.session_state.math_units = "הקבצה א' / מצוינות"
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
student_context = f"שכבת לימוד: {st.session_state.chosen_grade}, מתמטיקה: {st.session_state.math_units}."

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

# הגדרת פרופיל נקייה לחלוטין (בלי שום סיידבר!)
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

# ----------------- חדר: מחולל מצגות -----------------
elif st.session_state.current_room == "מצגות":
    st.title("📊 מחולל מצגות מקצועי + הורדת PowerPoint")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        topic = st.text_input("נושא המצגת:", placeholder="למשל: תהליך הפוטוסינתזה, מלחמת העולם הראשונה...")
    with c_s2:
        count = st.slider("מספר שקופיות:", 3, 7, 5)

    if st.button("🔨 צור מצגת והכן קובץ PPTX", use_container_width=True) and topic:
        with st.spinner("בונה שקופיות ומעצב קובץ PowerPoint..."):
            prompt = (
                f"צור שלד מצגת של {count} שקופיות בנושא '{topic}' עבור {student_context}.\n"
                "החזר אך ורק מערך JSON תקני:\n"
                "[{\"slide_num\": 1, \"title\": \"כותרת\", \"bullets\": [\"נקודה 1\", \"נקודה 2\"], \"speaker_notes\": \"מה לומר בעל פה\"}]"
            )
            try:
                res_txt = generate_ai(prompt)
                st.session_state.slides_data = extract_json(res_txt)
                st.success("המצגת נוצרה בהצלחה!")
            except Exception:
                st.error("הייתה בעיה בפענוח המצגת, נסה שנית.")

    if st.session_state.slides_data:
        if PPTX_READY:
            pptx_bytes = build_pptx_file(st.session_state.slides_data, topic if topic else "Presentation")
            st.download_button(
                label="📥 הורד קובץ PowerPoint אמיתי (.pptx)",
                data=pptx_bytes,
                file_name=f"{topic if topic else 'presentation'}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )
        else:
            st.info("💡 כדי לאפשר הורדת קובץ PPTX, הוסף 'python-pptx' לקובץ requirements.txt ב-GitHub.")

        for s in st.session_state.slides_data:
            st.markdown(f"""
                <div class="clean-box">
                    <h3 style="color:#0f2b5c; margin:0 0 8px 0;">שקופית {s.get('slide_num')}: {s.get('title')}</h3>
                    <p><b>מה מקרינים:</b></p>
                    {''.join([f'<li>{b}</li>' for b in s.get('bullets', [])])}
                    <div style="background:#f1f5f9; padding:10px; border-radius:8px; margin-top:10px;">
                        <b>🗣️ הערות דובר:</b> {s.get('speaker_notes', '')}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# ----------------- חדר: סימולטור מבחן -----------------
elif st.session_state.current_room == "מבחני דמה":
    st.title("📝 סימולטור מבחן חי עם טיימר וכרטיס ציון")
    c_e1, c_e2 = st.columns(2)
    with c_e1:
        e_topic = st.text_input("נושא המבחן:", placeholder="למשל: סדרות חשבוניות, גנטיקה, אזרחות...")
    with c_e2:
        e_mins = st.slider("זמן מוקצב (בדקות):", 5, 45, 15)

    if st.button("התחל סימולציית מבחן ⏱️", use_container_width=True) and e_topic:
        with st.spinner("מכין שאלות בגרות ומפעיל שעון..."):
            prompt = f"צור מבחן קצר של 3 שאלות (2 אמריקאיות, 1 פתוחה) בנושא {e_topic} עבור {student_context}. החזר כ-JSON: [{{\"id\": 1, \"type\": \"mcq\", \"q\": \"שאלה\", \"options\": [\"א\", \"ב\", \"ג\", \"ד\"], \"ans\": \"א\"}}, {{\"id\": 2, \"type\": \"open\", \"q\": \"שאלה פתוחה\", \"ideal\": \"תשובה מלאה\"}}]"
            try:
                st.session_state.mock_exam_data = extract_json(generate_ai(prompt))
                st.session_state.exam_start_time = time.time()
                st.success("המבחן החל! הזמן רץ.")
            except Exception:
                st.error("הייתה תקלה ביצירת המבחן, נסה שוב.")

    if st.session_state.mock_exam_data:
        elapsed = int(time.time() - st.session_state.exam_start_time)
        remain = max(0, (e_mins * 60) - elapsed)
        st.info(f"⏳ זמן שנותר: {remain // 60:02d}:{remain % 60:02d} דקות")
        
        user_answers = {}
        for item in st.session_state.mock_exam_data:
            st.markdown(f"**שאלה {item['id']}:** {item['q']}")
            if item.get("type") == "mcq":
                user_answers[item["id"]] = st.radio(f"בחר תשובה לשאלה {item['id']}:", item["options"], key=f"q_ans_{item['id']}")
            else:
                user_answers[item["id"]] = st.text_area(f"תשובתך לשאלה {item['id']}:", key=f"q_ans_{item['id']}")

        if st.button("🏁 הגש מבחן לקבלת ציון ומשוב", use_container_width=True):
            with st.spinner("מעריך את המבחן ומחשב ציון סופי..."):
                grade_prompt = f"הערך מבחן זה עבור {student_context}. שאלות: {json.dumps(st.session_state.mock_exam_data, ensure_ascii=False)}. תשובות תלמיד: {json.dumps(user_answers, ensure_ascii=False)}. החזר ציון מספרי מ-0 עד 100, פירוט ניקוד ואיפה ירדו נקודות."
                feedback = generate_ai(grade_prompt)
                st.markdown(f"""
                    <div class="clean-box" style="border-right: 5px solid #16a34a;">
                        <h3 style="color:#16a34a; margin:0 0 10px 0;">🎯 דוח ציון ומשוב בוחן (Scorecard):</h3>
                        <p>{feedback}</p>
                    </div>
                """, unsafe_allow_html=True)

# ----------------- שאר החדרים -----------------
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
        st.session_state.zoom_chat_history.append({"role": "assistant", "content": res})
        st.rerun()

elif st.session_state.current_room == "סורק תמונות":
    st.title("📸 סורק תמונות ושיעורי בית")
    file = st.file_uploader("העלה תמונת תרגיל:", type=["png", "jpg", "jpeg"])
    if file and st.button("פתור תרגיל", use_container_width=True):
        img = Image.open(file)
        with st.spinner("מפענח..."):
            res = generate_ai([f"פתור את התרגיל שבתמונה צעד אחרי צעד עבור {student_context}", img])
            st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "חילוץ לילה":
    st.title("🆘 מצב חילוץ ב-3 בלילה")
    top = st.text_input("חומר למבחן מחר:")
    if top and st.button("הצל אותי עכשיו", use_container_width=True):
        with st.spinner("מחלץ..."):
            res = generate_ai(f"תוכנית חילוץ לפני מבחן: {top}. 3 מושגי חובה, טעויות קלאסיות ומשפטי מפתח.")
            st.markdown(f'<div class="panic-box">{res}</div>', unsafe_allow_html=True)
            if st.button("💾 שמור חילוץ זה לכספת"):
                st.session_state.saved_vault.append({"title": f"חילוץ לילה: {top}", "content": res})
                st.success("נשמר בכספת!")

elif st.session_state.current_room == "שליף חירום":
    st.title("🚨 שליף חירום: 60 שניות לפני מבחן")
    top = st.text_input("נושא המבחן:")
    if top and st.button("הצג שליף", use_container_width=True):
        with st.spinner("מכין..."):
            res = generate_ai(f"שליף של 60 שניות בנושא: {top}. תכל'ס בלבד.")
            st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)
            if st.button("💾 שמור שליף לכספת"):
                st.session_state.saved_vault.append({"title": f"שליף: {top}", "content": res})
                st.success("נשמר!")

elif st.session_state.current_room == "מערכי שיעור":
    st.title("⏱️ מחולל מערך שיעור (45 דק')")
    top = st.text_input("נושא:")
    if top and st.button("בנה מערך", use_container_width=True):
        with st.spinner("מכין..."):
            res = generate_ai(f"מערך שיעור 45 דק' בנושא {top} עם פתיחה, הקניה ותרגול.")
            st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "בחנים ומחוונים":
    st.title("📝 בוחן פתע ומחוון")
    top = st.text_input("נושא:")
    if top and st.button("ייצר בוחן ומחוון", use_container_width=True):
        with st.spinner("מכין..."):
            res = generate_ai(f"בוחן 15 דק' ומחוון בנושא {top}")
            st.markdown(f'<div class="clean-box">{res}</div>', unsafe_allow_html=True)
