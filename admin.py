import streamlit as st
from datetime import date
from db import (
    verify_admin_password,
    insert_banner,
    get_all_banners,
    delete_banner,
    insert_post,
)


def render_admin_sidebar():
    with st.sidebar:
        st.markdown("### 🔐 관리자")

        # 로그인 전
        if not st.session_state.is_admin:
            username = st.text_input("Admin ID", value="admin")
            pw = st.text_input("비밀번호", type="password")
            if st.button("로그인"):
                if verify_admin_password(username, pw):
                    st.session_state.is_admin = True
                    st.session_state.admin_username = username
                    st.success("관리자 로그인 성공")
                    st.rerun()
                else:
                    st.error("ID 또는 비밀번호가 올바르지 않습니다.")
            return  # 로그인 전이면 아래는 안 보이게

        # 로그인 후
        st.success(f"관리자 모드 ON ({st.session_state.admin_username})")

        # 비밀번호 변경
        with st.expander("🔑 비밀번호 변경"):
            cur_pw = st.text_input("현재 비밀번호", type="password")
            new_pw = st.text_input("새 비밀번호", type="password")
            new_pw2 = st.text_input("새 비밀번호 확인", type="password")
            if st.button("비밀번호 변경"):
                from db import verify_admin_password as _verify  # 순환 import 방지

                if new_pw != new_pw2:
                    st.error("새 비밀번호가 일치하지 않습니다.")
                elif not _verify(st.session_state.admin_username, cur_pw):
                    st.error("현재 비밀번호가 올바르지 않습니다.")
                else:
                    import sqlite3
                    from db import DB_PATH
                    import bcrypt

                    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                    cur = conn.cursor()
                    new_hash = bcrypt.hashpw(
                        new_pw.encode(), bcrypt.gensalt()
                    ).decode()
                    cur.execute(
                        "UPDATE admin_users SET password_hash=? WHERE username=?",
                        (new_hash, st.session_state.admin_username),
                    )
                    conn.commit()
                    conn.close()
                    st.success("비밀번호가 변경되었습니다.")

        # 롤링 배너 등록
        st.markdown("#### 📢 롤링 배너 등록")
        with st.form("banner_form"):
            b_title = st.text_input("배너 제목")
            b_img = st.text_input("배너 이미지 URL")
            b_link = st.text_input("배너 링크 URL", value="https://kpii.or.kr/")
            b_start = st.date_input("시작일", value=date.today())
            b_end = st.date_input("종료일", value=date(2026, 12, 31))
            b_order = st.number_input("노출 순서(작을수록 먼저)", value=1, step=1)
            submitted = st.form_submit_button("배너 등록")
            if submitted:
                insert_banner(b_title, b_img, b_link, b_start, b_end, int(b_order))
                st.success("배너가 등록되었습니다.")
                st.rerun()

        # 배너 목록 + 삭제
        st.markdown("#### 📋 롤링 배너 목록")
        banners_df = get_all_banners()
        if banners_df.empty:
            st.caption("등록된 배너가 없습니다.")
        else:
            for _, b in banners_df.iterrows():
                st.markdown(f"- **{b['title']}** ({b['start_date']} ~ {b['end_date']})")
                st.caption(b["image_url"])
                if st.button("삭제", key=f"del_banner_{b['id']}"):
                    delete_banner(int(b["id"]))
                    st.success("배너를 삭제했습니다.")
                    st.rerun()

        # 게시글 수동 등록
        st.markdown("#### 📝 게시글 수동 등록")
        with st.form("post_form"):
            p_board = st.selectbox(
                "게시판 선택",
                ["notice", "goodmorning", "report", "photo", "intro", "library", "csr"],
            )
            p_title = st.text_input("제목")
            p_content = st.text_area(
                "내용 (HTML 허용, 신뢰된 관리자만 입력하는 환경을 전제로 합니다.)"
            )
            p_img = st.text_input("이미지 URL")
            p_link = st.text_input("링크 URL", value="https://kpii.or.kr/")
            p_start = st.date_input("게시 시작일", value=date.today())
            p_end = st.date_input("게시 종료일", value=date(2026, 12, 31))
            if st.form_submit_button("게시글 등록"):
                insert_post(
                    p_board,
                    p_title,
                    p_content,
                    p_img,
                    p_link,
                    p_start,
                    p_end,
                )
                st.success("게시글이 등록되었습니다.")
                st.rerun()
