FROM python:3.12.12-slim-bookworm
ENV TZ=America/Lima PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends graphviz poppler-utils fonts-dejavu-core xvfb xauth && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.lock /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN playwright install --with-deps chromium && chmod -R a+rX /ms-playwright
RUN useradd --uid 1000 --create-home appuser || true
COPY . /app
USER 1000:1000
CMD ["python", "-m", "sunat.main"]
