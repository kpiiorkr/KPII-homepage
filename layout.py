import streamlit as st
from db import get_banners, get_posts

def inject_global_css():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 메인 컨테이너 폭 / 여백 조정 */
.block-container {
  padding-top: 1.2rem;
  padding-bottom: 2.5rem;
  max-width: 1200px;
}

/* 상단 헤더 그라데이션 배경 */
.header-container {
    background: linear-gradient(90deg, #004080 0%, #0080ff 50%, #4dabff 100%);
    color: #ffffff;
    padding: 18px 28px 14px 28px;
    border-radius: 0 0 16px 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 상단 메뉴 버튼 */
.header-menu button {
    background-color: rgba(255,255,255,0.12) !important;
    color: #ffffff !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    padding: 0.25rem 0.9rem !important;
}
.header-menu button:hover {
    background-color: rgba(255,255,255,0.25) !important;
}

/* 카드형 컨테이너 */
.card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08);
    transition: transform 0.15s ease-out, box-shadow 0.15s ease-out;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.18);
}

/* 배너 dot 인디케이터 */
.banner-dots {
    text-align: center;
    margin-top: 6px;
}
.banner-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    margin: 0 3px;
    border-radius: 50%;
    background-color: #d0d7e2;
}
.banner-dot.active {
    background-color: #004080;
}

/* 섹션 제목/텍스트 */
h2, h3 {
    color: #00254d;
}

/* 섹션 여백 */
section.kpii-section {
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}
hr {
    margin-top: 1.4rem;
    margin-bottom: 1.4rem;
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
<div class="header-container">
  <div style="display:flex; align-items:center; justify-content:space-between;">
    <div>
      <div style="font-size:26px; font-weight:700;">한국프로세스혁신협회 KPII</div>
      <div style="font-size:13px; opacity:0.9;">협회 느낌 + IT/디지털 + 신뢰감을 주는 프로세스 혁신 전문 플랫폼</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # 상단 메뉴 버튼 줄
    menu_cols = st.columns([1, 1, 1, 1])
    with menu_cols[0]:
        if st.button("협회소개"):
            st.session_state.target_section = "intro"
            st.rerun()
    with menu_cols[1]:
        if st.button("사회공헌활동"):
            st.session_state.target_section = "csr"
            st.rerun()
    with menu_cols[2]:
        if st.button("자료실"):
            st.session_state.target_section = "library"
            st.rerun()
    with menu_cols[3]:
        if st.button("회원사"):
            st.session_state.target_section = "members"
            st.rerun()

    # 검색 영역
    col1, col2 = st.columns([3, 1])
    with col1:
        q = st.text_input(
            "",
            placeholder="프로세스 혁신, 무엇이 궁금하세요?",
            key="search_query",
        )
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
    st.markdown("---")
    st.markdown(
        "<div style='background-color:#f8fafc; padding:16px 8px; border-radius:16px;'>",
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
        st.markdown('<section class="kpii-section">', unsafe_allow_html=True)
        st.subheader("협회 주요 안내")
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
                         style="width:100%; max-height:380px; object-fit:cover; border-radius:12px;" />
                </a>
                <p style="margin-top:8px; font-weight:600; font-size:18px; color:#003366;">
                    {row['title']}
                </p>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

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
                dots_html = '<div class="banner-dots">'
                for i in range(len(banners)):
                    cls = "banner-dot active" if i == idx else "banner-dot"
                    dots_html += f'<span class="{cls}"></span>'
                dots_html += "</div>"
                st.markdown(dots_html, unsafe_allow_html=True)
        st.markdown("</div></section>", unsafe_allow_html=True)

    # 공지
    with right:
        st.markdown('<section class="kpii-section">', unsafe_allow_html=True)
        st.subheader("협회 소식")
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown("</div></section>", unsafe_allow_html=True)


def render_bottom_area():
    c1, c2, c3 = st.columns([1.3, 1.7, 1.2])

    # 굿모닝
    with c1:
        st.markdown('<section class="kpii-section">', unsafe_allow_html=True)
        st.subheader("☀️ 굿모닝 KPII")
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown("</div></section>", unsafe_allow_html=True)

    # 보고서
    with c2:
        st.markdown('<section class="kpii-section">', unsafe_allow_html=True)
        st.subheader("📊 보고서·자료실")
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown("</div></section>", unsafe_allow_html=True)

    # 포토 뉴스
    with c3:
        st.markdown('<section class="kpii-section">', unsafe_allow_html=True)
        st.subheader("📸 포토 뉴스")
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown("</div></section>", unsafe_allow_html=True)


def render_about_section():
    st.markdown("---")
    st.subheader("협회소개 · 사회공헌활동 · 자료실 · 회원사")

    tabs = st.tabs(["협회소개", "사회공헌활동", "자료실", "회원사"])
    tab_intro, tab_csr, tab_lib, tab_members = tabs

    with tab_intro:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        df = get_posts("intro", 3)
        if df.empty:
            st.write("협회소개 내용이 없습니다.")
        else:
            r = df.iloc[0]
            st.markdown(f"### {r['title']}")
            st.write(r["content"])
            if r["link_url"]:
                st.markdown(f"[자세히 보기]({r['link_url']})")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_csr:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        df = get_posts("csr", 20)
        if df.empty:
            st.write("사회공헌활동 게시글이 없습니다.")
        else:
            for _, r in df.iterrows():
                st.markdown(
                    f"**[{r['title']}]({r['link_url']})**"
                    if r["link_url"]
                    else f"**{r['title']}**"
                )
                date_text = r["start_date"] or str(r["created_at"])[:10]
                st.caption(f"📅 {date_text}")
                if r["content"]:
                    st.write(r["content"][:120] + "...")
                st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_lib:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        df = get_posts("library", 20)
        if df.empty:
            st.write("자료실 게시글이 없습니다.")
        else:
            for _, r in df.iterrows():
                st.markdown(
                    f"**[{r['title']}]({r['link_url']})**"
                    if r["link_url"]
                    else f"**{r['title']}**"
                )
                if r["content"]:
                    st.caption(r["content"][:100] + "...")
                st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_members:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("회원사 목록 및 소개는 추후 업데이트 예정입니다.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_footer():
    st.markdown("---")
    st.caption(
        "서울특별시 (예시 주소) | 대표전화 010-0000-0000 | 사업자등록번호 000-00-00000"
    )
    st.caption("COPYRIGHT © 한국프로세스혁신협회. ALL RIGHTS RESERVED.")
