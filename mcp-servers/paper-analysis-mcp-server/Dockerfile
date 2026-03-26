FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY mcp-servers/paper-analysis-mcp-server/pyproject.toml mcp-servers/paper-analysis-mcp-server/uv.lock ./

RUN uv sync --frozen --no-install-project

COPY mcp-servers/paper-analysis-mcp-server/ ./
COPY CoScientist/paper_parser /app/server/CoScientist/paper_parser
COPY definitions.py /app/server/.

CMD ["uv", "run", "--no-project", "python", "server/paper_analysis_server.py"]