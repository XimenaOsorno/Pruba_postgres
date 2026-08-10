from db import get_connection


def get_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)

    tables = [row[0] for row in cursor.fetchall()]

    cursor.close()

    return tables


def get_columns(conn, table_name):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
            AND table_name = %s
        ORDER BY ordinal_position;
    """, (table_name,))

    columns = cursor.fetchall()

    cursor.close()

    return columns


def get_primary_keys(conn, table_name):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = 'public'
            AND tc.table_name = %s
        ORDER BY kcu.ordinal_position;
    """, (table_name,))

    primary_keys = [row[0] for row in cursor.fetchall()]

    cursor.close()

    return primary_keys


def get_foreign_keys(conn, table_name):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            AND tc.table_name = %s;
    """, (table_name,))

    foreign_keys = []

    for row in cursor.fetchall():
        foreign_keys.append({
            "column": row[0],
            "references_table": row[1],
            "references_column": row[2]
        })

    cursor.close()

    return foreign_keys


def inspect_database():

    conn = get_connection()

    schema = {}

    try:

        tables = get_tables(conn)

        for table in tables:

            columns = get_columns(conn, table)
            primary_keys = get_primary_keys(conn, table)
            foreign_keys = get_foreign_keys(conn, table)

            schema[table] = {
                "columns": [
                    {
                        "name": name,
                        "type": data_type,
                        "nullable": nullable == "YES"
                    }
                    for name, data_type, nullable in columns
                ],

                "primary_keys": primary_keys,

                "foreign_keys": foreign_keys
            }

    finally:
        conn.close()

    return schema