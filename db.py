import sqlite3
import pandas as pd
from datetime import date
import bcrypt
import streamlit as st

DB_PATH = "kita.db"


@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 배너 테이블
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

    # 게시글 테이블
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

    # 관리자 테이블
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )

    # 기본 admin 계정
    cur.execute("SELECT COUNT(*) FROM admin_users WHERE username='admin'")
    if cur.fetchone()[0] == 0:
        raw_pw = "kita_admin_1234"
        pw_hash = bcrypt.hashpw(raw_pw.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            ("admin", pw_hash),
        )

    # 기본 배너
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
            INSERT INTO banners (title, image_url, link_url, start_date, end_date, order_index)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            dummy_banners,
        )

    # 기본 posts
    cur.execute("SELECT COUNT(*) FROM posts")
    if cur.fetchone()[0] == 0:
        dummy_posts = [
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


def get_all_banners():
    conn = get_connection()
    return pd.read_sql_query(
        "SELECT * FROM banners ORDER BY order_index, id", conn
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


def delete_banner(banner_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM banners WHERE id=?", (banner_id,))
    conn.commit()


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
