# -*- coding: utf-8 -*-
"""
تطبيق إدارة لائحة المشاركين - المخيم الصيفي
Streamlit app for managing summer camp participants with admin auth,
room-based subscriptions, barcode-based check-in and a Palestine-themed
responsive UI.
"""

import io
import hashlib
from datetime import date, datetime

import streamlit as st
import pandas as pd
import sqlite3
import barcode
from barcode.writer import ImageWriter

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
DB_PATH = "camp.db"
ROOMS = [1, 2, 3, 4, 5]
ROOM_CAPACITY = 10
CAMP_NAME = "المخيم الصيفي"

WILAYAS = [
    "أدرار", "الشلف", "الأغواط", "أم البواقي", "باتنة", "بجاية", "بسكرة",
    "بشار", "البليدة", "البويرة", "تمنراست", "تبسة", "تلمسان", "تيارت",
    "تيزي وزو", "الجزائر", "الجلفة", "جيجل", "سطيف", "سعيدة", "سكيكدة",
    "سيدي بلعباس", "عنابة", "قالمة", "قسنطينة", "المدية", "مستغانم",
    "المسيلة", "معسكر", "ورقلة", "وهران", "البيض", "إليزي", "برج بوعريريج",
    "بومرداس", "الطارف", "تندوف", "تيسمسيلت", "الوادي", "خنشلة", "سوق أهراس",
    "تيبازة", "ميلة", "عين الدفلى", "النعامة", "عين تموشنت", "غرداية",
    "غليزان", "تيميمون", "برج باجي مختار", "أولاد جلال", "بني عباس",
    "عين صالح", "عين قزام", "تقرت", "جانت", "المغير", "المنيعة",
]

TRANSPORT_OPTIONS = ["حافلة الجمعية", "سيارة خاصة", "قطار", "نقل عام", "أخرى"]

# ----------------------------------------------------------------------------
# DATABASE
# ----------------------------------------------------------------------------
@st.cache_resource
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS admins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS participants(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        wilaya TEXT,
        phone TEXT,
        transport TEXT,
        entry_date TEXT,
        room INTEGER NOT NULL,
        subscription REAL NOT NULL DEFAULT 0,
        code TEXT UNIQUE,
        created_by TEXT,
        created_at TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id INTEGER NOT NULL,
        att_date TEXT NOT NULL,
        att_time TEXT NOT NULL,
        marked_by TEXT,
        UNIQUE(participant_id, att_date),
        FOREIGN KEY(participant_id) REFERENCES participants(id)
    )""")
    conn.commit()
    c.execute("SELECT COUNT(*) FROM admins")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO admins(username, password_hash, created_at) VALUES (?,?,?)",
            ("admin", hash_password("admin123"), datetime.now().isoformat()),
        )
        conn.commit()


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def verify_admin(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT password_hash FROM admins WHERE username=?", (username,))
    row = c.fetchone()
    return bool(row) and row[0] == hash_password(password)


def admin_exists(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM admins WHERE username=?", (username,))
    return c.fetchone() is not None


def add_admin(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO admins(username, password_hash, created_at) VALUES (?,?,?)",
        (username, hash_password(password), datetime.now().isoformat()),
    )
    conn.commit()


def list_admins():
    conn = get_conn()
    return pd.read_sql_query(
        "SELECT username AS 'اسم المستخدم', created_at AS 'تاريخ الإنشاء' FROM admins ORDER BY id",
        conn,
    )


def room_count(room):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM participants WHERE room=?", (room,))
    return c.fetchone()[0]


def add_participant(first_name, last_name, wilaya, phone, transport, entry_date_str,
                     room, subscription, created_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """INSERT INTO participants
           (first_name,last_name,wilaya,phone,transport,entry_date,room,subscription,code,created_by,created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (first_name, last_name, wilaya, phone, transport, entry_date_str, room,
         subscription, "", created_by, datetime.now().isoformat()),
    )
    conn.commit()
    new_id = c.lastrowid
    code = f"CAMP-{new_id:04d}"
    c.execute("UPDATE participants SET code=? WHERE id=?", (code, new_id))
    conn.commit()
    return new_id, code


def delete_participant(pid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM attendance WHERE participant_id=?", (pid,))
    c.execute("DELETE FROM participants WHERE id=?", (pid,))
    conn.commit()


def get_all_participants_df():
    conn = get_conn()
    return pd.read_sql_query("SELECT * FROM participants ORDER BY room, id", conn)


def get_room_total(room):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(subscription),0) FROM participants WHERE room=?", (room,))
    return c.fetchone()[0]


def get_grand_total():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(subscription),0) FROM participants")
    return c.fetchone()[0]


def get_participant_by_code(code):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM participants WHERE code=?", (code.strip(),))
    row = c.fetchone()
    if not row:
        return None
    cols = [d[0] for d in c.description]
    return dict(zip(cols, row))


def mark_attendance(participant_id, marked_by):
    conn = get_conn()
    c = conn.cursor()
    today_str = date.today().isoformat()
    time_str = datetime.now().strftime("%H:%M:%S")
    try:
        c.execute(
            "INSERT INTO attendance(participant_id, att_date, att_time, marked_by) VALUES (?,?,?,?)",
            (participant_id, today_str, time_str, marked_by),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def today_attendance_df():
    conn = get_conn()
    today_str = date.today().isoformat()
    return pd.read_sql_query(
        """SELECT p.first_name AS 'الاسم', p.last_name AS 'اللقب', p.room AS 'الغرفة',
                  a.att_time AS 'وقت الحضور', a.marked_by AS 'سجّله'
           FROM attendance a JOIN participants p ON p.id = a.participant_id
           WHERE a.att_date = ? ORDER BY a.att_time DESC""",
        conn, params=(today_str,),
    )


def full_attendance_df():
    conn = get_conn()
    return pd.read_sql_query(
        """SELECT p.first_name AS 'الاسم', p.last_name AS 'اللقب', p.room AS 'الغرفة',
                  a.att_date AS 'التاريخ', a.att_time AS 'الوقت', a.marked_by AS 'سجّله'
           FROM attendance a JOIN participants p ON p.id = a.participant_id
           ORDER BY a.att_date DESC, a.att_time DESC""",
        conn,
    )


def generate_barcode_bytes(code):
    code128 = barcode.get_barcode_class("code128")
    obj = code128(code, writer=ImageWriter())
    buf = io.BytesIO()
    obj.write(buf, options={
        "module_height": 12.0, "font_size": 9, "text_distance": 4, "quiet_zone": 3,
    })
    return buf.getvalue()


# ----------------------------------------------------------------------------
# STYLE
# ----------------------------------------------------------------------------
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

        html, body, [class*="css"], .stMarkdown, .stTextInput, .stSelectbox, .stButton {
            font-family: 'Tajawal', sans-serif !important;
        }
        .block-container{
            direction: rtl;
            text-align: right;
            padding-top: 1.2rem;
            max-width: 1150px;
        }
        [data-testid="stForm"]{
            direction: rtl;
            text-align: right;
        }
        label, .stMarkdown, p, span, div{
            text-align: right;
        }

        /* ===== Flag banner ===== */
        .flag-banner{
            position: relative;
            background: linear-gradient(180deg, #000000 0%, #000000 33%, #ffffff 33%, #ffffff 66%, #149954 66%, #149954 100%);
            border-radius: 20px;
            padding: 34px 26px;
            text-align: center;
            overflow: hidden;
            margin-bottom: 1.6rem;
            box-shadow: 0 10px 30px rgba(0,0,0,.35);
        }
        .flag-banner::after{
            content:"";
            position:absolute; top:0; right:0; height:100%; width:80px;
            background:#E4312B;
            clip-path: polygon(0 0, 100% 50%, 0 100%);
        }
        .flag-banner .title-wrap{
            background: rgba(0,0,0,0.55);
            display:inline-block;
            padding: 12px 30px;
            border-radius: 14px;
            backdrop-filter: blur(2px);
        }
        .flag-banner h1{
            color:#fff; margin:0; font-size:2rem; font-weight:900;
        }
        .flag-banner p{
            color:#f2f2f2; margin:6px 0 0; font-size:1rem; font-weight:500;
        }

        /* ===== Sidebar ===== */
        section[data-testid="stSidebar"]{
            background: linear-gradient(180deg, #0e3d24 0%, #149954 100%);
        }
        section[data-testid="stSidebar"] *{
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] .stRadio > label{
            font-weight: 700;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label{
            background: rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 8px 10px;
            margin-bottom: 6px;
            transition: all .15s ease;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover{
            background: rgba(228,49,43,0.55);
        }

        /* ===== Buttons ===== */
        div.stButton > button, div.stFormSubmitButton > button{
            background: linear-gradient(135deg, #149954, #0e7a41);
            color: white !important;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.4rem;
            font-weight: 700;
            width: 100%;
            transition: all .2s ease;
            box-shadow: 0 4px 12px rgba(20,153,84,0.3);
        }
        div.stButton > button:hover, div.stFormSubmitButton > button:hover{
            background: linear-gradient(135deg, #E4312B, #b5251f);
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(228,49,43,0.4);
        }

        /* ===== Metrics ===== */
        div[data-testid="stMetric"]{
            background: white;
            border-radius: 14px;
            padding: 16px 14px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
            border-right: 6px solid #E4312B;
        }
        [data-testid="stMetricValue"]{
            color:#149954 !important; font-weight:900 !important;
        }

        /* ===== Cards ===== */
        .cam-card{
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 6px 20px rgba(0,0,0,.08);
            border-top: 5px solid #149954;
            margin-bottom: 1rem;
        }
        .present-badge{
            display:inline-block;
            background: linear-gradient(135deg,#149954,#0e7a41);
            color:white; font-weight:800;
            padding: 10px 22px; border-radius: 30px;
            font-size: 1.1rem;
            box-shadow: 0 4px 14px rgba(20,153,84,.4);
        }
        .already-badge{
            display:inline-block;
            background: linear-gradient(135deg,#E4312B,#b5251f);
            color:white; font-weight:800;
            padding: 10px 22px; border-radius: 30px;
            font-size: 1.05rem;
            box-shadow: 0 4px 14px rgba(228,49,43,.4);
        }
        .room-pill{
            display:inline-block;
            background:#000; color:#fff; font-weight:700;
            padding: 3px 12px; border-radius: 20px; font-size: .85rem;
        }
        footer, #MainMenu {visibility:hidden;}

        @media (max-width: 640px){
            .flag-banner h1{ font-size: 1.35rem; }
            .flag-banner p{ font-size: .85rem; }
            .block-container{ padding-left: 0.6rem; padding-right: 0.6rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def banner(subtitle):
    st.markdown(
        f"""
        <div class="flag-banner">
            <div class="title-wrap">
                <h1>🏕️ {CAMP_NAME}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# PAGES
# ----------------------------------------------------------------------------
def page_login():
    banner("لائحة المشاركين — تسجيل دخول المسؤولين")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="cam-card">', unsafe_allow_html=True)
        st.subheader("🔐 تسجيل الدخول")
        with st.form("login_form"):
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            submitted = st.form_submit_button("دخول")
            if submitted:
                if verify_admin(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("⚠️ اسم المستخدم أو كلمة المرور غير صحيحة")
        st.caption("الحساب الافتراضي عند أول تشغيل: **admin** / **admin123** — يرجى تغييره بإضافة حساب جديد.")
        st.markdown("</div>", unsafe_allow_html=True)


def page_dashboard():
    banner("لوحة التحكم")
    df = get_all_participants_df()
    total = len(df)
    capacity = len(ROOMS) * ROOM_CAPACITY
    present_today = len(today_attendance_df())
    grand_total = get_grand_total()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 عدد المشاركين", f"{total} / {capacity}")
    c2.metric("✅ الحاضرون اليوم", present_today)
    c3.metric("💰 المجموع العام للاشتراكات", f"{grand_total:,.0f}")
    c4.metric("🚪 عدد الغرف", f"{len(ROOMS)} غرف")

    st.markdown("### 🛏️ توزيع المشاركين حسب الغرف")
    room_data = pd.DataFrame({
        "الغرفة": [f"غرفة {r}" for r in ROOMS],
        "عدد المشاركين": [room_count(r) for r in ROOMS],
    }).set_index("الغرفة")
    st.bar_chart(room_data)

    st.markdown("### 📋 آخر المشاركين المسجلين")
    if total:
        recent = df.sort_values("id", ascending=False).head(5)[
            ["first_name", "last_name", "room", "wilaya", "subscription"]
        ]
        recent.columns = ["الاسم", "اللقب", "الغرفة", "الولاية", "الاشتراك"]
        st.dataframe(recent, use_container_width=True, hide_index=True)
    else:
        st.info("لا يوجد مشاركون بعد. أضف أول مشارك من القائمة الجانبية.")


def page_add_participant():
    banner("➕ إضافة مشارك جديد")

    st.markdown("#### 📊 حالة امتلاء الغرف")
    fill_df = pd.DataFrame({
        "الغرفة": [f"غرفة {r}" for r in ROOMS],
        "الأماكن المشغولة": [f"{room_count(r)} / {ROOM_CAPACITY}" for r in ROOMS],
    })
    st.dataframe(fill_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="cam-card">', unsafe_allow_html=True)
    with st.form("add_participant_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("الاسم *")
            wilaya = st.selectbox("الولاية *", WILAYAS)
            transport = st.selectbox("وسيلة النقل *", TRANSPORT_OPTIONS)
            room = st.selectbox("الغرفة *", ROOMS, format_func=lambda r: f"غرفة {r}")
        with col2:
            last_name = st.text_input("اللقب *")
            phone = st.text_input("رقم الهاتف *", placeholder="0555xxxxxx")
            transport_other = st.text_input("حدد وسيلة النقل (إذا اخترت 'أخرى')", "")
            subscription = st.number_input("الاشتراك (المبلغ) *", min_value=0.0, step=100.0)

        entry_date_val = st.date_input("تاريخ الدخول *", value=date.today())

        submitted = st.form_submit_button("💾 حفظ المشارك")
        if submitted:
            errors = []
            if not first_name.strip():
                errors.append("الاسم مطلوب")
            if not last_name.strip():
                errors.append("اللقب مطلوب")
            if not phone.strip().isdigit() or not (8 <= len(phone.strip()) <= 12):
                errors.append("رقم الهاتف غير صحيح (أرقام فقط)")
            if room_count(room) >= ROOM_CAPACITY:
                errors.append(f"غرفة {room} ممتلئة بالكامل ({ROOM_CAPACITY} أشخاص)")

            if errors:
                for e in errors:
                    st.error(f"⚠️ {e}")
            else:
                final_transport = transport_other.strip() if transport == "أخرى" and transport_other.strip() else transport
                new_id, code = add_participant(
                    first_name.strip(), last_name.strip(), wilaya, phone.strip(),
                    final_transport, entry_date_val.isoformat(), room, subscription,
                    st.session_state.username,
                )
                st.success(f"✅ تم إضافة {first_name} {last_name} في غرفة {room} بنجاح!")
                st.markdown(f"**رمز المشارك:** `{code}`")
                img_bytes = generate_barcode_bytes(code)
                st.image(img_bytes, caption="الباركود الخاص بالمشارك", width=320)
                st.download_button("⬇️ تحميل الباركود", data=img_bytes,
                                    file_name=f"{code}.png", mime="image/png")
    st.markdown("</div>", unsafe_allow_html=True)


def page_participant_list():
    banner("📋 لائحة المشاركين")
    df = get_all_participants_df()

    search = st.text_input("🔎 بحث بالاسم أو اللقب أو الولاية")
    if search:
        mask = (
            df["first_name"].str.contains(search, case=False, na=False)
            | df["last_name"].str.contains(search, case=False, na=False)
            | df["wilaya"].str.contains(search, case=False, na=False)
        )
        df = df[mask]

    tabs = st.tabs([f"🛏️ غرفة {r}" for r in ROOMS] + ["📖 الكل"])

    display_cols = {
        "first_name": "الاسم", "last_name": "اللقب", "wilaya": "الولاية",
        "phone": "رقم الهاتف", "transport": "وسيلة النقل",
        "entry_date": "تاريخ الدخول", "subscription": "الاشتراك", "code": "الرمز",
    }

    for i, r in enumerate(ROOMS):
        with tabs[i]:
            room_df = df[df["room"] == r]
            if room_df.empty:
                st.info("لا يوجد مشاركون في هذه الغرفة بعد.")
            else:
                show = room_df[list(display_cols.keys())].rename(columns=display_cols)
                st.dataframe(show, use_container_width=True, hide_index=True)
            st.metric(f"💰 مجموع اشتراكات غرفة {r}", f"{get_room_total(r):,.0f}")

    with tabs[-1]:
        if df.empty:
            st.info("لا يوجد مشاركون مسجّلون بعد.")
        else:
            show = df[list(display_cols.keys()) + ["room"]].rename(
                columns={**display_cols, "room": "الغرفة"}
            )
            st.dataframe(show, use_container_width=True, hide_index=True)
        st.markdown(
            f'<div class="cam-card" style="text-align:center;">'
            f'<h2 style="color:#149954;margin:0;">💰 المجموع العام: {get_grand_total():,.0f}</h2>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with st.expander("🗑️ إدارة المشاركين (حذف)"):
        if not df.empty:
            options = {f'{row.first_name} {row.last_name} — غرفة {row.room} ({row.code})': row.id
                       for row in df.itertuples()}
            choice = st.selectbox("اختر مشاركًا للحذف", list(options.keys()))
            confirm = st.checkbox("أؤكد رغبتي في حذف هذا المشارك نهائيًا")
            if st.button("حذف المشارك"):
                if confirm:
                    delete_participant(options[choice])
                    st.success("تم الحذف بنجاح.")
                    st.rerun()
                else:
                    st.warning("يرجى تأكيد الحذف أولاً.")
        else:
            st.caption("لا يوجد مشاركون لحذفهم.")


def page_checkin():
    banner("🛂 تسجيل الحضور بالباركود")
    st.caption("امسح الباركود بجهاز القارئ أو أدخل الرمز يدويًا ثم اضغط Enter.")

    with st.form("checkin_form", clear_on_submit=True):
        code = st.text_input("رمز المشارك", placeholder="CAMP-0001")
        submitted = st.form_submit_button("تحقق وسجّل الحضور")

    if submitted and code.strip():
        participant = get_participant_by_code(code)
        if not participant:
            st.error("❌ الرمز غير صحيح، لا يوجد مشارك بهذا الرمز.")
        else:
            ok = mark_attendance(participant["id"], st.session_state.username)
            name = f'{participant["first_name"]} {participant["last_name"]}'
            st.markdown('<div class="cam-card">', unsafe_allow_html=True)
            st.markdown(f"### {name}")
            st.markdown(f'<span class="room-pill">غرفة {participant["room"]}</span>', unsafe_allow_html=True)
            st.write(f"📞 {participant['phone']}  |  📍 {participant['wilaya']}")
            if ok:
                st.markdown('<div class="present-badge">✅ أنا حاضر — تم تسجيل الحضور</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="already-badge">ℹ️ تم تسجيل حضور هذا المشارك اليوم مسبقًا</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### ✅ الحاضرون اليوم")
    today_df = today_attendance_df()
    if today_df.empty:
        st.info("لم يتم تسجيل أي حضور اليوم بعد.")
    else:
        st.dataframe(today_df, use_container_width=True, hide_index=True)

    with st.expander("📜 سجل الحضور الكامل (كل الأيام)"):
        hist = full_attendance_df()
        if hist.empty:
            st.caption("لا يوجد سجل بعد.")
        else:
            st.dataframe(hist, use_container_width=True, hide_index=True)


def page_barcodes():
    banner("🪪 بطاقات الباركود للطباعة")
    df = get_all_participants_df()
    if df.empty:
        st.info("لا يوجد مشاركون بعد.")
        return
    options = {f'{row.first_name} {row.last_name} — غرفة {row.room} ({row.code})': row
               for row in df.itertuples()}
    choice = st.selectbox("اختر مشاركًا", list(options.keys()))
    row = options[choice]
    st.markdown('<div class="cam-card" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown(f"### {row.first_name} {row.last_name}")
    st.markdown(f'<span class="room-pill">غرفة {row.room}</span>', unsafe_allow_html=True)
    img_bytes = generate_barcode_bytes(row.code)
    st.image(img_bytes, width=360)
    st.download_button("⬇️ تحميل الباركود", data=img_bytes,
                        file_name=f"{row.code}.png", mime="image/png")
    st.markdown("</div>", unsafe_allow_html=True)


def page_add_admin():
    banner("👤 إضافة مسؤول جديد")
    st.markdown('<div class="cam-card">', unsafe_allow_html=True)
    with st.form("add_admin_form", clear_on_submit=True):
        username = st.text_input("اسم المستخدم الجديد")
        password = st.text_input("كلمة المرور", type="password")
        confirm = st.text_input("تأكيد كلمة المرور", type="password")
        submitted = st.form_submit_button("➕ إضافة المسؤول")
        if submitted:
            if not username.strip() or not password:
                st.error("⚠️ يرجى تعبئة جميع الحقول.")
            elif password != confirm:
                st.error("⚠️ كلمتا المرور غير متطابقتين.")
            elif admin_exists(username.strip()):
                st.error("⚠️ اسم المستخدم موجود مسبقًا.")
            else:
                add_admin(username.strip(), password)
                st.success(f"✅ تم إنشاء حساب المسؤول '{username}' بنجاح.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### 👥 المسؤولون الحاليون")
    st.dataframe(list_admins(), use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title=f"{CAMP_NAME} | لائحة المشاركين",
        page_icon="🏕️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    init_db()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.logged_in:
        page_login()
        return

    with st.sidebar:
        st.markdown(f"### 🏕️ {CAMP_NAME}")
        st.markdown(f"👋 مرحبًا، **{st.session_state.username}**")
        st.markdown("---")
        choice = st.radio(
            "التنقل",
            [
                "🏠 لوحة التحكم",
                "➕ إضافة مشارك",
                "🛂 تسجيل الحضور",
                "📋 لائحة المشاركين",
                "🪪 بطاقات الباركود",
                "👤 إضافة مسؤول",
            ],
            label_visibility="collapsed",
        )
        st.markdown("---")
        if st.button("🚪 تسجيل الخروج"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    if choice == "🏠 لوحة التحكم":
        page_dashboard()
    elif choice == "➕ إضافة مشارك":
        page_add_participant()
    elif choice == "🛂 تسجيل الحضور":
        page_checkin()
    elif choice == "📋 لائحة المشاركين":
        page_participant_list()
    elif choice == "🪪 بطاقات الباركود":
        page_barcodes()
    elif choice == "👤 إضافة مسؤول":
        page_add_admin()


if __name__ == "__main__":
    main()
