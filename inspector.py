from db import get_connection


def get_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)

    tables = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return tables


def get_columns(table_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """, (table_name,))

    columns = cursor.fetchall()

    cursor.close()
    conn.close()

    return columns