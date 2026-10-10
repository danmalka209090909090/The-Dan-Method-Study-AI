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
    page_title="The Dan Method",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# סגנון Dark Dashboard מודרני ונקי
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Assistant', -apple-system, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    .stApp {
        direction: rtl;
        text-align: right;
        background-color: #0b0f17;
        color: #f8fafc;
    }

    [data-testid="stSidebar"] {
        background-color: #0d131f !important;
        border-left: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 36px 20px 20px 20px;
        max-width: 850px;
        margin: 0 auto;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.1);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 14px;
    }
    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 25px;
    }

    /* Cards Grid */
    .tool-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.2s ease;
    }
    .tool-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
    }
    .card-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: #1e293b;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 14px;
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 6px;
    }
    .card-desc {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 0;
    }

    /* טבלת השוואה: The Dan Method מול AI רגיל */
    .compare-container {
        margin-top: 40px;
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 26px;
    }
    .compare-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        text-align: right;
    }
    .compare-table th {
        padding: 12px;
        border-bottom: 1px solid #1f2937;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .compare-table td {
        padding: 14px 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.95rem;
    }
    .col-highlight {
        color: #38bdf8;
        font-weight: 600;
    }
    .col-regular {
        color: #94a3b8;
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
if "zoom_chat_history" not in st.session_state:
    st.session_state.zoom_chat_history = []
if "mock_exam_data" not in st.session_state:
    st.session_state.mock_exam_data = None
if "exam_submitted" not in st.session_state:
    st.session_state.exam_submitted = False

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ מפתח GEMINI_API_KEY חסר בהגדרות ה-Secrets.")
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

# סרגל צד
with st.sidebar:
    st.caption("בס״ד")
    st.title("The Dan Method ⚡")
    st.caption("למידה מבוססת מחוון ישראלי")
    st.markdown("---")
    
    st.subheader("פרופיל לימודי")
    chosen_grade = st.selectbox("שכבה:", ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב"], index=2)
    math_level = st.selectbox("מתמטיקה:", ["הקבצה א' / מצוינות / 5 יח'", "הקבצה ב' / 4 יח'", "רמה רגילה / 3 יח'"])
    chosen_major = st.selectbox("מסלול לימוד:", ["מקצועות ליבה", "מדעי המחשב וסייבר", "ביולוגיה ומדעים", "פיזיקה", "כלכלה ומנהל"])
    
    st.markdown("---")
    st.subheader("ניווט")
    nav_mode = st.radio("מעבר לכלי:", [
        "דף הבית (לוח בקרה)",
        "שיעור פרטי 1-על-1",
        "סורק תרגילים ודפי עבודה",
        "מבחני דמה ומחוון",
        "מפרק מתמטיקה ומדעים",
        "שליף חירום למבחן",
        "דפי תרגול להדפסה"
    ])

student_context = f"{chosen_grade}, {math_level}, מגמה: {chosen_major}"

# ---------------- 1. דף הבית ----------------
if nav_mode == "דף הבית (לוח בקרה)":
    st.markdown("""
        <div class="hero-container">
            <span class="hero-badge">גרסה ממוקדת מבחנים</span>
            <div class="hero-title">The Dan Method</div>
            <div class="hero-subtitle">
                בלי סיכומים ארוכים, בלי הסברים מייגעים. מקבלים בדיוק את מה שצריך כדי לסגור מאיות במבחנים ובגרויות בזמן הקצר ביותר.
            </div>
        </div>
    """, unsafe_allow_html=True)

    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        st.markdown("""
            <div class="tool-card">
                <div>
                    <div class="card-icon">⚡</div>
                    <div class="card-title">שיעור פרטי מהיר</div>
                    <div class="card-desc">המורה מיה מסבירה ישירות לנקודה בלי יאפ ובלי חפירות מיותרות.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with r1c2:
        st.markdown("""
            <div class="tool-card">
                <div>
                    <div class="card-icon">📸</div>
                    <div class="card-title">סורק תרגילים</div>
                    <div class="card-desc">מעלים תמונה של שיעורי בית או דף עבודה ומקבלים פתרון שלב אחר שלב.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with r1c3:
        st.markdown("""
            <div class="tool-card">
                <div>
                    <div class="card-icon">📝</div>
                    <div class="card-title">מבחני דמה</div>
                    <div class="card-desc">סימולציה עם שאלות אמריקאיות ופתוחות ובדיקה מחמירה לפי מחוון משרד החינוך.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        st.markdown("""
            <div class="tool-card">
                <div>
                    <div class="card-icon">📐</div>
                    <div class="card-title">מפרק מתמטיקה</div>
                    <div class="card-desc">פתרונות מפורטים בדיוק לרמת ההקבצה והיחידות שלך עם כל הנימוקים.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with r2c2:
        st.markdown("""
            <div class="tool-card">
                <div>
                    <div class="card-icon">🔥</div>
                    <div class="card-title">שליף חירום</div>
                    <div class="card-desc">כל הנוסחאות, הדגשים והשאלות שחובה לדעת בול 10 דקות לפני הכניסה לכיתה.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with r2c3:
        st.markdown("""
            <div class="tool-card">
                <div>
                    <div class="card-icon">✨</div>
                    <div class="card-title">מלטשת תשובות</div>
                    <div class="card-desc">מדביקים ניסוח תשובה רגיל ומקבלים תשובת מחוון מושלמת ששווה 100 עגול.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # טבלת השוואה
    st.markdown("""
        <div class="compare-container">
            <h3 style="margin-top: 0; color: #ffffff; font-size: 1.25rem;">למה The Dan Method ולא סתם ChatGPT / Claude?</h3>
            <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;">AI גנרי נותן תשובות ארוכות מדי, לא מכיר את המחוונים הישראליים וסתם מבזבז לך זמן.</p>
            <table class="compare-table">
                <thead>
                    <tr>
                        <th>תכונה</th>
                        <th style="color: #38bdf8;">The Dan Method ⚡</th>
                        <th>מודל AI רגיל</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>התאמה למערכת החינוך</strong></td>
                        <td class="col-highlight">מכויל בול לפי מחווני בגרות, הקבצות וכיתות ז'-י"ב</td>
                        <td class="col-regular">תשובות כלליות מהאינטרנט באנגלית שתורגמו לעברית</td>
                    </tr>
                    <tr>
                        <td><strong>אורך המענה והיעילות</strong></td>
                        <td class="col-highlight">מצב תכל'ס (No Yap) – פירוק מדויק ב-3 שורות או שלבים</td>
                        <td class="col-regular">פסקאות פתיחה וסיום ארוכות, דיבור מנופח וחפירות</td>
                    </tr>
                    <tr>
                        <td><strong>בדיקת מבחנים וציונים</strong></td>
                        <td class="col-highlight">חישוב ציון אמיתי עם הורדת נקודות לפי נימוקים חסרים</td>
                        <td class="col-regular">סתם מחמיא לתשובה בלי לתת ניקוד מספרי מדויק</td>
                    </tr>
                    <tr>
                        <td><strong>הכנה של 10 דקות לפני מבחן</strong></td>
                        <td class="col-highlight">שליפי חירום מרוכזים ודפי עבודה נקיים להדפסה</td>
                        <td class="col-regular">מייצר טקסטים ענקיים שאי אפשר לקרוא בלחץ</td>
                    </tr>
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)

# ---------------- 2. שיעור פרטי ----------------
elif nav_mode == "שיעור פרטי 1-על-1":
    st.title("שיעור פרטי עם המורה מיה")
    st.caption(f"מותאם עבור: {student_context}")
    
    col_tutor, col_chat = st.columns([1, 2])
    with col_tutor:
        st.markdown("""
            <div style="background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 24px; text-align: center;">
                <div style="font-size: 50px; margin-bottom: 10px;">👩‍🏫</div>
                <h3 style="margin: 0; color: #fff;">המורה מיה</h3>
                <p style="color: #10b981; font-size: 0.85rem; margin-top: 4px;">● זמינה בשיעור</p>
            </div>
        """, unsafe_allow_html=True)
        t_sub = st.selectbox("נושא השיעור:", ["מתמטיקה", "היסטוריה", "אזרחות", "אנגלית", "מדעים / ביולוגיה", chosen_major])
    
    with col_chat:
        chat_box = st.container(height=350)
        with chat_box:
            if not st.session_state.zoom_chat_history:
                st.write(f"👋 **המורה מיה:** היי! בוא נפתח את {t_sub}. איזה תרגיל או נושא לא יושב לך ב-100%?")
            for m in st.session_state.zoom_chat_history:
                with st.chat_message(m["role"]):
                    st.write(m["content"])
        
        user_input = st.chat_input("שאל את מיה שאלה קצרה...")
        if user_input:
            st.session_state.zoom_chat_history.append({"role": "user", "content": user_input})
            prompt = f"את המורה מיה. התלמיד ב-{student_context}. נושא: {t_sub}. עני ב-2-3 משפטים ממוקדים בלי שום חפירה, ישר לעניין. שאלה: {user_input}"
            with st.spinner("עונה..."):
                res = generate_ai(prompt)
                st.session_state.zoom_chat_history.append({"role": "assistant", "content": res.text})
                st.rerun()

# ---------------- 3. סורק תרגילים ----------------
elif nav_mode == "סורק תרגילים ודפי עבודה":
    st.title("סורק תרגילים")
    st.caption("פתרון שלב-אחר-שלב מתמונה")
    
    file = st.file_uploader("העלה תמונת תרגיל מהמחברת או הספר:", type=["png", "jpg", "jpeg"])
    if file:
        img = Image.open(file)
        st.image(img, width=320)
        if st.button("פענח ופתור", use_container_width=True):
            with st.spinner("מנתח..."):
                res = generate_ai([f"פתור את התרגיל שלב-אחר-שלב בצורה חדה לפי מחוון {student_context}", img])
                st.markdown("### פתרון:")
                st.markdown(res.text)

# ---------------- 4. מבחני דמה ----------------
elif nav_mode == "מבחני דמה ומחוון":
    st.title("מבחן דמה מותאם מחוון")
    subj = st.text_input("איזה נושא נבחן?", placeholder="למשל: סדרות חשבוניות, הצהרת בלפור...")
    if st.button("ייצר שאלון קצר"):
        if not subj.strip():
            st.warning("נא לציין נושא.")
        else:
            prompt = f"צור 2 שאלות מבחן (אחת אמריקאית ואחת פתוחה) בנושא {subj} עבור {student_context} כולל מחוון מלא."
            with st.spinner("מייצר מבחן..."):
                res = generate_ai(prompt)
                st.markdown(res.text)

# ---------------- 5. מפרק מתמטיקה ----------------
elif nav_mode == "מפרק מתמטיקה ומדעים":
    st.title("מפרק תרגילים")
    t_text = st.text_area("הדבק או הקלד את השאלה/משוואה:", height=100)
    if st.button("פרק לצעדים", use_container_width=True):
        if t_text.strip():
            with st.spinner("מפרק..."):
                res = generate_ai(f"פרק לצעדים ברורים עם נימוק מתמטי קצר עבור {student_context}: {t_text}")
                st.markdown(res.text)

# ---------------- 6. שליף חירום ----------------
elif nav_mode == "שליף חירום למבחן":
    st.title("שליף חירום (10 דקות לפני מבחן)")
    topic_quick = st.text_input("נושא המבחן:", placeholder="למשל: טריגונומטריה במישור, המהפכה התעשייתית...")
    if st.button("הפק שליף ממוקד"):
        if topic_quick.strip():
            with st.spinner("מייצר שליף..."):
                res = generate_ai(f"הפק שליף חירום מרוכז לתלמיד ב-{student_context} בנושא {topic_quick}. הצג אך ורק נוסחאות, מלכודות נפוצות במבחן והגדרות חובה בבולטים.")
                st.markdown(res.text)

# ---------------- 7. דפי תרגול להדפסה ----------------
elif nav_mode == "דפי תרגול להדפסה":
    st.title("דפי תרגול להדפסה")
    st.caption("הפקת דפי עבודה נקיים שמוכנים להדפסה במדפסת ביתית.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        sheet_topic = st.text_input("נושא דף התרגול:", placeholder="למשל: משוואות ריבועיות, גנטיקה...")
        sheet_subject = st.selectbox("מקצוע:", ["מתמטיקה", "אנגלית", "מדעי המחשב", "ביולוגיה", "היסטוריה", "לשון"])
    with col_p2:
        sheet_length = st.selectbox("היקף הדף:", ["דף תרגול קצר (4-5 שאלות)", "מבחן מלא כולל ניקוד"])
        include_answers = st.checkbox("הוספת דף תשובות בסוף", value=True)

    if st.button("ייצר דף תרגול", use_container_width=True):
        if not sheet_topic.strip():
            st.warning("נא להזין נושא.")
        else:
            prompt = (
                f"צור דף תרגול ומבחן מעוצב וברור בעברית לתלמיד ב-{student_context}.\n"
                f"מקצוע: {sheet_subject}, נושא: {sheet_topic}, היקף: {sheet_length}.\n"
                "מבנה הדף:\n"
                "1. כותרת עליונה עם שם הדף, כיתה ומקום לציון ולשם תלמיד.\n"
                "2. שאלות מנוסחות ברמות קושי עולות עם מקום לתשובה.\n"
                + ("3. בסוף הדף: מחוון תשובות מלא לבדיקה עצמית.\n" if include_answers else "")
            )
            with st.spinner("מרכיב דף עבודה..."):
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
                <button onclick="window.print()" style="padding: 10px 22px; font-size: 15px; background-color: #38bdf8; color: #0b0f17; border: none; border-radius: 8px; cursor: pointer; font-weight: 800;">
                    🖨️ הדפס דף תרגול
                </button>
            </div>
        """, unsafe_allow_html=True)
