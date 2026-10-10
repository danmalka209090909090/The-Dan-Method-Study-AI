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
    initial_sidebar_state="expanded"
)

# שפת עיצוב LearnIt / EdTech מודרנית ונקייה (Light Aesthetic)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700;800;900&display=swap');

    * {
        font-family: 'Assistant', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    .stApp {
        direction: rtl;
        text-align: right;
        background-color: #f8fafc;
        color: #0f172a;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-left: 1px solid #e2e8f0;
        box-shadow: -2px 0 10px rgba(0, 0, 0, 0.02);
    }

    /* Header עליון אלגנטי בסגנון LearnIt */
    .learnit-navbar {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 14px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }
    .brand-logo {
        font-size: 1.45rem;
        font-weight: 800;
        color: #1e3a8a;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-slogan {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
        margin-right: 4px;
    }

    /* Hero Banner עם רקע חם ונקי */
    .hero-banner {
        background: linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.94)), 
                    url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80') center/cover no-repeat;
        border: 1px solid #e2e8f0;
        border-radius: 24px;
        padding: 50px 40px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
        margin-bottom: 28px;
        text-align: center;
    }
    .hero-main-title {
        font-size: 3rem;
        font-weight: 900;
        color: #0f2b5c;
        line-height: 1.25;
        margin-bottom: 12px;
    }
    .hero-desc {
        font-size: 1.25rem;
        color: #475569;
        margin-bottom: 28px;
        font-weight: 500;
    }

    /* שורת יתרונות (Feature Badges) */
    .features-ribbon {
        display: flex;
        justify-content: space-around;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 16px 20px;
        margin-bottom: 34px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
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
    .ribbon-title {
        font-weight: 700;
        color: #0f172a;
        font-size: 0.95rem;
    }
    .ribbon-subtitle {
        color: #64748b;
        font-size: 0.8rem;
    }

    /* כרטיסיות צבעוניות פסטליות של מקצועות */
    .category-card {
        border-radius: 18px;
        padding: 24px 18px;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
        margin-bottom: 16px;
    }
    .category-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }
    .cat-icon {
        font-size: 34px;
        margin-bottom: 10px;
    }
    .cat-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 4px;
    }
    .cat-meta {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
    }

    .cat-purple { background: #f3e8ff; border-color: #e9d5ff; }
    .cat-blue   { background: #e0f2fe; border-color: #bae6fd; }
    .cat-green  { background: #dcfce7; border-color: #bbf7d0; }
    .cat-orange { background: #ffedd5; border-color: #fed7aa; }
    .cat-yellow { background: #fef9c3; border-color: #fef08a; }
    .cat-slate  { background: #f1f5f9; border-color: #e2e8f0; }

    /* כרטיסיית חדר זום מעוצבת */
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

    /* טופס מבחן ושליף חירום */
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

    /* כפתורי פורטלים */
    .portal-tag-learnit {
        display: inline-block;
        padding: 9px 18px;
        background: #f8fafc;
        color: #1e3a8a !important;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 700;
        margin-left: 8px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .portal-tag-learnit:hover {
        background: #1e3a8a;
        color: #ffffff !important;
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
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "השליף חירום סגר לי את החומר לפני המבחן בהיסטוריה."},
        {"name": "נועה ל.", "grade": "כיתה י\"א (ביולוגיה)", "rating": 5, "text": "עיצוב מהמם, נעים וכיף ללמוד בלי עומס בעיניים."},
        {"name": "מאיה ר.", "grade": "כיתה י\"א (5 יח')", "rating": 5, "text": "מפרק המתמטיקה מסביר לפי מחוון בגרות בדיוק כמו שצריך."}
    ]

if "mock_exam_data" not in st.session_state:
    st.session_state.mock_exam_data = None
if "exam_submitted" not in st.session_state:
    st.session_state.exam_submitted = False
if "zoom_chat_history" not in st.session_state:
    st.session_state.zoom_chat_history = []
if "last_voice_reply" not in st.session_state:
    st.session_state.last_voice_reply = None

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
    text = re.sub(r"^```json\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text.strip(), flags=re.MULTILINE)
    return json.loads(text.strip("`").strip())

def get_tts_audio_url(text):
    clean_text = re.sub(r"[*#_`>\[\]\(\)]", "", text)
    clean_text = clean_text[:200]
    encoded = urllib.parse.quote(clean_text)
    return f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl=iw&client=tw-ob"

# --- סרגל צד (Sidebar) ---
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
    st.subheader("📚 ניווט בחדרים")
    room = st.radio(
        "מעבר בין הכלים:",
        [
            "🏠 דף הבית",
            "📹 חדר זום עם מורה פרטית (Live Zoom)",
            "📸 סורק תמונות ושיעורי בית",
            "📝 מחולל מבחני דמה (Mock Exam)",
            "🎬 ספריית וידאו ושיעורים ענקית",
            "🏫 חיבור ל-Classroom וספרי לימוד",
            "🖨️ דפי תרגול ומבחנים להדפסה",
            "💯 מלטשת תשובות למאיות",
            "📐 מעבדת מתמטיקה ומדעים",
            "🚨 שליף חירום (לפני מבחן)",
            "📅 מתכנן לו״ז למבחן",
            "⭐ חוות דעת והצעות"
        ]
    )
    
    st.markdown("---")
    no_yap = st.toggle("מצב תכל'ס (מענה ממוקד ולעניין)", value=True)

anti_yap_rule = "השב ישירות לתכל'ס, ללא פסקאות פתיחה או סיום מיותרות." if no_yap else ""
student_context = f"שכבת לימוד: {chosen_grade}, מתמטיקה: {math_units}, אנגלית: {eng_units}, מגמה: {chosen_major}."

# ----------------- 0. דף הבית (בעיצוב LearnIt המדויק) -----------------
if room == "🏠 דף הבית":
    # נאובר עליון
    st.markdown("""
        <div class="learnit-navbar">
            <div class="brand-logo">
                <span>The Dan Method</span>
                <span class="brand-slogan">| לומדים. מתקדמים.</span>
            </div>
            <div style="color: #64748b; font-size: 0.95rem; font-weight: 600;">
                מחובר: <b>""" + chosen_grade + """ (""" + math_units + """)</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Hero Banner בסגנון התמונה
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-main-title">הדרך שלך להצלחה<br>מתחילה כאן.</h1>
            <p class="hero-desc">
                לימודים קלים יותר, בכל מקום ובכל זמן.<br>
                כל מה שצריך כדי להצליח – במקום אחד ממוקד מחוון.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # סרט היתרונות (Ribbon) כמו בתמונה
    st.markdown("""
        <div class="features-ribbon">
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #f3e8ff; color: #9333ea;">📖</div>
                <div>
                    <div class="ribbon-title">תוכן איכותי ומדויק</div>
                    <div class="ribbon-subtitle">הסברים בהירים וממוקדים לבגרות</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #e0f2fe; color: #0284c7;">⏱️</div>
                <div>
                    <div class="ribbon-title">לומדים בקצב שלך</div>
                    <div class="ribbon-subtitle">גישה חופשית ומיידית 24/7</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #dcfce7; color: #16a34a;">👥</div>
                <div>
                    <div class="ribbon-title">מגוון רחב של מקצועות</div>
                    <div class="ribbon-subtitle">כל המגמות וההקבצות במקום אחד</div>
                </div>
            </div>
            <div class="ribbon-item">
                <div class="ribbon-icon-circle" style="background: #fef9c3; color: #ca8a04;">⭐</div>
                <div>
                    <div class="ribbon-title">מתאים לכל תלמיד</div>
                    <div class="ribbon-subtitle">מחטיבת הביניים ועד י"ב ובגרות</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # כרטיסיות מקצועות פסטליות בדיוק כמו בתמונה
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h2 style="font-size: 1.5rem; font-weight: 800; color: #0f2b5c; margin: 0;">קטגוריות לימוד</h2>
            <span style="color: #64748b; font-weight: 600; font-size: 0.95rem;">בחר תחום כדי לתרגל</span>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown("""
            <div class="category-card cat-purple">
                <div class="cat-icon">📐</div>
                <div class="cat-title">מתמטיקה</div>
                <div class="cat-meta">הקבצות ו-3/4/5 יח'</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class="category-card cat-blue">
                <div class="cat-icon">🧪</div>
                <div class="cat-title">מדעים</div>
                <div class="cat-meta">ביולוגיה ופיזיקה</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
            <div class="category-card cat-green">
                <div class="cat-icon">📖</div>
                <div class="cat-title">אנגלית</div>
                <div class="cat-meta">דקדוק ו-Module A-G</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
            <div class="category-card cat-orange">
                <div class="cat-icon">🏛️</div>
                <div class="cat-title">היסטוריה</div>
                <div class="cat-meta">אירועים ומחווני בגרות</div>
            </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown("""
            <div class="category-card cat-yellow">
                <div class="cat-icon">🌍</div>
                <div class="cat-title">אזרחות ותנ"ך</div>
                <div class="cat-meta">מושגי חובה ופרקים</div>
            </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown("""
            <div class="category-card cat-slate">
                <div class="cat-icon">💻</div>
                <div class="cat-title">מחשבים ומגמות</div>
                <div class="cat-meta">מדמ"ח, כלכלה ועוד</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # טבלת השוואה נקייה: The Dan Method מול AI רגיל
    st.markdown("""
        <div class="clean-box" style="margin-top: 10px;">
            <h3 style="margin-top: 0; color: #0f2b5c; font-size: 1.3rem; font-weight: 800;">למה The Dan Method ולא סתם בינה מלאכותית רגילה?</h3>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 20px;">AI גנרי חופר ומנותק מתוכנית הלימודים. כאן מקבלים רק את מה שסוגר את מלוא הנקודות במבחן.</p>
            <table style="width: 100%; border-collapse: collapse; text-align: right;">
                <thead>
                    <tr style="border-bottom: 2px solid #e2e8f0; color: #64748b; font-weight: 700;">
                        <th style="padding: 10px;">תכונה</th>
                        <th style="padding: 10px; color: #1e3a8a;">The Dan Method 🎓</th>
                        <th style="padding: 10px;">ChatGPT / מודל רגיל</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 12px 10px; font-weight: 600;">התאמה למערכת החינוך</td>
                        <td style="padding: 12px 10px; color: #16a34a; font-weight: 700;">מכויל בול לפי מחווני בגרות, הקבצות וכיתות ז'-י"ב</td>
                        <td style="padding: 12px 10px; color: #64748b;">תשובות גנריות באנגלית שתורגמו לעברית</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 12px 10px; font-weight: 600;">אורך המענה והיעילות</td>
                        <td style="padding: 12px 10px; color: #16a34a; font-weight: 700;">מצב תכל'ס (No Yap) – פירוק מדויק ב-3 שורות או שלבים</td>
                        <td style="padding: 12px 10px; color: #64748b;">פסקאות פתיחה וסיום ארוכות וחפירות מיותרות</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 12px 10px; font-weight: 600;">בדיקת מבחנים וציונים</td>
                        <td style="padding: 12px 10px; color: #16a34a; font-weight: 700;">חישוב ציון אמיתי עם הורדת נקודות לפי נימוקים חסרים</td>
                        <td style="padding: 12px 10px; color: #64748b;">סתם מחמיא לתשובה בלי לתת ניקוד מספרי מדויק</td>
                    </tr>
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)

# ----------------- 1. חדר זום עם מורה פרטית -----------------
elif room == "📹 חדר זום עם מורה פרטית (Live Zoom)":
    st.title("📹 שיעור פרטי בזום עם המורה מיה")
    st.caption(f"מותאם אישית עבור {chosen_grade} | {math_units} | {chosen_major}")
    
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
        
        if st.button("🧹 איפוס שיחה והתחלה מחדש", use_container_width=True):
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
                    if m["role"] == "user":
                        with st.chat_message("user"):
                            st.write(m["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(m["content"])

        st.caption("🎙️ דיבור במיקרופון ישירות למורה:")
        audio_prompt = st.audio_input("הקלט שאלה קולית:")

        if audio_prompt is not None:
            with st.spinner("המורה מיה מקשיבה לשאלה שלך ועונה..."):
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
                except Exception as e:
                    st.error(f"שגיאה: {e}")

        text_spoken = st.chat_input("או כתוב כאן למורה מיה...")
        if text_spoken:
            st.session_state.zoom_chat_history.append({"role": "user", "content": text_spoken})
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.zoom_chat_history[-6:]])
            zoom_prompt = (
                f"את המורה מיה, מורה פרטית ישראלית מקצועית וסבלנית בשיעור עם תלמיד.\n"
                f"פרטי התלמיד: {student_context}.\n"
                f"מקצוע: {z_subject}. מטרה: {z_goal}.\n\n"
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
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 2. סורק תמונות ושיעורי בית -----------------
elif room == "📸 סורק תמונות ושיעורי בית":
    st.title("📸 סורק תמונות ושיעורי בית")
    st.caption("העלאת צילום מהמחברת או מספר הלימוד לפיענוח שלב-אחר-שלב.")
    
    photo_topic = st.text_input("מה החומר או המקצוע?", placeholder="תרגיל בפיזיקה, אלגברה, שאלות בגרות בתנ\"ך...")
    input_method = st.radio("מקור התמונה:", ["📁 העלאת קובץ מהמכשיר", "🔗 קישור ישיר (URL)"], horizontal=True)
    
    img_to_solve = None
    if input_method == "📁 העלאת קובץ מהמכשיר":
        file = st.file_uploader("בחר קובץ תמונה (JPG/PNG):", type=["png", "jpg", "jpeg"])
        if file:
            try:
                img_to_solve = Image.open(file)
                st.image(img_to_solve, caption="התמונה שהועלתה", width=340)
            except Exception as e:
                st.error(f"שגיאה בפתיחת קובץ: {e}")
    else:
        url_input = st.text_input("הדבק כתובת URL לתמונה:", placeholder="https://example.com/homework.jpg")
        if url_input.strip():
            try:
                with st.spinner("טוען תמונה מהקישור..."):
                    response = requests.get(url_input.strip(), timeout=10)
                    response.raise_for_status()
                    img_to_solve = Image.open(BytesIO(response.content))
                    st.image(img_to_solve, caption="תמונה מקישור", width=340)
            except Exception as e:
                st.error(f"לא ניתן לטעון תמונה: {e}")

    action = st.text_input("הנחיה לפיתרון:", value="פתור והסבר שלב אחרי שלב בצורה ברורה ומדויקת")
    
    if st.button("פענח ופתור ⚡", use_container_width=True):
        if not photo_topic.strip():
            st.warning("נא לציין מקצוע או נושא.")
        elif img_to_solve is None:
            st.warning("נא לספק תמונה תחילה.")
        else:
            with st.spinner("מפענח את התמונה ומחשב פתרון..."):
                try:
                    prompt = f"התלמיד ב-{student_context}. החומר: {photo_topic}. הנחיה: {action}. {anti_yap_rule}"
                    res = generate_ai([prompt, img_to_solve])
                    st.markdown("""<div class="clean-box"><h3>פתרון מפורט:</h3></div>""", unsafe_allow_html=True)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה בפענוח: {e}")

# ----------------- 3. מחולל מבחני דמה -----------------
elif room == "📝 מחולל מבחני דמה (Mock Exam)":
    st.title("📝 מחולל מבחני דמה מלאים (Mock Exam)")
    st.caption("סימולציית מבחן אינטראקטיבית עם בדיקה אוטומטית לפי מחוון.")
    
    with st.expander("⚙️ הגדרות מבחן הדמה", expanded=(st.session_state.mock_exam_data is None)):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            exam_subject = st.selectbox("מקצוע המבחן:", [
                "מתמטיקה", "היסטוריה", "אזרחות", "אנגלית", "תנ\"ך", "לשון והבעה", "ביולוגיה", "פיזיקה", "מדעי המחשב", chosen_major
            ])
            exam_topic = st.text_input("הנושא המדויק של המבחן:", placeholder="למשל: סדרות חשבוניות, העלייה השנייה, חוקי ניוטון...")
        with col_m2:
            q_count = st.slider("מספר שאלות במבחן:", 2, 5, 3)
            exam_level = st.select_slider("רמת קושי:", ["בסיסית", "רמת מבחן כיתתי", "רמת בגרות מלאה"], value="רמת מבחן כיתתי")
            
        if st.button("🔨 צור לי מבחן דמה עכשיו!", use_container_width=True):
            if not exam_topic.strip():
                st.warning("חובה לציין את הנושא למבחן!")
            else:
                prompt_gen = (
                    f"אתה מורה שבונה מבחן דמה לתלמיד ב-{student_context}.\n"
                    f"מקצוע: {exam_subject}, נושא: {exam_topic}, רמה: {exam_level}, מספר שאלות: {q_count}.\n"
                    "בנה מבחן דמה והחזר אך ורק מערך JSON תקין (ללא הערות מסביב):\n"
                    "[\n"
                    "  {\n"
                    '    "id": 1,\n'
                    '    "type": "multiple_choice",\n'
                    '    "question": "ניסוח השאלה כאן",\n'
                    '    "points": 30,\n'
                    '    "options": ["אפשרות א", "אפשרות ב", "אפשרות ג", "אפשרות ד"],\n'
                    '    "correct_answer": "אפשרות א",\n'
                    '    "explanation": "הסבר מפורט למה זו התשובה"\n'
                    "  },\n"
                    "  {\n"
                    '    "id": 2,\n'
                    '    "type": "open",\n'
                    '    "question": "ניסוח שאלה פתוחה",\n'
                    '    "points": 35,\n'
                    '    "ideal_answer": "תשובה מושלמת לפי מחוון"\n'
                    "  }\n"
                    "]"
                )
                with st.spinner("מרכיב את מבחן הדמה שלך..."):
                    try:
                        res = generate_ai(prompt_gen)
                        st.session_state.mock_exam_data = extract_json(res.text)
                        st.session_state.exam_submitted = False
                        st.success("המבחן מוכן! ענה על השאלות למטה.")
                    except Exception as e:
                        st.error(f"שגיאה ביצירת המבחן: {e}")

    if st.session_state.mock_exam_data:
        st.markdown("---")
        st.subheader("📋 טופס מבחן הדמה שלך:")
        
        user_answers = {}
        for q in st.session_state.mock_exam_data:
            st.markdown(f"""
                <div class="clean-box">
                    <h4 style="margin-top:0; color: #1e3a8a;">שאלה {q['id']} ({q.get('points', 25)} נקודות)</h4>
                    <p style="font-size: 1.05rem; margin-bottom: 0;">{q['question']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if q["type"] == "multiple_choice":
                user_answers[q["id"]] = st.radio(
                    f"בחר תשובה לשאלה {q['id']}:",
                    q["options"],
                    key=f"mcq_{q['id']}",
                    index=None
                )
            else:
                user_answers[q["id"]] = st.text_area(
                    f"כתוב את תשובתך לשאלה {q['id']}:",
                    key=f"open_{q['id']}",
                    height=90
                )
            st.write("")

        col_sub1, col_sub2 = st.columns([2, 1])
        with col_sub1:
            if st.button("🏁 הגש את מבחן הדמה ובדוק לי ציון!", use_container_width=True):
                st.session_state.exam_submitted = True
                st.session_state.submitted_answers = user_answers
        with col_sub2:
            if st.button("🔄 התחל מבחן חדש מאפס", use_container_width=True):
                st.session_state.mock_exam_data = None
                st.session_state.exam_submitted = False
                st.rerun()

        if st.session_state.exam_submitted:
            st.markdown("---")
            with st.spinner("הבוחן בודק את המבחן ומחשב ציון..."):
                try:
                    prompt_grade = (
                        f"אתה בוחן משרד החינוך שמעריך מבחן דמה עבור תלמיד ב-{student_context}.\n"
                        f"טופס המבחן והמחוון:\n{json.dumps(st.session_state.mock_exam_data, ensure_ascii=False)}\n\n"
                        f"תשובות התלמיד:\n{json.dumps(st.session_state.submitted_answers, ensure_ascii=False)}\n\n"
                        "החזר דוח ציונים מפורט בעברית הכולל:\n"
                        "1. ציון סופי משוקלל מתוך 100\n"
                        "2. פירוט עבור כל שאלה: כמה נקודות קיבל, מה היה נכון, מה היה שגוי, ואיך מנסחים תשובת 100 מושלמת לפי מחוון\n"
                        "3. טיפ זהב אחד להצלחה במבחן האמיתי"
                    )
                    res_feedback = generate_ai(prompt_grade)
                    st.markdown("""
                        <div class="clean-box" style="border-right: 4px solid #10b981;">
                            <h2 style="color: #059669; margin: 0;">🎉 תוצאות מבחן הדמה שלך</h2>
                            <p style="color: #64748b; margin: 4px 0 0 0;">דוח בדיקה מלא ומחוון ציונים:</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(res_feedback.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 4. ספריית וידאו עשירה -----------------
elif room == "🎬 ספריית וידאו ושיעורים ענקית":
    st.title("🎬 ספריית וידאו ושיעורים ענקית")
    st.caption("שיעורים ממוקדים לצפייה ישירה ומסודרת.")
    
    category = st.selectbox("בחר מקצוע או תחום לימוד:", [
        "מתמטיקה: גאומטריה ופיתגורס",
        "מתמטיקה: אלגברה וחדו\"א",
        "אנגלית: זמנים ודקדוק (Grammar)",
        "מגמת מדעי המחשב: יסודות תכנות ואלגוריתמיקה",
        "מגמות מדעיות: ביולוגיה ופיזיקה",
        "מגמות חברה ועסקים: פסיכולוגיה, סוציולוגיה, כלכלה וניהול",
        "מגמות אמנותיות: קולנוע, צילום ואמנות",
        "מקצועות הומניים: היסטוריה, אזרחות ולשון"
    ])
    
    video_db = {
        "מתמטיקה: גאומטריה ופיתגורס": {
            "משפט פיתגורס - בסיס וחישוב צלעות": "https://www.youtube.com/watch?v=xAgLlIAum3c",
            "משפט תאלס והרחבותיו": "https://www.youtube.com/watch?v=sI3q6Q_Hk84",
            "טריגונומטריה במשולש ישר זווית (Sin, Cos, Tan)": "https://www.youtube.com/watch?v=aa7bC_rFq4c"
        },
        "מתמטיקה: אלגברה וחדו\"א": {
            "משוואות ממעלה ראשונה עם סוגריים ושברים": "https://www.youtube.com/watch?v=lj6ONyl932A",
            "משוואה ריבועית ונוסחת שורשים": "https://www.youtube.com/watch?v=fghk_W4x_eM",
            "חקירת פונקציות ונגזרות (מבוא לחדו\"א)": "https://www.youtube.com/watch?v=5yflv3j7T30"
        },
        "אנגלית: זמנים ודקדוק (Grammar)": {
            "זמנים בסיסיים: Present Simple vs Progressive": "https://www.youtube.com/watch?v=L9AWrJnhsRI",
            "עבר פשוט ועבר ממושך (Past Simple & Continuous)": "https://www.youtube.com/watch?v=0k53_u1N9Yk",
            "כתיבת חיבור דעה מושלם (Opinion Essay)": "https://www.youtube.com/watch?v=7P_k3j_4X4w"
        },
        "מגמת מדעי המחשב: יסודות תכנות ואלגוריתמיקה": {
            "מבוא לתכנות ולולאות (For / While)": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
            "מערכים ומחרוזות בקלות": "https://www.youtube.com/watch?v=xk4_1vDrzzo"
        },
        "מגמות מדעיות: ביולוגיה ופיזיקה": {
            "שלושת חוקי ניוטון בפיזיקה": "https://www.youtube.com/watch?v=kKKM8Y-u7ds",
            "מבנה התא, ממברנה ופוטוסינתזה (ביולוגיה)": "https://www.youtube.com/watch?v=68_jtXv9k4c"
        },
        "מגמות חברה ועסקים: פסיכולוגיה, סוציולוגיה, כלכלה וניהול": {
            "פסיכולוגיה: תיאוריית הצרכים של מאסלו": "https://www.youtube.com/watch?v=O-4ithG_07Q",
            "כלכלה: ביקוש, היצע ושיווי משקל שוק": "https://www.youtube.com/watch?v=g9aDizJpd_s"
        },
        "מגמות אמנותיות: קולנוע, צילום ואמנות": {
            "קולנוע וצילום: זוויות צילום ומשמעותן (Camera Angles)": "https://www.youtube.com/watch?v=7y90UqWIdvU",
            "אמנות: שפת האמנות וקומפוזיציה": "https://www.youtube.com/watch?v=sOvhb2k1l_8"
        },
        "מקצועות הומניים: היסטוריה, אזרחות ולשון": {
            "היסטוריה: הגורמים למלחמת העולם הראשונה": "https://www.youtube.com/watch?v=SLj5r2nZHB8",
            "אזרחות: שלטון החוק וזכויות אדם": "https://www.youtube.com/watch?v=cMKe0k_k1Qk"
        }
    }
    
    current_videos = video_db.get(category, {})
    chosen_video_title = st.selectbox("בחר שיעור ספציפי:", list(current_videos.keys()))
    selected_url = current_videos[chosen_video_title]
    
    col_play, col_notes = st.columns([1.25, 0.75])
    with col_play:
        st.video(selected_url)
        st.markdown(f"[🔗 לחץ כאן לצפייה ישירה ב-YouTube]({selected_url})")
    with col_notes:
        st.subheader("📝 סיכום נקודתי")
        if st.button("סכם לי את עיקרי הנושא בבולטים ⚡", use_container_width=True):
            prompt = f"סכם ב-4 בולטים ברורים את הנושא: {chosen_video_title} עבור תלמיד ב-{chosen_grade} במגמת {chosen_major}. {anti_yap_rule}"
            with st.spinner("מחלץ סיכום..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 5. חיבור ל-Classroom וספרי לימוד -----------------
elif room == "🏫 חיבור ל-Classroom וספרי לימוד":
    st.title("🏫 חיבור לבית הספר: Classroom & ספרי לימוד")
    st.write("גישה מהירה לפורטלים הלימודיים ומפענח מטלות חכם:")
    
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <a class="portal-tag-learnit" href="https://classroom.google.com" target="_blank">🌐 Google Classroom</a>
            <a class="portal-tag-learnit" href="https://www.classoos.com" target="_blank">📖 Classoos (ספרי לימוד)</a>
            <a class="portal-tag-learnit" href="https://my.education.gov.il" target="_blank">🏛️ פורטל משרד החינוך</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📥 מפענח מטלות ושיעורי בית מהמורה")
    teacher_post = st.text_area("הדבק כאן את נוסח המטלה / ההודעה מ-Classroom:", height=120)
    
    if st.button("פרק לי את המטלה למשימות ושלבי ביצוע 📋", use_container_width=True):
        if not teacher_post.strip():
            st.warning("הדבק קודם את הודעת המורה!")
        else:
            prompt = (
                f"התלמיד ב-{student_context} קיבל את הודעת המטלה הבאה:\n{teacher_post}\n\n"
                "בצע פירוק חכם:\n"
                "1. מה נדרש להגיש ומתי (דד-ליין מדויק)\n"
                "2. אילו ספרים, עמודים או תרגילים צריך לפתור\n"
                "3. תוכנית פעולה מהירה שלב אחרי שלב כדי לסיים את זה מהר\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנתח מטלה..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 6. דפי תרגול ומבחנים להדפסה -----------------
elif room == "🖨️ דפי תרגול ומבחנים להדפסה":
    st.title("🖨️ מחולל דפי עבודה ותרגול להדפסה")
    st.caption("הפקת דפי תרגול נקיים המוכנים להדפסה ישירה במדפסת ביתית.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        sheet_topic = st.text_input("📚 מה נושא דף התרגול?", placeholder="למשל: תורשה וגנטיקה, משוואות ריבועיות...")
        sheet_subject = st.selectbox("מקצוע / מגמה:", [
            "מתמטיקה", "אנגלית", "מדעי המחשב", "ביולוגיה", "פיזיקה", "פסיכולוגיה", "סוציולוגיה", "כלכלה", "ניהול עסקי", "קולנוע ותקשורת", "צילום", "אמנות", "היסטוריה / אזרחות / תנ\"ך", "לשון"
        ])
    with col_p2:
        sheet_length = st.selectbox("היקף הדף:", ["דף עבודה מהיר (4-5 שאלות)", "מבחן מלא (8-10 שאלות כולל ניקוד)"])
        include_answers = st.checkbox("הוסף דף תשובות ומחוון בסוף הדף", value=True)

    if st.button("ייצר דף תרגול להדפסה 📄", use_container_width=True):
        if not sheet_topic.strip():
            st.warning("חובה לציין את נושא דף התרגול!")
        else:
            prompt = (
                f"צור דף תרגול ומבחן מקצועי ומעוצב בעברית לתלמיד ב-{student_context}.\n"
                f"מקצוע/מגמה: {sheet_subject}, נושא: {sheet_topic}, היקף: {sheet_length}.\n"
                "מבנה הדף:\n"
                "1. כותרת עליונה עם שם המבחן/הדף, כיתה, מגמה ומקום לשם תלמיד וציון.\n"
                "2. שאלות מנוסחות ברמה גבוהה לפי מחוון משרד החינוך עם מקום מסומן לתשובה.\n"
                + ("3. בסוף הדף: מחוון תשובות מלא ומדויק לבדיקה עצמית.\n" if include_answers else "")
            )
            with st.spinner("מייצר דף עבודה..."):
                try:
                    res = generate_ai(prompt)
                    st.session_state["printable_sheet"] = res.text
                except Exception as e:
                    st.error(f"שגיאה: {e}")

    if "printable_sheet" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state["printable_sheet"])
        st.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <button onclick="window.print()" style="padding: 12px 24px; font-size: 16px; background-color: #1e3a8a; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: 800;">
                    🖨️ הדפס דף תרגול זה (Print)
                </button>
            </div>
        """, unsafe_allow_html=True)

# ----------------- 7. מלטשת תשובות -----------------
elif room == "💯 מלטשת תשובות למאיות":
    st.title("💯 מלטשת תשובות לציון 100")
    st.caption("שדרוג והתאמת ניסוח התשובה לפי מחווני הבדיקה של משרד החינוך.")
    
    ans_topic = st.text_input("📚 מה החומר והמקצוע/המגמה?", placeholder="למשל: סוציולוגיה, אזרחות, היסטוריה...")
    q_text = st.text_input("❓ מה השאלה שנשאלת?")
    user_ans = st.text_area("✍️ מה התשובה שכתבת:", height=120)
    
    if st.button("שדרג לי את התשובה ל-100 🚀", use_container_width=True):
        if not ans_topic.strip() or not user_ans.strip():
            st.warning("מלא את החומר הנלמד ואת התשובה שכתבת!")
        else:
            prompt = (
                f"אתה מעריך בחינות ובגרויות קפדן שבודק תשובה של תלמיד ב-{student_context}.\n"
                f"החומר: {ans_topic}\nשאלה: {q_text}\nתשובה: {user_ans}\n\n"
                "החזר:\n1. ציון מוערך (מתוך 100)\n2. מה חסר לפי מחוון הבדיקה\n3. תשובה מושלמת סופית: נוסח שסוגר את מלוא הנקודות.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנתח לפי מחוון..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown("""<div class="clean-box"><h3>משוב ושדרוג:</h3></div>""", unsafe_allow_html=True)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 8. מעבדת מתמטיקה -----------------
elif room == "📐 מעבדת מתמטיקה ומדעים":
    st.title("📐 מעבדת פירוק מתמטיקה ומדעים")
    st.caption(f"פתרון צעד-אחר-צעד עם נימוקים מותאם לרמת {math_units}.")
    
    math_topic = st.text_input("📚 מה הנושא הנלמד כרגע?", placeholder="חקירת פולינום, טריגו, תנועה בפיזיקה...")
    math_input = st.text_area("🔢 הזן את התרגיל או השאלה:", height=110)
    
    if st.button("פרק לי את התרגיל לפי רמת היחידות 🧠", use_container_width=True):
        if not math_topic.strip() or not math_input.strip():
            st.warning("ציין את הנושא ואת התרגיל!")
        else:
            prompt = (
                f"פתור את התרגיל הבא עבור תלמיד ב-{student_context}.\n"
                f"הנושא: {math_topic}\nתרגיל: {math_input}\n\n"
                "פתור שלב אחרי שלב בבירור עם נימוק קצר ליד כל שלב, וסמן תוצאה סופית מודגשת.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner(f"פותר לפי רמת {math_units}..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 9. שליף חירום -----------------
elif room == "🚨 שליף חירום (לפני מבחן)":
    st.title("🚨 שליף חירום: 60 שניות לפני מבחן")
    st.caption("נקודות ברזל קריטיות שחובה לדעת רגע לפני שנכנסים לכיתה.")
    
    panic_topic = st.text_input("📚 מה החומר / הנושא של המבחן כרגע?", placeholder="משפט חוצה זווית, שיווי משקל שוק, גנטיקה...")
    
    if st.button("הצל אותי עכשיו ⚡", use_container_width=True):
        if not panic_topic.strip():
            st.warning("הזן קודם את החומר הנלמד!")
        else:
            prompt = (
                f"התלמיד ב-{student_context} נכנס בעוד דקה למבחן על החומר: {panic_topic}.\n"
                "החזר אך ורק:\n1. 3 משפטי זהב שחייבים לרשום במבחן.\n2. הטעות הנפוצה ביותר שתלמידים נופלים בה.\n3. מושג חובה אחד שהבוחן מחפש בעין.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מחלץ שליף..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(f'<div class="cheat-learnit">{res.text}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 10. מתכנן לו״ז -----------------
elif room == "📅 מתכנן לו״ז למבחן":
    st.title("📅 מתכנן לוח זמנים אישי למבחן")
    topics = st.text_area("📚 מה כל החומר והנושאים שצריך להספיק למבחן?", placeholder="פרקים 1 עד 4 בספר, שאלות בגרות...")
    c1, c2 = st.columns(2)
    with c1:
        exam_subj = st.text_input("מקצוע או מגמה:", placeholder="מתמטיקה / ביולוגיה / פיזיקה...")
        days = st.number_input("כמה ימים נשארו עד המבחן?", min_value=1, max_value=30, value=3, step=1)
    with c2:
        hours_selected = st.select_slider(
            "כמה שעות למידה פנויות יש לך בכל יום?",
            options=["1 שעה ביום", "2 שעות ביום", "3 שעות ביום", "4 שעות ביום", "5 שעות ביום", "6 שעות ביום"],
            value="2 שעות ביום"
        )
        
    if st.button("בנה לי תוכנית עבודה 🗓️", use_container_width=True):
        if not topics.strip():
            st.warning("הזן קודם את החומר הנלמד!")
        else:
            prompt = (
                f"בנה לוח זמנים פרקטי ללימוד למבחן עבור תלמיד ב-{student_context}.\n"
                f"מקצוע: {exam_subj}, ימים שנותרו: {days}, שעות למידה פנויות: {hours_selected}, חומר: {topics}.\n"
                "חלק את המשימות בצורה הגיונית לפי ימים, כולל זמני מנוחה ותרגול מעשי."
            )
            with st.spinner("מתכנן לו״ז..."):
                try:
                    res = generate_ai(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ----------------- 11. חוות דעת -----------------
elif room == "⭐ חוות דעת והצעות":
    st.title("⭐ חוות דעת והצעות לשיפור")
    st.caption("נשמח לשמוע איך המערכת עובדת עבורך ומה עוד כדאי להוסיף.")
    
    with st.form("feedback_form", clear_on_submit=True):
        fb_name = st.text_input("שם או כינוי:")
        fb_grade = st.selectbox("כיתה:", ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב"], index=2)
        fb_major = st.text_input("מגמה (אם יש):", value=chosen_major)
        fb_rating = st.slider("דירוג החוויה שלך (כוכבים):", min_value=1, max_value=5, value=5)
        fb_text = st.text_area("מה דעתך על האתר? מה כדאי להוסיף או לשפר?")
        submitted = st.form_submit_button("שלח חוות דעת 🚀")
        
        if submitted:
            if not fb_text.strip():
                st.warning("כתוב משהו לפני השליחה!")
            else:
                grade_display = f"{fb_grade} ({fb_major})" if fb_major.strip() else fb_grade
                st.session_state.reviews.insert(0, {
                    "name": fb_name if fb_name.strip() else "אנונימי",
                    "grade": grade_display,
                    "rating": fb_rating,
                    "text": fb_text
                })
                st.success("תודה על חוות הדעת! המשוב שלך נוסף בהצלחה.")
                st.balloons()

    st.markdown("---")
    st.subheader("💬 מה שתלמידים אומרים על The Dan Method:")
    for r in st.session_state.reviews:
        stars = "⭐" * r["rating"]
        st.markdown(f"""
            <div class="clean-box">
                <b>{r['name']}</b> ({r['grade']}) — {stars}<br>
                <span style="color: #475569;">{r['text']}</span>
            </div>
        """, unsafe_allow_html=True)
