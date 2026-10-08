import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(
    page_title="The Dan Method: Study AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# הגדרת סגנון, יישור לימין (RTL) והתאמה להדפסה
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
    .portal-link {
        display: inline-block;
        padding: 10px 18px;
        background-color: #2563eb;
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        margin-left: 8px;
        margin-bottom: 8px;
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

# אתחול Session State לחוות דעת ולהיסטוריית צ'אט
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {"name": "עידו כ.", "grade": "כיתה ט'", "rating": 5, "text": "השליף חירום הציל אותי לפני מבחן בהיסטוריה!"},
        {"name": "מאיה ר.", "grade": "כיתה י\"א (5 יח')", "rating": 5, "text": "מפרק המתמטיקה מסביר לפי מחוון בגרות בדיוק כמו שצריך."}
    ]

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ מפתח GEMINI_API_KEY לא מוגדר ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- סרגל צד (Sidebar): שכבה, יחידות וניווט ---
with st.sidebar:
    st.title("⚡ The Dan Method")
    st.caption("פלטפורמת הלימוד והבגרויות המובילה")
    st.markdown("---")
    
    st.subheader("🎓 1. בחר כיתה ויחידות לימוד:")
    chosen_grade = st.selectbox(
        "שכבת לימוד:",
        ["כיתה ז'", "כיתה ח'", "כיתה ט'", "כיתה י'", "כיתה י\"א", "כיתה י\"ב (בגרות)"],
        index=2
    )
    
    if chosen_grade in ["כיתה ז'", "כיתה ח'", "כיתה ט'"]:
        math_units = st.selectbox("מתמטיקה:", ["הקבצה א' / מצוינות", "הקבצה ב'", "רמה רגילה"])
        eng_units = st.selectbox("אנגלית:", ["הקבצה א' / דוברי אנגלית", "הקבצה ב'", "רמה רגילה"])
    else:
        math_units = st.selectbox("מתמטיקה (יחידות לימוד):", ["5 יחידות", "4 יחידות", "3 יחידות"])
        eng_units = st.selectbox("אנגלית (יחידות לימוד):", ["5 יחידות / דוברי אנגלית", "4 יחידות (Module E)", "3 יחידות"])
    
    st.markdown("---")
    st.subheader("🚪 2. בחר חדר עבודה:")
    room = st.radio(
        "מעבר לחדר:",
        [
            "👨‍🏫 מורה פרטי כולל (AI Tutor)",
            "🎬 ספריית וידאו ושיעורים ענקית",
            "🏫 חיבור ל-Classroom וספרי לימוד",
            "🖨️ דפי תרגול ומבחנים להדפסה",
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
    st.caption("The Dan Method v6.0 Super")

anti_yap_rule = "השב ישירות לתכל'ס, ללא פסקאות פתיחה או סיום מיותרות." if no_yap else ""
student_context = f"שכבת לימוד: {chosen_grade}, מתמטיקה: {math_units}, אנגלית: {eng_units}."

# ----------------- חדר 1: מורה פרטי כוללני -----------------
if room == "👨‍🏫 מורה פרטי כולל (AI Tutor)":
    st.title("👨‍🏫 המורה הפרטי האישי שלך (לכל המקצועות)")
    st.write(f"התאמה מלאה לרמת **{chosen_grade}** ({math_units} / {eng_units}). שאל כל שאלה בכל מקצוע ונהל שיחה רציפה.")
    
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        current_subject = st.selectbox("בחר מקצוע עבור המורה:", [
            "מתמטיקה", "אנגלית", "היסטוריה", "אזרחות", "תנ\"ך", "לשון והבעה", "פיזיקה / מדעים", "ביולוגיה", "ספרות"
        ])
    with col_t2:
        teaching_style = st.selectbox("סגנון הוראה:", [
            "בגובה העיניים (ברור ופשוט)", "קפדן ומכוון למחוון 100", "סבלני עם הסברים מפורטים"
        ])

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("שאל את המורה כל דבר...")
    if user_query:
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("המורה עונה..."):
                system_prompt = (
                    f"אתה מורה פרטי מקצועי וסבלני בישראל. פרטי התלמיד: {student_context}.\n"
                    f"מקצוע הלימוד כרגע: {current_subject}. סגנון ההוראה המבוקש: {teaching_style}.\n"
                    f"הנחיות: ענה ברור, ממוקד, בדוק הבנה בסוף. {anti_yap_rule}"
                )
                history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_messages[-4:]])
                prompt = f"{system_prompt}\n\nהיסטוריית השיחה:\n{history_text}\n\nשאלה אחרונה: {user_query}"
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)
                st.session_state.chat_messages.append({"role": "assistant", "content": res.text})

# ----------------- חדר 2: ספריית וידאו עשירה -----------------
elif room == "🎬 ספריית וידאו ושיעורים ענקית":
    st.title("🎬 ספריית וידאו עשירה ומסודרת לפי נושאים")
    st.write(f"שיעורים ממוקדים לצפייה ישירה עבור **{chosen_grade}**:")
    
    category = st.selectbox("בחר מקצוע ותחום:", [
        "מתמטיקה: גאומטריה ופיתגורס",
        "מתמטיקה: אלגברה, משוואות וחדו\"א",
        "אנגלית: זמנים ודקדוק (Grammar)",
        "מדעים ופיזיקה: כוחות, אנרגיה ותנועה",
        "לשון והבעה עברית: תחביר, מערכת הצורות והבנת הנקרא",
        "היסטוריה, תנ\"ך ואזרחות: פרקי חובה"
    ])
    
    video_db = {
        "מתמטיקה: גאומטריה ופיתגורס": {
            "משפט פיתגורס - בסיס וחישוב צלעות": "https://www.youtube.com/watch?v=xAgLlIAum3c",
            "משפט תאלס והרחבותיו": "https://www.youtube.com/watch?v=sI3q6Q_Hk84",
            "טריגונומטריה במשולש ישר זווית (Sin, Cos, Tan)": "https://www.youtube.com/watch?v=aa7bC_rFq4c"
        },
        "מתמטיקה: אלגברה, משוואות וחדו\"א": {
            "משוואות ממעלה ראשונה עם סוגריים ושברים": "https://www.youtube.com/watch?v=lj6ONyl932A",
            "משוואה ריבועית ונוסחת שורשים": "https://www.youtube.com/watch?v=fghk_W4x_eM",
            "חקירת פונקציות ונגזרות (מבוא לחדו\"א)": "https://www.youtube.com/watch?v=5yflv3j7T30",
            "משוואות עם פרמטרים": "https://www.youtube.com/watch?v=QIsqPGX7Ebc"
        },
        "אנגלית: זמנים ודקדוק (Grammar)": {
            "זמנים בסיסיים: Present Simple vs Progressive": "https://www.youtube.com/watch?v=L9AWrJnhsRI",
            "עבר פשוט ועבר ממושך (Past Simple & Past Continuous)": "https://www.youtube.com/watch?v=0k53_u1N9Yk",
            "כתיבת חיבור דעה מושלם (Opinion Essay)": "https://www.youtube.com/watch?v=7P_k3j_4X4w"
        },
        "מדעים ופיזיקה: כוחות, אנרגיה ותנועה": {
            "שלושת חוקי ניוטון מוסברים ב-5 דקות": "https://www.youtube.com/watch?v=kKKM8Y-u7ds",
            "אנרגיה קינטית ופוטנציאלית": "https://www.youtube.com/watch?v=ASZv3tIK54k",
            "מבנה התא, גרעין ופוטוסינתזה": "https://www.youtube.com/watch?v=68_jtXv9k4c"
        },
        "לשון והבעה עברית: תחביר, מערכת הצורות והבנת הנקרא": {
            "מערכת הצורות: זיהוי שורש ובניינים": "https://www.youtube.com/watch?v=uK1X_0kZq6g",
            "תחביר: משפט פשוט, מחובר ומורכב": "https://www.youtube.com/watch?v=5VjWl-z_c_U"
        },
        "היסטוריה, תנ\"ך ואזרחות: פרקי חובה": {
            "היסטוריה: הגורמים למלחמת העולם הראשונה": "https://www.youtube.com/watch?v=SLj5r2nZHB8",
            "אזרחות: עקרון שלטון החוק וזכויות האדם": "https://www.youtube.com/watch?v=cMKe0k_k1Qk"
        }
    }
    
    current_videos = video_db.get(category, {})
    chosen_video_title = st.selectbox("בחר שיעור ספציפי:", list(current_videos.keys()))
    selected_url = current_videos[chosen_video_title]
    
    col_play, col_notes = st.columns([1.2, 0.8])
    with col_play:
        st.video(selected_url)
        st.markdown(f"[🔗 לחץ כאן לצפייה ישירה ב-YouTube]({selected_url})")
    with col_notes:
        st.subheader("📝 סיכום מהיר של השיעור")
        st.caption("רוצה נקודות ברזל על נושא הסרטון?")
        if st.button("סכם לי את עיקרי הנושא בבולטים ⚡", use_container_width=True):
            prompt = f"סכם ב-4 בולטים ברורים את הנושא: {chosen_video_title} עבור תלמיד ב-{chosen_grade}. {anti_yap_rule}"
            with st.spinner("מחלץ סיכום..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 3: חיבור לבית ספר וספרים -----------------
elif room == "🏫 חיבור ל-Classroom וספרי לימוד":
    st.title("🏫 חיבור לבית הספר: Classroom & ספרי לימוד דיגיטליים")
    st.write("גישה מהירה לפורטלים הלימודיים ומפענח מטלות חכם:")
    
    st.markdown("""
        <div>
            <a class="portal-link" href="https://classroom.google.com" target="_blank">🌐 פתח Google Classroom</a>
            <a class="portal-link" href="https://www.classoos.com" target="_blank">📖 פתח Classoos (ספרי לימוד)</a>
            <a class="portal-link" href="https://my.education.gov.il" target="_blank">🏛️ פורטל משרד החינוך</a>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("📥 מפענח מטלות ושיעורי בית מהמורה")
    st.write("העתק את ההודעה שהמורה פרסם/ה ב-Classroom או בוואטסאפ של הכיתה, וה-AI יפרק לך אותה למשימות ברורות:")
    
    teacher_post = st.text_area("הדבק כאן את נוסח המטלה / ההודעה:", height=130, placeholder="למשל: למחר לפתוח ספר מתמטיקה עמוד 142 תרגילים 5-12 ולהגיש סיכום על מרד בר כוכבא...")
    
    if st.button("פרק לי את המטלה למשימות ושלבי ביצוע 📋", use_container_width=True):
        if not teacher_post.strip():
            st.warning("הדבק קודם את הודעת המורה!")
        else:
            prompt = (
                f"התלמיד ב-{student_context} קיבל את הודעת המטלה הבאה:\n{teacher_post}\n\n"
                "בצע פירוק חכם:\n"
                "1. **מה נדרש להגיש ומתי (דד-ליין)**\n"
                "2. **אילו ספרים, עמודים או תרגילים צריך לפתור**\n"
                "3. **תוכנית פעולה מהירה שלב אחרי שלב כדי לסיים את זה מהר**\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנתח מטלה..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 4: דפי תרגול להדפסה -----------------
elif room == "🖨️ דפי תרגול ומבחנים להדפסה":
    st.title("🖨️ מחולל דפי עבודה, תרגול ומבחנים להדפסה")
    st.write(f"הפק דף תרגול מושלם ומעוצב עבור **{chosen_grade}** שניתן להדפיס בלחיצה אחת!")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        sheet_topic = st.text_input("📚 מה נושא דף התרגול?", placeholder="למשל: משוואות ריבועיות, זמנים באנגלית, הגורמים לעלייה השנייה...")
        sheet_subject = st.selectbox("מקצוע:", ["מתמטיקה", "אנגלית", "מדעים", "היסטוריה / אזרחות / תנ\"ך", "לשון"])
    with col_p2:
        sheet_length = st.selectbox("היקף הדף:", ["דף עבודה מהיר (4-5 שאלות)", "מבחן מלא (8-10 שאלות כולל ניקוד)"])
        include_answers = st.checkbox("הוסף דף תשובות בסוף הדף", value=True)

    if st.button("ייצר דף תרגול להדפסה 📄", use_container_width=True):
        if not sheet_topic.strip():
            st.warning("חובה לציין את נושא דף התרגול!")
        else:
            prompt = (
                f"צור דף תרגול ומבחן ברור ומקצועי בעברית לתלמיד ב-{student_context}.\n"
                f"מקצוע: {sheet_subject}, נושא: {sheet_topic}, היקף: {sheet_length}.\n"
                "דרישות הדף:\n"
                "1. כותרת עליונה עם שם הדף, כיתה ומקום לציון ולשם תלמיד.\n"
                "2. שאלות מנוסחות היטב ברמות קושי עולות עם מקום לכתיבת תשובה.\n"
                + ("3. בסוף הדף הוסף חלק של 'מחוון ותשובות סופיות לבדיקה עצמית'.\n" if include_answers else "")
            )
            with st.spinner("מייצר דף עבודה..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.session_state["printable_sheet"] = res.text

    if "printable_sheet" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state["printable_sheet"])
        st.markdown("""
            <div style="text-align: center; margin-top: 20px;">
                <button onclick="window.print()" style="padding: 12px 24px; font-size: 16px; background-color: #16a34a; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">
                    🖨️ הדפס דף תרגול זה (Print)
                </button>
            </div>
        """, unsafe_allow_html=True)

# ----------------- חדר 5: סורק תמונות -----------------
elif room == "📸 סורק תמונות ומבחנים":
    st.title("📸 סורק תמונות ושיעורי בית")
    st.write(f"העלה צילום מדף העבודה או הספר עבור **{chosen_grade}** ({math_units} / {eng_units}):")
    
    photo_topic = st.text_input("📚 1. מה החומר / הנושא שמופיע בתמונה?", placeholder="למשל: גאומטריה אנליטית, שאלות בגרות בתנ\"ך...")
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

# ----------------- חדר 6: מלטשת תשובות -----------------
elif room == "💯 מלטשת תשובות למאיות":
    st.title("💯 מלטשת תשובות לציון 100")
    st.write(f"התאמת ניסוח למחוון בחינה עבור **{chosen_grade}** ({math_units} / {eng_units}).")
    
    ans_topic = st.text_input("📚 1. מה החומר / הנושא הנלמד והמקצוע?", placeholder="למשל: היסטוריה - העלייה השנייה / אזרחות - זכויות אדם...")
    q_text = st.text_input("❓ 2. מה השאלה שנשאלת?")
    user_ans = st.text_area("✍️ 3. מה התשובה שכתבת:", height=130)
    
    if st.button("שדרג לי את התשובה ל-100 🚀", use_container_width=True):
        if not ans_topic.strip() or not user_ans.strip():
            st.warning("חובה למלא את החומר הנלמד ואת התשובה שכתבת!")
        else:
            prompt = (
                f"אתה מעריך בחינות קפדן שבודק תשובה של תלמיד ב-{chosen_grade} ({math_units}, {eng_units}).\n"
                f"החומר הנלמד: {ans_topic}\nשאלה: {q_text}\nתשובה: {user_ans}\n\n"
                "החזר:\n1. **ציון מוערך (מתוך 100)**\n2. **מה חסר לפי מחוון הבדיקה**\n3. **תשובה מושלמת סופית**: נוסח שסוגר את מלוא הנקודות.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מנתח לפי מחוון..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 7: מעבדת מתמטיקה -----------------
elif room == "📐 מעבדת מתמטיקה ומדעים":
    st.title("📐 מעבדת פירוק מתמטיקה ומדעים")
    st.write(f"פתרון שלב-אחר-שלב המותאם בדיוק לרמת: **{chosen_grade} — {math_units}**")
    
    math_topic = st.text_input("📚 1. מה הנושא הנלמד כרגע?", placeholder="למשל: חקירת פולינום, טריגונומטריה, משוואות ריבועיות...")
    math_input = st.text_area("🔢 2. הזן את התרגיל או השאלה:", height=120)
    
    if st.button("פרק לי את התרגיל לפי רמת היחידות 🧠", use_container_width=True):
        if not math_topic.strip() or not math_input.strip():
            st.warning("חובה לציין את הנושא הנלמד ואת התרגיל!")
        else:
            prompt = (
                f"פתור את תרגיל המתמטיקה הבא עבור תלמיד ב-{chosen_grade} ברמת {math_units}.\n"
                f"הנושא: {math_topic}\nתרגיל: {math_input}\n\n"
                "פתור שלב אחרי שלב בבירור עם נימוק קצר ליד כל שלב, וסמן תוצאה סופית מודגשת.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner(f"פותר לפי רמת {math_units}..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 8: שליף חירום -----------------
elif room == "🚨 שליף חירום (לפני מבחן)":
    st.title("🚨 שליף חירום: 60 שניות לפני מבחן")
    st.write(f"תמצית ברזל עבור **{chosen_grade}** ({math_units} / {eng_units}):")
    
    panic_topic = st.text_input("📚 מה החומר / הנושא של המבחן כרגע?", placeholder="למשל: משפט חוצה זווית, מרד בר כוכבא, Module E connectors...")
    
    if st.button("הצל אותי עכשיו ⚡", use_container_width=True):
        if not panic_topic.strip():
            st.warning("הזן קודם את החומר הנלמד!")
        else:
            prompt = (
                f"התלמיד ב-{chosen_grade} ({math_units}, {eng_units}) נכנס בעוד דקה למבחן על החומר: {panic_topic}.\n"
                "החזר אך ורק:\n1. **3 משפטי זהב** שחייבים לרשום במבחן.\n2. **הטעות הנפוצה ביותר** שתלמידים נופלים בה.\n3. **מושג חובה אחד** שהבוחן מחפש בעין.\n"
                f"{anti_yap_rule}"
            )
            with st.spinner("מחלץ שליף..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(f'<div class="cheat-card">{res.text}</div>', unsafe_allow_html=True)

# ----------------- חדר 9: מחולל בחנים -----------------
elif room == "🧠 מחולל בחנים אינטראקטיבי":
    st.title("🧠 מחולל בחנים אינטראקטיבי")
    st.write(f"תרגול ממוקד לרמת **{chosen_grade}** ({math_units} / {eng_units}):")
    
    quiz_topic = st.text_input("📚 מה החומר / הנושא שתרצה לבחון עליו את עצמך?", placeholder="למשל: אנרגיה קינטית, טריגו במרחב...")
    
    if st.button("ייצר לי שאלות בדיקה 🎯", use_container_width=True):
        if not quiz_topic.strip():
            st.warning("הזן קודם את החומר הנלמד!")
        else:
            prompt = (
                f"צור 3 שאלות תרגול עבור תלמיד ב-{chosen_grade} ({math_units}, {eng_units}) על החומר: {quiz_topic}.\n"
                "לכל שאלה ספק 4 אפשרויות (א-ד), ומתחת לכל שאלה הוסף את התשובה הנכונה עם הסבר קצרצר."
            )
            with st.spinner("בונה שאלות..."):
                res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                st.markdown(res.text)

# ----------------- חדר 10: מתכנן לו״ז -----------------
elif room == "📅 מתכנן לו״ז למבחן":
    st.title("📅 מתכנן לוח זמנים אישי למבחן")
    st.write(f"תוכנית עבודה מותאמת ל-**{chosen_grade}**:")
    
    topics = st.text_area("📚 1. מה כל החומר והנושאים שצריך להספיק למבחן?", placeholder="למשל: פרקים 1 עד 4 בספר, בעיות קיצון...")
    
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

# ----------------- חדר 11: חוות דעת -----------------
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
