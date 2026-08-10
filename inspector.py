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
            unique_constraints = get_unique_constraints(conn, table)

            
            
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

    "foreign_keys": foreign_keys,

    "unique_constraints": unique_constraints
}

    finally:
        conn.close()

    return schema

def get_dependencies(schema):
    dependencies = {}

    for table, info in schema.items():

        dependencies[table] = []

        for foreign_key in info["foreign_keys"]:

            referenced_table = foreign_key["references_table"]

            if referenced_table not in dependencies[table]:
                dependencies[table].append(referenced_table)

    return dependencies


def get_insertion_order(schema):

    dependencies = get_dependencies(schema)

    order = []

    while dependencies:

        # Buscar tablas que ya no tengan dependencias
        available_tables = [
            table
            for table, deps in dependencies.items()
            if not deps
        ]

        if not available_tables:
            raise ValueError(
                "No se puede determinar el orden. "
                "Puede existir una dependencia circular."
            )

        # Agregar las tablas disponibles al orden
        for table in available_tables:
            order.append(table)

        # Eliminar esas tablas
        for table in available_tables:
            del dependencies[table]

        # Eliminar esas tablas de las dependencias restantes
        for deps in dependencies.values():
            for table in available_tables:
                if table in deps:
                    deps.remove(table)

    return order

def get_unique_constraints(conn, table_name):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            tc.constraint_name,
            kcu.column_name,
            kcu.ordinal_position
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
            AND tc.table_name = kcu.table_name
        WHERE tc.constraint_type = 'UNIQUE'
            AND tc.table_schema = 'public'
            AND tc.table_name = %s
        ORDER BY tc.constraint_name, kcu.ordinal_position;
    """, (table_name,))

    rows = cursor.fetchall()

    cursor.close()

    unique_constraints = {}

    for constraint_name, column_name, position in rows:

        if constraint_name not in unique_constraints:
            unique_constraints[constraint_name] = []

        unique_constraints[constraint_name].append(column_name)

    return [
        {
            "constraint": constraint_name,
            "columns": columns
        }
        for constraint_name, columns in unique_constraints.items()
    ]