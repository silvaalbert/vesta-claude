# syntax=docker/dockerfile:1
# ── Stage 1: export pinned requirements ───────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir poetry==2.1.1 poetry-plugin-export

COPY pyproject.toml poetry.lock ./

RUN poetry export \
      --only=main \
      --format=requirements.txt \
      --output=requirements.txt \
      --without-hashes

# ── Stage 2: minimal runtime image ────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

# Install dependencies from the pinned requirements file
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY vesta_claude/ ./vesta_claude/

# Run as non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# The container runs the script and exits
CMD ["python", "-m", "vesta_claude.main"]
