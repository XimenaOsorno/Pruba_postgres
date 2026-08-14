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
    
    
    
def generate_row(table_strategy):
    row = {}

    for column in table_strategy.columns:

        strategy = column.strategy

        if strategy == "foreign_key":
            #Por ahora no
            continue

        row[column.column] = generate_value(strategy)

    return row

def generate_table_data(table_strategy, amount=10):
    rows = []

    for _ in range(amount):
        row = generate_row(table_strategy)
        rows.append(row)

    return rows