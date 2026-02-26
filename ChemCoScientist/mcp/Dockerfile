FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml README.md ./
RUN poetry install --no-interaction --no-ansi --no-root

RUN pip install --no-cache-dir --no-deps git+https://github.com/aimclub/ProtoLLM.git@main

COPY ChemCoScientist/ ChemCoScientist/
COPY CoScientist/ CoScientist/
COPY definitions.py .
COPY config.env .

RUN mkdir -p /app/downloaded_papers

EXPOSE 7331

CMD ["python", "-m", "ChemCoScientist.mcp.papers_search_server"]