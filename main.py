import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(
    page_title="The Dan Method: Study AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# הגדרת סגנון, יישור לימין (RTL) ועיצוב כרטיסיות
st.markdown("""
<style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    div[data-testid="stExpander"] {
        text-align: right;
    }
    .cheat-card {
        background: #1e1b4b;
        border: 1px solid #6366f1;
        padding: 16px;
        border-radius: 10px;
        color: #e0e7ff;
        margin-top: 10px;
    }
    .review-card {
        background: #0f172a;
        border: 1px solid #334155;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# אתחול Session State לחוות דעת
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "השליף חירום הציל אותי לפני מבחן בהיסטוריה!"},
        {"name": "מאיה ר.", "grade": "כיתה י\"א", "rating": 5, "text": "מפרק המתמטיקה מסביר יותר טוב מהמורה הפרטי שלי."}
    ]

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ מפתח GEMINI_API_KEY לא מוגדר ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- סרגל צד (Sidebar): בחירת כיתה וניווט בין חדרים ---
with st.sidebar:
    st.title("⚡ The Dan Method")
    st.caption("פלטפורמת הלימוד האישית שלך")
    st.markdown("---")
    
    st.subheader("🎓 1. בחר את הכיתה שלך:")
    chosen_grade = st.selectbox(
        "שכבת לימוד:",
        ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב (בגרות)"]
    )
    
    st.markdown("---")
    st.subheader("🚪 2. בחר חדר עבודה:")
    room = st.radio(
        "מעבר לחדר:",
        [
            "🎬 חדר וידאו ושיעורים",
            "📸 סורק תמונות ומבחנים",
            "💯 מלטשת תשובות למאיות",
            "📐 מעבדת מתמטיקה ומדעים",
            "🚨 שליף חירום (לפני מבחן)",
            "🧠 מחולל בחנים אינטראקטיבי",
            "📅 מתכנן לו״ז למבחן",
            "⭐ חוות דעת והצעות"
        ]
    )
    
    st.markdown("---")
    no_yap = st.toggle("מצב תכל'ס (ללא חפירות)", value=True)
    st.caption("The Dan Method v5.0")

# תוספת הנחיה לפילטר
anti_yap_rule = "השב ישירות לתכל'ס, ללא פסקאות פתיחה או סיום מיותרות." if no_yap else ""

# ----------------- חדר 1: וידאו ושיעורים -----------------
if room == "🎬 חדר וידאו ושיעורים":
    st.title("🎬 חדר וידאו ושיעורים מוקלטים")
    st.write(f"הסברים ממוקדים שמותאמים ספציפית ל-**{chosen_grade}**:")
    
    col_v1, col_v2 = st.columns([1, 1])
    
    with col_v1:
        # סרטונים מותאמים לשכבת הגיל
        if chosen_grade in ["כיתה ז'", "כיתה ח'", "כיתה ט'"]:
            video_options = {
                "מתמטיקה: פתרון משוואות ממעלה ראשונה": "https://www.youtube.com/watch?v=5VjWl-z_c_U",
                "מתמטיקה: יחס ופרופורציה בקלות": "https://www.youtube.com/watch?v=sI3q6Q_Hk84",
                "מדעים: כוחות וחוקי ניוטון": "https://www.youtube.com/watch?v=kKKM8Y-u7ds",
                "אנגלית: זמנים בסיסיים (Present Simple)": "https://www.youtube.com/watch?v=x1a_9gq1pLg"
            }
        else:
            video_options = {
                "מתמטיקה: משוואה ריבועית ונוסחת שורשים": "https://www.youtube.com/watch?v=fghk_W4x_eM",
                "מתמטיקה: משפט פיתגורס וטריגונומטריה": "https://www.youtube.com/watch?v=aa7bC_rFq4c",
                "מתמטיקה: מבוא לנגזרות וחדו\"א": "https://www.youtube.com/watch?v=5yflv3j7T30",
                "היסטוריה: הגורמים למלחמת העולם הראשונה": "https://www.youtube.com/watch?v=SLj5r2nZHB8"
            }
            
        chosen_v = st.selectbox("בחר שיעור לצפייה:", list(video_options.keys()))
        st.video(video_options[chosen_v])
        
    with col_v2:
        st.subheader("💡 המורה הוירטואלי: הסבר לי נושא")
        st.caption(f"הסבר מותאם רמה ל-**{chosen_grade}**.")
        ask_topic = st.text_input("איזה נושא או מושג תרצה להבין?", placeholder="למשל: שטחים, כבידה, מטפורה, משוואה...")
        
        if st.button("הסבר לי בפשטות 🧠", use_container_width=True):
            if not ask_topic.strip():
                st.warning("הזן נושא!")
            else:
                prompt = (
                    f"הסבר לתלמיד ב-{chosen_grade} את הנושא הבא בצורה ברורה, מעניינת ולעניין:\n{ask_topic}\n\n"
                    "1. הגדרה תמציתית ב-2 משפטים.\n"
                    "2. דוגמה יומיומית שממחישה את זה.\n"
                    "3. שלושת הדברים שהכי חשוב לזכור במבחן.\n"
                    f"{anti_yap_rule}"
                )
                with st.spinner("מכין הסבר..."):
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("ההסבר מוכן:")
                    st.markdown(res.text)

# ----------------- חדר 2: סורק תמונות -----------------
elif room == "📸 סורק תמונות ומבחנים":
    st.title("📸 סורק תמונות ושיעורי בית")
    st.write(f"העלה צילום מדף העבודה או הספר עבור **{chosen_grade}**:")
    
    file = st.file_uploader("בחר קובץ תמונה (JPG/PNG):", type=["png", "jpg", "jpeg"])
    action = st.text_input("מה לבצע?", value="פתור והסבר שלב אחרי שלב בצורה ברורה")
    
    if file:
        img = Image.open(file)
        st.image(img, caption="התמונה שהועלתה", width=360)
        
        if st.button("פענח ופתור ⚡", use_container_width=True):
            with st.spinner("מפענח את התמונה..."):
                prompt = f"התלמיד ב-{chosen_grade}. {action}. {anti_yap_rule}"
                res = client.models.generate_content(model="gemini-3.8-flash", contents=[prompt, img])
                st.success("הפתרון לתמונה:")
                st.markdown(res.text)

# ----------------- חדר 3: מלטשת תשובות -----------------
elif room == "💯 מלטשת תשובות למאיות":
    st.title("💯 מלטשת תשובות לציון 100")
    st.write(f"התאמת ניסוח למחוון בחינה עבור **{chosen_grade}**.")
    
    q_text = st.text_input("השאלה:")
    user_ans = st.text_area("התשובה שכתבת:", height=130)
    
    if st.button("שדרג לי את התשובה 🚀", use_container_width=True):
        if not user_ans.strip():
            st.warning("הזן קודם את התשובה שלך!")
        else:
            prompt = (
                f"אתה מעריך בחינות קפדן שבודק תשובה של תלמיד ב-{chosen_grade}.\n"
                f"שאלה: {q_text}\nתשובה: {user_ans}\n\n"
                "החזר:\n"
                "1. **ציון מוערך (מתוך 100)**\n"
                "2. **מה חסר לקבלת 100 עגול**\n"
                "3. **תשובה מושלמת סופית**: נוסח שסוגר את מלוא הנקודות.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנתח לפי מחוון..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 4: מעבדת מתמטיקה -----------------
elif room == "📐 מעבדת מתמטיקה ומדעים":
    st.title("📐 מעבדת פירוק מתמטיקה ומדעים")
    st.write(f"פתרון צעד-אחר-צעד עם נימוקים המותאם לרמת **{chosen_grade}**:")
    
    math_input = st.text_area("הזן את התרגיל או הבעיה המילולית:", height=120)
    
    if st.button("פרק לי את התרגיל 🧠", use_container_width=True):
        if not math_input.strip():
            st.warning("הזן תרגיל!")
        else:
            prompt = (
                f"פתור את התרגיל הבא שלב אחרי שלב עבור תלמיד ב-{chosen_grade}:\n{math_input}\n\n"
                "הצג כל שלב בבירור עם הסבר קצר על הכלל או הנוסחה שהופעלו, והדגש את התוצאה הסופית.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מחשב ומנמק..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 5: שליף חירום -----------------
elif room == "🚨 שליף חירום (לפני מבחן)":
    st.title("🚨 שליף חירום: 60 שניות לפני מבחן")
    st.write("נכנס עוד דקה לכיתה? תזרוק את הנושא ותקבל אך ורק מה שחובה לדעת.")
    
    panic_topic = st.text_input("נושא המבחן / הבוחן:", placeholder="למשל: חוקי נירנברג, משפט פיתגורס, פוטוסינתזה...")
    
    if st.button("הצל אותי עכשיו ⚡", use_container_width=True):
        if not panic_topic.strip():
            st.warning("הזן נושא!")
        else:
            prompt = (
                f"התלמיד ב-{chosen_grade} נכנס בעוד דקה למבחן על: {panic_topic}.\n"
                "החזר אך ורק:\n"
                "1. **3 משפטי זהב** שחייבים לרשום כדי לקבל נקודות.\n"
                "2. **הטעות הנפוצה ביותר** שנכשלים עליה.\n"
                "3. **מושג חובה אחד** שחובה לשלב בתשובה.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מחלץ שליף..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(f'<div class="cheat-card">{res.text}</div>', unsafe_allow_html=True)

# ----------------- חדר 6: מחולל בחנים -----------------
elif room == "🧠 מחולל בחנים אינטראקטיבי":
    st.title("🧠 מחולל בחנים אינטראקטיבי")
    st.write(f"בדוק אם אתה באמת שולט בחומר של **{chosen_grade}**:")
    
    quiz_topic = st.text_input("על איזה נושא תרצה שאלות?", placeholder="למשל: מערכת השמש, מלחמת העולם השנייה, שברים...")
    
    if st.button("ייצר לי שאלות בדיקה 🎯", use_container_width=True):
        if not quiz_topic.strip():
            st.warning("הזן נושא לבחינה!")
        else:
            prompt = (
                f"צור 3 שאלות תרגול ממוקדות עבור תלמיד ב-{chosen_grade} על הנושא: {quiz_topic}.\n"
                "לכל שאלה ספק 4 אפשרויות (א-ד), ומתחת לכל שאלה הוסף את התשובה הנכונה עם הסבר קצר."
            )
            with st.spinner("בונה שאלות..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 7: מתכנן לו״ז -----------------
elif room == "📅 מתכנן לו״ז למבחן":
    st.title("📅 מתכנן לוח זמנים אישי למבחן")
    st.write("בנה תוכנית עבודה יומית כדי לא להגיע ללילה לפני המבחן בלחץ:")
    
    c1, c2 = st.columns(2)
    with c1:
        exam_subj = st.text_input("מקצוע:")
        days = st.number_input("כמה ימים נשארו?", 1, 30, 3)
    with c2:
        hours = st.slider("שעות למידה פנויות ביום:", 1, 6, 2)
        topics = st.text_area("אילו נושאים צריך להספיק?")
        
    if st.button("בנה לי תוכנית עבודה 🗓️", use_container_width=True):
        prompt = (
            f"בנה לוח זמנים פרקטי ללימוד למבחן עבור תלמיד ב-{chosen_grade}.\n"
            f"מקצוע: {exam_subj}, ימים: {days}, שעות ביום: {hours}, נושאים: {topics}.\n"
            "חלק את המשימות לפי ימים, כולל זמני מנוחה ותרגול מעשי."
        )
        with st.spinner("מתכנן לו״ז..."):
            res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
            st.markdown(res.text)

# ----------------- חדר 8: חוות דעת -----------------
elif room == "⭐ חוות דעת והצעות":
    st.title("⭐ חוות דעת והצעות לשיפור")
    st.write("איך האתר עובד לך? יש פיצ'ר שאתה רוצה שנוסיף? כתוב לנו כאן:")
    
    with st.form("feedback_form", clear_on_submit=True):
        fb_name = st.text_input("שם או כינוי:")
        fb_grade = st.selectbox("כיתה:", ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב"], index=2)
        fb_rating = st.slider("דירוג החוויה שלך (כוכבים):", 1, 5, 5)
        fb_text = st.text_area("מה דעתך על האתר? מה כדאי להוסיף או לשפר?")
        submitted = st.form_submit_button("שלח חוות דעת 🚀")
        
        if submitted:
            if not fb_text.strip():
                st.warning("כתוב משהו לפני השליחה!")
            else:
                st.session_state.reviews.insert(0, {
                    "name": fb_name if fb_name.strip() else "אנונימי",
                    "grade": fb_grade,
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
            <div class="review-card">
                <b>{r['name']}</b> ({r['grade']}) — {stars}<br>
                <span>{r['text']}</span>
            </div>
        """, unsafe_allow_html=True)
