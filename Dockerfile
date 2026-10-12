# Railway runs this on a host with a real disk, so unlike the Vercel
# deployment the API here is fully read-write. Stdlib only: no
# requirements.txt needed, pip install resolves zero dependencies.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CARBONSTACK_DB=/data/carbonstack.db \
    PORT=8000

WORKDIR /app

COPY pyproject.toml ./
COPY src/ src/
COPY dashboard/pilot.db dashboard/pilot.db
RUN pip install --no-cache-dir .

EXPOSE 8000

# Seed the volume from the committed demo database on first boot, then serve
# on Railway's $PORT. Explicit flags beat env-aware defaults here so the
# boot path stays visible in one place.
# Shell form deliberately: the trailing exec replaces the shell so python is
# PID 1 and receives SIGTERM directly on redeploy.
CMD mkdir -p "$(dirname "$CARBONSTACK_DB")" && if [ ! -s "$CARBONSTACK_DB" ] && [ -f dashboard/pilot.db ]; then cp dashboard/pilot.db "$CARBONSTACK_DB"; fi && exec python -m carbonstack --db "$CARBONSTACK_DB" serve --host 0.0.0.0 --port "$PORT"
