FROM python:3.14-trixie

COPY --from=ghcr.io/astral-sh/uv:0.12.24 /uv /uvx /bin/

WORKDIR /usr/src/app

COPY pyproject.toml uv.lock .

ENV UV_NO_DEV=1

RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]
