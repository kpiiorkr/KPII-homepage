"""
KPII homepage – 한국프로세스혁신협회 Streamlit 홈페이지 엔트리

실행:
1) pip install -r requirements.txt
2) streamlit run app.py
"""

import streamlit as st
from db import init_db
from layout import (
    inject_global_css,
    render_header,
    render_icon_menu,
    render_main_area,
    render_bottom_area,
    render_about_section,
    render_footer,
)
from admin import render_admin_sidebar

st.set_page_config(
    page_title="한국프로세스혁신협회 | KPII",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 세션 상태 기본값
if "banner_index" not in st.session_state:
    st.session_state.banner_index = 0
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "admin_username" not in st.session_state:
    st.session_state.admin_username = None
if "target_section" not in st.session_state:
    st.session_state.target_section = None

# DB 초기화
init_db()

# 전역 CSS
inject_global_css()

# 관리자 사이드바
render_admin_sidebar()

# 메인 레이아웃
render_header()
render_icon_menu()
render_main_area()
render_bottom_area()
render_about_section()
render_footer()
