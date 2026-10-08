import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(
    page_title="The Dan Method: Study AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב מודרני מיושר לימין וכרטיסיות נקיות
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
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ חסר GEMINI_API_KEY ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- סרגל צד (Sidebar) ---
with st.sidebar:
    st.title("⚡ The Dan Method")
    st.caption("מערכת ה-AI לכל השכבות: כיתה ז' עד י״ב")
    st.markdown("---")
    
    grade_level = st.selectbox(
        "🎓 בחר את שכבת הגיל שלך:",
        ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב (בגרות)"],
        index=2
    )
    
    st.markdown("---")
    st.subheader("⏱️ טיימר ריכוז (25 דקות)")
    st.caption("פוקוס נקי בלי הסחות דעת.")
    if st.button("התחל סשן למידה 🚀", use_container_width=True):
        st.info(f"סשן פעיל עבור {grade_level}! שים טלפון על שקט ותתחיל לפוצץ חומר.")

    st.markdown("---")
    target_score = st.slider("🎯 יעד הציון שלך:", 70, 100, 100)
    st.success(f"מכוונים ל-{target_score} עגול!")

    st.markdown("---")
    st.caption("The Dan Method v4.0 Ultimate")

# --- כותרת ראשית ומדדים ---
col_h, col_b = st.columns([3, 1])
with col_h:
    st.title("⚡ The Dan Method: Study AI")
    st.write(f"מרכז הלימוד המקיף לכל המקצועות • מותאם כעת ל:**{grade_level}**")

with col_b:
    st.markdown("""
        <div class="metric-box">
            <span style="background-color: #f59e0b; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.75rem;">ULTIMATE</span>
            <h3 style="margin: 8px 0; color: #38bdf8;">ז' - י"ב</h3>
            <p style="margin: 0; font-size: 0.8rem; color: #cbd5e1;">סרטונים + פותר צילומים</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
m1.metric("שכבת לימוד פעילה", grade_level, "מותאם אישית")
m2.metric("זמן תגובה", "1.1 שנ'", "מהיר")
m3.metric("ספריית שיעורים", "עשרות סרטונים", "זמינים")
m4.metric("יעד אישי", f"{target_score}", "💯")

st.write("")

# --- לשוניות המערכת ---
t_vid, t_photo, t_ans, t_math, t_sum, t_plan, t_chat = st.tabs([
    "🎬 חדר סרטונים ושיעורים",
    "📸 פותר תמונות ומבחנים",
    "💯 משדרג ל-100",
    "📐 מפרק מתמטיקה",
    "⚡ שליף סיכום",
    "📅 בונה לו״ז למבחן",
    "💬 מורה פרטי צמוד"
])

# 1. חדר סרטונים ענק
with t_vid:
    st.subheader("🎬 ספריית סרטוני הסבר מהירים (עובדים וסוגרים פינה)")
    st.write("בחר תחום ושכבה כדי לצפות בשיעור ממוקד בלי חפירות:")
    
    v_col1, v_col2 = st.columns([1, 1])
    
    with v_col1:
        subject_choice = st.selectbox("בחר מקצוע:", [
            "מתמטיקה: חטיבה (משוואות, יחס, שטחים)",
            "מתמטיקה: תיכון (טריגו, חדו\"א, משוואות ריבועיות)",
            "אנגלית: דקדוק וזמנים (Grammar)",
            "מדעים ופיזיקה: כוחות, אנרגיה וחוקי ניוטון",
            "היסטוריה ואזרחות: סיכומים ממוקדים"
        ])
        
        video_links = {
            "מתמטיקה: חטיבה (משוואות, יחס, שטחים)": {
                "פתרון משוואות ממעלה ראשונה": "https://www.youtube.com/watch?v=5VjWl-z_c_U",
                "יחס ופרופורציה בקלות": "https://www.youtube.com/watch?v=sI3q6Q_Hk84",
                "שטחים והיקפים של מצולעים": "https://www.youtube.com/watch?v=uK1X_0kZq6g"
            },
            "מתמטיקה: תיכון (טריגו, חדו\"א, משוואות ריבועיות)": {
                "משוואה ריבועית ונוסחת שורשים": "https://www.youtube.com/watch?v=fghk_W4x_eM",
                "משפט פיתגורס וטריגונומטריה": "https://www.youtube.com/watch?v=aa7bC_rFq4c",
                "מבוא לנגזרות וחדו\"א": "https://www.youtube.com/watch?v=5yflv3j7T30"
            },
            "אנגלית: דקדוק וזמנים (Grammar)": {
                "Present Simple vs Present Progressive": "https://www.youtube.com/watch?v=x1a_9gq1pLg",
                "Past Simple בקלות": "https://www.youtube.com/watch?v=0k53_u1N9Yk",
                "איך לכתוב פסקת חיבור מושלמת (Opinion Essay)": "https://www.youtube.com/watch?v=7P_k3j_4X4w"
            },
            "מדעים ופיזיקה: כוחות, אנרגיה וחוקי ניוטון": {
                "חוקי ניוטון מוסברים ב-5 דקות": "https://www.youtube.com/watch?v=kKKM8Y-u7ds",
                "אנרגיה פוטנציאלית וקינטית": "https://www.youtube.com/watch?v=ASZv3tIK54k",
                "מבנה התא ופוטוסינתזה": "https://www.youtube.com/watch?v=68_jtXv9k4c"
            },
            "היסטוריה ואזרחות: סיכומים ממוקדים": {
                "הגורמים למלחמת העולם הראשונה": "https://www.youtube.com/watch?v=SLj5r2nZHB8",
                "עקרונות הדמוקרטיה (אזרחות)": "https://www.youtube.com/watch?v=cMKe0k_k1Qk",
                "העלייה הראשונה והשנייה": "https://www.youtube.com/watch?v=QZ0p8V5Q8sY"
            }
        }
        
        current_options = list(video_links[subject_choice].keys())
        chosen_lesson = st.selectbox("בחר שיעור:", current_options)
        st.video(video_links[subject_choice][chosen_lesson])

    with v_col2:
        st.markdown("**💡 המורה הוירטואלי: 'הסבר לי ב-3 דקות'**")
        st.caption(f"הסבר מותאם ספציפית ל-**{grade_level}** – פשוט, יסודי ועם דוגמה יומיומית.")
        custom_topic = st.text_input("איזה נושא תרצה שיסבירו לך?", placeholder="למשל: משפט תאלס, שיווי משקל כימי, מטפורה...")
        
        if st.button("תסביר לי יסודי 🧠", use_container_width=True, key="btn_exp_deep"):
            if not custom_topic.strip():
                st.warning("הזן נושא!")
            else:
                prompt = (
                    f"אתה מורה אלוף שמסביר לתלמיד ב-{grade_level}.\n"
                    f"הסבר את הנושא: {custom_topic}\n\n"
                    "כללים:\n"
                    "1. הגדרה סופר ברורה ב-2 משפטים.\n"
                    "2. דוגמה יומיומית מהחיים שמסבירה את העיקרון מיד.\n"
                    "3. שלושת שלבי העבודה או הנקודות שחייבים לזכור במבחן.\n"
                    "התאם את השפה בדיוק לרמת הגיל הזו בלי התנשאות ובלי חפירות."
                )
                with st.spinner("מכין הסבר..."):
                    try:
                        res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                        st.success("ההסבר שלך:")
                        st.markdown(res.text)
                    except Exception as e:
                        st.error(f"שגיאה: {e}")

# 2. פותר תמונות ומבחנים
with t_photo:
    st.subheader("📸 פותר תרגילים ודפי עבודה מתמונות")
    st.write("צילמת שאלה מספר או מהלוח? העלה אותה לכאן וקבל פתרון והסבר.")
    
    uploaded_file = st.file_uploader("העלה תמונה (PNG/JPG):", type=["png", "jpg", "jpeg"])
    photo_prompt = st.text_input("מה תרצה שנעשה עם התמונה? (אופציונלי):", value="פתור את התרגיל או ענה על השאלה בתמונה שלב אחרי שלב")
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="התמונה שהועלתה", use_container_width=True)
        
        if st.button("פענח ופתור את התמונה ⚡", use_container_width=True, key="btn_img_solve"):
            with st.spinner("מפענח את התמונה ופותר..."):
                try:
                    res = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=[f"התלמיד נמצא ב-{grade_level}. הנחיה: {photo_prompt}", img]
                    )
                    st.success("פתרון התמונה:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה בעיבוד התמונה: {e}")

# 3. משדרג ל-100
with t_ans:
    st.subheader("💯 משדרג תשובות לציון 100")
    st.write(f"התאם אישית מחוון בדיקה עבור **{grade_level}**.")
    
    col_q1, col_subj = st.columns([3, 1])
    with col_q1:
        quest = st.text_input("השאלה:")
    with col_subj:
        subject_name = st.selectbox("מקצוע:", ["היסטוריה / אזרחות / תנ\"ך", "ספרות / עברית", "מדעים / ביולוגיה", "אחר"])
        
    user_draft = st.text_area("התשובה שכתבת:", height=120)
    
    if st.button("שדרג תשובה לפי מחוון 🚀", use_container_width=True, key="btn_eval"):
        if not user_draft.strip():
            st.warning("הזן קודם את התשובה שלך!")
        else:
            prompt = (
                f"אתה מורה קפדן שמעריך תשובה של תלמיד ב-{grade_level} במקצוע {subject_name}.\n"
                f"שאלה: {quest}\nתשובה: {user_draft}\n\n"
                "החזר:\n"
                "1. **ציון מוערך (מתוך 100)**\n"
                "2. **מה חסר לקבלת 100 עגול**\n"
                "3. **תשובת 100 מושלמת ומנוסחת פיקס**"
            )
            with st.spinner("בודק..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("הערכת מחוון:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# 4. מפרק מתמטיקה
with t_math:
    st.subheader("📐 מפרק מתמטיקה שלב אחרי שלב")
    st.caption(f"הפתרון יותאם לחומר ולרמה של **{grade_level}**.")
    math_txt = st.text_area("הקלד תרגיל (משוואות, גאומטריה, פונקציות, שאלות מילוליות):", height=110)
    
    if st.button("פרק לי את התרגיל 🧠", use_container_width=True, key="btn_math_full"):
        if not math_txt.strip():
            st.warning("הזן תרגיל!")
        else:
            prompt = (
                f"פתור את תרגיל המתמטיקה הבא עבור תלמיד ב-{grade_level}:\n{math_txt}\n\n"
                "דרישות:\n"
                "1. פתור שלב אחרי שלב.\n"
                "2. ליד כל שלב כתוב נימוק פשוט.\n"
                "3. הדגש בבירור את **התשובה הסופית**."
            )
            with st.spinner("פותר..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("הפתרון המלא:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# 5. שליף סיכום
with t_sum:
    st.subheader("⚡ שליף סיכום מהיר למבחן")
    sum_in = st.text_area("הדבק כאן חומר קריאה ארוך:", height=140)
    
    if st.button("חלץ שליף למבחן 📑", use_container_width=True, key="btn_quick_sum"):
        if not sum_in.strip():
            st.warning("הזן טקסט לסיכום!")
        else:
            prompt = (
                f"תמצת את הטקסט הבא לתלמיד ב-{grade_level} שלומד למבחן:\n{sum_in}\n\n"
                "- עד 4 נקודות קריטיות שחובה לדעת.\n"
                "- מושגי מפתח ומילות חובה שהבוחן יחפש.\n"
                "- טיפ זיכרון מהיר."
            )
            with st.spinner("מחלץ תמצית..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("שליף המבחן מוכן:")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# 6. בונה לו״ז למבחן
with t_plan:
    st.subheader("📅 מתכנן לוח זמנים אישי למבחן")
    st.write("נשאר מעט זמן למבחן? תן ל-AI לחלק לך את החומר ללו״ז יומי שלא תיתקע בלילה האחרון.")
    
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        test_sub = st.text_input("מקצוע המבחן:", placeholder="למשל: היסטוריה / מתמטיקה / מדעים")
        days_left = st.number_input("כמה ימים נשארו למבחן?", min_value=1, max_value=30, value=3)
    with c_p2:
        study_hours = st.slider("כמה שעות ביום אתה יכול ללמוד?", 1, 6, 2)
        topics_list = st.text_area("אילו נושאים צריך להספיק?", placeholder="פרק 1, פרק 3, פתרון בגרויות...")

    if st.button("בנה לי תוכנית עבודה יומית 🎯", use_container_width=True, key="btn_schedule"):
        prompt = (
            f"בנה לוח זמנים מפורט ופרקטי לתלמיד ב-{grade_level}.\n"
            f"מקצוע: {test_sub}\nימים עד המבחן: {days_left}\nשעות לימוד ליום: {study_hours}\nנושאים: {topics_list}\n\n"
            "חלק ללוח זמנים לפי ימים: מה ללמוד בדיוק בכל יום, מתי לעשות הפסקות ומתי להקדיש זמן לתרגול שאלות ומבחן לדוגמה."
        )
        with st.spinner("בונה לו״ז..."):
            try:
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.success("תוכנית הלימודים שלך:")
                st.markdown(res.text)
            except Exception as e:
                st.error(f"שגיאה: {e}")

# 7. צ'אט מורה פרטי
with t_chat:
    st.subheader(f"💬 מורה פרטי צמוד 24/7 ({grade_level})")
    st.write("שאל כל שאלה קטנה שנתקעת עליה תוך כדי הכנת שיעורי בית או חזרה למבחן:")
    
    quick_q = st.text_input("שאל את המורה:", placeholder="איך זוכרים נוסחה מסוימת? מה ההבדל בין שתי הגדרות?...")
    if st.button("שלח שאלה למורה 💡", use_container_width=True, key="btn_ask_teacher"):
        if not quick_q.strip():
            st.warning("הזן שאלה!")
        else:
            prompt = (
                f"אתה מורה פרטי סבלני, חכם וחברי של תלמיד ב-{grade_level}.\n"
                f"ענה ישירות, בקצרה ובפשטות על השאלה הבאה: {quick_q}"
            )
            with st.spinner("המורה כותב תשובה..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.info(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")
