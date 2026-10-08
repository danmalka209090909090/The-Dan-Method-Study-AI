import streamlit as st
from google import genai

st.set_page_config(
    page_title="The Dan Method: Study AI",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ The Dan Method: Study AI")
st.caption("השיטה המהירה לסיכומי מבחן, פיצוח שאלות ופתרון מתמטיקה")

# משיכת מפתח אוטומטית מהגדרות Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

mode = st.radio(
    "בחר מצב עבודה:",
    ["תקצר לי למבחן", "איך להוציא 100", "פירוק מתמטיקה שלב אחרי שלב"],
    horizontal=True
)

user_text = st.text_area(
    "הדבק כאן את החומר, השאלה או התרגיל:",
    height=160,
    placeholder="למשל: סיכום בהיסטוריה, תשובה שכתבת, או תרגיל במתמטיקה..."
)

if st.button("🚀 הפעל את השיטה", use_container_width=True):
    if not api_key:
        st.error("חסר GEMINI_API_KEY בהגדרות המערכת!")
    elif not user_text.strip():
        st.warning("הזן קודם טקסט או תרגיל לניתוח!")
    else:
        client = genai.Client(api_key=api_key)
        
        if mode == "תקצר לי למבחן":
            prompt = (
                "אתה עוזר לימודי ממוקד לתלמידי תיכון בישראל. "
                "החזר אך ורק סיכום קצר, חד ולעניין: "
                "1. עד 4 בולטים קריטיים בלבד. "
                "2. רשימת 'מושגי חובה' שהבוחן במבחן מחפש בעין. "
                "בלי שום הקדמות או חפירות."
            )
        elif mode == "איך להוציא 100":
            prompt = (
                "אתה מורה פרטי שבודק תשובה של תלמיד. "
                "בדוק את התשובה, תן ציון משוער מתוך 100, "
                "וכתוב בדיוק איזה משפט להוסיף כדי לקבל 100 מלא."
            )
        else:
            prompt = (
                "אתה מורה מעולה למתמטיקה. "
                "פתור את התרגיל שלב אחרי שלב. בכל שלב תסביר במשפט קצר מה עשית ומדוע. "
                "הדגש את התוצאה הסופית."
            )

        with st.spinner("מעבד תשובה..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=f"{prompt}\n\nתוכן התלמיד:\n{user_text}"
                )
                st.success("התוצאה מוכנה:")
                st.write(response.text)
            except Exception as e:
                st.error(f"שגיאה בהפעלת המודל: {e}")
