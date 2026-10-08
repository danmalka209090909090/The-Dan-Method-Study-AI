import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(
    page_title="The Dan Method: Study AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב מודרני מיושר לימין (RTL)
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
        {"name": "מאיה ר.", "grade": "כיתה י\"א (5 יח')", "rating": 5, "text": "מפרק המתמטיקה מסביר לפי מחוון בגרות בדיוק כמו שצריך."}
    ]

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ מפתח GEMINI_API_KEY לא מוגדר ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- סרגל צד (Sidebar): שכבה, יחידות וניווט ---
with st.sidebar:
    st.title("⚡ The Dan Method")
    st.caption("פלטפורמת הלימוד והבגרויות שלך")
    st.markdown("---")
    
    st.subheader("🎓 1. בחר כיתה ויחידות לימוד:")
    chosen_grade = st.selectbox(
        "שכבת לימוד:",
        ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב (בגרות)"],
        index=2
    )
    
    # חלוקה ליחידות לימוד
    if chosen_grade in ["כיתה ז'", "כיתה ח'", "כיתה ט'"]:
        math_units = st.selectbox("רמת מתמטיקה:", ["הקבצה א' / מצוינות", "הקבצה ב'", "רמה רגילה"])
        eng_units = st.selectbox("רמת אנגלית:", ["הקבצה א' / דוברי אנגלית", "הקבצה ב'", "רמה רגילה"])
    else:
        math_units = st.selectbox("מתמטיקה (יחידות לימוד):", ["5 יחידות", "4 יחידות", "3 יחידות"])
        eng_units = st.selectbox("אנגלית (יחידות לימוד):", ["5 יחידות / דוברי אנגלית", "4 יחידות (Module E)", "3 יחידות"])
    
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
    st.caption("The Dan Method v5.5 Pro")

# תוספת הנחיות מערכת לפילטר ולרמת התלמיד
anti_yap_rule = "השב ישירות לתכל'ס, ללא פסקאות פתיחה או סיום מיותרות." if no_yap else ""
student_context = f"שכבת לימוד: {chosen_grade}, רמת מתמטיקה: {math_units}, רמת אנגלית: {eng_units}."

# ----------------- חדר 1: וידאו ושיעורים -----------------
if room == "🎬 חדר וידאו ושיעורים":
    st.title("🎬 חדר וידאו ושיעורים מוקלטים")
    st.write(f"הסברים ממוקדים שמותאמים ספציפית ל-**{chosen_grade}** ({math_units} / {eng_units}):")
    
    col_v1, col_v2 = st.columns([1.1, 0.9])
    
    with col_v1:
        if chosen_grade in ["כיתה ז'", "כיתה ח'", "כיתה ט'"]:
            video_options = {
                "מתמטיקה: משפט פיתגורס - הסבר פשוט": "https://www.youtube.com/watch?v=xAgLlIAum3c",
                "מתמטיקה: משוואות ממעלה ראשונה": "https://www.youtube.com/watch?v=lj6ONyl932A",
                "אנגלית: זמנים בסיסיים (Present Simple)": "https://www.youtube.com/watch?v=L9AWrJnhsRI",
                "מדעים: כוחות וחוקי התנועה": "https://www.youtube.com/watch?v=kKKM8Y-u7ds"
            }
        else:
            video_options = {
                "מתמטיקה: משפט פיתגורס וטריגונומטריה": "https://www.youtube.com/watch?v=xAgLlIAum3c",
                "מתמטיקה: משוואות עם פרמטרים וטכניקה אלגברית": "https://www.youtube.com/watch?v=QIsqPGX7Ebc",
                "מתמטיקה: חקירת משוואות (5 יחידות)": "https://www.youtube.com/watch?v=gUFnMrzYdCc",
                "היסטוריה: הגורמים למלחמת העולם הראשונה": "https://www.youtube.com/watch?v=SLj5r2nZHB8"
            }
            
        chosen_v = st.selectbox("בחר שיעור לצפייה:", list(video_options.keys()))
        selected_url = video_options[chosen_v]
        
        st.video(selected_url)
        st.markdown(f"[🔗 לחץ כאן לפתיחת הסרטון ישירות ב-YouTube]({selected_url})")
        
    with col_v2:
        st.subheader("💡 המורה הוירטואלי: הסבר לי נושא")
        st.caption(f"הסבר מותאם רמה ל-**{chosen_grade}**.")
        
        # שאלה ראשונה קבועה: מה החומר הנלמד?
        topic_subject = st.text_input("📚 1. מה החומר / הנושא הנלמד כרגע?", placeholder="למשל: סדרות חשבוניות, מלחמת העולם הראשונה, פוטוסינתזה...")
        ask_topic = st.text_input("❓ 2. מה בדיוק לא הבנת בנושא הזה?", placeholder="למשל: איך מוצאים את d? מה ההבדל בין שתי ההגדרות?...")
        
        if st.button("הסבר לי בפשטות 🧠", use_container_width=True):
            if not topic_subject.strip():
                st.warning("חובה לציין קודם מה החומר הנלמד!")
            else:
                prompt = (
                    f"אתה מורה פרטי שמלמד תלמיד ב-{chosen_grade} ({math_units}, {eng_units}).\n"
                    f"החומר הנלמד: {topic_subject}\n"
                    f"שאלת התלמיד: {ask_topic}\n\n"
                    "החזר הסבר קצר, בהיר ולעניין:\n"
                    "1. הגדרה תמציתית ב-2 משפטים.\n"
                    "2. דוגמה יומיומית שממחישה את זה מיד.\n"
                    "3. שלושת הדברים שהכי חשוב לזכור במבחן.\n"
                    f"{anti_yap_rule}"
                )
                with st.spinner("מכין הסבר ממוקד..."):
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("ההסבר מוכן:")
                    st.markdown(res.text)

# ----------------- חדר 2: סורק תמונות -----------------
elif room == "📸 סורק תמונות ומבחנים":
    st.title("📸 סורק תמונות ושיעורי בית")
    st.write(f"העלה צילום מדף העבודה או הספר עבור **{chosen_grade}** ({math_units} / {eng_units}):")
    
    # שאלה ראשונה קבועה: מה החומר הנלמד?
    photo_topic = st.text_input("📚 1. מה החומר / הנושא שמופיע בתמונה?", placeholder="למשל: גאומטריה אנליטית, שאלות בגרות בתנ\"ך, דקדוק באנגלית...")
    file = st.file_uploader("📷 2. בחר קובץ תמונה (JPG/PNG):", type=["png", "jpg", "jpeg"])
    action = st.text_input("3. מה לבצע בתמונה?", value="פתור והסבר שלב אחרי שלב בצורה ברורה")
    
    if file:
        img = Image.open(file)
        st.image(img, caption="התמונה שהועלתה", width=360)
        
        if st.button("פענח ופתור ⚡", use_container_width=True):
            if not photo_topic.strip():
                st.warning("ציין קודם מה החומר הנלמד!")
            else:
                with st.spinner("מפענח את התמונה..."):
                    prompt = f"התלמיד ב-{chosen_grade} ({math_units}, {eng_units}). החומר הנלמד: {photo_topic}. הנחיה: {action}. {anti_yap_rule}"
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=[prompt, img])
                    st.success("הפתרון לתמונה:")
                    st.markdown(res.text)

# ----------------- חדר 3: מלטשת תשובות -----------------
elif room == "💯 מלטשת תשובות למאיות":
    st.title("💯 מלטשת תשובות לציון 100")
    st.write(f"התאמת ניסוח למחוון בחינה עבור **{chosen_grade}** ({math_units} / {eng_units}).")
    
    # שאלה ראשונה קבועה: מה החומר הנלמד?
    ans_topic = st.text_input("📚 1. מה החומר / הנושא הנלמד והמקצוע?", placeholder="למשל: היסטוריה - העלייה השנייה / אזרחות - זכויות אדם...")
    q_text = st.text_input("❓ 2. מה השאלה שנשאלת?")
    user_ans = st.text_area("✍️ 3. מה התשובה שכתבת (או טיוטה ראשונית):", height=130)
    
    if st.button("שדרג לי את התשובה ל-100 🚀", use_container_width=True):
        if not ans_topic.strip() or not user_ans.strip():
            st.warning("חובה למלא את החומר הנלמד ואת התשובה שכתבת!")
        else:
            prompt = (
                f"אתה מעריך בחינות קפדן שבודק תשובה של תלמיד ב-{chosen_grade} ({math_units}, {eng_units}).\n"
                f"החומר הנלמד: {ans_topic}\n"
                f"שאלה: {q_text}\nתשובה: {user_ans}\n\n"
                "החזר:\n"
                "1. **ציון מוערך (מתוך 100)**\n"
                "2. **מה חסר לפי מחוון הבדיקה** (קצר וחד)\n"
                "3. **תשובה מושלמת סופית**: נוסח שסוגר את מלוא הנקודות.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנתח לפי מחוון..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 4: מעבדת מתמטיקה -----------------
elif room == "📐 מעבדת מתמטיקה ומדעים":
    st.title("📐 מעבדת פירוק מתמטיקה ומדעים")
    st.write(f"פתרון שלב-אחר-שלב המותאם בדיוק לרמת: **{chosen_grade} — {math_units}**")
    
    # שאלה ראשונה קבועה: מה החומר הנלמד?
    math_topic = st.text_input("📚 1. מה הנושא הנלמד כרגע?", placeholder="למשל: חקירת פולינום, טריגונומטריה, משוואות ריבועיות, גיאומטריה...")
    math_input = st.text_area("🔢 2. הזן את התרגיל או השאלה:", height=120)
    
    if st.button("פרק לי את התרגיל לפי רמת היחידות 🧠", use_container_width=True):
        if not math_topic.strip() or not math_input.strip():
            st.warning("חובה לציין את הנושא הנלמד ואת התרגיל!")
        else:
            prompt = (
                f"פתור את תרגיל המתמטיקה הבא עבור תלמיד ב-{chosen_grade} ברמת {math_units}.\n"
                f"הנושא הנלמד: {math_topic}\n"
                f"התרגיל: {math_input}\n\n"
                f"שים לב: התאם את הפתרון והמשפטים בדיוק לרמת {math_units} (לא מסובך מדי ולא פשוט מדי).\n"
                "דרישות:\n"
                "1. פתור שלב אחרי שלב בבירור.\n"
                "2. ליד כל שלב כתוב נימוק קצר על הכלל/המשפט שהופעל.\n"
                "3. הדגש בריבוע ברור את **התשובה הסופית**.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner(f"פותר לפי רמת {math_units}..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 5: שליף חירום -----------------
elif room == "🚨 שליף חירום (לפני מבחן)":
    st.title("🚨 שליף חירום: 60 שניות לפני מבחן")
    st.write(f"תמצית ברזל עבור **{chosen_grade}** ({math_units} / {eng_units}):")
    
    # שאלה ראשונה קבועה: מה החומר הנלמד?
    panic_topic = st.text_input("📚 מה החומר / הנושא של המבחן כרגע?", placeholder="למשל: משפט חוצה זווית, מרד בר כוכבא, Module E connectors...")
    
    if st.button("הצל אותי עכשיו ⚡", use_container_width=True):
        if not panic_topic.strip():
            st.warning("הזן קודם את החומר הנלמד!")
        else:
            prompt = (
                f"התלמיד ב-{chosen_grade} ({math_units}, {eng_units}) נכנס בעוד דקה למבחן על החומר: {panic_topic}.\n"
                "החזר אך ורק:\n"
                "1. **3 משפטי זהב** שחייבים לרשום במבחן כדי לקבל נקודות.\n"
                "2. **הטעות הנפוצה ביותר** שתלמידים נופלים בה.\n"
                "3. **מושג חובה אחד** שהבוחן מחפש בעין.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מחלץ שליף..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(f'<div class="cheat-card">{res.text}</div>', unsafe_allow_html=True)

# ----------------- חדר 6: מחולל בחנים -----------------
elif room == "🧠 מחולל בחנים אינטראקטיבי":
    st.title("🧠 מחולל בחנים אינטראקטיבי")
    st.write(f"תרגול ממוקד לרמת **{chosen_grade}** ({math_units} / {eng_units}):")
    
    # שאלה ראשונה קבועה: מה החומר הנלמד?
    quiz_topic = st.text_input("📚 מה החומר / הנושא שתרצה לבחון עליו את עצמך?", placeholder="למשל: אנרגיה קינטית, טריגו במרחב, דקדוק באנגלית...")
    
    if st.button("ייצר לי שאלות בדיקה 🎯", use_container_width=True):
        if not quiz_topic.strip():
            st.warning("הזן קודם את החומר הנלמד!")
        else:
            prompt = (
                f"צור 3 שאלות תרגול עבור תלמיד ב-{chosen_grade} ({math_units}, {eng_units}) על החומר: {quiz_topic}.\n"
                "התאם את השאלות במדויק לרמת היחידות שנבחרה.\n"
                "לכל שאלה ספק 4 אפשרויות (א-ד), ומתחת לכל שאלה הוסף את התשובה הנכונה עם הסבר קצרצר."
            )
            with st.spinner("בונה שאלות..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 7: מתכנן לו״ז -----------------
elif room == "📅 מתכנן לו״ז למבחן":
    st.title("📅 מתכנן לוח זמנים אישי למבחן")
    st.write(f"תוכנית עבודה מותאמת ל-**{chosen_grade}**:")
    
    # שאלה ראשונה קבועה: מה החומר הנלמד?
    topics = st.text_area("📚 1. מה כל החומר והנושאים שצריך להספיק למבחן?", placeholder="למשל: פרקים 1 עד 4 בספר, בעיות קיצון, מבחן בגרות קיץ 2024...")
    
    c1, c2 = st.columns(2)
    with c1:
        exam_subj = st.text_input("2. איזה מקצוע המבחן?", placeholder="מתמטיקה / היסטוריה / אנגלית...")
        days = st.number_input("3. כמה ימים נשארו למבחן?", 1, 30, 3)
    with c2:
        hours = st.slider("4. כמה שעות למידה פנויות יש לך ביום?", 1, 6, 2)
        
    if st.button("בנה לי תוכנית עבודה 🗓️", use_container_width=True):
        if not topics.strip():
            st.warning("הזן קודם את החומר הנלמד למבחן!")
        else:
            prompt = (
                f"בנה לוח זמנים פרקטי ללימוד למבחן עבור תלמיד ב-{chosen_grade} ({math_units}, {eng_units}).\n"
                f"מקצוע: {exam_subj}, ימים: {days}, שעות ביום: {hours}, חומר נלמד: {topics}.\n"
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
        fb_units = st.text_input("יחידות לימוד (למשל 4 יח' מתמטיקה, 5 יח' אנגלית):")
        fb_rating = st.slider("דירוג החוויה שלך (כוכבים):", 1, 5, 5)
        fb_text = st.text_area("מה דעתך על האתר? מה כדאי להוסיף או לשפר?")
        submitted = st.form_submit_button("שלח חוות דעת 🚀")
        
        if submitted:
            if not fb_text.strip():
                st.warning("כתוב משהו לפני השליחה!")
            else:
                grade_display = f"{fb_grade} ({fb_units})" if fb_units.strip() else fb_grade
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
            <div class="review-card">
                <b>{r['name']}</b> ({r['grade']}) — {stars}<br>
                <span>{r['text']}</span>
            </div>
        """, unsafe_allow_html=True)
