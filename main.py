from inspector import inspect_database, get_dependencies, get_insertion_order


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