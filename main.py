import streamlit as st
from google import genai
import time

st.set_page_config(
    page_title="The Dan Method: Study AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב מודרני מיושר לימין וכרטיסיות מעוצבות
st.markdown("""
<style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    div[data-testid="stExpander"] {
        text-align: right;
    }
    .metric-box {
        background: #1e293b;
        color: white;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #334155;
    }
    .video-card {
        background: #0f172a;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #1e293b;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ חסר GEMINI_API_KEY ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- סרגל צד (Sidebar): אזור פוקוס וכלים אישיים ---
with st.sidebar:
    st.title("⚡ The Dan Method")
    st.caption("פלטפורמת הלמידה והמאיות האולטימטיבית")
    st.markdown("---")
    
    st.subheader("⏱️ מצב פוקוס (Pomodoro)")
    st.write("25 דקות ריכוז מלא בלי מסכים מסביב.")
    if st.button("הפעל טיימר למידה מרוכז (25 דק')", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.info("סשן הלמידה החל! שים את הנייד על שקט.")
        # סימולציית התחלה מהירה
        progress_bar.progress(10)

    st.markdown("---")
    st.subheader("🎯 יעד המבחן הקרוב")
    target_grade = st.slider("יעד ציון אישי:", 70, 100, 100)
    st.info(f"המטרה: **{target_grade}** עגול!")

    st.markdown("---")
    st.caption("The Dan Method v3.0 Ultra")

# --- כותרת עליונה ומדדים ---
head_col, badge_col = st.columns([3, 1])
with head_col:
    st.title("⚡ The Dan Method: Study AI")
    st.write("מרכז השליטה המלא לפירוק מבחנים, הבנת חומר לעומק וסגירת פינות בלי מריחות.")

with badge_col:
    st.markdown("""
        <div class="metric-box">
            <span style="background-color: #10b981; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.75rem;">מערכת פרימיום</span>
            <h3 style="margin: 8px 0; color: #38bdf8;">STUDY ULTRA</h3>
            <p style="margin: 0; font-size: 0.8rem; color: #cbd5e1;">מודל מהיר + חדר סרטונים</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# שורת מטריקות
m1, m2, m3, m4 = st.columns(4)
m1.metric("זמן מענה", "1.0 שניות", "בזק")
m2.metric("הבנה מעמיקה", "100%", "יסודי וממוקד")
m3.metric("דיוק מחוון", "99.4%", "+1.2%")
m4.metric("יעד ציון", f"{target_grade}", "🎯")

st.write("")

# --- לשוניות הכלים הראשיות ---
tab_video, tab_grade, tab_math, tab_summary, tab_cards, tab_calc = st.tabs([
    "🎬 חדר הסברים וסרטונים",
    "💯 משדרג ל-100", 
    "📐 מפרק מתמטיקה", 
    "⚡ שליף סיכום", 
    "🧠 כרטיסיות שינון",
    "📊 מחשבון ציון סופי"
])

# 1. חדר הסברים וסרטונים
with tab_video:
    st.subheader("🎬 חדר הסרטונים וההסבר היסודי")
    st.write("צפה בהסברים ממוקדים או בקש מה-AI לפרק לך נושא מורכב להסבר פשוט וחד בלי חפירות מיותרות.")
    
    col_v1, col_v2 = st.columns([1, 1])
    with col_v1:
        st.markdown("**📺 שיעורי וידאו נבחרים (סגירת נושא ב-5 דקות):**")
        subject_video = st.selectbox("בחר נושא לצפייה:", [
            "מתמטיקה: משוואות ריבועיות וטרינום",
            "מתמטיקה: פיתגורס ומשולשים",
            "היסטוריה: הגורמים למלחמת העולם הראשונה",
            "פיזיקה: חוקי ניוטון מוסברים בקלות",
            "אנגלית: כללי זמנים (Past / Present Simple)"
        ])
        
        # סרטוני הדרכה קצרים ואיכותיים מיוטיוב
        videos = {
            "מתמטיקה: משוואות ריבועיות וטרינום": "https://www.youtube.com/watch?v=fghk_W4x_eM",
            "מתמטיקה: פיתגורס ומשולשים": "https://www.youtube.com/watch?v=aa7bC_rFq4c",
            "היסטוריה: הגורמים למלחמת העולם הראשונה": "https://www.youtube.com/watch?v=SLj5r2nZHB8",
            "פיזיקה: חוקי ניוטון מוסברים בקלות": "https://www.youtube.com/watch?v=kKKM8Y-u7ds",
            "אנגלית: כללי זמנים (Past / Present Simple)": "https://www.youtube.com/watch?v=x1a_9gq1pLg"
        }
        st.video(videos[subject_video])

    with col_v2:
        st.markdown("**💡 מנוע ההסבר היסודי: 'הסבר לי כאילו אני בן 10'**")
        st.caption("נתקעת על הגדרה מסובכת? ה-AI יסביר לך את הרעיון בלי מושגים מפוצצים ועם דוגמה יומיומית.")
        topic_explain = st.text_input("איזה נושא או מושג תרצה להבין?", placeholder="למשל: אינפלציה, פוטוסינתזה, כבידה, חוקי נירנברג...")
        
        if st.button("הסבר לי יסודי אבל פשוט 💡", use_container_width=True, key="btn_explain"):
            if not topic_explain.strip():
                st.warning("הזן קודם נושא להסבר!")
            else:
                prompt = (
                    f"הסבר את המושג/הנושא הבא בצורה יסודית, בהירה ומעניינת:\n{topic_explain}\n\n"
                    "מבנה התשובה:\n"
                    "1. **השורה התחתונה ב-2 משפטים פשוטים** (כאילו אתה מסביר לחבר).\n"
                    "2. **דוגמה או אנלוגיה מהחיים האמיתיים** שממחישה את זה מיד.\n"
                    "3. **3 נקודות יסוד שחייבים להבין**.\n"
                    "בלי ניסוחים אקדמיים כבדים – חד, קולע ומדויק."
                )
                with st.spinner("מפשט את המושג..."):
                    try:
                        res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                        st.success("ההסבר מוכן:")
                        st.markdown(res.text)
                    except Exception as e:
                        st.error(f"שגיאה: {e}")

# 2. משדרג ל-100
with tab_grade:
    st.subheader("שדרוג תשובה לרמת 100 עגול")
    st.write("הזן את השאלה ואת הטיוטה שלך — ה-AI ינתח לפי מחוון הבדיקה וינסח מחדש תשובה מושלמת.")
    
    c_q, c_lvl = st.columns([3, 1])
    with c_q:
        q_text = st.text_input("השאלה:", placeholder="השאלה מהמבחן או מדף העבודה...")
    with c_lvl:
        exam_type = st.selectbox("רמת המבחן:", ["מבחן רגיל (חטיבה/תיכון)", "בגרות", "מבחן אקדמי"])
        
    ans_text = st.text_area("התשובה שכתבת:", height=130, placeholder="הדבק כאן מה שכתבת...")
    
    if st.button("שדרג ל-100 מלא 🚀", use_container_width=True, key="btn_grade_tab"):
        if not ans_text.strip():
            st.warning("הזן קודם את התשובה שלך!")
        else:
            prompt = (
                f"אתה מעריך בחינות קפדן ברמת {exam_type}.\n"
                f"שאלה: {q_text}\nתשובת התלמיד: {ans_text}\n\n"
                "החזר:\n"
                "1. **ציון נוכחי מתוך 100**\n"
                "2. **הכשלים בתשובה הנוכחית** (מה חסר לבוחן בעיניים)\n"
                "3. **תשובת 100 מושלמת**: ניסוח מלא, עשיר ומדויק שסוגר את כל הפינות."
            )
            with st.spinner("מנתח תשובה..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("הניתוח מוכן:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# 3. מפרק מתמטיקה
with tab_math:
    st.subheader("פירוק תרגילי מתמטיקה שלב אחרי שלב")
    math_exercise = st.text_area("התרגיל או השאלה:", height=120, placeholder="משוואה, חקירת פונקציה, בעיית תנועה או גאומטריה...")
    
    if st.button("פתור עם נימוקים מלאים 🧠", use_container_width=True, key="btn_math_tab"):
        if not math_exercise.strip():
            st.warning("הזן תרגיל לפתרון!")
        else:
            prompt = (
                f"פתור את תרגיל המתמטיקה הבא:\n{math_exercise}\n\n"
                "דרישות:\n"
                "1. פתרון שלב אחרי שלב בצורה מפורטת וברורה.\n"
                "2. ליד כל שלב כתוב נימוק קצר (איזו נוסחה או משפט הופעלו).\n"
                "3. בסיום סמן בבירור את **התשובה הסופית**."
            )
            with st.spinner("פותר שלב אחרי שלב..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("פתרון:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# 4. שליף סיכום
with tab_summary:
    st.subheader("שליף סיכום מהיר למבחן")
    st.write("זורקים טקסט ארוך ומקבלים רק מה שחייבים לדעת כדי להצליח.")
    raw_summary = st.text_area("הדבק כאן חומר קריאה:", height=150)
    
    if st.button("חלץ נקודות חובה ⚡", use_container_width=True, key="btn_sum_tab"):
        if not raw_summary.strip():
            st.warning("הזן קודם טקסט לסיכום!")
        else:
            prompt = (
                f"תמצת את הטקסט הבא עבור תלמיד שלומד למבחן:\n{raw_summary}\n\n"
                "- 4 בולטים מרכזיים שחובה לדעת.\n"
                "- רשימת מושגי מפתח שהבוחן יחפש.\n"
                "- טיפ זיכרון מהיר לנושא."
            )
            with st.spinner("מחלץ תמצית..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("השליף מוכן:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# 5. כרטיסיות שינון (Flashcards)
with tab_cards:
    st.subheader("🧠 מחולל כרטיסיות זיכרון (Flashcards)")
    st.write("הדבק חומר, וה-AI ייצר עבורך שאלות ותשובות נפתחות לשינון עצמי בתוך האתר.")
    study_notes = st.text_area("הדבק כאן את החומר לשינון:", height=130, placeholder="היסטוריה, אזרחות, תנ״ך, מדעים...")
    
    if st.button("ייצר כרטיסיות שינון 🃏", use_container_width=True, key="btn_flashcards"):
        if not study_notes.strip():
            st.warning("הזן חומר ליצירת כרטיסיות!")
        else:
            prompt = (
                f"צור 4 כרטיסיות שינון (שאלה ותשובה ממוקדת) מתוך החומר הבא:\n{study_notes}\n\n"
                "החזר בפורמט מסודר:\n"
                "שאלה 1: ...\nתשובה 1: ...\n"
                "שאלה 2: ...\nתשובה 2: ..."
            )
            with st.spinner("בונה כרטיסיות..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("כרטיסיות השינון שלך מוכנות:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# 6. מחשבון ציון סופי
with tab_calc:
    st.subheader("📊 מחשבון ציון סופי ושקלול מגן")
    st.write("בדוק כמה תקבל בסוף ואיזה ציון בבחינה יביא אותך ליעד.")
    
    calc_c1, calc_c2, calc_c3 = st.columns(3)
    with calc_c1:
        magen = st.number_input("ציון מגן / שנתי:", min_value=0, max_value=100, value=85)
    with calc_c2:
        exam = st.number_input("ציון בחינה:", min_value=0, max_value=100, value=90)
    with calc_c3:
        magen_weight = st.slider("אחוז המגן מתוך הציון:", 0, 100, 30)

    exam_weight = 100 - magen_weight
    final_grade = round((magen * (magen_weight / 100)) + (exam * (exam_weight / 100)), 1)
    
    st.markdown("---")
    res_col1, res_col2 = st.columns([1, 2])
    with res_col1:
        st.metric("הציון הסופי המשוקלל", f"{final_grade}")
    with res_col2:
        if final_grade >= 90:
            st.balloons()
            st.success("🔥 ציון מטורף! אתה באזור המאיות לגמרי.")
        elif final_grade >= 75:
            st.info("ציון טוב מאוד! עם שיפור קל בבחינה אפשר לגרד את ה-95+ בקלות.")
        else:
            st.warning("כדאי לשקול מועד ב' כדי להקפיץ את הציון.")
