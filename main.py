from inspector import inspect_database, get_dependencies, get_insertion_order
from gemini_client import generate_database_strategy
from data_generator import  generate_table_data


schema = inspect_database()

print("=== ESQUEMA ===")
print(schema)

print("\n=== DEPENDENCIAS ===")

dependencies = get_dependencies(schema)

for table, deps in dependencies.items():
    print(f"{table} depende de: {deps}")


print("\n=== ORDEN DE INSERCIÓN ===")

order = get_insertion_order(schema)

for position, table in enumerate(order, start=1):
    print(f"{position}. {table}")
    
    
print("\n=== VALORES ÚNICOS ===")
    
for table, info in schema.items():
    print("Unique:")
    print(info["unique_constraints"])
    

print("\n=== ESTRATEGIA DE IA ===")

strategy = generate_database_strategy(schema)

print(strategy)



print("\n=== DATOS GENERADOS ===")

generated_data = {}

for table in strategy.tables:

    print(f"\nTabla: {table.table}")

    rows = generate_table_data(
        table,
        schema,
        generated_data,
        amount=3
    )

    generated_data[table.table] = rows

    for row in rows:
        print(row)