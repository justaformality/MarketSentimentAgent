import sqlite3
from datetime import datetime

import pandas as pd


DB_NAME = "market_sentiment.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oidc_subject TEXT NOT NULL UNIQUE,
            name TEXT,
            email TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            ticker TEXT,
            company_name TEXT,
            price_change REAL,
            avg_sentiment REAL,
            signal TEXT,
            ai_summary TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        PRAGMA table_info(analysis_history)
    """)

    existing_columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "user_id" not in existing_columns:
        cursor.execute("""
            ALTER TABLE analysis_history
            ADD COLUMN user_id INTEGER
        """)

    conn.commit()
    conn.close()


def get_or_create_user(
    oidc_subject,
    name,
    email
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM users
        WHERE oidc_subject = ?
    """, (oidc_subject,))

    user = cursor.fetchone()

    if user:
        user_id = user[0]

        cursor.execute("""
            UPDATE users
            SET name = ?,
                email = ?
            WHERE id = ?
        """, (
            name,
            email,
            user_id
        ))

        conn.commit()
        conn.close()

        return user_id

    cursor.execute("""
        INSERT INTO users (
            oidc_subject,
            name,
            email,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        oidc_subject,
        name,
        email,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return user_id


def save_analysis(
    user_id,
    ticker,
    company_name,
    price_change,
    avg_sentiment,
    signal,
    ai_summary=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis_history (
            user_id,
            timestamp,
            ticker,
            company_name,
            price_change,
            avg_sentiment,
            signal,
            ai_summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        ticker.upper(),
        company_name,
        price_change,
        avg_sentiment,
        signal,
        ai_summary
    ))

    conn.commit()
    conn.close()


def get_history(
    user_id,
    ticker=None
):
    conn = get_connection()

    if ticker:
        query = """
            SELECT
                id,
                timestamp,
                ticker,
                company_name,
                price_change,
                avg_sentiment,
                signal,
                ai_summary
            FROM analysis_history
            WHERE user_id = ?
            AND ticker = ?
            ORDER BY timestamp ASC
        """

        df = pd.read_sql_query(
            query,
            conn,
            params=(
                user_id,
                ticker.upper()
            )
        )

    else:
        query = """
            SELECT
                id,
                timestamp,
                ticker,
                company_name,
                price_change,
                avg_sentiment,
                signal,
                ai_summary
            FROM analysis_history
            WHERE user_id = ?
            ORDER BY timestamp ASC
        """

        df = pd.read_sql_query(
            query,
            conn,
            params=(user_id,)
        )

    conn.close()

    return df