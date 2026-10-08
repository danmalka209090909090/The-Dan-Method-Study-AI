import streamlit as st
from google import genai

st.set_page_config(
    page_title="The Dan Method: Study AI",
    page_icon="⚡",
    layout="centered"
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
</style>
""", unsafe_allow_html=True)

st.title("⚡ The Dan Method: Study AI")
st.caption("פלטפורמת ה-AI החכמה לפיצוח מבחנים, שיעורי בית ומאיות")

api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ מפתח GEMINI_API_KEY לא מוגדר ב-Secrets של Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

# חלוקה ללשוניות מקצועיות
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💯 משדרג ל-100", 
    "📐 מפרק מתמטיקה", 
    "⚡ שליף סיכום", 
    "🎯 סימולציית מבחן",
    "🇬🇧 שדרוג אנגלית"
])

# --- לשונית 1: משדרג ל-100 ---
with tab1:
    st.subheader("שדרוג תשובה לרמת 100 עגול")
    st.write("הדבק את השאלה ואת התשובה שלך, וה-AI יבנה ממנה תשובה לציון מושלם.")
    q1 = st.text_input("השאלה מהמבחן / שיעורי הבית:", key="q1")
    ans1 = st.text_area("התשובה שכתבת:", height=130, key="ans1")
    
    if st.button("בדוק ושדרג ל-100 🚀", key="btn1", use_container_width=True):
        if not ans1.strip():
            st.warning("הזן קודם את התשובה שלך!")
        else:
            prompt = (
                "אתה מעריך מבחנים קפדן ומורה פרטי מקצועי. התלמיד ענה על השאלה הבאה.\n"
                f"שאלה: {q1}\nתשובת התלמיד: {ans1}\n\n"
                "החזר בפורמט הבא:\n"
                "1. **ציון מוערך כרגע (מתוך 100)**\n"
                "2. **מה היה חסר לפי מחוון הבדיקה** (קצר ומדויק)\n"
                "3. **תשובת 100 מושלמת**: נסח תשובה מלאה ואידיאלית שהבוחן ייתן עליה את מלוא הנקודות."
            )
            with st.spinner("מנתח תשובה..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("הניתוח מוכן:")
                    st.write(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# --- לשונית 2: מפרק מתמטיקה ---
with tab2:
    st.subheader("פירוק תרגילי מתמטיקה שלב אחרי שלב")
    st.write("מתאים לאלגברה, משוואות, גיאומטריה, חקירת פונקציות וטריגו.")
    math_input = st.text_area("כתוב את התרגיל (אפשר גם להעתיק ניסוח מילולי):", height=120, key="math_in")
    
    if st.button("פרק לי את הפתרון 🧠", key="btn2", use_container_width=True):
        if not math_input.strip():
            st.warning("הזן תרגיל לפתרון!")
        else:
            prompt = (
                "אתה מורה פרטי תותח למתמטיקה. פתור את התרגיל הבא:\n"
                f"{math_input}\n\n"
                "דרישות הפתרון:\n"
                "1. פתור שלב אחרי שלב בצורה ברורה.\n"
                "2. ליד כל שלב הסבר במשפט קצר מה הכלל או הנוסחה שהשתמשת בה.\n"
                "3. הדגש בצורה ברורה את **התשובה הסופית**."
            )
            with st.spinner("פותר שלב אחרי שלב..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("הפתרון:")
                    st.write(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# --- לשונית 3: שליף סיכום ---
with tab3:
    st.subheader("תקציר ממוקד לבחינה (בלי חפירות)")
    st.write("זורקים חומר גדול (היסטוריה, אזרחות, תנ״ך, ספרות) ומקבלים רק את מה שחייבים לזכור.")
    summary_input = st.text_area("הדבק כאן את הסיכום או הפרק:", height=150, key="sum_in")
    
    if st.button("חלץ נקודות מפתח ⚡", key="btn3", use_container_width=True):
        if not summary_input.strip():
            st.warning("הזן קודם טקסט לסיכום!")
        else:
            prompt = (
                "אתה מומחה להכנה למבחנים בתיכון. תמצת את החומר הבא עבור תלמיד שלומד למבחן:\n"
                f"{summary_input}\n\n"
                "כללים:\n"
                "- עד 5 נקודות קריטיות שחובה לדעת.\n"
                "- רשימת 'מילות מפתח ומושגי חובה' שהבוחן יחפש בתשובה.\n"
                "- טיפ זהב אחד איך לזכור את זה בקלות."
            )
            with st.spinner("מחלץ תמצית..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("השליף למבחן:")
                    st.write(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# --- לשונית 4: סימולציית מבחן ---
with tab4:
    st.subheader("בוחן פתע לבדיקת מוכנות")
    st.write("הזן את נושא המבחן או חומר הקריאה, וקבל שאלות סימולציה כדי לבחון את עצמך.")
    test_topic = st.text_area("על איזה נושא/חומר המבחן שלך?", height=120, key="test_in")
    
    if st.button("ייצר שאלות מבחן 🎯", key="btn4", use_container_width=True):
        if not test_topic.strip():
            st.warning("הזן נושא!")
        else:
            prompt = (
                "צור סימולציית מבחן ממוקדת על בסיס החומר הבא:\n"
                f"{test_topic}\n\n"
                "צור:\n"
                "1. שתי שאלות פתוחות ברמת בחינה אמיתית.\n"
                "2. שאלת חשיבה/יישום אחת מאתגרת.\n"
                "3. מתחת לכל שאלה כתוב בפירוט מה הנקודות שהתשובה חייבת להכיל (תשובון מקוצר)."
            )
            with st.spinner("בונה שאלות..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("שאלות המבחן:")
                    st.write(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# --- לשונית 5: שדרוג אנגלית ---
with tab5:
    st.subheader("שדרוג חיבורים וטקסטים באנגלית")
    st.write("הדבק את החיבור שלך (Essay) באנגלית כדי לשדרג את הדקדוק ואוצר המילים.")
    eng_text = st.text_area("החיבור שלך באנגלית:", height=140, key="eng_in")
    
    if st.button("שדרג לי את האנגלית ✨", key="btn5", use_container_width=True):
        if not eng_text.strip():
            st.warning("הזן טקסט באנגלית!")
        else:
            prompt = (
                "You are an expert English teacher. Review and improve this student essay:\n"
                f"{eng_text}\n\n"
                "Provide:\n"
                "1. Corrected & Polished Version (using rich high-school/matriculation level vocabulary).\n"
                "2. Key grammar or word choices improved (with Hebrew explanations)."
            )
            with st.spinner("משדרג את החיבור..."):
                try:
                    res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    st.success("הגרסה המשודרגת:")
                    st.write(res.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")
