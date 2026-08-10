from inspector import get_tables, get_columns

tables = get_tables()

for table in tables:

    print(f"\nTabla: {table}")

    columns = get_columns(table)

    for column in columns:
        print(column)

