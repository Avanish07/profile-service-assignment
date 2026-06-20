# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Create a venv we can copy later
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------- Stage 2: final ----------
FROM python:3.12-slim

WORKDIR /app

# Copy the ready-made venv from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app ./app

RUN useradd --create-home --uid 10001 appuser \
    && mkdir /data \
    && chown appuser:appuser /data

USER appuser

ENV DATABASE_URL=sqlite:////data/profiles.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]