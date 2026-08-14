from faker import Faker

fake = Faker()


def generate_value(strategy):
    if strategy == "unique_identifier":
        return fake.uuid4()

    elif strategy == "person_name":
        return fake.name()

    elif strategy == "unique_email":
        return fake.unique.email()

    elif strategy == "product_name":
        return fake.catch_phrase()

    elif strategy == "positive_integer":
        return fake.random_int(min=1, max=1000)

    elif strategy == "integer":
        return fake.random_int(min=-1000, max=1000)

    else:
        raise ValueError(f"Estrategia desconocida: {strategy}")
    
    
    
def generate_row(table_strategy, schema, generated_data):

    row = {}

    table_name = table_strategy.table

    for column in table_strategy.columns:

        strategy = column.strategy

        if strategy == "foreign_key":

            row[column.column] = generate_foreign_key_value(
                table_name,
                column.column,
                schema,
                generated_data
            )

        else:

            row[column.column] = generate_value(strategy)

    return row

def generate_table_data(
    table_strategy,
    schema,
    generated_data,
    amount=10
):

    rows = []

    for _ in range(amount):

        row = generate_row(
            table_strategy,
            schema,
            generated_data
        )

        rows.append(row)

    return rows




def generate_foreign_key_value(
    table_name,
    column_name,
    schema,
    generated_data
):
    table_info = schema[table_name]

    for foreign_key in table_info["foreign_keys"]:

        if foreign_key["column"] == column_name:

            referenced_table = foreign_key["references_table"]
            referenced_column = foreign_key["references_column"]

            if referenced_table not in generated_data:
                raise ValueError(
                    f"No existen datos generados para "
                    f"{referenced_table}"
                )

            values = [
                row[referenced_column]
                for row in generated_data[referenced_table]
            ]

            if not values:
                raise ValueError(
                    f"La tabla {referenced_table} "
                    f"no tiene valores disponibles"
                )

            return fake.random_element(values)

    raise ValueError(
        f"No se encontró información de FK para "
        f"{table_name}.{column_name}"
    )