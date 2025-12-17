"""
한국프로세스혁신협회(kpii.or.kr) 스타일 Streamlit 홈페이지 + 사회공헌활동 자동 마이그레이션

실행:
1) pip install -r requirements.txt
2) streamlit run app.py

배포:
- GitHub에 이 폴더를 push 후
- Streamlit Community Cloud에서 새 앱 생성, main file을 app.py로 지정
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import bcrypt
import requests
from bs4 import BeautifulSoup

# ------------------------
# 기본 설정 (SEO용 제목 등)
# ------------------------
st.set_page_config(
    page_title="한국프로세스혁신협회 | KPII",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB_PATH = "kita.db"
CSR_URL = "https://kpii.or.kr/board/%EC%82%AC%ED%9A%8C%EA%B3%B5%ED%97%8C%ED%99%9C%EB%8F%99/4/"  # 사회공헌활동 목록[web:63]


@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# ------------------------
# DB 초기화 + 기본 데이터 + 관리자 + CSR 마이그레이션
# ------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 배너
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS banners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            image_url TEXT,
            link_url TEXT,
            start_date DATE,
            end_date DATE,
            order_index INTEGER DEFAULT 0
        )
        """
    )

    # 게시글
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            board TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            image_url TEXT,
            link_url TEXT,
            start_date DATE,
            end_date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # 관리자 계정 테이블
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )

    # 기본 admin 생성
    cur.execute("SELECT COUNT(*) FROM admin_users WHERE username='admin'")
    if cur.fetchone()[0] == 0:
        raw_pw = "kita_admin_1234"
        pw_hash = bcrypt.hashpw(raw_pw.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            ("admin", pw_hash),
        )

    # 배너 더미 데이터
    cur.execute("SELECT COUNT(*) FROM banners")
    if cur.fetchone()[0] == 0:
        dummy_banners = [
            (
                "프로세스 혁신으로 만드는 더 나은 내일",
                "https://via.placeholder.com/1200x400/004080/FFFFFF?text=한국프로세스혁신협회+배너1",
                "https://kpii.or.kr/",
                "2025-01-01",
                "2026-12-31",
                1,
            ),
            (
                "디지털 전환(DT)·RPA·AI 혁신 세미나",
                "https://via.placeholder.com/1200x400/0066CC/FFFFFF?text=디지털+Insight+세미나",
                "https://event-us.kr/rpamaster/event/111478",
                "2025-01-01",
                "2026-12-31",
                2,
            ),
        ]
        cur.executemany(
            """
            INSERT INTO banners
            (title, image_url, link_url, start_date, end_date, order_index)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            dummy_banners,
        )

    # posts 기본 데이터 (공지/굿모닝/보고서/포토/협회소개/자료실)
    cur.execute("SELECT COUNT(*) FROM posts")
    if cur.fetchone()[0] == 0:
        dummy_posts = [
            # 공지
            (
                "notice",
                "한국프로세스혁신협회 홈페이지 오픈 안내",
                "한국프로세스혁신협회 홈페이지를 방문해주신 여러분 진심으로 환영합니다.",
                None,
                "https://kpii.or.kr/",
                "2025-01-01",
                "2026-12-31",
                None,
            ),
            # 굿모닝
            (
                "goodmorning",
                "굿모닝 KPII - 프로세스 혁신의 시작",
                "일 자체의 혁신, 디지털을 이용한 혁신, 조직 문화의 혁신을 함께 고민합니다.",
                "https://via.placeholder.com/400x250/007BFF/FFFFFF?text=Good+Morning+KPII",
                "https://kpii.or.kr/shopinfo/company.html",
                "2025-12-01",
                None,
                None,
            ),
            # report
            (
                "report",
                "프로세스 혁신 사례집 2025",
                "국내 공공기관과 민간기업의 프로세스 혁신 우수사례를 정리한 보고서입니다.",
                "https://via.placeholder.com/200x150/0056B3/FFFFFF?text=사례집+2025",
                "https://kpii.or.kr/",
                "2025-12-10",
                None,
                None,
            ),
            # photo
            (
                "photo",
                "디지털 Insight 세미나 현장",
                "참석자들과 함께한 네트워킹 및 세션 전경입니다.",
                "https://via.placeholder.com/300x200/003366/FFFFFF?text=세미나+현장",
                "https://event-us.kr/rpamaster/event/111478",
                "2025-09-26",
                None,
                None,
            ),
            # 협회소개 intro
            (
                "intro",
                "협회소개 및 인사말",
                """한국프로세스혁신협회 홈페이지를 방문해주신 여러분 진심으로 환영합니다.

일 자체의 혁신, 디지털을 이용한 혁신, 조직 문화의 혁신 등 모든 업무에 대한 개선과 발전을 주제로,
고착화 된 비효율을 제거하고 프로세스를 개선하는 토론과 공유의 장을 지향합니다.

협회가 조직 경영과 업무 혁신에 도움이 되는 소중한 장이 되기를 바라며 여러분의 믿음직한 동반자가 되도록 최선을 다하겠습니다.

한국프로세스혁신협회 설립자 강 승 원
""",
                None,
                "https://kpii.or.kr/shopinfo/company.html",
                "2025-01-01",
                None,
                None,
            ),
            # 자료실 library (안내용 한 건)
            (
                "library",
                "자료실 안내",
                "프로세스 혁신, 디지털 전환, RPA, AI 관련 자료를 모아 제공합니다.",
                None,
                "https://kpii.or.kr/board/%EC%9E%90%EB%A3%8C%EC%8B%A4/7/",
                "2025-01-01",
                None,
                None,
            ),
        ]
        cur.executemany(
            """
            INSERT INTO posts (board, title, content, image_url, link_url, start_date, end_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            dummy_posts,
        )

    conn.commit()

    # 사회공헌활동(csr) 게시판이 비어있으면 자동 마이그레이션
    cur.execute("SELECT COUNT(*) FROM posts WHERE board='csr'")
    if cur.fetchone()[0] == 0:
        migrate_csr_list(conn)


# ------------------------
# kpii.or.kr 사회공헌활동 목록 크롤링
# ------------------------
def crawl_csr_list():
    """사회공헌활동 목록 페이지에서 제목/링크/작성일 추출."""
    res = requests.get(CSR_URL, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    rows = []
    table = soup.find("table")
    if not table:
        return rows

    tbody = table.find("tbody")
    if not tbody:
        return rows

    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        title_a = tds[1].find("a")
        if not title_a:
            continue
        title = title_a.get_text(strip=True)
        link = title_a["href"]
        if link.startswith("/"):
            link_url = "https://kpii.or.kr" + link
        else:
            link_url = "https://kpii.or.kr/" + link
        writer = tds[2].get_text(strip=True)
        created = tds[3].get_text(strip=True)

        rows.append(
            {
                "title": title,
                "link_url": link_url,
                "writer": writer,
                "created_at": created,
            }
        )
    return rows


def migrate_csr_list(conn):
    """크롤링 결과를 posts(board='csr')에 INSERT."""
    data = crawl_csr_list()
    if not data:
        return

    cur = conn.cursor()
    for item in data:
        cur.execute(
            """
            INSERT INTO posts (board, title, content, image_url, link_url, start_date, end_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "csr",
                item["title"],
                f"작성자: {item['writer']}",
                None,
                item["link_url"],
                item["created_at"][:10],
                None,
                item["created_at"],
            ),
        )
    conn.commit()


# ------------------------
# 공통 쿼리 함수
# ------------------------
def get_banners():
    conn = get_connection()
    today = date.today().isoformat()
    return pd.read_sql_query(
        """
        SELECT * FROM banners
        WHERE start_date <= ?
          AND (end_date >= ? OR end_date IS NULL)
        ORDER BY order_index, id
        """,
        conn,
        params=[today, today],
    )


def get_posts(board: str, limit: int = 5):
    conn = get_connection()
    return pd.read_sql_query(
        """
        SELECT * FROM posts
        WHERE board = ?
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        """,
        conn,
        params=[board, limit],
    )


def insert_banner(title, image_url, link_url, start_date, end_date, order_index):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO banners (title, image_url, link_url, start_date, end_date, order_index)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (title, image_url, link_url, start_date, end_date, order_index),
    )
    conn.commit()


def insert_post(board, title, content, image_url, link_url, start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO posts (board, title, content, image_url, link_url, start_date, end_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (board, title, content, image_url, link_url, start_date, end_date),
    )
    conn.commit()


def verify_admin_password(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM admin_users WHERE username=?", (username,))
    row = cur.fetchone()
    if not row:
        return False
    stored = row[0]
    try:
        return bcrypt.checkpw(password.encode(), stored.encode())
    except Exception:
        return False


# ------------------------
# 세션 상태
# ------------------------
if "banner_index" not in st.session_state:
    st.session_state.banner_index = 0
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "admin_username" not in st.session_state:
    st.session_state.admin_username = None

# DB 초기화
init_db()


# ------------------------
# 레이아웃 함수들
# ------------------------
def render_header():
    st.markdown(
        "<h1 style='margin-bottom:0; color:#003366;'>한국프로세스혁신협회</h1>",
        unsafe_allow_html=True,
    )
    st.caption("일 자체의 혁신 · 디지털 혁신 · 조직 문화 혁신을 함께 만들어갑니다.")
    menu_cols = st.columns([1, 1, 1, 1])
    menu_cols[0].markdown("**협회소개**")
    menu_cols[1].markdown("**사회공헌활동**")
    menu_cols[2].markdown("**자료실·보고서**")
    menu_cols[3].markdown("**회원사·문의**")
    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        q = st.text_input("", placeholder="프로세스 혁신, 무엇이 궁금하세요?", key="search_query")
    with col2:
        if st.button("검색"):
            if q:
                st.write(f"검색어: {q}")

    kws = ["프로세스 혁신", "디지털 전환", "RPA", "AI 업무자동화", "조직문화 혁신"]
    cols = st.columns(len(kws))
    for i, kw in enumerate(kws):
        with cols[i]:
            if st.button(kw):
                st.session_state.search_query = kw
                st.rerun()


def render_icon_menu():
    st.markdown(
        "<div style='background-color:#f5f7fb; padding:16px 8px; border-radius:8px;'>",
        unsafe_allow_html=True,
    )
    items = [
        ("📌 협회 소개", "intro"),
        ("🎓 교육·세미나", "edu"),
        ("📘 자료실·보고서", "docs"),
        ("🤝 사회공헌활동", "csr"),
        ("💡 혁신 사례 공유", "cases"),
        ("📞 문의하기", "contact"),
    ]
    cols = st.columns(len(items))
    for (label, key), col in zip(items, cols):
        with col:
            if st.button(label, key=f"menu_{key}"):
                st.info("해당 메뉴는 준비 중입니다.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_main_area():
    left, right = st.columns([2, 1])

    # 배너
    with left:
        st.subheader("협회 주요 안내")
        banners = get_banners()
        if banners.empty:
            st.info("배너가 없습니다.")
        else:
            idx = st.session_state.banner_index
            idx = max(0, min(idx, len(banners) - 1))
            st.session_state.banner_index = idx
            row = banners.iloc[idx]
            html = f"""
            <div style="text-align:center;">
                <a href="{row['link_url']}" target="_blank" rel="noopener">
                    <img src="{row['image_url']}" 
                         style="width:100%; max-height:400px; object-fit:cover; border-radius:12px;" />
                </a>
                <p style="margin-top:8px; font-weight:bold; font-size:18px; color:#003366;">
                    {row['title']}
                </p>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)  # 신뢰된 관리자만 입력하는 환경 전제

            b1, b2, b3 = st.columns([1, 4, 1])
            with b1:
                if st.button("◀"):
                    st.session_state.banner_index = (idx - 1) % len(banners)
                    st.rerun()
            with b3:
                if st.button("▶"):
                    st.session_state.banner_index = (idx + 1) % len(banners)
                    st.rerun()
            with b2:
                st.caption(f"{idx+1} / {len(banners)}")

    # 공지/뉴스 자리 – 여기서는 공지만
    with right:
        st.subheader("협회 소식")
        notices = get_posts("notice", 5)
        if notices.empty:
            st.write("공지사항이 없습니다.")
        else:
            for _, r in notices.iterrows():
                st.markdown(f"**[{r['title']}]({r['link_url']})**")
                date_text = r["start_date"] or str(r["created_at"])[:10]
                st.caption(f"📅 {date_text}")
                st.write(r["content"][:60] + "..." if r["content"] else "")
                st.markdown("---")


def render_bottom_area():
    c1, c2, c3 = st.columns([1.3, 1.7, 1.2])

    # 굿모닝
    with c1:
        st.subheader("☀️ 굿모닝 KPII")
        df = get_posts("goodmorning", 1)
        if df.empty:
            st.write("굿모닝 콘텐츠가 없습니다.")
        else:
            r = df.iloc[0]
            if r["image_url"]:
                st.image(r["image_url"], use_column_width=True)
            st.markdown(f"**{r['title']}**")
            if r["content"]:
                st.write(r["content"][:80] + "...")
            if r["link_url"]:
                st.markdown(f"[자세히 보기]({r['link_url']})")

    # 보고서
    with c2:
        st.subheader("📊 보고서·자료실")
        df = get_posts("report", 3)
        if df.empty:
            st.write("보고서가 없습니다.")
        else:
            for _, r in df.iterrows():
                ci, ct = st.columns([1, 2])
                with ci:
                    if r["image_url"]:
                        st.image(r["image_url"], use_column_width=True)
                with ct:
                    st.markdown(f"**[{r['title']}]({r['link_url']})**")
                    if r["content"]:
                        st.caption(r["content"][:60] + "...")
                    date_text = r["start_date"] or str(r["created_at"])[:10]
                    st.caption(f"📅 {date_text}")
                st.markdown("---")

    # 포토뉴스
    with c3:
        st.subheader("📸 포토 뉴스")
        df = get_posts("photo", 3)
        if df.empty:
            st.write("포토 뉴스가 없습니다.")
        else:
            for _, r in df.iterrows():
                if r["image_url"]:
                    st.image(
                        r["image_url"],
                        use_column_width=True,
                        caption=f"{r['title']} ({r['start_date'] or str(r['created_at'])[:10]})",
                    )


def render_about_section():
    st.markdown("---")
    st.subheader("협회소개 · 사회공헌활동 · 자료실")

    tab_intro, tab_csr, tab_lib = st.tabs(["협회소개", "사회공헌활동", "자료실"])

    with tab_intro:
        df = get_posts("intro", 3)
        if df.empty:
            st.write("협회소개 내용이 없습니다.")
        else:
            r = df.iloc[0]
            st.markdown(f"### {r['title']}")
            st.write(r["content"])
            if r["link_url"]:
                st.markdown(f"[자세히 보기]({r['link_url']})")

    with tab_csr:
        conn = get_connection()
        # 많으니까 100개까지
        df = pd.read_sql_query(
            "SELECT * FROM posts WHERE board='csr' ORDER BY created_at DESC, id DESC LIMIT 100",
            conn,
        )
        if df.empty:
            st.write("사회공헌활동 게시글이 없습니다.")
        else:
            for _, r in df.iterrows():
                st.markdown(f"**[{r['title']}]({r['link_url']})**")
                date_text = r["start_date"] or str(r["created_at"])[:10]
                st.caption(f"📅 {date_text} | {r['content']}")
                st.markdown("---")

    with tab_lib:
        df = get_posts("library", 20)
        if df.empty:
            st.write("자료실 게시글이 없습니다.")
        else:
            for _, r in df.iterrows():
                st.markdown(f"**[{r['title']}]({r['link_url']})**")
                if r["content"]:
                    st.caption(r["content"][:80] + "...")
                st.markdown("---")


def render_footer():
    st.markdown("---")
    st.caption(
        "서울특별시 (예시 주소) | 대표전화 010-0000-0000 | 사업자등록번호 000-00-00000"
    )
    st.caption("COPYRIGHT © 한국프로세스혁신협회. ALL RIGHTS RESERVED.")


# ------------------------
# 관리자 사이드바
# ------------------------
with st.sidebar:
    st.markdown("### 🔐 관리자")

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
    else:
        st.success(f"관리자 모드 ON ({st.session_state.admin_username})")

        with st.expander("🔑 비밀번호 변경"):
            cur_pw = st.text_input("현재 비밀번호", type="password")
            new_pw = st.text_input("새 비밀번호", type="password")
            new_pw2 = st.text_input("새 비밀번호 확인", type="password")
            if st.button("비밀번호 변경"):
                if new_pw != new_pw2:
                    st.error("새 비밀번호가 일치하지 않습니다.")
                elif not verify_admin_password(
                    st.session_state.admin_username, cur_pw
                ):
                    st.error("현재 비밀번호가 올바르지 않습니다.")
                else:
                    conn = get_connection()
                    cur = conn.cursor()
                    new_hash = bcrypt.hashpw(
                        new_pw.encode(), bcrypt.gensalt()
                    ).decode()
                    cur.execute(
                        "UPDATE admin_users SET password_hash=? WHERE username=?",
                        (new_hash, st.session_state.admin_username),
                    )
                    conn.commit()
                    st.success("비밀번호가 변경되었습니다.")

        st.markdown("#### 📢 배너 등록")
        with st.form("banner_form"):
            b_title = st.text_input("배너 제목")
            b_img = st.text_input("배너 이미지 URL")
            b_link = st.text_input("배너 링크 URL", value="https://kpii.or.kr/")
            b_start = st.date_input("시작일", value=date.today())
            b_end = st.date_input("종료일", value=date(2026, 12, 31))
            b_order = st.number_input("정렬 순서", value=1, step=1)
            if st.form_submit_button("배너 등록"):
                insert_banner(b_title, b_img, b_link, b_start, b_end, int(b_order))
                st.success("배너가 등록되었습니다.")
                st.rerun()

        st.markdown("#### 📝 게시글 수동 등록")
        with st.form("post_form"):
            p_board = st.selectbox(
                "게시판 선택",
                ["notice", "goodmorning", "report", "photo", "intro", "library"],
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

        if st.button("사회공헌활동 목록 다시 가져오기"):
            conn = get_connection()
            migrate_csr_list(conn)
            st.success("사회공헌활동 목록 재마이그레이션 완료")
            st.rerun()


# ------------------------
# 메인 렌더링
# ------------------------
render_header()
render_icon_menu()
render_main_area()
render_bottom_area()
render_about_section()
render_footer()
