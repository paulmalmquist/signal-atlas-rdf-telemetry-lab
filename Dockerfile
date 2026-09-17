FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home lab
COPY --chown=lab:lab backend backend
COPY --chown=lab:lab frontend frontend
COPY --chown=lab:lab ontology ontology
COPY --chown=lab:lab queries queries
COPY --chown=lab:lab data/raw data/raw
RUN mkdir -p data/generated && chown -R lab:lab data
USER lab
RUN python -m backend.build
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=3)"
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
