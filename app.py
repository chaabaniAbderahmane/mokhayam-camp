import streamlit as st
import sqlite3
import hashlib
import io
import random
from datetime import datetime, date

import pandas as pd

try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_OK = True
except Exception:
    BARCODE_OK = False

# =========================================================
#                     الإعدادات العامة
# =========================================================
DB_PATH = "camp.db"
ROOMS = [1, 2, 3, 4, 5]
ROOM_CAPACITY = 10

WILAYAS = [
    "أدرار", "الشلف", "الأغواط", "أم البواقي", "باتنة", "بجاية", "بسكرة", "بشار",
    "البليدة", "البويرة", "تمنراست", "تبسة", "تلمسان", "تيارت", "تيزي وزو",
    "الجزائر", "الجلفة", "جيجل", "سطيف", "سعيدة", "سكيكدة", "سيدي بلعباس",
    "عنابة", "قالمة", "قسنطينة", "المدية", "مستغانم", "المسيلة", "معسكر",
    "ورقلة", "وهران", "البيض", "إليزي", "برج بوعريريج", "بومرداس", "الطارف",
    "تندوف", "تيسمسيلت", "الوادي", "خنشلة", "سوق أهراس", "تيبازة", "ميلة",
    "عين الدفلى", "النعامة", "عين تموشنت", "غرداية", "غليزان", "تيميمون",
    "برج باجي مختار", "أولاد جلال", "بني عباس", "عين صالح", "عين قزام",
    "تقرت", "جانت", "المغير", "المنيعة",
]

TRANSPORT_OPTIONS = ["حافلة", "سيارة خاصة", "قطار", "دراجة نارية", "أخرى"]

# =========================================================
#                     قاعدة البيانات
# =========================================================
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            created_at TEXT
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            wilaya TEXT,
            phone TEXT,
            transport TEXT,
            entry_date TEXT,
            room_number INTEGER NOT NULL,
            subscription REAL NOT NULL DEFAULT 0,
            code TEXT UNIQUE,
            present INTEGER DEFAULT 0,
            present_time TEXT,
            added_by TEXT,
            created_at TEXT
        )"""
    )
    conn.commit()
    c.execute("SELECT COUNT(*) AS c FROM admins")
    if c.fetchone()["c"] == 0:
        c.execute(
            "INSERT INTO admins (username, password, full_name, created_at) VALUES (?,?,?,?)",
            ("admin", hash_pw("admin123"), "المدير العام", datetime.now().isoformat()),
        )
        conn.commit()
    conn.close()


def room_count(conn, room_number):
    c = conn.execute(
        "SELECT COUNT(*) AS c FROM participants WHERE room_number=?", (room_number,)
    )
    return c.fetchone()["c"]


def generate_code(conn, room_number):
    while True:
        candidate = f"MSC{room_number}{random.randint(10000, 99999)}"
        c = conn.execute("SELECT id FROM participants WHERE code=?", (candidate,))
        if c.fetchone() is None:
            return candidate


def make_barcode_png(code: str):
    if not BARCODE_OK:
        return None
    try:
        code128 = barcode.get_barcode_class("code128")
        writer = ImageWriter()
        writer.set_options(
            {"write_text": False, "module_height": 9.0, "quiet_zone": 2.0}
        )
        obj = code128(code, writer=writer)
        buf = io.BytesIO()
        obj.write(buf)
        return buf.getvalue()
    except Exception:
        return None


# =========================================================
#                     التنسيق والتصميم
# =========================================================
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

        html, body, [class*="css"], .stApp {
            font-family: 'Tajawal', sans-serif !important;
            direction: rtl;
        }

        :root{
            --black:#141414;
            --white:#ffffff;
            --green:#0b7a3c;
            --green-dark:#065a2b;
            --red:#c8102e;
            --bg:#f4f6f5;
            --card:#ffffff;
            --muted:#6b7280;
        }

        .stApp{
            background: var(--bg);
        }

        #MainMenu, footer, header {visibility: hidden;}

        .block-container{
            padding-top: 1rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }

        .camp-header{
            border-radius: 18px;
            overflow: hidden;
            margin-bottom: 1.3rem;
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        }
        .camp-header-strip{
            height: 8px;
            width: 100%;
            background: linear-gradient(90deg, var(--black) 0 33%, var(--white) 33% 66%, var(--green) 66% 100%);
        }
        .camp-header-body{
            background: linear-gradient(135deg, var(--green-dark), var(--green));
            padding: 22px 26px;
            position: relative;
            border-right: 8px solid var(--red);
        }
        .camp-header-body h1{
            color: var(--white);
            margin: 0;
            font-weight: 900;
            font-size: 1.9rem;
        }
        .camp-header-body p{
            color: rgba(255,255,255,0.9);
            margin: 4px 0 0 0;
            font-size: 0.95rem;
        }

        .camp-card{
            background: var(--card);
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: 0 3px 14px rgba(0,0,0,0.07);
            margin-bottom: 14px;
            border-top: 4px solid var(--green);
        }
        .camp-card.red{ border-top-color: var(--red); }
        .camp-card.black{ border-top-color: var(--black); }

        .metric-box{
            text-align: center;
            padding: 14px 8px;
            border-radius: 14px;
            background: var(--card);
            box-shadow: 0 3px 12px rgba(0,0,0,0.07);
            border-bottom: 5px solid var(--green);
        }
        .metric-box .num{
            font-size: 1.6rem;
            font-weight: 900;
            color: var(--black);
        }
        .metric-box .lbl{
            font-size: 0.85rem;
            color: var(--muted);
            margin-top: 2px;
        }

        .stButton>button{
            border-radius: 12px;
            font-weight: 700;
            padding: 0.55rem 1.1rem;
            border: none;
            background: var(--green);
            color: white;
            width: 100%;
            transition: 0.15s ease-in-out;
        }
        .stButton>button:hover{
            background: var(--green-dark);
            transform: translateY(-1px);
        }

        .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"]{
            border-radius: 10px !important;
        }

        div[data-baseweb="tab-list"]{
            gap: 4px;
        }
        button[data-baseweb="tab"]{
            border-radius: 10px 10px 0 0 !important;
            font-weight: 700;
        }

        .present-yes{
            color: var(--green-dark);
            font-weight: 800;
        }
        .present-no{
            color: var(--red);
            font-weight: 800;
        }

        @media (max-width: 640px){
            .camp-header-body h1{ font-size: 1.35rem; }
            .camp-header-body{ padding: 16px 16px; }
            .block-container{ padding-left: 0.6rem; padding-right: 0.6rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def header():
    st.markdown(
        """
        <div class="camp-header">
            <div class="camp-header-strip"></div>
            <div class="camp-header-body">
                <h1>المخيم الصيفي</h1>
                <p>نظام تسجيل ومتابعة المشاركين</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_box(number, label):
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="num">{number}</div>
            <div class="lbl">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
#                     صفحة الدخول
# =========================================================
def login_page():
    header()
    st.markdown('<div class="camp-card">', unsafe_allow_html=True)
    st.subheader("تسجيل دخول المسؤول")
    with st.form("login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("دخول")
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        conn = get_conn()
        row = conn.execute(
            "SELECT * FROM admins WHERE username=?", (username.strip(),)
        ).fetchone()
        conn.close()
        if row and row["password"] == hash_pw(password):
            st.session_state.logged_in = True
            st.session_state.username = row["username"]
            st.session_state.full_name = row["full_name"]
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

    st.caption("الحساب الافتراضي: admin / admin123 — يُفضّل تغييره أو إضافة حساب جديد بعد الدخول")


# =========================================================
#                 لوحة التحكم / الإحصائيات
# =========================================================
def dashboard_tab():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM participants").fetchall()
    conn.close()

    df = pd.DataFrame([dict(r) for r in rows])

    total_participants = len(df)
    total_general = df["subscription"].sum() if not df.empty else 0
    total_present = int(df["present"].sum()) if not df.empty else 0

    cols = st.columns(3)
    with cols[0]:
        metric_box(total_participants, "عدد المشاركين")
    with cols[1]:
        metric_box(f"{total_general:.0f}", "المجموع العام للاشتراكات")
    with cols[2]:
        metric_box(total_present, "عدد الحاضرين")

    st.markdown("### مجموع الاشتراك لكل غرفة")
    room_cols = st.columns(5)
    for i, room in enumerate(ROOMS):
        if not df.empty:
            room_df = df[df["room_number"] == room]
            count = len(room_df)
            total_room = room_df["subscription"].sum()
        else:
            count, total_room = 0, 0
        with room_cols[i]:
            st.markdown(
                f"""
                <div class="camp-card{' red' if i % 2 else ''}" style="text-align:center;">
                    <div style="font-weight:900; font-size:1.05rem;">الغرفة {room}</div>
                    <div style="color:#6b7280; font-size:0.85rem; margin:4px 0;">{count} / {ROOM_CAPACITY} مشاركين</div>
                    <div style="font-weight:800; color:#0b7a3c;">{total_room:.0f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div class="camp-card black" style="text-align:center; margin-top: 6px;">
            <div style="font-size:0.95rem; color:#6b7280;">المجموع العام لكل الغرف</div>
            <div style="font-size:1.8rem; font-weight:900;">{total_general:.0f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
#                 إضافة مشارك
# =========================================================
def add_participant_tab():
    st.markdown('<div class="camp-card">', unsafe_allow_html=True)
    st.subheader("إضافة مشارك جديد")

    conn = get_conn()
    room_status = {r: room_count(conn, r) for r in ROOMS}
    conn.close()

    available_rooms = [r for r in ROOMS if room_status[r] < ROOM_CAPACITY]
    if not available_rooms:
        st.warning("جميع الغرف ممتلئة (5 غرف × 10 أشخاص)")
    else:
        with st.form("add_participant_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                first_name = st.text_input("الاسم")
                wilaya = st.selectbox("الولاية", WILAYAS)
                transport = st.selectbox("وسيلة النقل", TRANSPORT_OPTIONS)
                subscription = st.number_input("الاشتراك", min_value=0.0, step=100.0)
            with c2:
                last_name = st.text_input("اللقب")
                phone = st.text_input("رقم الهاتف")
                entry_date = st.date_input("تاريخ الدخول", value=date.today())
                room_number = st.selectbox(
                    "الغرفة",
                    available_rooms,
                    format_func=lambda r: f"الغرفة {r} ({room_status[r]}/{ROOM_CAPACITY})",
                )
            submitted = st.form_submit_button("إضافة المشارك")

        if submitted:
            if not first_name.strip() or not last_name.strip():
                st.error("الرجاء إدخال الاسم واللقب")
            else:
                conn = get_conn()
                if room_count(conn, room_number) >= ROOM_CAPACITY:
                    st.error("هذه الغرفة أصبحت ممتلئة، الرجاء اختيار غرفة أخرى")
                else:
                    code = generate_code(conn, room_number)
                    conn.execute(
                        """INSERT INTO participants
                        (first_name, last_name, wilaya, phone, transport, entry_date,
                         room_number, subscription, code, present, added_by, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,0,?,?)""",
                        (
                            first_name.strip(),
                            last_name.strip(),
                            wilaya,
                            phone.strip(),
                            transport,
                            entry_date.isoformat(),
                            room_number,
                            subscription,
                            code,
                            st.session_state.get("username", ""),
                            datetime.now().isoformat(),
                        ),
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"تمت إضافة {first_name} {last_name} بنجاح — الرمز: {code}")

                    png = make_barcode_png(code)
                    if png:
                        st.image(png, caption=f"رمز الدخول: {code}", width=280)
                    else:
                        st.info(f"رمز الدخول الخاص بالمشارك: {code}")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
#                 قائمة المشاركين
# =========================================================
def participants_tab():
    st.markdown('<div class="camp-card">', unsafe_allow_html=True)
    st.subheader("لائحة المشاركين")

    c1, c2 = st.columns([1, 2])
    with c1:
        room_filter = st.selectbox("تصفية حسب الغرفة", ["الكل"] + [f"الغرفة {r}" for r in ROOMS])
    with c2:
        search = st.text_input("بحث بالاسم أو اللقب أو الهاتف أو الرمز")

    conn = get_conn()
    rows = conn.execute("SELECT * FROM participants ORDER BY room_number, id").fetchall()
    conn.close()

    data = [dict(r) for r in rows]

    if room_filter != "الكل":
        room_num = int(room_filter.replace("الغرفة ", ""))
        data = [d for d in data if d["room_number"] == room_num]

    if search.strip():
        s = search.strip().lower()
        data = [
            d
            for d in data
            if s in (d["first_name"] or "").lower()
            or s in (d["last_name"] or "").lower()
            or s in (d["phone"] or "").lower()
            or s in (d["code"] or "").lower()
        ]

    st.markdown("</div>", unsafe_allow_html=True)

    if not data:
        st.info("لا يوجد مشاركون مطابقون")
        return

    for d in data:
        present_html = (
            '<span class="present-yes">حاضر</span>'
            if d["present"]
            else '<span class="present-no">غير حاضر</span>'
        )
        st.markdown(
            f"""
            <div class="camp-card">
                <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:6px;">
                    <div style="font-weight:900; font-size:1.05rem;">{d['first_name']} {d['last_name']}</div>
                    <div>{present_html}</div>
                </div>
                <div style="color:#6b7280; font-size:0.9rem; margin-top:6px; line-height:1.9;">
                    الولاية: {d['wilaya'] or '—'} &nbsp;|&nbsp; الهاتف: {d['phone'] or '—'}<br>
                    وسيلة النقل: {d['transport'] or '—'} &nbsp;|&nbsp; تاريخ الدخول: {d['entry_date'] or '—'}<br>
                    الغرفة: {d['room_number']} &nbsp;|&nbsp; الاشتراك: {d['subscription']:.0f}<br>
                    الرمز: {d['code']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("عرض الرمز الشريطي"):
            png = make_barcode_png(d["code"])
            if png:
                st.image(png, width=260)
            else:
                st.write(d["code"])


# =========================================================
#                 تسجيل الحضور
# =========================================================
def attendance_tab():
    st.markdown('<div class="camp-card">', unsafe_allow_html=True)
    st.subheader("تسجيل الحضور")
    st.caption("امسح الرمز الشريطي أو أدخله يدويًا ثم اضغط تأكيد")

    with st.form("attendance_form", clear_on_submit=True):
        code_input = st.text_input("رمز المشارك")
        submitted = st.form_submit_button("أنا حاضر")
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted and code_input.strip():
        conn = get_conn()
        row = conn.execute(
            "SELECT * FROM participants WHERE code=?", (code_input.strip(),)
        ).fetchone()
        if row is None:
            st.error("لم يتم العثور على مشارك بهذا الرمز")
        else:
            conn.execute(
                "UPDATE participants SET present=1, present_time=? WHERE id=?",
                (datetime.now().isoformat(), row["id"]),
            )
            conn.commit()
            st.success(f"أنا حاضر — {row['first_name']} {row['last_name']} (الغرفة {row['room_number']})")
        conn.close()


# =========================================================
#                 إدارة المسؤولين
# =========================================================
def admins_tab():
    st.markdown('<div class="camp-card">', unsafe_allow_html=True)
    st.subheader("إضافة مسؤول جديد")
    with st.form("add_admin_form", clear_on_submit=True):
        full_name = st.text_input("الاسم الكامل")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("إضافة المسؤول")
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not username.strip() or not password.strip():
            st.error("الرجاء إدخال اسم المستخدم وكلمة المرور")
        else:
            conn = get_conn()
            exists = conn.execute(
                "SELECT id FROM admins WHERE username=?", (username.strip(),)
            ).fetchone()
            if exists:
                st.error("اسم المستخدم موجود مسبقًا")
            else:
                conn.execute(
                    "INSERT INTO admins (username, password, full_name, created_at) VALUES (?,?,?,?)",
                    (username.strip(), hash_pw(password), full_name.strip(), datetime.now().isoformat()),
                )
                conn.commit()
                st.success(f"تمت إضافة المسؤول {username} بنجاح")
            conn.close()

    st.markdown('<div class="camp-card black">', unsafe_allow_html=True)
    st.subheader("قائمة المسؤولين")
    conn = get_conn()
    admins = conn.execute("SELECT username, full_name, created_at FROM admins").fetchall()
    conn.close()
    for a in admins:
        st.markdown(f"- **{a['full_name'] or a['username']}** ({a['username']})")
    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
#                     التطبيق الرئيسي
# =========================================================
def main():
    st.set_page_config(page_title="المخيم الصيفي", layout="wide")
    inject_css()
    init_db()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
        return

    header()

    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown(f"مرحبًا، **{st.session_state.get('full_name') or st.session_state.get('username')}**")
    with top_r:
        if st.button("تسجيل الخروج"):
            st.session_state.logged_in = False
            st.rerun()

    tabs = st.tabs(
        ["لوحة التحكم", "المشاركون", "إضافة مشارك", "تسجيل الحضور", "المسؤولون"]
    )
    with tabs[0]:
        dashboard_tab()
    with tabs[1]:
        participants_tab()
    with tabs[2]:
        add_participant_tab()
    with tabs[3]:
        attendance_tab()
    with tabs[4]:
        admins_tab()


if __name__ == "__main__":
    main()
