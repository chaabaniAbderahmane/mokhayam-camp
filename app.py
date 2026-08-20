# -*- coding: utf-8 -*-
"""
المخيم الصيفي — Streamlit application
Main entry point: routing between participant portal and admin dashboard.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date

import db
from db import (Admin, Room, Participant, AttendanceDay, Attendance, Announcement,
                 CampInfo, ActivityLog, hash_password, check_password, gen_token,
                 gen_reg_id, log_activity, MAX_ROOMS, MAX_CAPACITY)
from translations import t
from styles import inject_css, flag_header, stat_card_html, badge
from utils import make_qr_image, participant_portal_url, df_to_csv_bytes, df_to_excel_bytes

st.set_page_config(page_title="المخيم الصيفي", page_icon="🏕️", layout="centered")
db.init_db()

TRANSPORT_KEYS = ["bus", "private_car", "private_transport", "no_transport", "other"]
PRIORITY_KEYS = ["normal", "important", "urgent"]

# ----------------------------------------------------------------- State ---
if "lang" not in st.session_state:
    st.session_state.lang = "ar"
if "admin_id" not in st.session_state:
    st.session_state.admin_id = None
if "nav" not in st.session_state:
    st.session_state.nav = "dashboard"

lang = st.session_state.lang
inject_css(lang)


def L(key):
    return t(key, lang)


def toggle_lang():
    st.session_state.lang = "fr" if st.session_state.lang == "ar" else "ar"


def get_camp_info(session):
    rows = session.query(CampInfo).all()
    return {r.key: r.value for r in rows}


# ============================================================= PARTICIPANT PORTAL ===
def participant_header_lang_toggle():
    cols = st.columns([1, 1])
    with cols[1 if lang == "ar" else 0]:
        st.button(L("lang_toggle"), key="lang_btn_p", on_click=toggle_lang, use_container_width=True)


def render_participant_portal(token: str):
    session = db.get_session()
    try:
        p = session.query(Participant).filter(Participant.qr_token == token).first()
        participant_header_lang_toggle()
        flag_header(L("app_name"), L("nav_my_info"))
        if not p:
            st.error(L("invalid_token"))
            return
        info = get_camp_info(session)

        tabs = st.tabs([L("nav_home"), L("nav_my_info"), L("nav_my_room"),
                         L("nav_attendance"), L("nav_payments"), L("nav_announcements"),
                         L("nav_camp_info"), L("nav_my_qr")])

        # HOME
        with tabs[0]:
            st.markdown(f"### 👋 {p.first_name} {p.last_name}")
            st.markdown(f"**{L('reg_id')}:** {p.reg_id}")
            room = p.room
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(stat_card_html(room.name if room else "—", L("room")), unsafe_allow_html=True)
            with c2:
                st.markdown(stat_card_html(p.place_number if p.place_number else "—", L("place")), unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            last_att = (session.query(Attendance).filter(Attendance.participant_id == p.id)
                        .order_by(Attendance.recorded_at.desc()).first())
            att_txt = L("present") if last_att else L("not_recorded")
            with c3:
                st.markdown(stat_card_html(att_txt, L("attendance_status")), unsafe_allow_html=True)
            with c4:
                pay_badge_kind = {"paid": "green", "unpaid": "red", "partial": "gold"}[p.payment_status]
                st.markdown(f"<div class='stat-card'>{badge(L(p.payment_status), pay_badge_kind)}<div class='stat-label' style='margin-top:6px'>{L('payment_status')}</div></div>", unsafe_allow_html=True)

        # MY INFO
        with tabs[1]:
            st.markdown(f"""
            <div class="camp-card">
            <h4>{L('nav_my_info')}</h4>
            <b>{L('first_name')}:</b> {p.first_name}<br>
            <b>{L('last_name')}:</b> {p.last_name}<br>
            <b>{L('wilaya')}:</b> {p.wilaya or '—'}<br>
            <b>{L('phone')}:</b> {p.phone or '—'}<br>
            <b>{L('transport')}:</b> {L(p.transport)}<br>
            <b>{L('entry_date')}:</b> {p.entry_date or '—'}<br>
            <b>{L('reg_id')}:</b> {p.reg_id}
            </div>
            """, unsafe_allow_html=True)
            if p.notes:
                st.markdown(f"<div class='camp-card'><h4>{L('notes')}</h4>{p.notes}</div>", unsafe_allow_html=True)

        # MY ROOM
        with tabs[2]:
            room = p.room
            if not room:
                st.info(L("no_room"))
            else:
                occupants = (session.query(Participant).filter(Participant.room_id == room.id)
                             .order_by(Participant.place_number).all())
                st.markdown(f"""
                <div class="camp-card">
                <h4>{room.name}</h4>
                <b>{L('your_place')}:</b> {p.place_number or '—'} {L('of')} {room.capacity}<br>
                <b>{L('current_participants')}:</b> {len(occupants)} / {room.capacity}
                </div>
                """, unsafe_allow_html=True)
                show_rm = info.get("show_roommates_global", "true") == "true"
                if p.show_roommates_override is not None:
                    show_rm = p.show_roommates_override
                if show_rm:
                    st.markdown(f"**{L('roommates')}:**")
                    for o in occupants:
                        marker = " ⭐" if o.id == p.id else ""
                        st.write(f"{o.place_number or '—'}. {o.first_name} {o.last_name}{marker}")

        # ATTENDANCE
        with tabs[3]:
            records = (session.query(Attendance).filter(Attendance.participant_id == p.id)
                       .order_by(Attendance.recorded_at).all())
            if not records:
                st.info(L("not_recorded"))
            for r in records:
                st.markdown(f"- **{r.day.label}** ({r.day.day_date}) — {badge(L('present'),'green')}", unsafe_allow_html=True)

        # PAYMENTS
        with tabs[4]:
            kind = {"paid": "green", "unpaid": "red", "partial": "gold"}[p.payment_status]
            st.markdown(f"""
            <div class="camp-card">
            <h4>{L('nav_payments')}</h4>
            {badge(L(p.payment_status), kind)}<br><br>
            <b>{L('amount_required')}:</b> {p.subscription_amount:,.0f} {L('currency')}<br>
            <b>{L('amount_paid')}:</b> {p.paid_amount:,.0f} {L('currency')}<br>
            <b>{L('amount_remaining')}:</b> {p.remaining_amount:,.0f} {L('currency')}
            </div>
            """, unsafe_allow_html=True)

        # ANNOUNCEMENTS
        with tabs[5]:
            anns = session.query(Announcement).order_by(Announcement.created_at.desc()).all()
            if not anns:
                st.info(L("no_results"))
            for a in anns:
                cls = "urgent" if a.priority == "urgent" else ""
                kind = {"normal": "grey", "important": "gold", "urgent": "red"}[a.priority]
                st.markdown(f"""
                <div class="camp-card {cls}">
                <h4>{a.title} {badge(L(a.priority), kind)}</h4>
                <p>{a.content}</p>
                <small>{a.created_at.strftime('%Y-%m-%d')}</small>
                </div>
                """, unsafe_allow_html=True)

        # CAMP INFO
        with tabs[6]:
            fields = [("camp_program", "camp_program"), ("start_date", "start_date"), ("end_date", "end_date"),
                      ("camp_location", "camp_location"), ("gather_time", "gather_time"),
                      ("gather_place", "gather_place"), ("access_instructions", "access_instructions"),
                      ("required_items", "required_items"), ("rules", "rules"),
                      ("important_info", "important_info"), ("contact_numbers", "contact_numbers")]
            for key, label_key in fields:
                val = info.get(key, "")
                if val:
                    st.markdown(f"<div class='camp-card'><h4>{L(label_key)}</h4>{val}</div>", unsafe_allow_html=True)

        # QR
        with tabs[7]:
            st.markdown(f"### {L('participant_card')}")
            img = make_qr_image(participant_portal_url(info.get("app_url", ""), p.qr_token))
            st.image(img, width=240)
            st.markdown(f"**{p.first_name} {p.last_name}**  \n{L('reg_id')}: {p.reg_id}")
    finally:
        session.close()


# ================================================================ ADMIN AUTH ===
def render_login():
    participant_header_lang_toggle()
    flag_header(L("app_name"), L("welcome_admin"))

    with st.form("login_form"):
        u = st.text_input(L("username"))
        pw = st.text_input(L("password"), type="password")
        submitted = st.form_submit_button(L("login_btn"), use_container_width=True, type="primary")
    if submitted:
        session = db.get_session()
        try:
            admin = session.query(Admin).filter(Admin.username == u.strip()).first()
            if admin and check_password(pw, admin.password_hash):
                st.session_state.admin_id = admin.id
                st.rerun()
            else:
                st.error(L("login_error"))
        finally:
            session.close()

    st.divider()
    with st.expander(f"🔑 {L('nav_my_info')} / {L('scan_qr')}"):
        st.caption(L("portal_intro"))
        token_in = st.text_input(L("enter_token"), key="token_manual")
        if st.button(L("go"), key="go_token"):
            if token_in.strip():
                st.query_params["p"] = token_in.strip()
                st.rerun()


# ================================================================ ADMIN APP ===
NAV_ITEMS = [
    ("dashboard", "nav_dashboard", "📊"),
    ("participants", "nav_participants", "🧑‍🤝‍🧑"),
    ("rooms", "nav_rooms", "🏠"),
    ("attendance", "nav_attendance", "✅"),
    ("payments", "nav_payments", "💳"),
    ("transport", "nav_transport", "🚌"),
    ("announcements", "nav_announcements", "📢"),
    ("camp_info", "nav_camp_info", "ℹ️"),
    ("admins", "nav_admins", "👤"),
    ("settings", "nav_settings", "⚙️"),
    ("logs", "nav_logs", "📜"),
]


def render_admin_sidebar(current_admin):
    with st.sidebar:
        st.markdown(f"### 🏕️ {L('app_name')}")
        st.caption(f"{current_admin.full_name or current_admin.username} — {L(current_admin.role)}")
        st.button(L("lang_toggle"), on_click=toggle_lang, use_container_width=True)
        st.divider()
        items = NAV_ITEMS
        if current_admin.role != "super_admin":
            items = [i for i in items if i[0] not in ("admins",)]
        for key, label_key, icon in items:
            if st.button(f"{icon}  {L(label_key)}", key=f"nav_{key}", use_container_width=True):
                st.session_state.nav = key
                st.rerun()
        st.divider()
        if st.button(f"🚪 {L('logout')}", use_container_width=True):
            st.session_state.admin_id = None
            st.rerun()


def page_dashboard(session, admin):
    flag_header(L("app_name"), L("nav_dashboard"))
    participants = session.query(Participant).all()
    rooms = session.query(Room).all()
    total = len(participants)
    present_ids = {a.participant_id for a in session.query(Attendance).all()}
    present = len(present_ids)
    absent = total - present
    paid_n = sum(1 for p in participants if p.payment_status == "paid")
    unpaid_n = sum(1 for p in participants if p.payment_status != "paid")
    total_subs = sum(p.subscription_amount for p in participants)
    total_paid = sum(p.paid_amount for p in participants)
    total_remaining = sum(p.remaining_amount for p in participants)
    total_capacity = sum(r.capacity for r in rooms)
    remaining_places = total_capacity - total

    st.markdown(f"#### {L('stats')}")
    cols = st.columns(2)
    stats = [
        (total, "total_participants"), (present, "present_count"),
        (absent, "absent_count"), (paid_n, "paid_count"),
        (unpaid_n, "unpaid_count"), (len(rooms), "rooms_count"),
        (remaining_places, "places_remaining"),
    ]
    for i, (num, key) in enumerate(stats):
        with cols[i % 2]:
            st.markdown(stat_card_html(num, L(key)), unsafe_allow_html=True)
            st.write("")

    st.markdown(f"#### {L('total_subs')}")
    c1, c2, c3 = st.columns(3)
    c1.metric(L("total_subs"), f"{total_subs:,.0f} {L('currency')}")
    c2.metric(L("total_paid"), f"{total_paid:,.0f} {L('currency')}")
    c3.metric(L("total_remaining"), f"{total_remaining:,.0f} {L('currency')}")

    if total:
        st.markdown(f"#### {L('nav_rooms')}")
        room_df = pd.DataFrame([{
            L("room_name"): r.name,
            L("current_participants"): len(r.participants),
            L("capacity"): r.capacity,
            L("room_total_subs"): sum(pp.subscription_amount for pp in r.participants),
        } for r in rooms])
        st.bar_chart(room_df.set_index(L("room_name"))[L("current_participants")])


def _transport_options_labels():
    return {k: L(k) for k in TRANSPORT_KEYS}


def participant_form(session, admin, existing: Participant = None):
    rooms = session.query(Room).order_by(Room.number).all()
    room_options = {0: L("no_room")}
    room_options.update({r.id: f"{r.name} ({len(r.participants)}/{r.capacity})" for r in rooms})
    tr_labels = _transport_options_labels()

    with st.form("participant_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        first_name = c1.text_input(L("first_name"), value=existing.first_name if existing else "")
        last_name = c2.text_input(L("last_name"), value=existing.last_name if existing else "")
        c3, c4 = st.columns(2)
        wilaya = c3.text_input(L("wilaya"), value=existing.wilaya if existing else "")
        phone = c4.text_input(L("phone"), value=existing.phone if existing else "")
        c5, c6 = st.columns(2)
        transport = c5.selectbox(L("transport"), options=list(tr_labels.keys()),
                                  format_func=lambda k: tr_labels[k],
                                  index=list(tr_labels.keys()).index(existing.transport) if existing else 0)
        entry_date = c6.text_input(L("entry_date"), value=existing.entry_date if existing else "")

        c7, c8 = st.columns(2)
        room_id_sel = c7.selectbox(L("room"), options=list(room_options.keys()),
                                    format_func=lambda k: room_options[k],
                                    index=list(room_options.keys()).index(existing.room_id or 0) if existing else 0)
        place_number = c8.number_input(L("place"), min_value=0, max_value=MAX_CAPACITY,
                                        value=existing.place_number or 0 if existing else 0, step=1)

        c9, c10 = st.columns(2)
        sub_amount = c9.number_input(L("sub_amount"), min_value=0.0,
                                      value=float(existing.subscription_amount) if existing else 0.0, step=500.0)
        paid_amount = c10.number_input(L("amount_paid"), min_value=0.0,
                                        value=float(existing.paid_amount) if existing else 0.0, step=500.0)

        notes = st.text_area(L("notes"), value=existing.notes if existing else "")
        submitted = st.form_submit_button(L("save"), type="primary", use_container_width=True)

    if submitted:
        if not first_name.strip() or not last_name.strip():
            st.error("⚠️ " + L("first_name") + " / " + L("last_name"))
            return
        # Duplicate phone check
        if phone.strip():
            q = session.query(Participant).filter(Participant.phone == phone.strip())
            if existing:
                q = q.filter(Participant.id != existing.id)
            if q.first():
                st.warning(L("duplicate_warning"))

        room_id_final = room_id_sel if room_id_sel != 0 else None
        place_final = place_number if place_number > 0 else None

        # place uniqueness check within room
        if room_id_final and place_final:
            q = session.query(Participant).filter(Participant.room_id == room_id_final,
                                                    Participant.place_number == place_final)
            if existing:
                q = q.filter(Participant.id != existing.id)
            conflict = q.first()
            if conflict:
                st.error(f"⚠️ {L('place')} {place_final} — {conflict.first_name} {conflict.last_name}")
                return
        # capacity check
        if room_id_final:
            room = session.query(Room).get(room_id_final)
            current_count = len([pp for pp in room.participants if not existing or pp.id != existing.id])
            if current_count >= room.capacity:
                st.error(L("remaining_places") + ": 0")
                return

        if existing:
            existing.first_name = first_name.strip()
            existing.last_name = last_name.strip()
            existing.wilaya = wilaya.strip()
            existing.phone = phone.strip()
            existing.transport = transport
            existing.entry_date = entry_date.strip()
            existing.room_id = room_id_final
            existing.place_number = place_final
            existing.subscription_amount = sub_amount
            existing.paid_amount = paid_amount
            existing.notes = notes
            session.commit()
            log_activity(session, admin.username, f"Updated participant {existing.reg_id}")
            st.success(L("success_update"))
        else:
            p = Participant(
                reg_id=gen_reg_id(session),
                qr_token=gen_token(),
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                wilaya=wilaya.strip(),
                phone=phone.strip(),
                transport=transport,
                entry_date=entry_date.strip(),
                room_id=room_id_final,
                place_number=place_final,
                subscription_amount=sub_amount,
                paid_amount=paid_amount,
                notes=notes,
            )
            session.add(p)
            session.commit()
            log_activity(session, admin.username, f"Added participant {p.reg_id}")
            st.success(L("success_add"))
        st.rerun()


def page_participants(session, admin):
    flag_header(L("app_name"), L("nav_participants"))

    with st.expander(f"➕ {L('add_participant')}"):
        participant_form(session, admin, None)

    st.markdown(f"#### {L('participant_list')}")
    c1, c2 = st.columns(2)
    search = c1.text_input(f"🔎 {L('search')}")
    rooms = session.query(Room).order_by(Room.number).all()
    room_filter_opts = {0: L("all")}
    room_filter_opts.update({r.id: r.name for r in rooms})
    room_filter = c2.selectbox(L("filter") + " — " + L("room"), options=list(room_filter_opts.keys()),
                                format_func=lambda k: room_filter_opts[k])

    c3, c4 = st.columns(2)
    pay_filter = c3.selectbox(L("payment_status"), options=["all", "paid", "unpaid", "partial"],
                               format_func=lambda k: L("all") if k == "all" else L(k))
    tr_filter = c4.selectbox(L("transport"), options=["all"] + TRANSPORT_KEYS,
                              format_func=lambda k: L("all") if k == "all" else L(k))

    query = session.query(Participant)
    if room_filter != 0:
        query = query.filter(Participant.room_id == room_filter)
    if pay_filter != "all":
        pass  # filtered after (computed property)
    if tr_filter != "all":
        query = query.filter(Participant.transport == tr_filter)
    participants = query.order_by(Participant.created_at.desc()).all()

    if search.strip():
        s = search.strip().lower()
        participants = [p for p in participants if
                         s in p.first_name.lower() or s in p.last_name.lower() or
                         s in (p.phone or "").lower() or s in (p.reg_id or "").lower() or
                         s in (p.wilaya or "").lower()]
    if pay_filter != "all":
        participants = [p for p in participants if p.payment_status == pay_filter]

    st.caption(f"{len(participants)} {L('total_participants')}")

    # Export
    if participants:
        export_df = pd.DataFrame([{
            L("first_name"): p.first_name, L("last_name"): p.last_name, L("wilaya"): p.wilaya,
            L("phone"): p.phone, L("transport"): L(p.transport), L("entry_date"): p.entry_date,
            L("room"): p.room.name if p.room else "", L("place"): p.place_number,
            L("sub_amount"): p.subscription_amount, L("payment_status"): L(p.payment_status),
            L("reg_id"): p.reg_id,
        } for p in participants])
        ec1, ec2 = st.columns(2)
        ec1.download_button(f"⬇️ CSV", df_to_csv_bytes(export_df), "participants.csv", "text/csv", use_container_width=True)
        ec2.download_button(f"⬇️ Excel", df_to_excel_bytes(export_df), "participants.xlsx", use_container_width=True)

    pay_kind = {"paid": "green", "unpaid": "red", "partial": "gold"}
    for p in participants:
        with st.container():
            st.markdown(f"""
            <div class="camp-card">
            <h4>{p.first_name} {p.last_name} <small style="color:#888">#{p.reg_id}</small></h4>
            📍 {p.wilaya or '—'} &nbsp;|&nbsp; 📞 {p.phone or '—'} &nbsp;|&nbsp; 🚌 {L(p.transport)}<br>
            🏠 {p.room.name if p.room else L('no_room')} — {L('place')} {p.place_number or '—'} &nbsp;|&nbsp;
            {badge(L(p.payment_status), pay_kind[p.payment_status])}
            </div>
            """, unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            if b1.button(f"✏️ {L('edit')}", key=f"edit_{p.id}", use_container_width=True):
                st.session_state[f"editing_{p.id}"] = True
            if b2.button(f"🗑️ {L('delete')}", key=f"del_{p.id}", use_container_width=True):
                st.session_state[f"confirm_del_{p.id}"] = True
            b3, b4 = st.columns(2)
            if b3.button(f"📇 QR", key=f"qr_{p.id}", use_container_width=True):
                st.session_state[f"showqr_{p.id}"] = True
            if b4.button(f"✅ {L('mark_attendance')}", key=f"att_quick_{p.id}", use_container_width=True):
                st.session_state["quick_att_id"] = p.id
                st.session_state["nav"] = "attendance"
                st.rerun()

            if st.session_state.get(f"confirm_del_{p.id}"):
                st.warning(L("confirm_delete"))
                cc1, cc2 = st.columns(2)
                if cc1.button(L("yes"), key=f"yesdel_{p.id}", type="primary"):
                    session.delete(p)
                    session.commit()
                    log_activity(session, admin.username, f"Deleted participant {p.reg_id}")
                    st.success(L("success_delete"))
                    st.session_state.pop(f"confirm_del_{p.id}", None)
                    st.rerun()
                if cc2.button(L("no"), key=f"nodel_{p.id}"):
                    st.session_state.pop(f"confirm_del_{p.id}", None)
                    st.rerun()

            if st.session_state.get(f"editing_{p.id}"):
                participant_form(session, admin, p)
                if st.button(L("cancel"), key=f"canceledit_{p.id}"):
                    st.session_state.pop(f"editing_{p.id}", None)
                    st.rerun()

            if st.session_state.get(f"showqr_{p.id}"):
                info = get_camp_info(session)
                url = participant_portal_url(info.get("app_url", ""), p.qr_token)
                img = make_qr_image(url)
                st.image(img, width=200, caption=f"{p.first_name} {p.last_name} — {p.reg_id}")
                st.code(url, language=None)


def page_rooms(session, admin):
    flag_header(L("app_name"), L("nav_rooms"))
    rooms = session.query(Room).order_by(Room.number).all()

    for r in rooms:
        occ = len(r.participants)
        pct = int((occ / r.capacity) * 100) if r.capacity else 0
        total_subs = sum(pp.subscription_amount for pp in r.participants)
        st.markdown(f"""
        <div class="camp-card">
        <h4>{r.name} — {occ}/{r.capacity}</h4>
        {L('remaining_places')}: {r.capacity - occ} &nbsp;|&nbsp; {L('occupancy')}: {pct}%<br>
        {L('room_total_subs')}: {total_subs:,.0f} {L('currency')}
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(1.0, occ / r.capacity if r.capacity else 0))

        with st.expander(f"⚙️ {r.name} — {L('edit')} / {L('participant_list')}"):
            with st.form(f"room_edit_{r.id}"):
                name = st.text_input(L("room_name"), value=r.name)
                capacity = st.number_input(L("capacity"), min_value=1, max_value=MAX_CAPACITY, value=r.capacity)
                bed_label_names = {
                    "place": L("place"),
                    "bed": "السرير" if lang == "ar" else "Lit",
                    "seat": "المقعد" if lang == "ar" else "Siège",
                }
                bed_label_opt = st.selectbox(L("bed_label"), options=["place", "bed", "seat"],
                                              format_func=lambda k: bed_label_names[k],
                                              index=["place", "bed", "seat"].index(r.bed_label) if r.bed_label in ["place", "bed", "seat"] else 0)
                if st.form_submit_button(L("save"), type="primary"):
                    r.name = name
                    r.capacity = capacity
                    r.bed_label = bed_label_opt
                    session.commit()
                    log_activity(session, admin.username, f"Updated room {r.name}")
                    st.success(L("success_update"))
                    st.rerun()

            if r.participants:
                sorted_p = sorted(r.participants, key=lambda pp: (pp.place_number is None, pp.place_number or 0))
                df = pd.DataFrame([{
                    L("place"): pp.place_number or "—",
                    L("first_name") + " " + L("last_name"): f"{pp.first_name} {pp.last_name}",
                    L("payment_status"): L(pp.payment_status),
                } for pp in sorted_p])
                st.dataframe(df, use_container_width=True, hide_index=True)


def page_attendance(session, admin):
    flag_header(L("app_name"), L("nav_attendance"))
    days = session.query(AttendanceDay).order_by(AttendanceDay.day_date).all()

    with st.expander(f"➕ {L('add_day')}"):
        with st.form("add_day_form"):
            label = st.text_input(L("attendance_day"), value=f"{L('attendance_day')} {len(days)+1}")
            d = st.date_input(L("date"), value=date.today())
            if st.form_submit_button(L("add"), type="primary"):
                session.add(AttendanceDay(label=label, day_date=d))
                session.commit()
                st.success(L("success_add"))
                st.rerun()

    if not days:
        st.info(L("no_results"))
        return

    day_options = {dd.id: f"{dd.label} ({dd.day_date})" for dd in days}
    default_day = days[-1].id
    selected_day = st.selectbox(L("attendance_day"), options=list(day_options.keys()),
                                 format_func=lambda k: day_options[k],
                                 index=list(day_options.keys()).index(default_day))

    search = st.text_input(f"🔎 {L('search')}")
    participants = session.query(Participant).order_by(Participant.first_name).all()
    if search.strip():
        s = search.strip().lower()
        participants = [p for p in participants if s in p.first_name.lower() or s in p.last_name.lower()
                        or s in (p.reg_id or "").lower() or s in (p.phone or "").lower()]

    recorded_ids = {a.participant_id for a in session.query(Attendance).filter(Attendance.day_id == selected_day).all()}

    quick_id = st.session_state.pop("quick_att_id", None)
    if quick_id:
        participants = sorted(participants, key=lambda p: p.id != quick_id)

    for p in participants:
        is_present = p.id in recorded_ids
        c1, c2 = st.columns([3, 1])
        status_txt = f"{badge(L('present'),'green')}" if is_present else f"{badge(L('not_recorded'),'grey')}"
        c1.markdown(f"**{p.first_name} {p.last_name}** — {p.reg_id} {status_txt}", unsafe_allow_html=True)
        if not is_present:
            if c2.button(L("mark_attendance"), key=f"markatt_{p.id}_{selected_day}"):
                session.add(Attendance(participant_id=p.id, day_id=selected_day,
                                        status="present", recorded_by=admin.username))
                session.commit()
                log_activity(session, admin.username, f"Attendance for {p.reg_id}")
                st.success(L("attendance_recorded"))
                st.rerun()
        else:
            c2.write("✅")


def page_payments(session, admin):
    flag_header(L("app_name"), L("nav_payments"))
    participants = session.query(Participant).order_by(Participant.first_name).all()
    total_subs = sum(p.subscription_amount for p in participants)
    total_paid = sum(p.paid_amount for p in participants)
    c1, c2, c3 = st.columns(3)
    c1.metric(L("total_subs"), f"{total_subs:,.0f} {L('currency')}")
    c2.metric(L("total_paid"), f"{total_paid:,.0f} {L('currency')}")
    c3.metric(L("total_remaining"), f"{total_subs-total_paid:,.0f} {L('currency')}")

    search = st.text_input(f"🔎 {L('search')}")
    if search.strip():
        s = search.strip().lower()
        participants = [p for p in participants if s in p.first_name.lower() or s in p.last_name.lower()
                        or s in (p.reg_id or "").lower()]

    pay_kind = {"paid": "green", "unpaid": "red", "partial": "gold"}
    for p in participants:
        with st.expander(f"{p.first_name} {p.last_name} — {badge(L(p.payment_status), pay_kind[p.payment_status])}", expanded=False):
            st.markdown("", unsafe_allow_html=True)
            with st.form(f"pay_form_{p.id}"):
                req = st.number_input(L("amount_required"), min_value=0.0, value=float(p.subscription_amount), step=500.0)
                paid = st.number_input(L("amount_paid"), min_value=0.0, value=float(p.paid_amount), step=500.0)
                if st.form_submit_button(L("save"), type="primary"):
                    p.subscription_amount = req
                    p.paid_amount = paid
                    session.commit()
                    log_activity(session, admin.username, f"Payment updated for {p.reg_id}")
                    st.success(L("success_update"))
                    st.rerun()


def page_transport(session, admin):
    flag_header(L("app_name"), L("nav_transport"))
    participants = session.query(Participant).all()
    counts = {k: 0 for k in TRANSPORT_KEYS}
    for p in participants:
        counts[p.transport] = counts.get(p.transport, 0) + 1

    cols = st.columns(2)
    for i, k in enumerate(TRANSPORT_KEYS):
        with cols[i % 2]:
            st.markdown(stat_card_html(counts[k], L(k)), unsafe_allow_html=True)
            st.write("")

    df = pd.DataFrame({L("transport"): [L(k) for k in TRANSPORT_KEYS],
                        L("total_participants"): [counts[k] for k in TRANSPORT_KEYS]})
    st.bar_chart(df.set_index(L("transport")))

    st.markdown(f"#### {L('participant_list')}")
    for k in TRANSPORT_KEYS:
        group = [p for p in participants if p.transport == k]
        if group:
            with st.expander(f"{L(k)} ({len(group)})"):
                for p in group:
                    st.write(f"- {p.first_name} {p.last_name} — {p.phone or '—'}")


def page_announcements(session, admin):
    flag_header(L("app_name"), L("nav_announcements"))
    with st.expander(f"➕ {L('add')}"):
        with st.form("ann_form"):
            title = st.text_input(L("title"))
            content = st.text_area(L("content"))
            priority = st.selectbox(L("priority"), options=PRIORITY_KEYS, format_func=lambda k: L(k))
            if st.form_submit_button(L("save"), type="primary"):
                if title.strip():
                    session.add(Announcement(title=title.strip(), content=content.strip(), priority=priority))
                    session.commit()
                    log_activity(session, admin.username, f"Announcement: {title}")
                    st.success(L("success_add"))
                    st.rerun()

    anns = session.query(Announcement).order_by(Announcement.created_at.desc()).all()
    kind_map = {"normal": "grey", "important": "gold", "urgent": "red"}
    for a in anns:
        cls = "urgent" if a.priority == "urgent" else ""
        st.markdown(f"""
        <div class="camp-card {cls}">
        <h4>{a.title} {badge(L(a.priority), kind_map[a.priority])}</h4>
        <p>{a.content}</p>
        <small>{a.created_at.strftime('%Y-%m-%d %H:%M')}</small>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🗑️ {L('delete')}", key=f"delann_{a.id}"):
            session.delete(a)
            session.commit()
            st.rerun()


def page_camp_info(session, admin):
    flag_header(L("app_name"), L("nav_camp_info"))
    info = get_camp_info(session)
    fields = ["camp_program", "start_date", "end_date", "camp_location", "gather_time",
              "gather_place", "access_instructions", "required_items", "rules",
              "important_info", "contact_numbers"]
    with st.form("camp_info_form"):
        values = {}
        for f in fields:
            values[f] = st.text_area(L(f), value=info.get(f, ""), height=80)
        if st.form_submit_button(L("save"), type="primary", use_container_width=True):
            for f in fields:
                row = session.query(CampInfo).filter(CampInfo.key == f).first()
                if row:
                    row.value = values[f]
                else:
                    session.add(CampInfo(key=f, value=values[f]))
            session.commit()
            log_activity(session, admin.username, "Updated camp info")
            st.success(L("success_update"))
            st.rerun()


def page_admins(session, admin):
    flag_header(L("app_name"), L("nav_admins"))
    if admin.role != "super_admin":
        st.warning(L("invalid_token"))
        return

    with st.expander(f"➕ {L('add_admin')}"):
        with st.form("add_admin_form"):
            uname = st.text_input(L("username"))
            fname = st.text_input(L("full_name"))
            pw = st.text_input(L("password"), type="password")
            role = st.selectbox(L("role"), options=["admin", "super_admin"], format_func=lambda k: L(k))
            if st.form_submit_button(L("save"), type="primary"):
                if session.query(Admin).filter(Admin.username == uname.strip()).first():
                    st.error(L("duplicate_warning"))
                elif uname.strip() and pw.strip():
                    session.add(Admin(username=uname.strip(), password_hash=hash_password(pw),
                                       full_name=fname.strip(), role=role))
                    session.commit()
                    log_activity(session, admin.username, f"Added admin {uname}")
                    st.success(L("success_add"))
                    st.rerun()

    admins = session.query(Admin).all()
    for a in admins:
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"**{a.full_name or a.username}** (@{a.username}) — {badge(L(a.role), 'green' if a.role=='super_admin' else 'grey')}", unsafe_allow_html=True)
        if a.id != admin.id:
            if c2.button(f"🗑️", key=f"deladmin_{a.id}"):
                session.delete(a)
                session.commit()
                log_activity(session, admin.username, f"Deleted admin {a.username}")
                st.rerun()


def page_settings(session, admin):
    flag_header(L("app_name"), L("nav_settings"))
    info = get_camp_info(session)
    with st.form("settings_form"):
        app_url = st.text_input(L("app_url"), value=info.get("app_url", ""),
                                 placeholder="https://your-app.streamlit.app")
        show_rm = st.checkbox(L("show_roommates"), value=info.get("show_roommates_global", "true") == "true")
        if st.form_submit_button(L("save"), type="primary"):
            for k, v in [("app_url", app_url.strip()), ("show_roommates_global", "true" if show_rm else "false")]:
                row = session.query(CampInfo).filter(CampInfo.key == k).first()
                if row:
                    row.value = v
                else:
                    session.add(CampInfo(key=k, value=v))
            session.commit()
            st.success(L("success_update"))
            st.rerun()

    st.divider()
    st.markdown(f"#### {L('backup')}")
    try:
        with open(db.DB_PATH, "rb") as f:
            st.download_button(L("download_backup"), f.read(), "camp_backup.db", use_container_width=True)
    except FileNotFoundError:
        st.info(L("no_results"))


def page_logs(session, admin):
    flag_header(L("app_name"), L("nav_logs"))
    logs = session.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).limit(300).all()
    if not logs:
        st.info(L("no_results"))
    df = pd.DataFrame([{
        L("date"): lg.timestamp.strftime("%Y-%m-%d %H:%M"),
        L("by"): lg.admin_name,
        L("action"): lg.action,
    } for lg in logs])
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_admin_app(admin_id: int):
    session = db.get_session()
    try:
        admin = session.query(Admin).get(admin_id)
        if not admin:
            st.session_state.admin_id = None
            st.rerun()
            return
        render_admin_sidebar(admin)
        nav = st.session_state.nav
        pages = {
            "dashboard": page_dashboard, "participants": page_participants, "rooms": page_rooms,
            "attendance": page_attendance, "payments": page_payments, "transport": page_transport,
            "announcements": page_announcements, "camp_info": page_camp_info,
            "admins": page_admins, "settings": page_settings, "logs": page_logs,
        }
        page_fn = pages.get(nav, page_dashboard)
        page_fn(session, admin)
    finally:
        session.close()


# =================================================================== ROUTER ===
def main():
    qp = st.query_params
    token = qp.get("p")
    if token:
        render_participant_portal(token)
        st.divider()
        if st.button(L("back")):
            st.query_params.clear()
            st.rerun()
        return

    if st.session_state.admin_id:
        render_admin_app(st.session_state.admin_id)
    else:
        render_login()


if __name__ == "__main__":
    main()
