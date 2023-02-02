FROM python:3.10

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install --no-cache-dir --upgrade poetry

RUN poetry install

COPY ./sql /app/sql


CMD ["poetry", "run", "uvicorn", "sql.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
