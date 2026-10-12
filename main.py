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

APPROVED_STUDENT_EMAILS = [
    "dan.malka@tichonoz.org.il",
    "danmalka2090@gmail.com"
]

ALLOWED_SCHOOL_DOMAINS = [
    "tichonoz.org.il",
    "school.org.il",
    "msh.org.il",
    "k12.gov.il"
]

st.set_page_config(
    page_title="The Dan Method | מרחב למידה והוראה",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב מותאם ונעול שמונע בעיות צבע וניגודיות במק
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Rubik', -apple-system, BlinkMacSystemFont, sans-serif !important;
        direction: rtl;
        text-align: right;
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    #MainMenu, footer, div[data-testid="stDecoration"] {
        display: none !important;
    }

    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1100px;
        margin: 0 auto;
    }

    /* תוויות וטקסטים כהים וברורים */
    label, p, span, h1, h2, h3, h4, .stMarkdown {
        color: #0f172a !important;
    }

    /* תיקון קלט ל-Mac */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="input"] input, div[data-baseweb="select"] div {
        color: #0f172a !important;
        background-color: #ffffff !important;
    }

    /* כרטיס תוכן כללי */
    .room-content-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        margin-bottom: 18px;
    }

    /* באנר עליון */
    .hero-banner {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 32px 20px;
        margin-bottom: 20px;
        text-align: center;
    }

    .hero-main-title {
        font-size: 2.3rem;
        font-weight: 900;
        color: #0f2b5c;
        margin-bottom: 8px;
    }

    .hero-desc {
        font-size: 1.1rem;
        color: #475569;
        margin: 0;
    }

    /* טבלת השוואה */
    .compare-card-learnit {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        overflow-x: auto;
    }

    .compare-table-learnit {
        width: 100%;
        border-collapse: collapse;
        margin-top: 12px;
        text-align: right;
    }

    .compare-table-learnit th {
        padding: 12px;
        border-bottom: 2px solid #e2e8f0;
        font-weight: 800;
        color: #334155;
    }

    .compare-table-learnit td {
        padding: 12px;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.95rem;
    }

    /* תיקון קריטי לכל הכפתורים: צבע לבן ברור עם ניגודיות מלאה */
    div.stButton > button {
        background-color: #0f2b5c !important;
        border: 1px solid #0f2b5c !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        box-shadow: 0 2px 4px rgba(15, 23, 42, 0.1) !important;
    }

    div.stButton > button p, div.stButton > button span {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
    }

    div.stButton > button:hover {
        background-color: #1e3a8a !important;
        border-color: #1e3a8a !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- משתני סשן -----------------
if "approved_emails" not in st.session_state:
    st.session_state.approved_emails = set(APPROVED_STUDENT_EMAILS)
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

# ----------------- מסך כניסה מאובטח -----------------
if not st.session_state.user_authenticated:
    st.markdown("""
        <div class="room-content-card" style="text-align: center; max-width: 480px; margin: 30px auto; border-top: 5px solid #0f2b5c;">
            <div style="font-size: 42px; margin-bottom: 6px;">🎓</div>
            <h2 style="color: #0f2b5c; margin: 0 0 6px 0; font-weight: 800;">The Dan Method</h2>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 0;">
                מרחב למידה והוראה מותאם אישית
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.3, 1])
    with col_l2:
        chosen_type = st.radio("סוג משתמש:", ["תלמיד/ה 🎓", "מורה / איש צוות 🧑‍🏫"], horizontal=True)
        is_teacher = "מורה" in chosen_type

        with st.form("clean_login_form"):
            in_email = st.text_input("אימייל בית-ספרי:", placeholder="name@tichonoz.org.il")
            allow_guest = st.checkbox("אני מבית ספר אחר (פיילוט)")
            in_name = st.text_input("כינוי / שם לתצוגה:", placeholder="למשל: דן מלכה")
            
            avatar_list = ["👨‍🎓 תלמיד", "👩‍🎓 תלמידה", "🚀 יזם", "🧠 גאון", "⚡ מהיר", "🦉 חכם", "🧑‍🏫 מורה", "🔬 חוקר"]
            in_avatar = st.selectbox("בחר אווטאר:", avatar_list, index=6 if is_teacher else 0)
            
            teacher_pass_input = ""
            if is_teacher:
                teacher_pass_input = st.text_input("קוד גישה למורה:", type="password", placeholder="הזן סיסמת מורה...")

            btn_login = st.form_submit_button("כניסה למערכת 🚀", use_container_width=True)
            if btn_login:
                email_clean = in_email.strip().lower()
                domain_part = email_clean.split("@")[-1] if "@" in email_clean else ""
                
                if not email_clean or "@" not in email_clean:
                    st.error("נא להזין כתובת אימייל תקינה.")
                elif not allow_guest and not any(domain_part == d or domain_part.endswith("." + d) for d in ALLOWED_SCHOOL_DOMAINS):
                    st.error("האימייל אינו שייך לדומיין בית ספרי מאושר (@tichonoz.org.il).")
                elif not in_name.strip():
                    st.error("נא להזין שם או כינוי לתצוגה.")
                elif is_teacher:
                    if teacher_pass_input.strip() != st.session_state.teacher_current_code:
                        st.error("קוד גישה למורה שגוי.")
                    else:
                        st.session_state.user_email = email_clean
                        st.session_state.user_name = in_name.strip()
                        st.session_state.user_avatar = in_avatar.split()[0]
                        st.session_state.user_role = "מורה"
                        st.session_state.user_authenticated = True
                        st.session_state.current_room = "דף הבית"
                        st.rerun()
                else:
                    if allow_guest or email_clean in st.session_state.approved_emails:
                        st.session_state.user_email = email_clean
                        st.session_state.user_name = in_name.strip()
                        st.session_state.user_avatar = in_avatar.split()[0]
                        st.session_state.user_role = "תלמיד"
                        st.session_state.user_authenticated = True
                        st.session_state.current_room = "דף הבית"
                        st.rerun()
                    else:
                        st.error("כתובת אימייל זו אינה מופיעה ברשימת התלמידים המאושרים לפיילוט.")
    st.stop()

# ----------------- חיבור AI -----------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ מפתח GEMINI_API_KEY אינו מוגדר ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)
AVAILABLE_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]

def generate_ai(contents):
    last_err = None
    for m in AVAILABLE_MODELS:
        try:
            return client.models.generate_content(model=m, contents=contents)
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

    bio = BytesIO()
    prs.save(bio)
    bio.seek(0)
    return bio

# ----------------- סרגל צד -----------------
with st.sidebar:
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; background: #ffffff; padding: 10px 14px; border-radius: 14px; border: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 26px;">{st.session_state.user_avatar}</span>
                <div>
                    <div style="font-weight: 800; color: #0f2b5c; font-size: 0.95rem;">{st.session_state.user_name}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">סוג משתמש: <b>{st.session_state.user_role}</b></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 התנתק", use_container_width=True):
        st.session_state.user_authenticated = False
        st.session_state.user_role = "תלמיד"
        st.session_state.current_room = "דף הבית"
        st.rerun()

    chosen_grade = st.selectbox(
        "שכבת לימוד:",
        ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב (בגרות)"],
        index=2
    )
    student_context = f"משתמש: {st.session_state.user_name} ({st.session_state.user_role}), שכבה: {chosen_grade}."

# ----------------- סרגל עליון -----------------
col_nav_logo, col_nav_role_badge, col_nav_btn = st.columns([2.5, 1.5, 1])
with col_nav_logo:
    st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 10px 16px; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 24px;">{st.session_state.user_avatar}</span>
            <div style="text-align: right;">
                <div style="font-weight: 900; color: #0f2b5c; font-size: 1.1rem;">THE DAN METHOD</div>
                <div style="font-size: 0.8rem; color: #64748b;">שלום {st.session_state.user_name} • תיכון עוז</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_nav_role_badge:
    role_color = "#16a34a" if st.session_state.user_role == "תלמיד" else "#2563eb"
    st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:10px 14px; text-align:center; font-weight:800; color:{role_color};">
            מרחב: {st.session_state.user_role} 🔒
        </div>
    """, unsafe_allow_html=True)

with col_nav_btn:
    if st.button("🏠 דף הבית", key="nav_home_main", use_container_width=True):
        st.session_state.current_room = "דף הבית"
        st.rerun()

# ----------------- דף הבית -----------------
if st.session_state.current_room == "דף הבית":
    mode_title = "מרחב למידה והוראה מותאם אישית"
    mode_sub = "פלטפורמה פדגוגית חכמה לתרגול ממוקד, ליווי לימודי וסגירת פערים לימודיים בתיכון עוז."
    
    st.markdown(f"""
        <div class="hero-banner">
            <h1 class="hero-main-title">{mode_title}</h1>
            <p class="hero-desc">{mode_sub}</p>
        </div>
    """, unsafe_allow_html=True)

    query_search = st.text_input("🔍 מה תרצה ללמוד היום?", placeholder="הזן נושא, מושג או שאלה...")

    if query_search.strip():
        with st.spinner("מעבד מענה..."):
            try:
                res_bot = generate_ai(f"אתה עוזר לימודי אישי חכם עבור {st.session_state.user_role}. בהקשר: {student_context}. ענה ישירות: {query_search}.")
                st.markdown(f"""
                    <div class="room-content-card" style="border-right: 4px solid #2563eb;">
                        <span style="font-weight: 700; color: #2563eb;">💡 מענה מהיר של דן AI:</span>
                        <div style="font-size:1.05rem; line-height:1.7; margin-top: 8px;">{res_bot.text}</div>
                    </div>
                """, unsafe_allow_html=True)
            except Exception as err:
                st.error(f"שגיאה: {err}")

    # טבלת השוואה מותאמת תפקיד
    if st.session_state.user_role == "מורה":
        st.markdown("""
            <div class="compare-card-learnit">
                <h3 style="margin-top: 0; color: #0f2b5c; font-size: 1.3rem; font-weight: 800;">הערך הפדגוגי לצוות ההוראה: The Dan Method מול AI כללי</h3>
                <table class="compare-table-learnit">
                    <thead>
                        <tr>
                            <th style="width: 28%;">מדד מקצועי</th>
                            <th style="width: 36%; color: #2563eb;">🎓 The Dan Method (מרחב מורה)</th>
                            <th style="width: 36%; color: #64748b;">🤖 מודלים כלליים (ChatGPT)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="font-weight: 700;">מערכי שיעור ומצגות</td>
                            <td style="color: #16a34a; font-weight: 700;">✔️ חלוקה ל-45 דקות מדורגות ויצוא לקובץ PowerPoint</td>
                            <td style="color: #64748b;">❌ פסקאות טקסט כלליות ללא תזמון שיעור</td>
                        </tr>
                        <tr>
                            <td style="font-weight: 700;">בחנים ומחוונים רשמיים</td>
                            <td style="color: #16a34a; font-weight: 700;">✔️ מחוון ניקוד של משרד החינוך עם פתרון מלא</td>
                            <td style="color: #64748b;">❌ שאלות שטחיות ללא מחוון בדיקה</td>
                        </tr>
                        <tr>
                            <td style="font-weight: 700;">הוראה דיפרנציאלית</td>
                            <td style="color: #16a34a; font-weight: 700;">✔️ חלוקה ל-3 רמות קושי (בסיס, ליבה, מצוינות)</td>
                            <td style="color: #64748b;">❌ רמת קושי אחידה שאינה מותאמת לכיתה</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="compare-card-learnit">
                <h3 style="margin-top: 0; color: #0f2b5c; font-size: 1.3rem; font-weight: 800;">הערך המוסף של The Dan Method מול כלי AI כלליים</h3>
                <table class="compare-table-learnit">
                    <thead>
                        <tr>
                            <th style="width: 28%;">מדד פדגוגי</th>
                            <th style="width: 36%; color: #2563eb;">🎓 The Dan Method</th>
                            <th style="width: 36%; color: #64748b;">🤖 מודלים כלליים (ChatGPT)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="font-weight: 700;">התאמה לתוכנית הלימודים</td>
                            <td style="color: #16a34a; font-weight: 700;">✔️ כיול לפי מחווני בגרות והקבצות ז'-י"ב בישראל</td>
                            <td style="color: #64748b;">❌ מענה גנרי שאינו מכיר את מחווני משרד החינוך</td>
                        </tr>
                        <tr>
                            <td style="font-weight: 700;">מיקוד ויעילות זמן</td>
                            <td style="color: #16a34a; font-weight: 700;">✔️ מענה מדורג וממוקד ללא עומס קוגניטיבי</td>
                            <td style="color: #64748b;">❌ מלל ארוך ומפוזר הדורש סינון ומאריך את הלמידה</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<h3 style='color: #0f2b5c;'>מרחבי למידה וכלי עזר</h3>", unsafe_allow_html=True)

    # כרטיסים מאוחדים עם כפתורי כניסה ברורים
    if st.session_state.user_role == "תלמיד":
        tools = [
            ("מעבדת מתמטיקה", "🧮 מתמטיקה", "פירוק שלב-אחר-שלב", "#f3e8ff", "#6b21a8"),
            ("מצגות", "📊 מצגות", "בנייה והורדת PPTX", "#e0f2fe", "#0369a1"),
            ("חדר זום", "📹 חדר זום", "וידאו, קול ותרגול", "#dcfce7", "#15803d"),
            ("בגרות בעל פה", "🇬🇧 בגרות בעל פה", "English Oral COBE", "#e0e7ff", "#4338ca"),
            ("שליף חירום", "🚨 שליף חירום", "תקציר 60 שניות", "#fef9c3", "#a16207"),
            ("חילוץ לילה", "🆘 חילוץ לילה", "תוכנית חירום", "#fce7f3", "#be185d"),
            ("מבחני דמה", "📝 מבחני דמה", "סימולציה עם מחוון", "#f1f5f9", "#334155"),
            ("סורק תמונות", "📸 סורק תמונות", "פיענוח מדף/מחברת", "#ccfbf1", "#0f766e"),
            ("ערעור", "⚖️ מכתב ערעור", "ניסוח מנומק", "#e0f2fe", "#0369a1"),
            ("כרטיסיות", "🎴 כרטיסיות", "שינון מהיר", "#dcfce7", "#15803d"),
            ("רווחה", "🧘 מרחב רווחה", "ויסות ופוקוס", "#ffedd5", "#c2410c"),
            ("מחשבון", "🎯 מחשבון יעד", "חיזוי ציון סופי", "#fef9c3", "#a16207")
        ]
    else:
        tools = [
            ("לוח בקרה", "📊 לוח בקרה", "מדדי בית ספר", "#e0e7ff", "#4338ca"),
            ("מצגות", "📑 מצגת שיעור", "הורדת PPTX", "#e0f2fe", "#0369a1"),
            ("מערכי שיעור", "⏱️ מערך שיעור", "45 דק' מדורגות", "#dcfce7", "#15803d"),
            ("בחנים ומחוונים", "📝 בוחן + מחוון", "15 דק' עם ניקוד", "#fef9c3", "#a16207"),
            ("הערכה חלופית", "🔬 מטלת חקר (30%)", "הערכה חלופית", "#ccfbf1", "#0f766e"),
            ("הנהלה", "🏛️ מכתב להנהלה", "פיילוט וייעוץ", "#f1f5f9", "#334155"),
            ("בנק הערכות", "✍️ בנק הערכות", "משובים לתעודות", "#ffedd5", "#c2410c"),
            ("הודעות הורים", "📱 הודעה להורים", "וואטסאפ כיתתי", "#dcfce7", "#15803d"),
            ("מבדק דיפרנציאלי", "🪜 דיפרנציאלי", "3 רמות קושי", "#f3e8ff", "#6b21a8"),
            ("פתיחת שיעור", "💡 פתיחת שיעור", "Hook של 5 דקות", "#fef9c3", "#a16207"),
            ("רנטגן", "🩻 מוקשי למידה", "טעויות נפוצות", "#fce7f3", "#be185d"),
            ("דפי הדפסה", "🖨️ דפי הדפסה", "תרגול לכיתה", "#e0f2fe", "#0369a1")
        ]

    for i in range(0, len(tools), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(tools):
                room_id, title, desc, bg_color, text_color = tools[i + j]
                with cols[j]:
                    st.markdown(f"""
                        <div style="background-color: {bg_color}; border: 1px solid rgba(0,0,0,0.06); border-radius: 16px 16px 0 0; padding: 18px 12px; text-align: center;">
                            <div style="font-weight: 800; font-size: 1.05rem; color: {text_color};">{title}</div>
                            <div style="font-size: 0.82rem; color: #475569; margin-top: 4px;">{desc}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("כניסה לחדר ⬅️", key=f"btn_{room_id}", use_container_width=True):
                        st.session_state.current_room = room_id
                        st.rerun()

    # אזור חוות דעת
    st.markdown("<br><h3 style='color: #0f2b5c;'>⭐ חוות דעת תלמידים ומורים</h3>", unsafe_allow_html=True)
    col_rev1, col_rev2 = st.columns([1.8, 1.2])
    with col_rev1:
        for r in st.session_state.reviews:
            stars = "⭐" * r["rating"]
            st.markdown(f"""
                <div class="room-content-card" style="padding: 14px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="font-weight: 800; color: #0f2b5c;">{r['name']} ({r['grade']})</span>
                        <span>{stars}</span>
                    </div>
                    <div style="color: #334155; margin-top: 6px; font-size: 0.95rem;">{r['text']}</div>
                </div>
            """, unsafe_allow_html=True)
            
    with col_rev2:
        st.markdown('<div class="room-content-card"><h4 style="margin-top:0; color:#0f2b5c;">✍️ הוסף משוב:</h4>', unsafe_allow_html=True)
        with st.form("feedback_form_home", clear_on_submit=True):
            fb_name = st.text_input("שם או כינוי:", value=st.session_state.user_name)
            fb_grade = st.selectbox("תפקיד / כיתה:", ["כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב", "מורה מקצועי"])
            fb_rating = st.slider("דירוג:", 1, 5, 5)
            fb_text = st.text_area("משוב:")
            if st.form_submit_button("שלח משוב 🚀", use_container_width=True):
                if fb_text.strip():
                    st.session_state.reviews.insert(0, {
                        "name": fb_name.strip() if fb_name.strip() else "אנונימי",
                        "grade": fb_grade,
                        "rating": fb_rating,
                        "text": fb_text.strip()
                    })
                    st.success("תודה! המשוב נוסף.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- החדרים הפנימיים -----------------
elif st.session_state.current_room == "לוח בקרה":
    st.title("לוח בקרה ומדדי למידה בית-ספריים")
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("תרגילים שנפתרו", "2,480")
    col_s2.metric("שעות הוראה שנחסכו", "142 שעות")
    col_s3.metric("שביעות רצון פדגוגית", "87%")

elif st.session_state.current_room == "מצגות":
    st.title("מחולל מצגות PowerPoint")
    slide_topic = st.text_input("נושא המצגת:")
    slide_subject = st.selectbox("מקצוע:", ["היסטוריה", "ביולוגיה", "אזרחות", "ספרות", "אנגלית", "מדעים"])
    if st.button("בנה מצגת 🔨", use_container_width=True):
        if slide_topic:
            with st.spinner("בונה מצגת..."):
                prompt_slides = f"החזר מערך JSON של 5 שקופיות בנושא {slide_topic} ב{slide_subject}: [{{\"slide_num\": 1, \"title\": \"כותרת\", \"bullets\": [\"נקודה 1\", \"נקודה 2\"], \"speaker_notes\": \"הסבר\"}}]"
                res = generate_ai(prompt_slides)
                st.session_state.slides_data = extract_json(res.text)
                st.session_state.pptx_bytes = create_pptx_file(st.session_state.slides_data, slide_topic)
    if st.session_state.pptx_bytes:
        st.download_button("📥 הורד קובץ מצגת (.pptx)", st.session_state.pptx_bytes, file_name=f"presentation.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation", use_container_width=True)

elif st.session_state.current_room == "חדר זום":
    st.title("שיעור פרטי בזום עם המורה מיה")
    z_subject = st.selectbox("מקצוע השיעור:", ["מתמטיקה", "אנגלית", "היסטוריה", "לשון והבעה"])
    chat_box = st.container(height=260)
    with chat_box:
        for m in st.session_state.zoom_chat_history:
            with st.chat_message(m["role"]):
                st.write(m["content"])
    text_spoken = st.chat_input("הקלד הודעה למורה מיה...")
    if text_spoken:
        st.session_state.zoom_chat_history.append({"role": "user", "content": text_spoken})
        res_zoom = generate_ai(f"את המורה מיה בשיעור פרטי עם {st.session_state.user_name} ב{z_subject}. עני קצר ומעודד: {text_spoken}")
        st.session_state.zoom_chat_history.append({"role": "assistant", "content": res_zoom.text})
        st.session_state.last_voice_audio_bytes = create_audio_bytes(res_zoom.text)
        st.rerun()
    if st.session_state.last_voice_audio_bytes:
        st.audio(st.session_state.last_voice_audio_bytes, format="audio/mp3", autoplay=True)

elif st.session_state.current_room == "בגרות בעל פה":
    st.title("English Oral Bagrut Simulator")
    part_oral = st.selectbox("Part:", ["Part A: Interview", "Part B: Project", "Part C: Clip"])
    if st.button("Start Question 🚀", use_container_width=True):
        res_or = generate_ai(f"You are the official Bagrut Oral Examiner. Ask {st.session_state.user_name} one question for {part_oral}.")
        st.session_state.oral_chat_history = [{"role": "assistant", "content": res_or.text}]
        st.session_state.last_voice_audio_bytes = create_audio_bytes(res_or.text, lang='en')
        st.rerun()
    for msg in st.session_state.oral_chat_history:
        st.write(f"**{msg['role']}:** {msg['content']}")
    if st.session_state.last_voice_audio_bytes:
        st.audio(st.session_state.last_voice_audio_bytes, format="audio/mp3", autoplay=True)

elif st.session_state.current_room == "מעבדת מתמטיקה":
    st.title("מעבדת פירוק מתמטיקה")
    m_topic = st.text_input("נושא:")
    m_input = st.text_area("תרגיל:")
    if st.button("פתור שלב-אחר-שלב 🧠", use_container_width=True):
        if m_input:
            with st.spinner("פותר..."):
                res = generate_ai(f"פתור שלב אחרי שלב עבור {student_context}: {m_input}")
                st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "שליף חירום":
    st.title("שליף חירום: 60 שניות לפני מבחן")
    p_topic = st.text_input("נושא המבחן:")
    if st.button("הצג תמצית ⚡", use_container_width=True):
        if p_topic:
            with st.spinner("מחלץ..."):
                res = generate_ai(f"שליף של 60 שניות על {p_topic} עבור {student_context}.")
                st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "חילוץ לילה":
    st.title("מצב חילוץ ב-3 בלילה")
    panic_sub = st.text_input("מקצוע:")
    panic_top = st.text_area("חומר:")
    if st.button("הצל אותי 🚨", use_container_width=True):
        if panic_top:
            res = generate_ai(f"תוכנית חירום ללילה לפני מבחן ב{panic_sub}: {panic_top}")
            st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "מבחני דמה":
    st.title("מבחני דמה")
    exam_sub = st.text_input("מקצוע:")
    exam_top = st.text_input("נושא:")
    if st.button("בנה מבחן 📝", use_container_width=True):
        res = generate_ai(f"צור מבחן דמה עם מחוון ניקוד ב{exam_sub} על {exam_top}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "סורק תמונות":
    st.title("סורק תמונות ומחברת")
    photo_topic = st.text_input("נושא התרגיל:")
    file = st.file_uploader("העלה תמונה:", type=["png", "jpg", "jpeg"])
    if st.button("פענח 📸", use_container_width=True):
        if file and photo_topic:
            img = Image.open(file)
            res = generate_ai([f"פתור את התרגיל בתמונה בנושא {photo_topic}", img])
            st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "ערעור":
    st.title("מחולל מכתב ערעור")
    c_sub = st.text_input("מקצוע:")
    c_q = st.text_area("שאלה ותשובתך:")
    if st.button("נסח ערעור ⚖️", use_container_width=True):
        res = generate_ai(f"נסח ערעור מנומק למורה ב{c_sub}: {c_q}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "כרטיסיות":
    st.title("כרטיסיות שינון")
    f_topic = st.text_input("נושא:")
    if st.button("ייצר כרטיסיות 🎴", use_container_width=True):
        res = generate_ai(f"צור 4 כרטיסיות JSON: [{{\"front\":\"שאלה\",\"back\":\"תשובה\"}}] בנושא {f_topic}")
        st.session_state["flashcards"] = extract_json(res.text)
    if "flashcards" in st.session_state:
        for c in st.session_state["flashcards"]:
            with st.expander(c.get("front", "")):
                st.write(c.get("back", ""))

elif st.session_state.current_room == "רווחה":
    st.title("מרחב רווחה ופוקוס")
    st.write("תרגיל נשימה להורדת דופק (Box Breathing: 4 שניות שאיפה, 4 עצירה, 4 נשיפה, 4 עצירה)")
    if st.button("הפעל טיימר 30 שניות 🧘"):
        prog = st.progress(0)
        for i in range(30):
            time.sleep(1)
            prog.progress((i + 1) / 30)
        st.success("המוח מוכן ללמידה ממוקדת!")

elif st.session_state.current_room == "מחשבון":
    st.title("מחשבון יעד לבגרות")
    magen = st.number_input("ציון מגן:", 0, 100, 80)
    target = st.number_input("ציון מבוקש:", 0, 100, 90)
    needed = (target * 100 - (magen * 30)) / 70
    st.info(f"ציון הבגרות הנדרש כדי להגיע ליעד: {round(needed)}")

# חדרים למורים
elif st.session_state.current_room == "מערכי שיעור" and st.session_state.user_role == "מורה":
    st.title("מחולל מערכי שיעור (45 דק')")
    l_sub = st.text_input("מקצוע:")
    l_top = st.text_input("נושא:")
    if st.button("בנה מערך 📚", use_container_width=True):
        res = generate_ai(f"בנה מערך שיעור של 45 דק' ב{l_sub} על {l_top}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "בחנים ומחוונים" and st.session_state.user_role == "מורה":
    st.title("מחולל בוחן כיתתי + מחוון")
    q_sub = st.text_input("מקצוע:")
    q_top = st.text_input("נושא:")
    if st.button("ייצר בוחן ומחוון 📝", use_container_width=True):
        res = generate_ai(f"צור בוחן של 15 דקות ומחוון ניקוד משרד החינוך ב{q_sub} על {q_top}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "הערכה חלופית" and st.session_state.user_role == "מורה":
    st.title("מטלת חקר והערכה חלופית (30%)")
    p_sub = st.text_input("מקצוע:")
    p_top = st.text_input("נושא:")
    if st.button("בנה משימה ומחוון 🔬", use_container_width=True):
        res = generate_ai(f"צור מטלת חקר של 30% בגרות ומחוון הערכה ב{p_sub} על {p_top}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "הנהלה" and st.session_state.user_role == "מורה":
    st.title("מכתב להנהלת בית הספר")
    letter = f"""לכבוד: הנהלת תיכון עוז
מאת: {st.session_state.user_name}
הנדון: שילוב פלטפורמת 'The Dan Method' בפיילוט כיתתי

פלטפורמת The Dan Method נבנתה במטרה לייעל את הלמידה העצמאית של התלמידים, לסייע בהפחתת חרדת בחינות, ולחסוך שעות עבודה שבועיות לצוות ההוראה בהכנת מערכים ומחוונים.

אנו מציעים התנסות פיילוט מבוקרת בכיתה אחת למדידת שביעות הרצון וצמצום פערים לימודיים."""
    st.markdown(f'<div class="room-content-card" style="white-space: pre-wrap;">{letter}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "בנק הערכות" and st.session_state.user_role == "מורה":
    st.title("מחולל הערכות לתעודות")
    st_name = st.text_input("שם התלמיד/ה:")
    st_achieve = st.selectbox("הישגים:", ["מצטיין", "טוב מאוד", "בינוני", "דרוש שיפור"])
    if st.button("נסח הערכה ✍️", use_container_width=True):
        res = generate_ai(f"נסח משוב אישי ומעצים לתעודה עבור {st_name}, הישגים: {st_achieve}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "הודעות הורים" and st.session_state.user_role == "מורה":
    st.title("מחולל הודעות וואטסאפ להורים")
    p_topic = st.text_input("נושא ההודעה:")
    if st.button("צור הודעה 📱", use_container_width=True):
        res = generate_ai(f"נסח הודעת וואטסאפ רשמית ומסודרת להורים בנושא: {p_topic}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "מבדק דיפרנציאלי" and st.session_state.user_role == "מורה":
    st.title("מבדק דיפרנציאלי ב-3 רמות")
    d_sub = st.text_input("מקצוע:")
    d_top = st.text_input("נושא:")
    if st.button("בנה מבדק 🪜", use_container_width=True):
        res = generate_ai(f"צור מבדק ב-3 רמות קושי (בסיס, ליבה, אתגר) ב{d_sub} על {d_top}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "פתיחת שיעור" and st.session_state.user_role == "מורה":
    st.title("פתיחת שיעור מסקרנת (Hook)")
    h_sub = st.text_input("מקצוע:")
    h_top = st.text_input("נושא:")
    if st.button("צור רעיונות 💡", use_container_width=True):
        res = generate_ai(f"הצע 3 רעיונות לפתיחת שיעור של 5 דקות ב{h_sub} על {h_top}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "רנטגן" and st.session_state.user_role == "מורה":
    st.title("מוקשי למידה וטעויות נפוצות")
    x_top = st.text_input("נושא:")
    if st.button("חשוף מוקשים 🩻", use_container_width=True):
        res = generate_ai(f"פרט את 3 הטעויות והמלכודות הנפוצות ביותר של תלמידים בנושא {x_top}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)

elif st.session_state.current_room == "דפי הדפסה" and st.session_state.user_role == "מורה":
    st.title("מחולל דפי תרגול להדפסה")
    pr_top = st.text_input("נושא:")
    if st.button("ייצר דף עבודה 📄", use_container_width=True):
        res = generate_ai(f"צור דף עבודה מוכן להדפסה כולל שאלות ומקום לתשובות בנושא {pr_top}")
        st.markdown(f'<div class="room-content-card">{res.text}</div>', unsafe_allow_html=True)
        st.markdown('<button onclick="window.print()" style="padding: 8px 16px; background: #0f2b5c; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🖨️ הדפס</button>', unsafe_allow_html=True)
