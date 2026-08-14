import os

from dotenv import load_dotenv
from google import genai

from google.genai import types
from pydantic import BaseModel




load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No se encontró GEMINI_API_KEY")


client = genai.Client(api_key=api_key)


def ask_gemini(prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


class ColumnStrategy(BaseModel):
    column: str
    strategy: str


class TableStrategy(BaseModel):
    table: str
    columns: list[ColumnStrategy]


class DatabaseStrategy(BaseModel):
    tables: list[TableStrategy]
    
    
def generate_database_strategy(schema):

    prompt = f"""
Analiza la siguiente estructura de una base de datos PostgreSQL.

Tu tarea es determinar una estrategia apropiada para generar
datos de prueba para cada columna.

Debes respetar:

- claves primarias
- claves foráneas
- restricciones UNIQUE
- columnas NOT NULL
- valores DEFAULT
- columnas IDENTITY
- tipos de datos
- dependencias entre tablas

IMPORTANTE:

No generes todavía los datos.

Solamente indica qué estrategia debería utilizar Python
para generar cada columna.

Utiliza alguna de estas estrategias cuando corresponda:

- unique_identifier
- person_name
- unique_email
- product_name
- positive_integer
- integer
- decimal
- date
- boolean
- foreign_key
- database_generated

Si una columna es una clave foránea, utiliza "foreign_key".

Si una columna es generada automáticamente mediante IDENTITY
o tiene DEFAULT, utiliza "database_generated".

La respuesta debe contener todas las tablas y todas sus columnas.

ESTRUCTURA DE LA BASE:

{schema}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DatabaseStrategy,
        ),
    )

    return response.parsed